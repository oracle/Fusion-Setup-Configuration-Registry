#!/usr/bin/env python3
"""Prepare a registered Fusion HCM, SCM, or ERP file and initiate IMPORT_AND_LOAD."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import re
import sys
import urllib.parse
import uuid
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterable, NamedTuple

try:
    from cx_import_integrity import cx_import_group_bytes
    import data_loader_report
    import data_loader_metadata as metadata
    import xlsx_sample_workbook
except ModuleNotFoundError:  # Imported by tests from the skill root.
    from scripts.cx_import_integrity import cx_import_group_bytes
    from scripts import data_loader_report
    from scripts import data_loader_metadata as metadata
    from scripts import xlsx_sample_workbook

MEDIA_TYPE = "application/vnd.oracle.adf.action+json"
DOCUMENT_UPLOAD_PATH = "/documents/files/data"
INITIATE_PATH = "/hcmRestApi/resources/latest/dataLoaderDataSets/action/initiateDataLoad"
DATA_LOADER_DATA_SETS_DESCRIBE_PATH = "/hcmRestApi/resources/latest/dataLoaderDataSets/describe"
BUSINESS_OBJECTS_PATH = metadata.BUSINESS_OBJECTS_PATH
FBDI_ACTION_RESOURCE_PATH = metadata.FSCR_BUSINESS_OBJECTS_PATH
FBDI_FILENAME_ACTION = "findFbdiObjectsByFileName"
DEFAULT_CONFIG = metadata.DEFAULT_CONFIG
DEFAULT_RUN_CONFIG = metadata.DEFAULT_RUN_CONFIG
FDOS_ROOT = metadata.FDOS_ROOT
PROJECT_REVIEW_ARCHIVE_DIRECTORY = Path("artifacts/core/data-loader/current/mapping-reviews")
INITIALIZED_PROJECT_STATUSES = frozenset({"initialized", "in_progress", "blocked", "ready_for_review"})
REST_FRAMEWORK_VERSION_HEADER = metadata.REST_FRAMEWORK_VERSION_HEADER
REST_FRAMEWORK_VERSION = metadata.REST_FRAMEWORK_VERSION
SUPPORTED_SUFFIXES = frozenset({".zip", ".dat", ".txt", ".csv", ".xlsx"})
MULTI_SOURCE_ARCHIVE_NAME = "combined-data-load.zip"
MAX_ARCHIVE_FILENAME_LENGTH = 49
UCM_ARCHIVE_TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"
PREFLIGHT_ENVELOPE_SCHEMA_VERSION = "1.0"
UCM_DOCUMENT_ACCOUNT = "hcm$/dataloader$/import$"
FSM_UCM_DOCUMENT_ACCOUNT = "setup$/functionalSetupManager$/import$"
FSM_METADATA_MEMBER_NAME = "ASM_SETUP_CSV_METADATA.xml"
FSM_SOURCE_TYPE = "FSM"
FBDI_SOURCE_TYPE = "FBDI"
CX_IMPORT_SOURCE_TYPE = "ORA_CX_IMPORT"
CX_SECURITY_GROUP = "CRM"
CX_MAPPING_INITIATION_PREFIX = "M_"
CX_OBJECT_METADATA_PATH = "/crmRestApi/resources/11.13.18.05/objectMetadata/"
CX_MAPPING_METADATA_HEADER = (
    "map name",
    "map description",
    "import object",
    "object display name",
)
CX_MAPPING_COLUMNS_HEADER = (
    "column header",
    "target attribute code",
    "target attribute display name",
    "source attribute code",
)
IGNORED_MACOS_ARCHIVE_DIRECTORIES = frozenset({"_macosx", "__macosx"})
DataLoadError = metadata.DataLoadError
read_config = metadata.read_config
get_json = metadata.get_json


class PreparedArchive(NamedTuple):
    file_name: str
    content: bytes


class CxImportFile(NamedTuple):
    member_name: str
    file_name: str
    content: bytes
    is_mapping: bool


class FbdiRoute(NamedTuple):
    business_object: str
    ucm_account: str
    matched_files: tuple[str, ...]
    load_adapter_interface_id: Any


class FbdiRoutingEntry(NamedTuple):
    business_object: str
    ucm_account: Any
    prefixes: tuple[str, ...]
    load_adapter_interface_id: Any


def archive_sha256(content: bytes) -> str:
    """Return the immutable digest presented for a prepared upload archive."""
    return hashlib.sha256(content).hexdigest()


def _safe_archive_name_part(value: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip())
    return normalized.strip(".-_")


def timestamped_archive_name(source_name: str, *, now: datetime | None = None) -> str:
    """Return the UCM ZIP name, preserving the source stem and adding local time."""
    basename = Path(source_name).name
    stem = basename[:-4] if basename.casefold().endswith(".zip") else Path(basename).stem
    if not stem:
        raise DataLoadError("archive-preparation", "Source filename does not provide a ZIP name.")
    timestamp = (now or datetime.now()).strftime(UCM_ARCHIVE_TIMESTAMP_FORMAT)
    return f"{stem}_{timestamp}.zip"


def _root_record_details(content: bytes, discriminator: str) -> tuple[dict[str, str], int]:
    """Read the first root MERGE row and its count from a prepared DAT member."""
    try:
        lines = content.decode("utf-8").splitlines()
    except UnicodeDecodeError:
        return {}, 0
    headers: tuple[str, ...] = ()
    first_values: tuple[str, ...] | None = None
    count = 0
    for line in lines:
        values = line.split("|")
        if len(values) < 2 or values[1] != discriminator:
            continue
        if values[0] == "METADATA":
            headers = tuple(values[2:])
        elif values[0] == "MERGE":
            count += 1
            if first_values is None:
                first_values = tuple(values[2:])
    if first_values is None:
        return {}, count
    return dict(zip(headers, first_values)), count


def semantic_archive_name(
    schemas: Iterable[metadata.BusinessObjectSchema], members: Iterable[tuple[str, bytes]]
) -> str:
    """Build a short, deterministic archive name from validated root user keys."""
    member_content = dict(members)
    segments: list[str] = []
    row_suffixes: list[str] = []
    fallback_material: list[bytes] = []
    for schema in schemas:
        member_name = schema.discriminator + ".dat"
        content = member_content.get(member_name, b"")
        if not content:
            content = next(
                (
                    candidate
                    for candidate in member_content.values()
                    if _root_record_details(candidate, schema.discriminator)[1]
                ),
                b"",
            )
        values, row_count = _root_record_details(content, schema.discriminator)
        user_keys: list[str] = []
        for attribute in schema.attributes.get(schema.discriminator, ()):
            for name in metadata.user_key_attribute_names(attribute):
                if name not in user_keys:
                    user_keys.append(name)
        key_values = [_safe_archive_name_part(values.get(key, "")) for key in user_keys]
        key_values = [value for value in key_values if value]
        segment = _safe_archive_name_part(schema.discriminator)
        if key_values:
            segment += "-" + "-".join(key_values)
        if row_count > 1:
            row_suffixes.append(f"{row_count}rows")
        segments.append(segment)
        fallback_material.extend((member_name.encode("utf-8"), content))
    stem = "-".join(segment for segment in segments if segment)
    if not stem or all("-" not in segment for segment in segments):
        digest = hashlib.sha256(b"\0".join(fallback_material)).hexdigest()[:8]
        stem = ("-".join(segments) or "data-load") + "-" + digest
    limit = MAX_ARCHIVE_FILENAME_LENGTH - len(".zip")
    suffix = ("-" + "-".join(row_suffixes)) if row_suffixes else ""
    stem_limit = max(1, limit - len(suffix))
    return stem[:stem_limit].rstrip(".-_") + suffix + ".zip"


def project_review_archive_directory(project_root: Path) -> Path:
    """Return the durable review-archive location for one initialized project."""
    try:
        resolved = project_root.resolve(strict=True)
    except OSError as error:
        raise DataLoadError("artifact-persistence", f"Project root is not available: {project_root}") from error
    projects_root = (FDOS_ROOT / "project").resolve()
    try:
        state = json.loads(
            (resolved / "state" / "project-state.json").read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError):
        state = None
    if (
        resolved.parent != projects_root
        or not isinstance(state, dict)
        or state.get("status") not in INITIALIZED_PROJECT_STATUSES
    ):
        raise DataLoadError(
            "artifact-persistence",
            "--project-root must identify an initialized project/<project_id> workspace.",
        )
    directory = resolved / PROJECT_REVIEW_ARCHIVE_DIRECTORY
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    return directory


def explicit_review_output_directory(output_dir: Path) -> Path:
    """Create and return an explicitly requested writable review directory."""
    try:
        output_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        resolved = output_dir.resolve(strict=True)
    except OSError as error:
        raise DataLoadError(
            "artifact-persistence",
            f"Review output directory is not available: {output_dir}",
        ) from error
    if not resolved.is_dir():
        raise DataLoadError(
            "artifact-persistence",
            f"Review output directory is not a directory: {output_dir}",
        )
    return resolved


def persist_prepared_archive(
    prepared: PreparedArchive,
    directory: Path,
    *,
    project_review_directory: Path | None = None,
) -> Path:
    """Atomically publish a ZIP only after its bytes pass a local integrity check."""
    if not zipfile.is_zipfile(io.BytesIO(prepared.content)):
        raise DataLoadError("archive-preparation", "Prepared archive is not ZIP-valid.")
    output_path = directory / prepared.file_name
    temporary_path = output_path.with_name(output_path.name + ".tmp")
    try:
        temporary_path.write_bytes(prepared.content)
        os.replace(temporary_path, output_path)
    except OSError as source_error:
        if project_review_directory is None:
            raise DataLoadError(
                "artifact-persistence",
                "Unable to save the validated ZIP beside the source. Supply --review-output-dir "
                "or --project-root to store its validated archive elsewhere.",
            ) from source_error
        output_path = project_review_directory / prepared.file_name
        output_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        temporary_path = output_path.with_name(output_path.name + ".tmp")
        try:
            temporary_path.write_bytes(prepared.content)
            os.chmod(temporary_path, 0o600)
            os.replace(temporary_path, output_path)
        except OSError as exc:
            raise DataLoadError("artifact-persistence", f"Unable to save validated ZIP: {output_path}: {exc}") from exc
    return output_path.resolve()


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def build_preflight_envelope(preflight: dict[str, Any]) -> dict[str, Any]:
    """Bind validated routing metadata to one immutable upload artifact."""
    payload = {
        "schemaVersion": PREFLIGHT_ENVELOPE_SCHEMA_VERSION,
        "preflight": preflight,
    }
    payload["fingerprint"] = hashlib.sha256(_canonical_json(payload)).hexdigest()
    return payload


def persist_preflight_envelope(preflight: dict[str, Any], output_path: Path) -> Path:
    """Atomically persist an internal approval envelope with restrictive permissions."""
    envelope = build_preflight_envelope(preflight)
    try:
        output_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        resolved = output_path.resolve()
        temporary = resolved.with_name(resolved.name + ".tmp")
        temporary.write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")
        os.chmod(temporary, 0o600)
        os.replace(temporary, resolved)
    except OSError as error:
        raise DataLoadError(
            "artifact-persistence",
            f"Unable to save the internal preflight envelope: {output_path}",
        ) from error
    return resolved


def load_preflight_envelope(path: Path) -> dict[str, Any]:
    """Load and strictly verify one internally persisted preflight envelope."""
    try:
        envelope = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise DataLoadError("approval", f"Approved preflight envelope is unreadable: {path}") from error
    if not isinstance(envelope, dict):
        raise DataLoadError("approval", "Approved preflight envelope must be a JSON object.")
    if envelope.get("schemaVersion") != PREFLIGHT_ENVELOPE_SCHEMA_VERSION:
        raise DataLoadError("approval", "Approved preflight envelope has an unsupported schema version.")
    supplied_fingerprint = envelope.get("fingerprint")
    unsigned = {key: value for key, value in envelope.items() if key != "fingerprint"}
    expected_fingerprint = hashlib.sha256(_canonical_json(unsigned)).hexdigest()
    if not isinstance(supplied_fingerprint, str) or supplied_fingerprint.casefold() != expected_fingerprint:
        raise DataLoadError("approval", "Approved preflight envelope integrity verification failed.")
    preflight = envelope.get("preflight")
    if not isinstance(preflight, dict):
        raise DataLoadError("approval", "Approved preflight envelope is missing preflight metadata.")
    return preflight


def require_matching_review_archive(
    prepared: PreparedArchive,
    directory: Path,
    *,
    project_review_directory: Path | None = None,
) -> None:
    """Require that approval still covers the exact locally reviewed ZIP bytes."""
    review_path = directory / prepared.file_name
    try:
        reviewed_content = review_path.read_bytes()
    except OSError as exc:
        if project_review_directory is None:
            raise DataLoadError(
                "approval",
                "No matching validated ZIP is available for this approval. Validate the "
                "source again or supply the original review output directory.",
            ) from exc
        review_path = project_review_directory / prepared.file_name
        try:
            reviewed_content = review_path.read_bytes()
        except OSError as fallback_exc:
            raise DataLoadError(
                "approval",
                "No matching validated ZIP is available for this approval. Validate the "
                "source again or supply the original review output directory.",
            ) from fallback_exc
    if reviewed_content != prepared.content:
        raise DataLoadError(
            "approval",
            "The source no longer matches the reviewed ZIP. Validate and approve the current source again before upload.",
        )


class ValidationProgress(NamedTuple):
    event: str
    source_index: int
    source_total: int
    source_name: str
    business_object: str | None
    checkpoint_index: int | None
    checkpoint_total: int


ProgressCallback = Callable[[ValidationProgress], None]


def _approval_required_after_preflight(
    _url: str,
    _payload: dict[str, Any],
    _auth: Any,
    *,
    stage: str,
) -> dict[str, Any]:
    """Stop immediately before the first mutation after read-only validation."""
    raise DataLoadError(
        "approval",
        "Source validation succeeded. No data was uploaded. "
        "Review the prepared source, then approve upload and initiation.",
        response={"preflight": {"stage": stage}},
    )


_approval_required_after_preflight.preflight_only = True


def _raise_preflight_approval_required(
    eligible: list[dict[str, str]],
    prepared: PreparedArchive,
    source_paths: Iterable[Path],
    *,
    column_mappings: Iterable[metadata.ColumnMapping] = (),
    source_type: str | None = None,
    cx_files: Iterable[CxImportFile] = (),
    cx_import_object_code: str | None = None,
    cx_ucm_account: str | None = None,
    cx_import_high_volume_load: bool = False,
    fbdi_route: FbdiRoute | None = None,
    mapping_complete: bool = True,
    upload_file_name: str,
    environment: str,
    host: str,
    run_id: str | None,
    task_routed: bool,
    supports_run_book_task_code: bool,
    display_archive_name: str | None = None,
) -> None:
    """Return a reviewable archive and stop before the first live mutation."""
    paths = tuple(source_paths)
    error = DataLoadError(
        "approval",
        "Source validation succeeded for the eligible sources. No data was uploaded.",
        response={
            "preflight": {
                "eligible": eligible,
                "sourcePaths": [str(path.resolve()) for path in paths],
                "archiveName": display_archive_name or prepared.file_name,
                "archiveSha256": archive_sha256(prepared.content),
                "uploadFileName": upload_file_name,
                "environment": environment,
                "host": host,
                "runID": run_id,
                "taskRouted": task_routed,
                "supportsRunBookTaskCode": supports_run_book_task_code,
                "columnMappings": [mapping.__dict__ for mapping in column_mappings],
                "mappingComplete": mapping_complete,
                "sourceType": source_type,
                "cxImportObjectCode": cx_import_object_code,
                "cxUcmAccount": cx_ucm_account,
                "cxImportHighVolumeLoad": cx_import_high_volume_load,
                "fbdiBusinessObject": fbdi_route.business_object if fbdi_route else None,
                "fbdiUcmAccount": fbdi_route.ucm_account if fbdi_route else None,
                "fbdiFiles": list(fbdi_route.matched_files) if fbdi_route else [],
                "fbdiLoadAdapterInterfaceId": (
                    fbdi_route.load_adapter_interface_id if fbdi_route else None
                ),
                "cxFiles": [
                    {
                        "fileName": file.file_name,
                        "memberName": file.member_name,
                        "role": "Mapping" if file.is_mapping else "Data",
                    }
                    for file in cx_files
                ],
            }
        },
    )
    error.prepared_archive = prepared
    error.archive_directory = paths[0].parent
    raise error


def _notify_progress(
    progress: ProgressCallback | None,
    event: str,
    *,
    source_path: Path,
    source_index: int,
    source_total: int,
    business_object: str | None = None,
    checkpoint_index: int | None = None,
) -> None:
    if progress is None:
        return
    progress(
        ValidationProgress(
            event,
            source_index,
            source_total,
            source_path.name,
            business_object,
            checkpoint_index,
            4,
        )
    )


def _validation_progress_text(event: ValidationProgress) -> str | None:
    if event.event == "workbook_started":
        return (
            f"Validating workbook {event.source_index} of {event.source_total}: "
            f"{event.source_name}"
        )
    if event.event == "business_object_resolved":
        return (
            f"1/{event.checkpoint_total} Business object resolved: "
            f"{event.business_object}"
        )
    if event.event == "template_headers_validated":
        return (
            f"2/{event.checkpoint_total} Live case-sensitive template, sheets, "
            "and headers matched"
        )
    if event.event == "sections_keys_validated":
        return (
            f"3/{event.checkpoint_total} Parent/child sections and live key "
            "metadata validated"
        )
    if event.event == "dat_conversion_completed":
        return (
            f"4/{event.checkpoint_total} Converted in memory: "
            f"{event.business_object}.dat"
        )
    if event.event == "workbook_failed":
        return (
            f"Validation failed for workbook {event.source_index} of "
            f"{event.source_total} at checkpoint {event.checkpoint_index}/"
            f"{event.checkpoint_total}: {event.source_name}"
        )
    return None


def cli_validation_progress_reporter(stream: Any) -> ProgressCallback:
    def report(event: ValidationProgress) -> None:
        rendered = _validation_progress_text(event)
        if rendered is not None:
            print(rendered, file=stream, flush=True)

    return report


def select_source(
    explicit_path: str | None, ide_files: Iterable[str] = ()
) -> Path:
    sources = select_sources(explicit_path, ide_files)
    if len(sources) > 1:
        names = ", ".join(str(source) for source in sources)
        raise DataLoadError(
            "source-selection",
            f"Multiple supported data files are available; choose one explicitly: {names}",
        )
    return sources[0]


def select_sources(
    explicit_path: str | None, ide_files: Iterable[str] = (), *, cx_import: bool = False
) -> tuple[Path, ...]:
    if explicit_path:
        return (Path(explicit_path).expanduser(),)

    candidates = [
        Path(candidate).expanduser()
        for candidate in ide_files
        if Path(candidate).suffix.lower() in SUPPORTED_SUFFIXES
    ]
    if not candidates:
        raise DataLoadError(
            "source-selection",
            "No supported .zip, .dat, .txt, .csv, or .xlsx file was supplied or found in the shared IDE context.",
        )
    suffixes = {candidate.suffix.lower() for candidate in candidates}
    fsm_paths = tuple(
        candidate
        for candidate in candidates
        if candidate.suffix.lower() == ".zip" and _is_fsm_zip(candidate)
    )
    non_fsm_paths = tuple(candidate for candidate in candidates if candidate not in fsm_paths)
    non_fsm_suffixes = {candidate.suffix.lower() for candidate in non_fsm_paths}
    supported_separate_loads = bool(fsm_paths) and (
        not non_fsm_paths or non_fsm_suffixes in ({".dat"}, {".xlsx"})
    )
    direct_cx_csvs = cx_import and suffixes == {".csv"}
    if len(candidates) > 1 and suffixes not in ({".dat"}, {".xlsx"}) and not supported_separate_loads and not direct_cx_csvs:
        names = ", ".join(str(candidate) for candidate in candidates)
        raise DataLoadError(
            "source-selection",
            "Multiple supplied files can be combined only when every file is a .dat file "
            "or every file is an .xlsx file. FSM ZIP files may be submitted as "
            "separate loads alongside one homogeneous .dat or .xlsx group; "
            f"choose one explicitly: {names}",
        )
    return tuple(candidates)


def _validate_source_path(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        raise DataLoadError(
            "file-validation",
            f"Source file must have a .zip, .dat, .txt, or .csv extension or an .xlsx extension: {path}",
        )
    if not path.exists():
        raise DataLoadError("file-validation", f"Source file does not exist: {path}")
    if not path.is_file():
        raise DataLoadError("file-validation", f"Source path is not a regular file: {path}")
    return suffix


def _read_nonempty_file(path: Path) -> bytes:
    try:
        content = path.read_bytes()
    except OSError as exc:
        raise DataLoadError("file-validation", f"Unable to read source file: {path}: {exc}") from exc
    if not content:
        raise DataLoadError("file-validation", f"Source file is empty: {path}")
    return content


def _validate_utf8(content: bytes, path: Path) -> None:
    try:
        content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise DataLoadError(
            "file-validation", f"Source file must contain valid UTF-8 text: {path}"
        ) from exc


def _validate_dat_field(value: str, *, location: str) -> None:
    if "\r" in value or "\n" in value:
        raise DataLoadError(
            "file-validation",
            f"CSV {location} contains a line break that cannot be represented in the generated DAT file.",
        )


def _parse_and_validate_csv(path: Path, content: bytes) -> list[list[str]]:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise DataLoadError(
            "file-validation", f"CSV file must contain valid UTF-8 text: {path}"
        ) from exc

    try:
        rows = list(csv.reader(io.StringIO(text, newline=""), strict=True))
    except csv.Error as exc:
        raise DataLoadError("file-validation", f"Unable to parse CSV file {path}: {exc}") from exc

    while rows and (not rows[-1] or all(value == "" for value in rows[-1])):
        rows.pop()
    if not rows or not rows[0]:
        raise DataLoadError("file-validation", f"CSV header row was not found: {path}")

    header = rows[0]

    data_row_count = 0
    for row_number, row in enumerate(rows[1:], start=2):
        if not row or all(value == "" for value in row):
            continue
        if len(row) > len(header):
            raise DataLoadError(
                "file-validation",
                f"CSV row {row_number} has more values than headers: {path}",
            )
        values = row + [""] * (len(header) - len(row))
        for column_number, value in enumerate(values, start=1):
            _validate_dat_field(value, location=f"row {row_number}, column {column_number}")
        rows[row_number - 1] = values
        data_row_count += 1

    if data_row_count == 0:
        raise DataLoadError(
            "file-validation", f"CSV file must include at least one data row: {path}"
        )
    return rows


def _csv_to_dat(
    path: Path,
    content: bytes,
    *,
    discriminator: str | None = None,
    mapped_header: tuple[str, ...] | None = None,
    retained_indexes: tuple[int, ...] | None = None,
) -> bytes:
    rows = _parse_and_validate_csv(path, content)
    discriminator = discriminator or path.stem
    if not discriminator:
        raise DataLoadError(
            "file-validation", f"CSV filename does not provide a business-object discriminator: {path}"
        )

    header = list(mapped_header or rows[0])
    indexes = retained_indexes or tuple(range(len(rows[0])))
    dat_lines = ["METADATA|" + discriminator + "|" + "|".join(header)]
    for row in rows[1:]:
        if not row or all(value == "" for value in row):
            continue
        dat_lines.append(
            "MERGE|"
            + discriminator
            + "|"
            + "|".join(
                xlsx_sample_workbook.escape_dat_value(row[index]) for index in indexes
            )
        )
    return "\n".join(dat_lines).encode("utf-8")


def _create_zip(members: Iterable[tuple[str, bytes]]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for member_name, content in members:
            member = zipfile.ZipInfo(member_name, date_time=(1980, 1, 1, 0, 0, 0))
            member.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(member, content)
    return buffer.getvalue()


def prepare_archive(
    path: Path,
    *,
    xlsx_member_discriminator: str | None = None,
    csv_member_discriminator: str | None = None,
    schema: metadata.BusinessObjectSchema | None = None,
    converted_content: bytes | None = None,
) -> PreparedArchive:
    suffix = _validate_source_path(path)
    content = _read_nonempty_file(path)

    if suffix == ".zip":
        if not zipfile.is_zipfile(io.BytesIO(content)):
            raise DataLoadError(
                "file-validation", f"Source file is not a valid ZIP archive: {path}"
            )
        return PreparedArchive(file_name=path.name, content=content)

    if suffix == ".csv":
        discriminator = csv_member_discriminator or path.stem
        dat_content = converted_content or _csv_to_dat(path, content, discriminator=discriminator)
        member_name = discriminator + ".dat"
    elif suffix == ".xlsx":
        if not xlsx_member_discriminator:
            raise DataLoadError(
                "archive-preparation",
                "XLSX archive preparation requires the validated top-level business-object discriminator.",
            )
        dat_content = converted_content or _xlsx_to_dat(
            path,
            root_discriminator=xlsx_member_discriminator,
            object_type=schema.object_type if schema is not None else None,
            section_discriminators=(
                tuple(section.discriminator for section in schema.sections)
                if schema is not None else ()
            ),
        ).encode("utf-8")
        member_name = xlsx_member_discriminator + ".dat"
    else:
        _validate_utf8(content, path)
        dat_content = content
        member_name = path.name if suffix == ".dat" else path.stem + ".dat"

    archive_content = _create_zip(((member_name, dat_content),))
    if schema is None:
        return PreparedArchive(file_name=path.stem + ".zip", content=archive_content)
    return PreparedArchive(
        file_name=semantic_archive_name((schema,), ((member_name, dat_content),)),
        content=archive_content,
    )


def validate_local_source(path: Path) -> str:
    suffix = _validate_source_path(path)
    content = _read_nonempty_file(path)
    if suffix == ".zip":
        if not zipfile.is_zipfile(io.BytesIO(content)):
            raise DataLoadError(
                "file-validation", f"Source file is not a valid ZIP archive: {path}"
            )
    elif suffix == ".csv":
        _parse_and_validate_csv(path, content)
    elif suffix == ".xlsx":
        _xlsx_to_dat(path)
    else:
        _validate_utf8(content, path)
    return suffix


def _is_ignored_macos_archive_member(member_name: str) -> bool:
    """Return whether a ZIP member belongs to a macOS metadata directory."""
    return any(
        part.casefold() in IGNORED_MACOS_ARCHIVE_DIRECTORIES
        for part in member_name.split("/")[:-1]
    )


def _is_hidden_archive_member(member_name: str) -> bool:
    """Return whether any ZIP path component is a hidden entry."""
    return any(
        part.startswith(".") and part not in {".", ".."}
        for part in member_name.split("/")
    )


def _meaningful_archive_members(archive: zipfile.ZipFile) -> list[zipfile.ZipInfo]:
    """Return non-directory ZIP members, excluding hidden metadata entries."""
    return [
        member
        for member in archive.infolist()
        if not member.is_dir()
        and not _is_ignored_macos_archive_member(member.filename)
        and not _is_hidden_archive_member(member.filename)
    ]


def _normalized_cx_csv_row(row: Iterable[str]) -> tuple[str, ...]:
    """Normalize a CSV row only for CX mapping-signature comparison."""
    return tuple(value.strip().casefold() for value in row)


def _cx_mapping_header_kind(row: tuple[str, ...]) -> str | None:
    """Identify exact or reordered CX mapping headers."""
    if row == CX_MAPPING_METADATA_HEADER:
        return "metadata"
    if row == CX_MAPPING_COLUMNS_HEADER:
        return "columns"
    if len(row) == len(CX_MAPPING_METADATA_HEADER):
        if set(row) == set(CX_MAPPING_METADATA_HEADER):
            return "metadata-reordered"
        if set(row) == set(CX_MAPPING_COLUMNS_HEADER):
            return "columns-reordered"
    return None


def is_cx_mapping_content(content: bytes, *, member_name: str) -> bool:
    """Return whether CSV bytes contain the complete CX mapping signature.

    Files with only one header, reordered headers, reversed headers, duplicate
    headers, or a metadata header that is not the first nonblank row are
    rejected as malformed mapping candidates instead of being uploaded as data.
    """
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        return False
    try:
        rows = list(csv.reader(io.StringIO(text, newline=""), strict=True))
    except csv.Error:
        return False
    normalized_rows = [
        _normalized_cx_csv_row(row)
        for row in rows
        if row and any(value.strip() for value in row)
    ]
    markers = [
        (index, kind)
        for index, row in enumerate(normalized_rows)
        if (kind := _cx_mapping_header_kind(row)) is not None
    ]
    if not markers:
        return False

    metadata_positions = [index for index, kind in markers if kind == "metadata"]
    column_positions = [index for index, kind in markers if kind == "columns"]
    malformed = (
        any(kind.endswith("-reordered") for _index, kind in markers)
        or len(metadata_positions) != 1
        or len(column_positions) != 1
        or metadata_positions[0] != 0
        or column_positions[0] <= metadata_positions[0]
    )
    if malformed:
        raise DataLoadError(
            "file-validation",
            (
                "CX Import mapping CSV must contain the MAP NAME table header first "
                "and the COLUMN HEADER table header later, with each four-column "
                f"header in the required order: {member_name}"
            ),
        )
    return True


def _normalize_fbdi_ucm_account(value: Any) -> str:
    """Convert a live slash-form FBDI account to Documents API syntax."""
    if not isinstance(value, str):
        raise DataLoadError("catalog-or-metadata-mismatch", "FBDI metadata UcmAccount must be a string.")
    segments = value.strip().split("/")
    if not segments or not all(re.fullmatch(r"[A-Za-z0-9_-]+", segment or "") for segment in segments):
        raise DataLoadError("catalog-or-metadata-mismatch", "FBDI metadata UcmAccount must be a slash-delimited account path.")
    return "/".join(segment + "$" for segment in segments)


def _validated_fbdi_load_adapter_interface_id(
    value: Any, *, stage: str = "catalog-or-metadata-mismatch"
) -> Any:
    """Require a nonblank JSON scalar while preserving its exact value and type."""
    valid_string = isinstance(value, str) and bool(value.strip())
    valid_integer = isinstance(value, int) and not isinstance(value, bool)
    valid_float = (
        isinstance(value, float)
        and not isinstance(value, bool)
        and math.isfinite(value)
    )
    if not (valid_string or valid_integer or valid_float):
        raise DataLoadError(
            stage,
            "FBDI metadata requires a nonblank scalar loadAdapterInterfaceId.",
        )
    return value


def _fbdi_filename_action_available(
    config: dict[str, str], *, getter: Getter = get_json
) -> bool:
    """Detect the filename custom action on the business-object resource."""
    describe = getter(
        config["host"] + FBDI_ACTION_RESOURCE_PATH + "/describe",
        config["auth"], stage="fbdi-metadata",
    )
    resources = describe.get("Resources", describe.get("resources")) if isinstance(describe, dict) else None
    if isinstance(resources, dict):
        resource = resources.get("dataLoaderBusinessObjects")
    elif isinstance(resources, list):
        matches = [item for item in resources if isinstance(item, dict) and any(
            item.get(key) == "dataLoaderBusinessObjects"
            for key in ("name", "resourceName", "collectionName")
        )]
        resource = matches[0] if len(matches) == 1 else None
    else:
        resource = None
    if not isinstance(resource, dict):
        raise DataLoadError(
            "catalog-or-metadata-mismatch",
            "FBDI describe did not identify dataLoaderBusinessObjects.",
        )
    collection = resource.get("collection")
    # Fusion advertises collection actions here; retain older top-level layouts.
    if isinstance(collection, dict) and (
        "actions" in collection or "Actions" in collection
    ):
        actions = collection.get("actions", collection.get("Actions"))
    else:
        actions = resource.get("actions", resource.get("Actions", []))
    if isinstance(actions, dict):
        return FBDI_FILENAME_ACTION in actions
    if isinstance(actions, list) and all(
        isinstance(action, dict) and isinstance(action.get("name"), str)
        for action in actions
    ):
        return any(action["name"] == FBDI_FILENAME_ACTION for action in actions)
    raise DataLoadError(
        "catalog-or-metadata-mismatch", "FBDI describe returned malformed action definitions."
    )


def _load_fbdi_filename_metadata(
    config: dict[str, str], csv_members: list[zipfile.ZipInfo]
) -> tuple[FbdiRoutingEntry, ...]:
    """Adapt the filename action's flat rows to the existing routing entries."""
    stems = [Path(member.filename).name[:-4] for member in csv_members]
    if any(not stem.strip() or "," in stem for stem in stems):
        raise DataLoadError(
            "file-validation",
            "FBDI filename action requires nonblank CSV basenames without commas.",
        )
    response = metadata.request_json(
        config["host"] + FBDI_ACTION_RESOURCE_PATH + "/action/" + FBDI_FILENAME_ACTION,
        config["auth"], stage="fbdi-metadata", method="POST",
        data=json.dumps({"pFileName": ",".join(stems)}).encode("utf-8"),
        content_type=MEDIA_TYPE, refresh_http_statuses=frozenset(),
    )
    # ADF custom actions wrap their return value in result, often as JSON text.
    # Retain support for the bare-array response used by older integrations.
    if isinstance(response, dict) and "result" in response:
        response = response["result"]
        if isinstance(response, str):
            try:
                response = json.loads(response)
            except json.JSONDecodeError:
                raise DataLoadError(
                    "catalog-or-metadata-mismatch",
                    "FBDI filename action result contains malformed JSON.",
                ) from None
    if not isinstance(response, list):
        raise DataLoadError(
            "catalog-or-metadata-mismatch",
            "FBDI filename action must return an array, directly or in result.",
        )
    entries: list[FbdiRoutingEntry] = []
    for row in response:
        if not isinstance(row, dict):
            raise DataLoadError(
                "catalog-or-metadata-mismatch", "FBDI filename action returned a malformed row."
            )
        if row.get("ObjectType", FBDI_SOURCE_TYPE) != FBDI_SOURCE_TYPE:
            continue
        name = row.get("BusObjFileDiscriminator")
        prefixes = row.get("DataFileNamePrefixes")
        if not isinstance(name, str) or not name.strip():
            raise DataLoadError(
                "catalog-or-metadata-mismatch",
                "FBDI filename action requires a nonblank BusObjFileDiscriminator.",
            )
        if not isinstance(prefixes, list) or not prefixes or any(
            not isinstance(prefix, str) or not prefix.strip() for prefix in prefixes
        ):
            raise DataLoadError(
                "catalog-or-metadata-mismatch",
                "FBDI filename action requires nonblank DataFileNamePrefixes.",
            )
        entries.append(FbdiRoutingEntry(
            name.strip(), row.get("UcmAccount"), tuple(prefix.strip() for prefix in prefixes),
            row.get("LoadAdapterInterfaceId", row.get("loadAdapterInterfaceId")),
        ))
    return tuple(entries)


def _load_fbdi_metadata(
    config: dict[str, str], *, getter: Getter = get_json
) -> tuple[FbdiRoutingEntry, ...]:
    """Read every page of FBDI business-object metadata before routing."""
    offset = 0
    entries: list[FbdiRoutingEntry] = []
    while True:
        query = urllib.parse.urlencode({
            "q": "ObjectType='FBDI'",
            "expand": "fbdiMetadata",
            "onlyData": "true",
            "offset": str(offset),
        })
        response = getter(
            config["host"] + BUSINESS_OBJECTS_PATH + "?" + query,
            config["auth"],
            stage="fbdi-metadata",
        )
        if (
            not isinstance(response, dict)
            or not isinstance(response.get("items"), list)
            or not isinstance(response.get("hasMore"), bool)
            or isinstance(response.get("offset", offset), bool)
            or response.get("offset", offset) != offset
        ):
            raise DataLoadError(
                "catalog-or-metadata-mismatch", "FBDI metadata returned a malformed page."
            )
        items = response["items"]
        for item in items:
            if not isinstance(item, dict):
                raise DataLoadError(
                    "catalog-or-metadata-mismatch",
                    "FBDI metadata contains a malformed business object.",
                )
            nested = item.get("fbdiMetadata")
            if (
                not isinstance(nested, dict)
                or not isinstance(nested.get("items"), list)
                or not isinstance(nested.get("hasMore"), bool)
                or isinstance(nested.get("offset", 0), bool)
                or nested.get("offset", 0) != 0
            ):
                raise DataLoadError(
                    "catalog-or-metadata-mismatch",
                    "FBDI metadata contains a malformed fbdiMetadata collection.",
                )
            nested_rows = list(nested["items"])
            if nested["hasMore"]:
                business_object_id = item.get("BusinessObjectId")
                nested_offset = nested.get("offset", 0)
                if (
                    isinstance(business_object_id, bool)
                    or not str(business_object_id).isdecimal()
                    or int(business_object_id) < 1
                    or isinstance(nested_offset, bool)
                    or nested_offset != 0
                    or not nested_rows
                ):
                    raise DataLoadError(
                        "catalog-or-metadata-mismatch",
                        "FBDI fbdiMetadata has more pages but cannot be paginated safely.",
                    )
                child_offset = len(nested_rows)
                while True:
                    child_query = urllib.parse.urlencode({
                        "onlyData": "true", "limit": "500", "offset": str(child_offset),
                    })
                    child_response = getter(
                        config["host"] + BUSINESS_OBJECTS_PATH
                        + f"/{business_object_id}/child/fbdiMetadata?{child_query}",
                        config["auth"],
                        stage="fbdi-metadata",
                    )
                    if (
                        not isinstance(child_response, dict)
                        or not isinstance(child_response.get("items"), list)
                        or not isinstance(child_response.get("hasMore"), bool)
                        or not child_response["items"]
                        or isinstance(child_response.get("offset", child_offset), bool)
                        or child_response.get("offset", child_offset) != child_offset
                    ):
                        raise DataLoadError(
                            "catalog-or-metadata-mismatch",
                            "FBDI fbdiMetadata pagination returned a malformed page.",
                        )
                    nested_rows.extend(child_response["items"])
                    child_offset += len(child_response["items"])
                    if not child_response["hasMore"]:
                        break
            for row in nested_rows:
                if not isinstance(row, dict):
                    raise DataLoadError(
                        "catalog-or-metadata-mismatch",
                        "FBDI metadata contains a malformed routing row.",
                    )
                if row.get("ObjectType", FBDI_SOURCE_TYPE) != FBDI_SOURCE_TYPE:
                    continue
                name = item.get("BusObjTopDiscriminator")
                if not isinstance(name, str) or not name.strip():
                    raise DataLoadError(
                        "catalog-or-metadata-mismatch",
                        "FBDI parent business object requires a nonblank BusObjTopDiscriminator.",
                    )
                prefix = row.get("DataFileNamePrefix")
                if not isinstance(prefix, str) or not prefix.strip():
                    raise DataLoadError(
                        "catalog-or-metadata-mismatch",
                        "FBDI routing rows require a filename prefix.",
                    )
                entries.append(FbdiRoutingEntry(
                    name.strip(), row.get("UcmAccount"), (prefix.strip(),),
                    row.get("LoadAdapterInterfaceId", row.get("loadAdapterInterfaceId")),
                ))
        if not response["hasMore"]:
            return tuple(entries)
        if not items:
            raise DataLoadError(
                "catalog-or-metadata-mismatch",
                "FBDI metadata pagination returned an empty page before completion.",
            )
        offset += len(items)


def _fbdi_route_from_archive(
    archive: zipfile.ZipFile,
    entries: tuple[FbdiRoutingEntry, ...],
    *,
    business_object: str | None = None,
) -> FbdiRoute:
    """Choose the BO matching the most distinct CSV members."""
    members = _meaningful_archive_members(archive)
    unsafe_files: list[str] = []
    duplicate_basenames: list[str] = []
    csv_members: list[zipfile.ZipInfo] = []
    basenames: set[str] = set()
    for member in members:
        member_name = member.filename
        parts = member_name.split("/")
        basename = parts[-1]
        normalized_basename = basename.casefold()
        if not basename or member_name.startswith("/") or any(part in {"", ".", ".."} for part in parts):
            unsafe_files.append(member_name)
            continue
        if normalized_basename in basenames:
            duplicate_basenames.append(basename)
        basenames.add(normalized_basename)
        if not normalized_basename.endswith(".csv"):
            continue
        csv_members.append(member)

    if unsafe_files:
        raise DataLoadError("file-validation", "FBDI ZIP member paths must be relative and traversal-safe: " + ", ".join(unsafe_files))
    if duplicate_basenames:
        raise DataLoadError("file-validation", "FBDI ZIP members must have unique case-insensitive basenames: " + ", ".join(duplicate_basenames))
    matches: dict[str, list[zipfile.ZipInfo]] = {}
    rows: dict[str, list[FbdiRoutingEntry]] = {}
    for entry in entries:
        key = entry.business_object.casefold()
        rows.setdefault(key, []).append(entry)
        matched = matches.setdefault(key, [])
        for member in csv_members:
            stem = Path(member.filename).name[:-4].casefold()
            if any(stem.startswith(prefix.casefold()) for prefix in entry.prefixes) and member not in matched:
                matched.append(member)
    highest = max((len(group) for group in matches.values()), default=0)
    if highest == 0:
        raise DataLoadError("business-object-validation", "No ZIP CSV filename matches live FBDI metadata.")
    tied = [key for key, group in matches.items() if len(group) == highest]
    selected = business_object.strip() if isinstance(business_object, str) else None
    tied_names = {row.business_object for key in tied for row in rows[key]}
    if selected and (selected.casefold() not in tied or selected not in tied_names):
        raise DataLoadError(
            "business-object-validation",
            "The selected FBDI Business Object is not one of the highest-scoring candidates.",
        )
    if len(tied) > 1 and not selected:
        raise DataLoadError(
            "business-object-validation",
            "Multiple FBDI Business Objects match the same number of CSV files.",
            response={"fbdiSelectionRequired": True, "candidates": [
                {"businessObject": rows[key][0].business_object, "matchCount": highest}
                for key in tied
            ]},
        )
    key = selected.casefold() if selected else tied[0]
    selected_rows = [entry for entry in rows[key] if any(
        Path(member.filename).name[:-4].casefold().startswith(prefix.casefold())
        for member in matches[key] for prefix in entry.prefixes
    )]
    accounts = {_normalize_fbdi_ucm_account(entry.ucm_account) for entry in selected_rows}
    adapters = [
        _validated_fbdi_load_adapter_interface_id(entry.load_adapter_interface_id)
        for entry in selected_rows
    ]
    if len(accounts) != 1:
        raise DataLoadError(
            "catalog-or-metadata-mismatch",
            "Selected FBDI Business Object has conflicting UCM accounts.",
        )
    if any(type(value) is not type(adapters[0]) or value != adapters[0] for value in adapters[1:]):
        raise DataLoadError(
            "catalog-or-metadata-mismatch",
            "Selected FBDI Business Object has conflicting loadAdapterInterfaceId values.",
        )
    for member in matches[key]:
        if member.file_size == 0:
            raise DataLoadError("file-validation", f"Matched FBDI data files must not be empty: {member.filename}")
    matched_names = tuple(member.filename for member in csv_members if member in matches[key])
    return FbdiRoute(selected_rows[0].business_object, next(iter(accounts)), matched_names, adapters[0])


def resolve_fbdi_route(
    path: Path,
    config: dict[str, str],
    *,
    getter: Getter = get_json,
    business_object: str | None = None,
) -> FbdiRoute:
    """Prefer advertised filename discovery, retaining the existing ZIP matching."""
    try:
        with zipfile.ZipFile(path) as archive:
            csv_members = [
                member for member in _meaningful_archive_members(archive)
                if Path(member.filename).name.casefold().endswith(".csv")
            ]
            if csv_members and _fbdi_filename_action_available(config, getter=getter):
                entries = _load_fbdi_filename_metadata(config, csv_members)
            else:
                entries = _load_fbdi_metadata(config, getter=getter)
            return _fbdi_route_from_archive(archive, entries, business_object=business_object)
    except zipfile.BadZipFile as exc:
        raise DataLoadError("file-validation", f"Source file is not a valid ZIP archive: {path}") from exc


def archive_source_type(
    path: Path,
    *,
    cx_import: bool = False,
) -> str | None:
    """Classify a valid archive without extracting or changing its contents."""
    with zipfile.ZipFile(path) as archive:
        members = _meaningful_archive_members(archive)
        is_fsm = any(
            member.filename.rsplit("/", 1)[-1] == FSM_METADATA_MEMBER_NAME
            for member in members
        )
        has_cx_mapping = any(
            Path(member.filename).name.casefold().endswith(".csv")
            and is_cx_mapping_content(
                archive.read(member), member_name=member.filename
            )
            for member in members
        )
        if is_fsm and (cx_import or has_cx_mapping):
            raise DataLoadError(
                "source-selection",
                "The ZIP archive contains conflicting FSM and CX Import markers.",
            )
        if is_fsm:
            return FSM_SOURCE_TYPE
        if cx_import or has_cx_mapping:
            return CX_IMPORT_SOURCE_TYPE
    return None


def _archive_contains_csv(path: Path) -> bool:
    """Return whether an immutable ZIP has a meaningful CSV member."""
    with zipfile.ZipFile(path) as archive:
        return any(
            Path(member.filename).name.casefold().endswith(".csv")
            for member in _meaningful_archive_members(archive)
        )


def validate_cx_import_archive(path: Path) -> tuple[CxImportFile, ...]:
    """Validate and return immutable CX CSV members in upload order."""
    content = _read_nonempty_file(path)
    try:
        archive = zipfile.ZipFile(io.BytesIO(content))
    except zipfile.BadZipFile as exc:
        raise DataLoadError(
            "file-validation", f"Source file is not a valid ZIP archive: {path}"
        ) from exc
    with archive:
        members = _meaningful_archive_members(archive)
        if not members:
            raise DataLoadError(
                "file-validation", "CX Import ZIP must contain at least one CSV file."
            )
        member_names = [member.filename for member in members]
        if len(set(member_names)) != len(member_names):
            raise DataLoadError(
                "file-validation", "CX Import ZIP contains duplicate member names."
            )
        files: list[CxImportFile] = []
        basenames: set[str] = set()
        for member in members:
            member_name = member.filename
            path_parts = member_name.split("/")
            if (
                member_name.startswith(("/", "\\"))
                or "\\" in member_name
                or ".." in path_parts
                or any(not part for part in path_parts)
                or (path_parts and path_parts[0].endswith(":"))
            ):
                raise DataLoadError(
                    "file-validation", f"ZIP archive member path is unsafe: {member_name}"
                )
            file_name = Path(member_name).name
            if not file_name.casefold().endswith(".csv"):
                raise DataLoadError(
                    "file-validation",
                    f"CX Import ZIP contains a non-CSV member: {member_name}",
                )
            normalized_name = file_name.casefold()
            if normalized_name in basenames:
                raise DataLoadError(
                    "file-validation",
                    f"CX Import CSV basenames must be unique: {file_name}",
                )
            basenames.add(normalized_name)
            member_content = archive.read(member)
            if not member_content:
                raise DataLoadError(
                    "file-validation", f"CX Import CSV is empty: {member_name}"
                )
            files.append(
                CxImportFile(
                    member_name,
                    file_name,
                    member_content,
                    is_cx_mapping_content(
                        member_content, member_name=member_name
                    ),
                )
            )
    return _validate_cx_import_files(files, source_label="CX Import ZIP")


def _validate_cx_import_files(
    files: Iterable[CxImportFile], *, source_label: str
) -> tuple[CxImportFile, ...]:
    """Validate common CX CSV constraints and return mapping-first order."""
    files = tuple(files)
    basenames: set[str] = set()
    for file in files:
        if not file.content:
            raise DataLoadError("file-validation", f"CX Import CSV is empty: {file.member_name}")
        normalized_name = file.file_name.casefold()
        if normalized_name in basenames:
            raise DataLoadError(
                "file-validation", f"CX Import CSV basenames must be unique: {file.file_name}"
            )
        basenames.add(normalized_name)
    mapping_files = tuple(file for file in files if file.is_mapping)
    data_files = tuple(file for file in files if not file.is_mapping)
    if len(mapping_files) > 1:
        raise DataLoadError(
            "file-validation", f"{source_label} may contain only one mapping CSV."
        )
    if not data_files:
        raise DataLoadError(
            "file-validation",
            f"{source_label} must contain at least one non-mapping data CSV.",
        )
    return mapping_files + data_files


def validate_cx_import_files(paths: Iterable[Path]) -> tuple[CxImportFile, ...]:
    """Validate direct CSV sources for one CX Import group."""
    files: list[CxImportFile] = []
    for path in paths:
        if validate_local_source(path) != ".csv":
            raise DataLoadError(
                "source-selection", "Direct CX Import accepts only CSV source files."
            )
        content = _read_nonempty_file(path)
        files.append(
            CxImportFile(
                path.name,
                path.name,
                content,
                is_cx_mapping_content(content, member_name=path.name),
            )
        )
    return _validate_cx_import_files(files, source_label="Direct CX Import")


def direct_cx_upload_file_name(files: Iterable[CxImportFile]) -> str:
    """Name a direct CX group from its first data CSV, never its mapping CSV."""
    for file in files:
        if not file.is_mapping:
            return timestamped_archive_name(file.file_name)
    raise DataLoadError(
        "file-validation", "CX Import requires at least one data CSV file."
    )


def _mapping_import_object(file: CxImportFile) -> str:
    """Read and validate the authoritative IMPORT OBJECT mapping value."""
    try:
        text = file.content.decode("utf-8-sig")
        rows = list(csv.reader(io.StringIO(text, newline=""), strict=True))
    except (UnicodeDecodeError, csv.Error) as exc:
        raise DataLoadError(
            "file-validation",
            f"CX Import mapping CSV cannot be parsed: {file.member_name}",
        ) from exc
    nonblank_rows = [
        row for row in rows if row and any(value.strip() for value in row)
    ]
    column_header_index = next(
        (
            index
            for index, row in enumerate(nonblank_rows)
            if _normalized_cx_csv_row(row) == CX_MAPPING_COLUMNS_HEADER
        ),
        None,
    )
    if column_header_index is None or column_header_index <= 1:
        raise DataLoadError(
            "file-validation",
            "CX Import mapping CSV must include at least one mapping metadata row before "
            f"the COLUMN HEADER table: {file.member_name}",
        )
    object_codes: list[str] = []
    for row in nonblank_rows[1:column_header_index]:
        if len(row) != len(CX_MAPPING_METADATA_HEADER):
            raise DataLoadError(
                "file-validation",
                "CX Import mapping metadata rows must contain four columns before the "
                f"COLUMN HEADER table: {file.member_name}",
            )
        object_code = row[2].strip()
        if not object_code:
            raise DataLoadError(
                "file-validation",
                "CX Import mapping metadata rows require a nonblank IMPORT OBJECT value: "
                f"{file.member_name}",
            )
        object_codes.append(object_code)
    if len(set(object_codes)) != 1:
        raise DataLoadError(
            "file-validation",
            "CX Import mapping metadata rows must use one identical IMPORT OBJECT value: "
            f"{file.member_name}",
        )
    return object_codes[0]


def resolve_cx_import_object_code(
    files: tuple[CxImportFile, ...], supplied_object_code: str | None
) -> str:
    """Resolve a CX object code before preview, approval, or any UCM upload."""
    mapping_file = next((file for file in files if file.is_mapping), None)
    if mapping_file is not None:
        if supplied_object_code is not None:
            raise DataLoadError(
                "source-selection",
                "CX Import mapping CSV supplies IMPORT OBJECT; do not provide "
                "--cx-import-object-code.",
            )
        return _mapping_import_object(mapping_file)
    object_code = (supplied_object_code or "").strip()
    if not object_code:
        raise DataLoadError(
            "input-required",
            "What is the CX Business Object code for this file?",
        )
    return object_code


def resolve_cx_ucm_account(
    object_code: str,
    config: dict[str, str],
    *,
    getter: Getter = get_json,
) -> str:
    """Resolve the authoritative CX UCM account for one import object."""
    encoded_object_code = urllib.parse.quote(object_code, safe="")
    query = urllib.parse.urlencode({"fields": "UcmAccount", "onlyData": "true"})
    response = getter(
        config["host"] + CX_OBJECT_METADATA_PATH + encoded_object_code + "?" + query,
        config["auth"],
        stage="cx-object-metadata",
    )
    if not isinstance(response, dict):
        raise DataLoadError(
            "cx-object-metadata",
            "CX object metadata did not return a JSON object with UcmAccount.",
        )
    ucm_account = response.get("UcmAccount")
    if not isinstance(ucm_account, str) or not ucm_account.strip():
        raise DataLoadError(
            "cx-object-metadata",
            f"CX object metadata did not return a nonblank UcmAccount for {object_code}.",
        )
    segments = [segment for segment in ucm_account.strip().split("/") if segment]
    if not segments:
        raise DataLoadError(
            "cx-object-metadata",
            f"CX object metadata did not return a usable UcmAccount for {object_code}.",
        )
    return "$/".join(segments) + "$"


def _is_fsm_zip(path: Path) -> bool:
    """Return whether a selectable ZIP is an FSM archive without changing it."""
    try:
        return archive_source_type(path) == FSM_SOURCE_TYPE
    except (OSError, zipfile.BadZipFile):
        return False


def _redact_sensitive(value: Any, secrets: Iterable[str]) -> Any:
    active_secrets = [secret for secret in secrets if secret]
    if isinstance(value, str):
        redacted = value
        for secret in active_secrets:
            redacted = redacted.replace(secret, "<redacted>")
        return redacted
    if isinstance(value, list):
        return [_redact_sensitive(item, active_secrets) for item in value]
    if isinstance(value, dict):
        return {
            key: _redact_sensitive(item, active_secrets) for key, item in value.items()
        }
    return value


def _decode_response(body: bytes, stage: str, secrets: Iterable[str] = ()) -> Any:
    text = body.decode("utf-8", errors="replace")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise DataLoadError(
            stage,
            "Server returned a malformed JSON response.",
            response=_redact_sensitive(text, secrets),
        ) from exc


def post_json(
    url: str,
    payload: dict[str, Any],
    auth: metadata.OAuthSession,
    *,
    stage: str,
) -> Any:
    encoded_body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return metadata.request_json_or_empty(
        url,
        auth,
        stage=stage,
        method="POST",
        data=encoded_body,
        content_type=MEDIA_TYPE,
        sensitive_values=(payload.get("content", ""),),
    )


Getter = Callable[..., Any]
Poster = Callable[..., Any]
ByteGetter = Callable[..., bytes]
MultipartUploader = Callable[..., Any]


def _encode_multipart_upload(
    prepared: PreparedArchive,
    *,
    document_account: str | None = None,
    security_group: str = "FAFusionImportExport",
    primary_content_type: str = "application/zip",
) -> tuple[bytes, str]:
    """Encode the Fusion Documents upload form without altering ZIP bytes."""
    boundary = "----FDOSDataLoader" + uuid.uuid4().hex
    metadata_payload = {
        "dDocTitle": prepared.file_name,
        "dSecurityGroup": security_group,
        "dDocAccount": document_account or _ucm_document_account(prepared),
        "dDocType": "Document",
    }
    metadata_values = json.dumps(metadata_payload, separators=(",", ":")).encode("utf-8")
    delimiter = boundary.encode("ascii")
    body = b"\r\n".join(
        (
            b"--" + delimiter,
            b'Content-Disposition: form-data; name="metadataValues"',
            b"Content-Type: application/json; charset=utf-8",
            b"",
            metadata_values,
            b"--" + delimiter,
            (
                b'Content-Disposition: form-data; name="primaryFile"; filename="'
                + prepared.file_name.encode("utf-8")
                + b'"'
            ),
            b"Content-Type: " + primary_content_type.encode("ascii"),
            b"",
            prepared.content,
            b"--" + delimiter + b"--",
            b"",
        )
    )
    return body, f"multipart/form-data; boundary={boundary}"


def _ucm_document_account(prepared: PreparedArchive) -> str:
    """Select the UCM account from the immutable archive classification."""
    try:
        with zipfile.ZipFile(io.BytesIO(prepared.content)) as archive:
            is_fsm = any(
                Path(member.filename).name == FSM_METADATA_MEMBER_NAME
                for member in _meaningful_archive_members(archive)
            )
    except zipfile.BadZipFile:
        is_fsm = False
    return FSM_UCM_DOCUMENT_ACCOUNT if is_fsm else UCM_DOCUMENT_ACCOUNT


def post_ucm_multipart(
    url: str,
    prepared: PreparedArchive,
    auth: metadata.OAuthSession,
    *,
    document_account: str | None = None,
    security_group: str = "FAFusionImportExport",
    primary_content_type: str = "application/zip",
) -> Any:
    """Upload the approved archive through the Fusion Documents REST API."""
    body, content_type = _encode_multipart_upload(
        prepared,
        document_account=document_account,
        security_group=security_group,
        primary_content_type=primary_content_type,
    )
    return metadata.request_json(
        url,
        auth,
        stage="ucm-upload",
        method="POST",
        data=body,
        content_type=content_type,
        refresh_http_statuses=frozenset({401}),
    )


def validate_file_discriminator(
    source_path: Path,
    config: dict[str, str],
    *,
    business_object: str | None = None,
    getter: Getter = get_json,
    byte_getter: ByteGetter = metadata.get_bytes,
    progress: metadata.SchemaProgressCallback | None = None,
) -> metadata.BusinessObjectSchema:
    if source_path.suffix.lower() == ".xlsx":
        sheet_discriminators = xlsx_sample_workbook.xlsx_sheet_discriminators(source_path)
        business_object = (
            metadata.validate_selected_xlsx_root_business_object(
                sheet_discriminators, business_object
            )
            if business_object is not None
            else metadata.resolve_xlsx_root_business_object(
                sheet_discriminators,
                config,
                getter=getter,
            )
        )
    elif business_object is None:
        business_object = source_path.stem
    return metadata.load_business_object_schema(
        business_object,
        config,
        allow_aliases=False,
        fscr_business_object_lookup=True,
        getter=getter,
        byte_getter=byte_getter,
        progress=progress,
    )


def validate_source_attributes(
    source_path: Path,
    suffix: str,
    schema: metadata.BusinessObjectSchema,
    *,
    business_object: str | None = None,
    mapping_audit: list[metadata.ColumnMapping] | None = None,
) -> bytes | None:
    content = _read_nonempty_file(source_path)
    converted_content: bytes | None = None
    if suffix == ".csv":
        rows = _parse_and_validate_csv(source_path, content)
        mapped_header, indexes, audit = metadata.map_source_headers(
            business_object or source_path.stem, tuple(rows[0]), schema
        )
        if mapping_audit is not None:
            mapping_audit.extend(audit)
        if not mapped_header:
            raise DataLoadError("file-validation", f"CSV file has no mappable header columns: {source_path}")
        source_sections = (
            metadata.SourceSection(business_object or source_path.stem, mapped_header),
        )
        converted_content = _csv_to_dat(
            source_path, content, discriminator=business_object,
            mapped_header=mapped_header, retained_indexes=indexes,
        )
    elif suffix == ".xlsx":
        converted_text, source_sections = xlsx_sample_workbook.xlsx_to_dat(
            source_path,
            header_mapper=lambda section, headers: metadata.map_source_headers(section, headers, schema),
            mapping_audit=mapping_audit,
            root_discriminator=schema.discriminator,
            section_discriminators=tuple(section.discriminator for section in schema.sections),
            object_type=schema.object_type,
        )
        converted_content = converted_text.encode("utf-8")
    else:
        source_sections = metadata.parse_source_sections(
            content, source_name=str(source_path)
        )
    if metadata.mapping_preserves_unmapped() and suffix in {".csv", ".xlsx"}:
        source_sections_for_validation = tuple(
            metadata.SourceSection(item.discriminator, tuple(
                attribute for attribute in item.attributes
                if metadata.is_supported_source_attribute(item.discriminator, attribute, schema)
            )) for item in source_sections
        )
    else:
        source_sections_for_validation = source_sections
    metadata.validate_source_sections(source_sections_for_validation, schema)
    if suffix == ".csv" or (suffix == ".xlsx" and not metadata.mapping_preserves_unmapped()):
        generated_sections = metadata.parse_source_sections(
            converted_content,
            source_name=f"generated:{source_path}",
        )
        if suffix == ".xlsx":
            metadata.validate_source_sections(generated_sections, schema)
        if suffix == ".csv" and not metadata.mapping_preserves_unmapped() and generated_sections != source_sections:
            raise DataLoadError(
                "file-validation",
                "Lossy transformation: generated DAT sections do not preserve the validated CSV headers.",
            )
    return converted_content


def validate_zip_business_objects(
    source_path: Path,
    config: dict[str, str],
    *,
    getter: Getter = get_json,
    byte_getter: ByteGetter = metadata.get_bytes,
) -> tuple[metadata.BusinessObjectSchema, ...]:
    """Resolve and validate every DAT member in an explicit archive before upload."""
    content = _read_nonempty_file(source_path)
    try:
        archive = zipfile.ZipFile(io.BytesIO(content))
    except zipfile.BadZipFile as exc:
        raise DataLoadError(
            "file-validation", f"Source file is not a valid ZIP archive: {source_path}"
        ) from exc
    with archive:
        members = _meaningful_archive_members(archive)
        names = [item.filename for item in members]
        if len(set(names)) != len(names):
            raise DataLoadError(
                "file-validation", f"ZIP archive contains duplicate member names: {source_path}"
            )
        dat_members = [item for item in members if item.filename.lower().endswith(".dat")]
        opaque_members = [item.filename for item in members if item not in dat_members]
        if opaque_members:
            raise DataLoadError(
                "file-validation",
                "ZIP archive contains opaque non-DAT members before upload: "
                + ", ".join(opaque_members),
            )
        if not dat_members:
            raise DataLoadError(
                "file-validation",
                f"ZIP archive must contain parseable DAT members before upload: {source_path}",
            )

        schemas: list[metadata.BusinessObjectSchema] = []
        seen_roots: set[str] = set()
        parsed_sections: dict[str, tuple[metadata.SourceSection, ...]] = {}
        for member in dat_members:
            member_name = member.filename
            if member_name.startswith("/") or ".." in Path(member_name).parts:
                raise DataLoadError(
                    "file-validation", f"ZIP archive member path is unsafe: {member_name}"
                )
            parsed_sections[member_name] = metadata.parse_source_sections(
                archive.read(member), source_name=f"{source_path}:{member_name}"
            )
        candidate_discriminators = tuple(
            dict.fromkeys(
                section.discriminator
                for member in dat_members
                for section in parsed_sections[member.filename]
            )
        )
        top_level_discriminators = {
            metadata.discriminator_from_item(item)
            for candidate in candidate_discriminators
            for item in metadata.find_business_objects(config, candidate, getter=getter)
        }
        for member in dat_members:
            member_name = member.filename
            sections = parsed_sections[member_name]
            roots = [
                section.discriminator
                for section in sections
                if section.discriminator in top_level_discriminators
            ]
            if len(roots) != 1:
                raise DataLoadError(
                    "business-object-validation",
                    f"ZIP member must contain exactly one registered top-level business object: {member_name}",
                )
            root = roots[0]
            if root in seen_roots:
                raise DataLoadError(
                    "business-object-validation",
                    f"ZIP archive contains duplicate top-level business object {root}.",
                )
            schema = metadata.load_business_object_schema(
                root,
                config,
                allow_aliases=False,
                fscr_business_object_lookup=True,
                getter=getter,
                byte_getter=byte_getter,
            )
            metadata.validate_source_sections(sections, schema)
            schemas.append(schema)
            seen_roots.add(root)
    return tuple(schemas)


def _xlsx_to_dat(
    path: Path,
    *,
    root_discriminator: str | None = None,
    section_discriminators: tuple[str, ...] = (),
    object_type: str | None = None,
) -> str:
    """Convert an XLSX source without allowing truncated worksheet titles into DAT.

    Excel sheet titles are limited to 31 characters.  Callers that have
    resolved live schema therefore pass the registered discriminators so both
    METADATA and row directives retain their full names.
    """
    content, _sections = xlsx_sample_workbook.xlsx_to_dat(
        path,
        root_discriminator=root_discriminator,
        section_discriminators=section_discriminators,
        object_type=object_type,
    )
    return content


def _is_skippable_source_validation(error: DataLoadError) -> bool:
    """Return whether an error is local to one resolved source's schema.

    The shared metadata client uses the same stage for source validation and
    HTTP failures. Only the former may be confirmation-skipped; transport,
    authentication, and malformed-response failures must still block all
    sources.
    """
    return (
        error.stage == "business-object-validation"
        and error.http_status is None
        and not error.message.startswith("HTTP request failed")
        and not (
            isinstance(error.response, dict) and "offset" in error.response
        )
    )


def _validate_xlsx_with_progress(
    source_path: Path,
    config: dict[str, str],
    *,
    source_index: int,
    source_total: int,
    progress: ProgressCallback | None,
    getter: Getter,
    byte_getter: ByteGetter,
    business_object: str | None = None,
    mapping_audit: list[metadata.ColumnMapping] | None = None,
) -> tuple[metadata.BusinessObjectSchema, bytes]:
    current_checkpoint = 1
    resolved_business_object: str | None = None
    _notify_progress(
        progress,
        "workbook_started",
        source_path=source_path,
        source_index=source_index,
        source_total=source_total,
    )

    def report_schema_progress(event: metadata.SchemaProgressEvent) -> None:
        nonlocal current_checkpoint, resolved_business_object
        if event.event != "business_object_resolved":
            return
        resolved_business_object = event.business_object
        _notify_progress(
            progress,
            "business_object_resolved",
            source_path=source_path,
            source_index=source_index,
            source_total=source_total,
            business_object=resolved_business_object,
            checkpoint_index=1,
        )
        current_checkpoint = 2

    try:
        validate_local_source(source_path)
        # A mapped workbook exposes its intended root before the live-schema
        # lookup. Retain that exact discriminator so a multi-source caller can
        # offer a confirmation-gated skip only for this resolved source.
        resolved_business_object = xlsx_sample_workbook.xlsx_business_object_name(
            source_path
        )
        schema = validate_file_discriminator(
            source_path,
            config,
            business_object=business_object,
            getter=getter,
            byte_getter=byte_getter,
            progress=report_schema_progress,
        )
        converted_content = validate_source_attributes(
            source_path, ".xlsx", schema, mapping_audit=mapping_audit
        )
        if converted_content is None:
            raise DataLoadError(
                "archive-preparation",
                f"XLSX conversion did not produce DAT content: {source_path}",
            )
        _notify_progress(
            progress,
            "template_headers_validated",
            source_path=source_path,
            source_index=source_index,
            source_total=source_total,
            business_object=schema.discriminator,
            checkpoint_index=2,
        )
        current_checkpoint = 3
        _notify_progress(
            progress,
            "sections_keys_validated",
            source_path=source_path,
            source_index=source_index,
            source_total=source_total,
            business_object=schema.discriminator,
            checkpoint_index=3,
        )
        current_checkpoint = 4
        _notify_progress(
            progress,
            "dat_conversion_completed",
            source_path=source_path,
            source_index=source_index,
            source_total=source_total,
            business_object=schema.discriminator,
            checkpoint_index=4,
        )
        _notify_progress(
            progress,
            "workbook_completed",
            source_path=source_path,
            source_index=source_index,
            source_total=source_total,
            business_object=schema.discriminator,
            checkpoint_index=4,
        )
        return schema, converted_content
    except DataLoadError as error:
        _notify_progress(
            progress,
            "workbook_failed",
            source_path=source_path,
            source_index=source_index,
            source_total=source_total,
            business_object=resolved_business_object,
            checkpoint_index=current_checkpoint,
        )
        # DataLoadError deliberately has a small public shape. This optional
        # internal hint is consumed only by the multi-source preflight to
        # identify a business object that can be explicitly skipped later.
        error.business_object = resolved_business_object
        raise


def _is_run_id_action_rejection(error: DataLoadError) -> bool:
    """Return whether Fusion rejected the optional runID as an action payload field."""
    if error.http_status != 400 or not isinstance(error.response, dict):
        return False
    details = error.response.get("o:errorDetails")
    if not isinstance(details, list):
        return False
    return any(
        isinstance(detail, dict)
        and str(detail.get("o:errorCode") or "") == "27503"
        and "does not represent an action" in str(detail.get("detail") or "")
        for detail in details
    )


def _fbdi_run_id_value(run_id: str | None) -> int | None:
    """Return the FBDI runID as the positive JSON number required by Fusion."""
    if run_id is None:
        return None
    value = run_id.strip()
    if not re.fullmatch(r"[1-9][0-9]*", value):
        raise DataLoadError(
            "run-configuration",
            "FBDI runID must be a positive integer when it is configured.",
        )
    return int(value)


def _contains_run_book_task_code(value: Any) -> bool:
    """Return whether one initiateDataLoad action definition exposes the field."""
    if isinstance(value, dict):
        if value.get("name") == "runBookTaskCode" or "runBookTaskCode" in value:
            return True
        return any(_contains_run_book_task_code(child) for child in value.values())
    if isinstance(value, list):
        return any(_contains_run_book_task_code(child) for child in value)
    return False


def _initiate_action_supports_run_book_task_code(
    config: dict[str, str], *, getter: Getter
) -> bool:
    """Check live Data Loader action metadata without making support mandatory."""
    try:
        describe = getter(
            config["host"] + DATA_LOADER_DATA_SETS_DESCRIBE_PATH,
            config["auth"],
            stage="data-load-initiation-metadata",
        )
    except DataLoadError:
        return False
    if not isinstance(describe, dict):
        return False

    def action_definition(value: Any) -> Any:
        if not isinstance(value, dict):
            return None
        for key in ("actions", "Actions"):
            actions = value.get(key)
            if isinstance(actions, dict) and "initiateDataLoad" in actions:
                return actions["initiateDataLoad"]
            if isinstance(actions, list):
                for action in actions:
                    if isinstance(action, dict) and action.get("name") == "initiateDataLoad":
                        return action
        for child in value.values():
            found = action_definition(child)
            if found is not None:
                return found
        return None

    return _contains_run_book_task_code(action_definition(describe))


def _initiate_data_load(
    file_name: str,
    content_id: str,
    config: dict[str, str],
    run_id: str | None,
    *,
    poster: Poster,
    run_book_task_code: str | None = None,
    source_type: str | None = None,
    cx_import_object_name: str | None = None,
    cx_import_high_volume_load: bool = False,
    load_adapter_interface_id: Any = None,
) -> dict[str, Any]:
    """Initiate one approved load using already-created UCM content."""
    initiate_payload = {
        "contentId": content_id,
        "fileAction": "IMPORT_AND_LOAD",
        "dataSetName": file_name,
        "importConcurrentThreads": 8,
        "loadConcurrentThreads": 8,
        "importMaxErrorPercentage": 100,
        "loadMaxErrorPercentage": 100,
        "fileEncryption": "NONE",
        "verificationKey": None,
        "startDate": None,
        "deleteSourceFileFlag": "Y",
        "generateMappingFileFlag": "N",
        "uiInvoke": "Y",
    }
    if run_id is not None:
        initiate_payload["runID"] = (
            _fbdi_run_id_value(run_id)
            if source_type == FBDI_SOURCE_TYPE
            else run_id
        )
    if run_book_task_code is not None:
        initiate_payload["runBookTaskCode"] = run_book_task_code
    if source_type is not None:
        initiate_payload["sourceType"] = source_type
    if cx_import_object_name is not None:
        initiate_payload["cxImportObjectName"] = cx_import_object_name
    if cx_import_high_volume_load:
        if source_type != CX_IMPORT_SOURCE_TYPE:
            raise DataLoadError(
                "source-selection",
                "High-volume mode is supported only for CX Import.",
            )
        initiate_payload["cxImportHighVolumeLoad"] = "YES"
    if source_type == FBDI_SOURCE_TYPE:
        initiate_payload["loadAdapterInterfaceId"] = (
            _validated_fbdi_load_adapter_interface_id(
                load_adapter_interface_id
            )
        )
    elif load_adapter_interface_id is not None:
        raise DataLoadError(
            "source-selection",
            "loadAdapterInterfaceId is supported only for FBDI.",
        )

    try:
        initiate_response = poster(
            config["host"] + INITIATE_PATH,
            initiate_payload,
            config["auth"],
            stage="data-load-initiation",
        )
    except DataLoadError as error:
        if run_id is None or not _is_run_id_action_rejection(error):
            raise DataLoadError(
                error.stage,
                error.message,
                http_status=error.http_status,
                response=error.response,
                content_id=content_id,
            ) from error
        initiate_payload.pop("runID", None)
        initiate_payload.pop("runBookTaskCode", None)
        initiate_response = poster(
            config["host"] + INITIATE_PATH,
            initiate_payload,
            config["auth"],
            stage="data-load-initiation",
        )
    initiate_result = (
        initiate_response.get("result") if isinstance(initiate_response, dict) else None
    )
    if not isinstance(initiate_result, dict) or initiate_result.get("Status") != "SUCCESS":
        raise DataLoadError(
            "data-load-initiation",
            "Data-load initiation did not return Status=SUCCESS.",
            response=initiate_response,
            content_id=content_id,
        )
    request_id = initiate_result.get("RequestId")
    if not isinstance(request_id, (str, int)) or not str(request_id).strip():
        raise DataLoadError(
            "data-load-initiation",
            "Data-load initiation response did not contain a RequestId.",
            response=initiate_response,
            content_id=content_id,
        )
    result = {
        "fileName": file_name,
        "dataSetName": file_name,
        "uploadStatus": "SUCCESS",
        "ContentId": content_id,
        "initiationStatus": "SUCCESS",
        "RequestId": str(request_id),
        "initiationOptions": {
            key: initiate_payload[key]
            for key in (
                "fileAction",
                "importConcurrentThreads",
                "loadConcurrentThreads",
                "importMaxErrorPercentage",
                "loadMaxErrorPercentage",
                "fileEncryption",
                "deleteSourceFileFlag",
                "generateMappingFileFlag",
                "uiInvoke",
                "sourceType",
                "cxImportObjectName",
                "cxImportHighVolumeLoad",
                "loadAdapterInterfaceId",
            )
            if key in initiate_payload
        },
    }
    return result


def _upload_and_initiate_prepared(
    prepared: PreparedArchive,
    config: dict[str, str],
    run_id: str | None,
    *,
    poster: Poster,
    run_book_task_code: str | None = None,
    multipart_uploader: MultipartUploader = post_ucm_multipart,
    source_type: str | None = None,
    document_account: str | None = None,
    load_adapter_interface_id: Any = None,
) -> dict[str, Any]:
    file_name = prepared.file_name

    if source_type == FBDI_SOURCE_TYPE:
        _validated_fbdi_load_adapter_interface_id(load_adapter_interface_id)
    elif load_adapter_interface_id is not None:
        raise DataLoadError(
            "source-selection",
            "loadAdapterInterfaceId is supported only for FBDI.",
        )

    upload_kwargs: dict[str, str] = {}
    if document_account is not None:
        upload_kwargs["document_account"] = document_account
    upload_response = multipart_uploader(
        config["host"] + DOCUMENT_UPLOAD_PATH,
        prepared,
        config["auth"],
        **upload_kwargs,
    )
    if not isinstance(upload_response, dict):
        raise DataLoadError(
            "ucm-upload",
            "UCM upload did not return a JSON response.",
            response=_redact_sensitive(upload_response, config["auth"].secrets()),
        )
    content_id = upload_response.get("dDocName")
    if not isinstance(content_id, str) or not content_id.strip():
        raise DataLoadError(
            "ucm-upload",
            "UCM upload response did not contain a dDocName.",
            response=_redact_sensitive(upload_response, config["auth"].secrets()),
        )

    result = _initiate_data_load(
        file_name,
        content_id,
        config,
        run_id,
        poster=poster,
        run_book_task_code=run_book_task_code,
        source_type=source_type,
        load_adapter_interface_id=load_adapter_interface_id,
    )
    result.update(
        {
            "archiveName": prepared.file_name,
            "archiveSha256": archive_sha256(prepared.content),
            "sourceType": source_type,
        }
    )
    if document_account is not None:
        result["ucmAccount"] = document_account
    return result


def _upload_and_initiate_cx(
    archive_name: str,
    files: tuple[CxImportFile, ...],
    config: dict[str, str],
    run_id: str | None,
    *,
    cx_import_object_code: str,
    cx_ucm_account: str,
    poster: Poster,
    run_book_task_code: str | None = None,
    cx_import_high_volume_load: bool = False,
    multipart_uploader: MultipartUploader = post_ucm_multipart,
    approved_artifact_content: bytes | None = None,
) -> dict[str, Any]:
    """Upload each approved CX CSV separately, then initiate one CX import."""
    uploaded_content_ids: list[str] = []
    initiation_content_ids: list[str] = []
    uploaded_files: list[dict[str, str]] = []
    for file in files:
        try:
            upload_response = multipart_uploader(
                config["host"] + DOCUMENT_UPLOAD_PATH,
                PreparedArchive(file.file_name, file.content),
                config["auth"],
                document_account=cx_ucm_account,
                security_group=CX_SECURITY_GROUP,
                primary_content_type="text/csv",
            )
        except DataLoadError as error:
            raise DataLoadError(
                error.stage,
                error.message,
                http_status=error.http_status,
                response={
                    "uploadError": error.response,
                    "uploadedFiles": uploaded_files,
                },
                content_id=";".join(uploaded_content_ids) or None,
            ) from error
        if not isinstance(upload_response, dict):
            raise DataLoadError(
                "ucm-upload",
                f"CX Import upload did not return JSON for {file.file_name}.",
                response={"uploadedFiles": uploaded_files},
                content_id=";".join(uploaded_content_ids) or None,
            )
        content_id = upload_response.get("dDocName")
        if not isinstance(content_id, str) or not content_id.strip():
            raise DataLoadError(
                "ucm-upload",
                f"CX Import upload response did not contain a dDocName for {file.file_name}.",
                response={"uploadedFiles": uploaded_files},
                content_id=";".join(uploaded_content_ids) or None,
            )
        content_id = content_id.strip()
        uploaded_content_ids.append(content_id)
        initiation_content_ids.append(
            CX_MAPPING_INITIATION_PREFIX + content_id if file.is_mapping else content_id
        )
        uploaded_files.append({"fileName": file.file_name, "contentId": content_id})

    combined_content_id = ";".join(initiation_content_ids)
    result = _initiate_data_load(
        archive_name,
        combined_content_id,
        config,
        run_id,
        poster=poster,
        run_book_task_code=run_book_task_code,
        source_type=CX_IMPORT_SOURCE_TYPE,
        cx_import_object_name=cx_import_object_code,
        cx_import_high_volume_load=cx_import_high_volume_load,
    )
    result.update(
        {
            "archiveName": archive_name,
            "archiveSha256": archive_sha256(
                approved_artifact_content
                if approved_artifact_content is not None
                else cx_import_group_bytes(files)
            ),
            "sourceType": CX_IMPORT_SOURCE_TYPE,
            "businessObject": cx_import_object_code,
            "ucmAccount": cx_ucm_account,
            "uploadedFiles": uploaded_files,
        }
    )
    return result


def require_approved_sha256(
    content: bytes, expected_sha256: str | None, *, source_label: str = "ZIP"
) -> None:
    """Require CX approval to cover the exact source bytes."""
    expected = (expected_sha256 or "").strip().casefold()
    if not re.fullmatch(r"[0-9a-f]{64}", expected):
        raise DataLoadError(
            "approval",
            f"CX Import validation requires the complete internal integrity digest for {source_label}.",
        )
    if archive_sha256(content).casefold() != expected:
        raise DataLoadError(
            "approval",
            f"The CX Import {source_label} no longer matches its validated integrity digest. "
            "Validate it again before upload.",
        )


def _require_approved_task_validation(
    prepared: PreparedArchive, envelope_path: Path
) -> str:
    """Fail closed unless approval covers the final prepared archive bytes."""
    try:
        envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise DataLoadError("task-validation", f"Task Validation envelope is unreadable: {envelope_path}") from error
    if not isinstance(envelope, dict):
        raise DataLoadError("task-validation", "Task Validation envelope must be a JSON object.")
    validator_scripts = Path(__file__).resolve().parent.parent / "task-validator" / "scripts"
    if str(validator_scripts) not in sys.path:
        sys.path.insert(0, str(validator_scripts))
    try:
        from task_rule_execution import approved_loader_payload
        payload = approved_loader_payload(envelope.get("preview"), envelope.get("approval"))
    except (ImportError, ValueError) as error:
        raise DataLoadError("task-validation", "Task Validation envelope is invalid.") from error
    final_data = payload.get("finalData")
    expected = final_data.get("archiveSha256") if isinstance(final_data, dict) else None
    if not isinstance(expected, str) or not expected.strip():
        raise DataLoadError("task-validation", "Task Validation is missing its required integrity digest.")
    if expected.casefold() != archive_sha256(prepared.content).casefold():
        raise DataLoadError("task-validation", "Task Validation does not match the final prepared archive integrity digest.")
    task_code = payload.get("taskCode")
    if not isinstance(task_code, str) or not task_code.strip():
        raise DataLoadError("task-validation", "Task Validation is missing its required task code.")
    return task_code


def _optional_run_book_task_code(
    prepared: PreparedArchive,
    envelope_path: Path | None,
    run_id: str | None,
    config: dict[str, str],
    *,
    getter: Getter,
) -> str | None:
    """Return the approved Run Book task code when the live action accepts it."""
    if envelope_path is None:
        return None
    task_code = _require_approved_task_validation(prepared, envelope_path)
    if run_id is None:
        return None
    if not _initiate_action_supports_run_book_task_code(config, getter=getter):
        return None
    return task_code


def _approved_artifact(preflight: dict[str, Any]) -> PreparedArchive:
    """Read the exact artifact authorized by preflight without rebuilding it."""
    artifact_path = preflight.get("approvedArtifactPath") or preflight.get("archivePath")
    upload_file_name = preflight.get("uploadFileName")
    expected_digest = preflight.get("archiveSha256")
    if not isinstance(artifact_path, str) or not artifact_path.strip():
        raise DataLoadError("approval", "Approved preflight metadata is missing the artifact path.")
    if not isinstance(upload_file_name, str) or not upload_file_name.strip():
        raise DataLoadError("approval", "Approved preflight metadata is missing the upload filename.")
    if not isinstance(expected_digest, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected_digest):
        raise DataLoadError("approval", "Approved preflight metadata has an invalid artifact integrity value.")
    try:
        content = Path(artifact_path).read_bytes()
    except OSError as error:
        raise DataLoadError("approval", f"Approved upload artifact is unavailable: {artifact_path}") from error
    if not content:
        raise DataLoadError("approval", "Approved upload artifact is empty.")
    if archive_sha256(content).casefold() != expected_digest.casefold():
        raise DataLoadError(
            "approval",
            "The approved upload artifact no longer matches its integrity value. Validate and approve it again.",
        )
    return PreparedArchive(upload_file_name.strip(), content)


def _approved_cx_files(
    artifact: PreparedArchive, entries: Any
) -> tuple[CxImportFile, ...]:
    """Extract the already-approved CX members without repeating source validation."""
    if not isinstance(entries, list) or not entries:
        raise DataLoadError("approval", "Approved CX preflight metadata has no upload files.")
    try:
        with zipfile.ZipFile(io.BytesIO(artifact.content)) as archive:
            names = archive.namelist()
            files: list[CxImportFile] = []
            for entry in entries:
                if not isinstance(entry, dict):
                    raise DataLoadError("approval", "Approved CX file metadata is invalid.")
                member_name = entry.get("memberName")
                file_name = entry.get("fileName")
                role = entry.get("role")
                if (
                    not isinstance(member_name, str)
                    or not member_name
                    or not isinstance(file_name, str)
                    or not file_name
                    or role not in {"Mapping", "Data"}
                    or names.count(member_name) != 1
                ):
                    raise DataLoadError("approval", "Approved CX file metadata does not match the artifact.")
                files.append(
                    CxImportFile(
                        member_name,
                        file_name,
                        archive.read(member_name),
                        role == "Mapping",
                    )
                )
    except (OSError, zipfile.BadZipFile, KeyError) as error:
        raise DataLoadError("approval", "Approved CX artifact cannot be read.") from error
    return tuple(files)


def upload_approved_preflight(
    envelope_path: Path,
    config_path: Path = DEFAULT_CONFIG,
    *,
    run_config_path: Path = DEFAULT_RUN_CONFIG,
    auth_options: dict[str, Any] | None = None,
    task_validation_envelope: Path | None = None,
    poster: Poster = post_json,
    multipart_uploader: MultipartUploader = post_ucm_multipart,
) -> dict[str, Any]:
    """Upload an approved artifact without reopening sources or repeating live validation."""
    preflight = load_preflight_envelope(envelope_path)
    artifact = _approved_artifact(preflight)
    config = read_config(config_path, **(auth_options or {}))
    approved_host = preflight.get("host")
    if not isinstance(approved_host, str) or config["host"] != approved_host:
        raise DataLoadError(
            "approval",
            "The configured Fusion environment no longer matches the approved preflight.",
        )
    approved_environment = preflight.get("environment")
    current_environment = config.get("environment") or config["host"]
    if (
        not isinstance(approved_environment, str)
        or not approved_environment
        or current_environment != approved_environment
    ):
        raise DataLoadError(
            "approval",
            "The configured Fusion environment name no longer matches the approved preflight.",
        )
    run_id = metadata.read_run_id(run_config_path)
    approved_run_id = preflight.get("runID")
    if approved_run_id is not None and not isinstance(approved_run_id, str):
        raise DataLoadError("approval", "Approved preflight metadata has an invalid Run Book context.")
    if run_id != approved_run_id:
        raise DataLoadError(
            "approval",
            "The configured Run Book context no longer matches the approved preflight.",
        )

    task_routed = preflight.get("taskRouted")
    supports_task_code = preflight.get("supportsRunBookTaskCode")
    if not isinstance(task_routed, bool) or not isinstance(supports_task_code, bool):
        raise DataLoadError("approval", "Approved preflight metadata has invalid task routing.")
    if task_routed:
        if task_validation_envelope is None:
            raise DataLoadError(
                "task-validation",
                "Task-routed approved artifacts require an approved Task Validator envelope.",
            )
        task_code = _require_approved_task_validation(artifact, task_validation_envelope)
        run_book_task_code = task_code if run_id is not None and supports_task_code else None
    else:
        raise DataLoadError("task-validation", "Data Loader execution must be task-routed.")

    source_paths = preflight.get("sourcePaths")
    if not isinstance(source_paths, list) or not source_paths or not all(
        isinstance(path, str) and path for path in source_paths
    ):
        raise DataLoadError("approval", "Approved preflight metadata has invalid source identities.")
    source_files = [Path(path).name for path in source_paths]
    source_type = preflight.get("sourceType")
    if source_type not in {None, FSM_SOURCE_TYPE, FBDI_SOURCE_TYPE, CX_IMPORT_SOURCE_TYPE}:
        raise DataLoadError("approval", "Approved preflight metadata has an unsupported source type.")
    cx_import_high_volume_load = preflight.get("cxImportHighVolumeLoad", False)
    if not isinstance(cx_import_high_volume_load, bool):
        raise DataLoadError(
            "approval",
            "Approved preflight metadata has an invalid CX high-volume setting.",
        )
    if cx_import_high_volume_load and source_type != CX_IMPORT_SOURCE_TYPE:
        raise DataLoadError(
            "approval",
            "Approved CX high-volume mode is valid only for CX Import.",
        )
    load_adapter_interface_id = preflight.get("fbdiLoadAdapterInterfaceId")
    if source_type == FBDI_SOURCE_TYPE:
        load_adapter_interface_id = _validated_fbdi_load_adapter_interface_id(
            load_adapter_interface_id,
            stage="approval",
        )
    elif load_adapter_interface_id is not None:
        raise DataLoadError(
            "approval",
            "Approved non-FBDI preflight metadata contains an FBDI load adapter interface ID.",
        )

    if source_type == CX_IMPORT_SOURCE_TYPE:
        object_code = preflight.get("cxImportObjectCode")
        ucm_account = preflight.get("cxUcmAccount")
        if not isinstance(object_code, str) or not object_code.strip():
            raise DataLoadError("approval", "Approved CX preflight metadata is missing the object code.")
        if not isinstance(ucm_account, str) or not ucm_account.strip():
            raise DataLoadError("approval", "Approved CX preflight metadata is missing the UCM account.")
        files = _approved_cx_files(artifact, preflight.get("cxFiles"))
        result = _upload_and_initiate_cx(
            artifact.file_name,
            files,
            config,
            run_id,
            cx_import_object_code=object_code,
            cx_ucm_account=ucm_account,
            poster=poster,
            multipart_uploader=multipart_uploader,
            run_book_task_code=run_book_task_code,
            cx_import_high_volume_load=cx_import_high_volume_load,
            approved_artifact_content=artifact.content,
        )
    else:
        document_account = preflight.get("fbdiUcmAccount") if source_type == FBDI_SOURCE_TYPE else None
        if source_type == FBDI_SOURCE_TYPE and (
            not isinstance(document_account, str) or not document_account.strip()
        ):
            raise DataLoadError("approval", "Approved FBDI preflight metadata is missing the UCM account.")
        result = _upload_and_initiate_prepared(
            artifact,
            config,
            run_id,
            poster=poster,
            multipart_uploader=multipart_uploader,
            run_book_task_code=run_book_task_code,
            source_type=source_type,
            document_account=document_account,
            load_adapter_interface_id=load_adapter_interface_id,
        )
        if source_type == FBDI_SOURCE_TYPE:
            business_object = preflight.get("fbdiBusinessObject")
            if isinstance(business_object, str) and business_object:
                result["businessObject"] = business_object

    result["sourceFiles"] = source_files
    column_mappings = preflight.get("columnMappings")
    result["columnMappings"] = column_mappings if isinstance(column_mappings, list) else []
    return result


def upload_and_initiate(
    source_path: Path,
    config_path: Path = DEFAULT_CONFIG,
    *,
    run_config_path: Path = DEFAULT_RUN_CONFIG,
    auth_options: dict[str, Any] | None = None,
    business_object: str | None = None,
    getter: Getter = get_json,
    byte_getter: ByteGetter = metadata.get_bytes,
    poster: Poster = post_json,
    multipart_uploader: MultipartUploader = post_ucm_multipart,
    progress: ProgressCallback | None = None,
    require_review_archive: bool = False,
    cx_import: bool = False,
    cx_import_object_code: str | None = None,
    cx_import_high_volume_load: bool = False,
    approved_sha256: str | None = None,
    task_routed: bool = True,
    task_validation_envelope: Path | None = None,
    project_review_directory: Path | None = None,
) -> dict[str, Any]:
    if task_routed is not True:
        raise DataLoadError(
            "task-validation",
            "Data Loader execution must be task-routed.",
        )
    suffix = validate_local_source(source_path)
    if (
        task_routed
        and task_validation_envelope is None
        and not getattr(poster, "preflight_only", False)
    ):
        raise DataLoadError(
            "task-validation",
            "Task-routed uploads require an approved Task Validator envelope.",
        )
    if business_object and suffix not in {".csv", ".xlsx", ".zip"}:
        raise DataLoadError(
            "source-selection",
            "--business-object is supported only for a single CSV, XLSX, or FBDI ZIP source.",
        )
    if cx_import and suffix != ".zip":
        raise DataLoadError(
            "source-selection",
            "--cx-import requires exactly one ZIP source.",
        )
    if cx_import_object_code is not None and not cx_import and suffix != ".zip":
        raise DataLoadError(
            "source-selection",
            "--cx-import-object-code is supported only for a CX Import ZIP source.",
        )
    source_type: str | None = None
    fbdi_route: FbdiRoute | None = None
    cx_files: tuple[CxImportFile, ...] | None = None
    resolved_cx_import_object_code: str | None = None
    config: dict[str, str] | None = None
    if suffix == ".zip":
        source_type = archive_source_type(source_path, cx_import=cx_import)
        if business_object and source_type in {FSM_SOURCE_TYPE, CX_IMPORT_SOURCE_TYPE}:
            raise DataLoadError("source-selection", "--business-object cannot select an FSM or CX ZIP.")
        if source_type == CX_IMPORT_SOURCE_TYPE:
            cx_files = validate_cx_import_archive(source_path)
            resolved_cx_import_object_code = resolve_cx_import_object_code(
                cx_files, cx_import_object_code
            )
        elif source_type is None and _archive_contains_csv(source_path):
            config = read_config(config_path, **(auth_options or {}))
            fbdi_route = resolve_fbdi_route(
                source_path,
                config,
                getter=getter,
                business_object=business_object,
            )
            if fbdi_route is not None:
                source_type = FBDI_SOURCE_TYPE
        elif business_object:
            raise DataLoadError(
                "source-selection", "--business-object is supported only for CSV, XLSX, or FBDI ZIP sources."
            )
    if cx_import_high_volume_load and source_type != CX_IMPORT_SOURCE_TYPE:
        raise DataLoadError(
            "source-selection",
            "--cx-import-high-volume-load is supported only for CX Import.",
        )
    if config is None:
        config = read_config(config_path, **(auth_options or {}))
    run_id = metadata.read_run_id(run_config_path)
    if source_type == FBDI_SOURCE_TYPE:
        _fbdi_run_id_value(run_id)
    upload_file_name = (
        source_path.name
        if suffix == ".zip"
        else timestamped_archive_name(source_path.name)
    )
    supports_run_book_task_code = bool(
        task_routed
        and run_id is not None
        and getattr(poster, "preflight_only", False)
        and _initiate_action_supports_run_book_task_code(config, getter=getter)
    )
    schema: metadata.BusinessObjectSchema | None = None
    converted_content: bytes | None = None
    column_mappings: list[metadata.ColumnMapping] = []
    if suffix == ".zip":
        if source_type == CX_IMPORT_SOURCE_TYPE:
            assert cx_files is not None
            assert resolved_cx_import_object_code is not None
            resolved_cx_ucm_account = resolve_cx_ucm_account(
                resolved_cx_import_object_code, config, getter=getter
            )
            prepared = prepare_archive(source_path)
            if getattr(poster, "preflight_only", False):
                _raise_preflight_approval_required(
                    [{"sourceName": source_path.name, "businessObject": "CX Import"}],
                    prepared,
                    (source_path,),
                    source_type=CX_IMPORT_SOURCE_TYPE,
                    cx_files=cx_files,
                    cx_import_object_code=resolved_cx_import_object_code,
                    cx_ucm_account=resolved_cx_ucm_account,
                    cx_import_high_volume_load=cx_import_high_volume_load,
                    upload_file_name=upload_file_name,
                    environment=config.get("environment") or config["host"],
                    host=config["host"],
                    run_id=run_id,
                    task_routed=task_routed,
                    supports_run_book_task_code=supports_run_book_task_code,
                )
            upload_prepared = PreparedArchive(source_path.name, prepared.content)
            run_book_task_code = _optional_run_book_task_code(
                upload_prepared,
                task_validation_envelope,
                run_id,
                config,
                getter=getter,
            )
            result = _upload_and_initiate_cx(
                source_path.name,
                cx_files,
                config,
                run_id,
                cx_import_object_code=resolved_cx_import_object_code,
                cx_ucm_account=resolved_cx_ucm_account,
                poster=poster,
                multipart_uploader=multipart_uploader,
                run_book_task_code=run_book_task_code,
                cx_import_high_volume_load=cx_import_high_volume_load,
                approved_artifact_content=prepared.content,
            )
            result.update(
                {
                    "sourceFiles": [source_path.name],
                    "archiveName": source_path.name,
                    "archiveSha256": archive_sha256(prepared.content),
                }
            )
            return result
        if cx_import_object_code is not None:
            raise DataLoadError(
                "source-selection",
                "--cx-import-object-code is supported only for a CX Import ZIP source.",
            )
        if source_type == FSM_SOURCE_TYPE:
            schemas = ()
        elif source_type == FBDI_SOURCE_TYPE:
            schemas = ()
        else:
            schemas = validate_zip_business_objects(
                source_path, config, getter=getter, byte_getter=byte_getter
            )
    elif suffix == ".xlsx" and progress is not None:
        schema, _converted_content = _validate_xlsx_with_progress(
            source_path,
            config,
            source_index=1,
            source_total=1,
            progress=progress,
            getter=getter,
            byte_getter=byte_getter,
            business_object=business_object,
            mapping_audit=column_mappings,
        )
        converted_content = _converted_content
        schemas = (schema,)
    else:
        schema = validate_file_discriminator(
            source_path,
            config,
            business_object=business_object,
            getter=getter,
            byte_getter=byte_getter,
        )
        converted_content = validate_source_attributes(
            source_path, suffix, schema, business_object=business_object,
            mapping_audit=column_mappings,
        )
        schemas = (schema,)
    if suffix in {".csv", ".xlsx"} and schema is not None and metadata.mapping_preserves_unmapped():
        metadata.save_mapping_review(source_path, schema)
    prepared = prepare_archive(
        source_path,
        xlsx_member_discriminator=(schema.discriminator if suffix == ".xlsx" else None),
        csv_member_discriminator=(schema.discriminator if suffix == ".csv" else None),
        schema=schema,
        converted_content=converted_content,
    )
    mapping_complete = not metadata.mapping_requires_review(column_mappings)
    if not mapping_complete:
        eligible = [
            {"sourceName": source_path.name, "businessObject": item.discriminator}
            for item in schemas
        ]
        _raise_preflight_approval_required(
            eligible,
            prepared,
            (source_path,),
            column_mappings=column_mappings,
            mapping_complete=False,
            source_type=source_type,
            fbdi_route=fbdi_route,
            upload_file_name=upload_file_name,
            environment=config.get("environment") or config["host"],
            host=config["host"],
            run_id=run_id,
            task_routed=task_routed,
            supports_run_book_task_code=supports_run_book_task_code,
        )
    if getattr(poster, "preflight_only", False):
        eligible = (
            [{"sourceName": source_path.name, "businessObject": "FSM Setup"}]
            if source_type == FSM_SOURCE_TYPE
            else [{"sourceName": source_path.name, "businessObject": fbdi_route.business_object}]
            if source_type == FBDI_SOURCE_TYPE and fbdi_route is not None
            else [
                {"sourceName": source_path.name, "businessObject": item.discriminator}
                for item in schemas
            ]
        )
        _raise_preflight_approval_required(
            eligible,
            prepared,
            (source_path,),
            column_mappings=column_mappings,
            mapping_complete=mapping_complete,
            source_type=source_type,
            fbdi_route=fbdi_route,
            upload_file_name=upload_file_name,
            environment=config.get("environment") or config["host"],
            host=config["host"],
            run_id=run_id,
            task_routed=task_routed,
            supports_run_book_task_code=supports_run_book_task_code,
        )
    if require_review_archive and suffix != ".zip":
        require_matching_review_archive(
            prepared,
            source_path.parent,
            project_review_directory=project_review_directory,
        )
    upload_prepared = PreparedArchive(upload_file_name, prepared.content)
    run_book_task_code = _optional_run_book_task_code(
        upload_prepared,
        task_validation_envelope,
        run_id,
        config,
        getter=getter,
    )
    result = _upload_and_initiate_prepared(
        upload_prepared,
        config,
        run_id,
        poster=poster,
        multipart_uploader=multipart_uploader,
        run_book_task_code=run_book_task_code,
        source_type=source_type,
        document_account=fbdi_route.ucm_account if fbdi_route is not None else None,
        load_adapter_interface_id=(
            fbdi_route.load_adapter_interface_id if fbdi_route is not None else None
        ),
    )
    result["sourceFiles"] = [source_path.name]
    result["columnMappings"] = [mapping.__dict__ for mapping in column_mappings]
    if source_type == FBDI_SOURCE_TYPE and fbdi_route is not None:
        result["businessObject"] = fbdi_route.business_object
    return result


def upload_and_initiate_sources(
    source_paths: Iterable[Path],
    config_path: Path = DEFAULT_CONFIG,
    *,
    run_config_path: Path = DEFAULT_RUN_CONFIG,
    auth_options: dict[str, Any] | None = None,
    business_object: str | None = None,
    getter: Getter = get_json,
    byte_getter: ByteGetter = metadata.get_bytes,
    poster: Poster = post_json,
    multipart_uploader: MultipartUploader = post_ucm_multipart,
    progress: ProgressCallback | None = None,
    require_review_archive: bool = False,
    cx_import: bool = False,
    approved_sha256: str | None = None,
    cx_import_object_code: str | None = None,
    cx_import_high_volume_load: bool = False,
    task_routed: bool = True,
    task_validation_envelope: Path | None = None,
    skip_business_objects: Iterable[str] = (),
    project_review_directory: Path | None = None,
) -> dict[str, Any]:
    if task_routed is not True:
        raise DataLoadError(
            "task-validation",
            "Data Loader execution must be task-routed.",
        )
    paths = tuple(source_paths)
    if (
        task_routed
        and task_validation_envelope is None
        and not getattr(poster, "preflight_only", False)
    ):
        raise DataLoadError(
            "task-validation",
            "Task-routed uploads require an approved Task Validator envelope.",
        )
    skipped = tuple(skip_business_objects)
    suffixes = {path.suffix.lower() for path in paths}
    if cx_import and suffixes == {".csv"}:
        if skipped:
            raise DataLoadError(
                "source-selection", "--skip-business-object is not supported for CX Import."
            )
        if business_object:
            raise DataLoadError(
                "source-selection", "--business-object is not supported for CX Import."
            )
        cx_files = validate_cx_import_files(paths)
        resolved_cx_import_object_code = resolve_cx_import_object_code(
            cx_files, cx_import_object_code
        )
        config = read_config(config_path, **(auth_options or {}))
        run_id = metadata.read_run_id(run_config_path)
        supports_run_book_task_code = bool(
            task_routed
            and run_id is not None
            and getattr(poster, "preflight_only", False)
            and _initiate_action_supports_run_book_task_code(config, getter=getter)
        )
        resolved_cx_ucm_account = resolve_cx_ucm_account(
            resolved_cx_import_object_code, config, getter=getter
        )
        approved_artifact = _create_zip(
            (file.member_name, file.content) for file in cx_files
        )
        prepared = PreparedArchive("direct-cx-import-approved.zip", approved_artifact)
        upload_file_name = direct_cx_upload_file_name(cx_files)
        if getattr(poster, "preflight_only", False):
            _raise_preflight_approval_required(
                [{"sourceName": path.name, "businessObject": "CX Import"} for path in paths],
                prepared,
                paths,
                source_type=CX_IMPORT_SOURCE_TYPE,
                cx_files=cx_files,
                cx_import_object_code=resolved_cx_import_object_code,
                cx_ucm_account=resolved_cx_ucm_account,
                cx_import_high_volume_load=cx_import_high_volume_load,
                upload_file_name=upload_file_name,
                environment=config.get("environment") or config["host"],
                host=config["host"],
                run_id=run_id,
                task_routed=task_routed,
                supports_run_book_task_code=supports_run_book_task_code,
                display_archive_name=upload_file_name,
            )
        run_book_task_code = _optional_run_book_task_code(
            prepared,
            task_validation_envelope,
            run_id,
            config,
            getter=getter,
        )
        result = _upload_and_initiate_cx(
            upload_file_name,
            cx_files,
            config,
            run_id,
            cx_import_object_code=resolved_cx_import_object_code,
            cx_ucm_account=resolved_cx_ucm_account,
            poster=poster,
            multipart_uploader=multipart_uploader,
            run_book_task_code=run_book_task_code,
            cx_import_high_volume_load=cx_import_high_volume_load,
            approved_artifact_content=approved_artifact,
        )
        result.update(
            {
                "sourceFiles": [path.name for path in paths],
                "archiveSha256": archive_sha256(approved_artifact),
            }
        )
        return result
    if len(paths) == 1:
        if skipped:
            raise DataLoadError(
                "source-selection",
                "--skip-business-object is supported only for multi-DAT or multi-XLSX submissions.",
            )
        return upload_and_initiate(
            paths[0],
            config_path,
            run_config_path=run_config_path,
            auth_options=auth_options,
            business_object=business_object,
            getter=getter,
            byte_getter=byte_getter,
            poster=poster,
            multipart_uploader=multipart_uploader,
            progress=progress,
            require_review_archive=require_review_archive,
            cx_import=cx_import,
            approved_sha256=approved_sha256,
            cx_import_object_code=cx_import_object_code,
            cx_import_high_volume_load=cx_import_high_volume_load,
            task_routed=task_routed,
            task_validation_envelope=task_validation_envelope,
            project_review_directory=project_review_directory,
        )
    if cx_import_high_volume_load:
        raise DataLoadError(
            "source-selection",
            "--cx-import-high-volume-load is supported only for CX Import.",
        )
    if cx_import:
        raise DataLoadError(
            "source-selection",
            "--cx-import accepts one ZIP source or one or more CSV source files.",
        )
    config = read_config(config_path, **(auth_options or {}))
    cx_paths = tuple(
        path
        for path in paths
        if path.suffix.lower() == ".zip"
        and validate_local_source(path) == ".zip"
        and archive_source_type(path) == CX_IMPORT_SOURCE_TYPE
    )
    if cx_paths:
        raise DataLoadError(
            "source-selection",
            "CX Import accepts exactly one ZIP source and cannot be combined with other files.",
        )
    fbdi_paths = tuple(
        path
        for path in paths
        if path.suffix.lower() == ".zip"
        and validate_local_source(path) == ".zip"
        and archive_source_type(path) is None
        and _archive_contains_csv(path)
        and resolve_fbdi_route(path, config, getter=getter) is not None
    )
    if fbdi_paths:
        raise DataLoadError(
            "source-selection",
            "FBDI accepts exactly one ZIP source and cannot be combined with other files.",
        )
    fsm_paths: tuple[Path, ...] = tuple(
        path
        for path in paths
        if path.suffix.lower() == ".zip"
        and validate_local_source(path) == ".zip"
        and archive_source_type(path) == FSM_SOURCE_TYPE
    )
    non_fsm_paths = tuple(path for path in paths if path not in fsm_paths)
    run_id = metadata.read_run_id(run_config_path)
    supports_run_book_task_code = bool(
        task_routed
        and run_id is not None
        and getattr(poster, "preflight_only", False)
        and _initiate_action_supports_run_book_task_code(config, getter=getter)
    )
    non_fsm_suffixes = {path.suffix.lower() for path in non_fsm_paths}
    if fsm_paths:
        if skipped:
            raise DataLoadError(
                "source-selection",
                "--skip-business-object is not supported for FSM ZIP submissions.",
            )
        if business_object:
            raise DataLoadError(
                "source-selection",
                "--business-object is supported only for a single CSV or XLSX source.",
            )
        if non_fsm_paths and non_fsm_suffixes not in ({".dat"}, {".xlsx"}):
            raise DataLoadError(
                "source-selection",
                "FSM ZIP files may be submitted as separate loads only alongside "
                "one homogeneous .dat or .xlsx group.",
            )
        results: list[dict[str, Any]] = []
        if non_fsm_paths:
            results.append(upload_and_initiate_sources(
                non_fsm_paths,
                config_path,
                run_config_path=run_config_path,
                auth_options=auth_options,
                getter=getter,
                byte_getter=byte_getter,
                poster=poster,
                multipart_uploader=multipart_uploader,
                progress=progress,
                require_review_archive=require_review_archive,
                task_routed=task_routed,
                task_validation_envelope=task_validation_envelope,
                project_review_directory=project_review_directory,
            ))
        for path in fsm_paths:
            results.append(upload_and_initiate(
                path,
                config_path,
                run_config_path=run_config_path,
                auth_options=auth_options,
                getter=getter,
                byte_getter=byte_getter,
                poster=poster,
                multipart_uploader=multipart_uploader,
                progress=progress,
                require_review_archive=require_review_archive,
                task_routed=task_routed,
                task_validation_envelope=task_validation_envelope,
                project_review_directory=project_review_directory,
            ))
        return {"loads": results}

    if len(paths) < 2 or suffixes not in ({".dat"}, {".xlsx"}):
        raise DataLoadError(
            "source-selection",
            "Multiple supplied files can be combined only when every file is a .dat file "
            "or every file is an .xlsx file.",
        )
    if business_object:
        raise DataLoadError(
            "source-selection",
            "--business-object is supported only for a single CSV or XLSX source.",
        )

    if len(set(skipped)) != len(skipped):
        raise DataLoadError(
            "source-selection",
            "Each --skip-business-object discriminator may be supplied only once.",
        )

    contents: list[tuple[str, bytes]] = []
    preflight_eligible: list[dict[str, str]] = []
    column_mappings: list[metadata.ColumnMapping] = []
    if suffixes == {".dat"}:
        member_names = tuple(path.name for path in paths)
        if len(set(member_names)) != len(member_names):
            raise DataLoadError(
                "source-selection",
                "Multiple DAT files must have unique basenames before they can be combined.",
            )
        schemas: list[tuple[Path, metadata.BusinessObjectSchema]] = []
        failures: list[dict[str, Any]] = []
        for path in paths:
            schema: metadata.BusinessObjectSchema | None = None
            try:
                validate_local_source(path)
                schema = validate_file_discriminator(
                    path, config, getter=getter, byte_getter=byte_getter
                )
                validate_source_attributes(path, ".dat", schema)
                schemas.append((path, schema))
            except DataLoadError as error:
                if not _is_skippable_source_validation(error):
                    raise
                business_object_name = (
                    schema.discriminator if schema is not None else path.stem
                )
                failures.append(
                    {
                        "businessObject": business_object_name,
                        "sourceName": path.name,
                        "message": error.message,
                        "mismatchDetails": list(
                            metadata.validation_mismatch_details(error.response)
                        ),
                    }
                )
        _require_confirmed_partial_validation(failures, schemas, skipped)
        contents.extend((path.name, _read_nonempty_file(path)) for path, _schema in schemas)
        preflight_eligible = [
            {"sourceName": path.name, "businessObject": schema.discriminator}
            for path, schema in schemas
        ]
    else:
        schemas: list[tuple[Path, metadata.BusinessObjectSchema, bytes]] = []
        failures: list[dict[str, Any]] = []
        for source_index, path in enumerate(paths, start=1):
            source_column_mappings: list[metadata.ColumnMapping] = []
            try:
                schema, converted_content = _validate_xlsx_with_progress(
                    path,
                    config,
                    source_index=source_index,
                    source_total=len(paths),
                    progress=progress,
                    getter=getter,
                    byte_getter=byte_getter,
                    mapping_audit=source_column_mappings,
                )
                schemas.append((path, schema, converted_content))
                column_mappings.extend(source_column_mappings)
            except DataLoadError as error:
                if not _is_skippable_source_validation(error):
                    raise
                business_object_name = getattr(error, "business_object", None)
                if not business_object_name:
                    raise
                failures.append(
                    {
                        "businessObject": business_object_name,
                        "sourceName": path.name,
                        "message": error.message,
                        "mismatchDetails": list(
                            metadata.validation_mismatch_details(error.response)
                        ),
                    }
                )
        _require_confirmed_partial_validation(failures, schemas, skipped)
        contents.extend(
            (schema.discriminator + ".dat", converted_content)
            for _path, schema, converted_content in schemas
        )
        member_names = tuple(member_name for member_name, _content in contents)
        preflight_eligible = [
            {"sourceName": path.name, "businessObject": schema.discriminator}
            for path, schema, _content in schemas
        ]
        if len(set(member_names)) != len(member_names):
            raise DataLoadError(
                "source-selection",
                "Multiple XLSX files must resolve to unique top-level business-object "
                "discriminators before they can be combined.",
            )

    prepared = PreparedArchive(
        semantic_archive_name((item[1] for item in schemas), contents),
        _create_zip(contents),
    )
    upload_file_name = timestamped_archive_name(MULTI_SOURCE_ARCHIVE_NAME)
    if metadata.mapping_preserves_unmapped() and suffixes == {".xlsx"}:
        for path, schema, _content in schemas:
            metadata.save_mapping_review(path, schema)
    mapping_complete = not metadata.mapping_requires_review(column_mappings)
    if not mapping_complete:
        _raise_preflight_approval_required(
            preflight_eligible,
            prepared,
            paths,
            column_mappings=column_mappings,
            mapping_complete=False,
            upload_file_name=upload_file_name,
            environment=config.get("environment") or config["host"],
            host=config["host"],
            run_id=run_id,
            task_routed=task_routed,
            supports_run_book_task_code=supports_run_book_task_code,
        )
    if getattr(poster, "preflight_only", False):
        _raise_preflight_approval_required(
            preflight_eligible,
            prepared,
            paths,
            column_mappings=column_mappings,
            mapping_complete=mapping_complete,
            upload_file_name=upload_file_name,
            environment=config.get("environment") or config["host"],
            host=config["host"],
            run_id=run_id,
            task_routed=task_routed,
            supports_run_book_task_code=supports_run_book_task_code,
        )
    if require_review_archive:
        require_matching_review_archive(
            prepared,
            paths[0].parent,
            project_review_directory=project_review_directory,
        )
    upload_prepared = PreparedArchive(upload_file_name, prepared.content)
    run_book_task_code = _optional_run_book_task_code(
        upload_prepared,
        task_validation_envelope,
        run_id,
        config,
        getter=getter,
    )
    result = _upload_and_initiate_prepared(
        upload_prepared,
        config,
        run_id,
        poster=poster,
        multipart_uploader=multipart_uploader,
        run_book_task_code=run_book_task_code,
    )
    result.update(
        {
            "sourceFiles": [path.name for path in paths],
            "includedFiles": list(member_names),
            "columnMappings": [mapping.__dict__ for mapping in column_mappings],
        }
    )
    return result


def _require_confirmed_partial_validation(
    failures: list[dict[str, Any]],
    eligible: Iterable[tuple[Any, metadata.BusinessObjectSchema, Any] | tuple[Path, metadata.BusinessObjectSchema]],
    skipped: tuple[str, ...],
) -> None:
    """Require an exact, fresh confirmation before omitting failed sources."""
    if not failures:
        if skipped:
            raise DataLoadError(
                "source-selection",
                "--skip-business-object did not match a currently failed business object.",
            )
        return
    failed_names = tuple(item["businessObject"] for item in failures)
    if len(failed_names) != len(set(failed_names)):
        raise DataLoadError(
            "business-object-validation",
            "Multiple supplied files resolved to the same failed business object; correct the duplicate sources before retrying.",
        )
    if not tuple(eligible):
        raise DataLoadError(
            "business-object-validation",
            "Every supplied business object failed validation. No data was uploaded.",
            response={"partialBusinessObjectValidation": {"failed": failures, "eligible": []}},
        )
    if set(skipped) == set(failed_names) and len(skipped) == len(failed_names):
        return
    raise DataLoadError(
        "partial-business-object-validation",
        "One or more business objects failed validation. No data was uploaded.",
        response={
            "partialBusinessObjectValidation": {
                "failed": failures,
                "eligible": [
                    {
                        "businessObject": item[1].discriminator,
                        "sourceName": item[0].name,
                    }
                    for item in eligible
                ],
                "requiredSkipBusinessObjects": list(failed_names),
            }
        },
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare a registered Fusion HCM, SCM, or ERP ZIP, DAT, TXT, CSV, or XLSX file, upload it to UCM, and initiate IMPORT_AND_LOAD."
    )
    parser.add_argument(
        "source_path",
        nargs="?",
        help="Explicit .zip, .dat, .txt, .csv, or .xlsx path; takes precedence.",
    )
    parser.add_argument(
        "--ide-file",
        action="append",
        default=[],
        help="File shared by the IDE; homogeneous groups of .dat or .xlsx files are combined when no source path is given.",
    )
    metadata.add_oauth_arguments(parser)
    parser.add_argument(
        "--run-config",
        type=Path,
        default=DEFAULT_RUN_CONFIG,
        help=(
            "Optional run ID properties file (default: "
            "core/data-loader/config/env.properties)."
        ),
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        help=(
            "Initialized project/<project_id> workspace used when the source directory "
            "cannot hold the reviewed ZIP."
        ),
    )
    parser.add_argument(
        "--review-output-dir",
        type=Path,
        help=(
            "Explicit writable directory for a validated archive when the source "
            "directory cannot hold it."
        ),
    )
    parser.add_argument(
        "--approve-upload",
        action="store_true",
        help="Internal execution flag for one explicitly user-authorized upload and initiation request.",
    )
    parser.add_argument(
        "--confirm-upload",
        action="store_true",
        help="Submit a retained approved preflight after a later user confirmation.",
    )
    parser.add_argument(
        "--preflight-envelope-output",
        type=Path,
        help="Internal path for retaining validated artifact and routing metadata until later approval.",
    )
    parser.add_argument(
        "--approved-preflight-envelope",
        type=Path,
        help="Internal approved preflight envelope; uploads its exact artifact without source revalidation.",
    )
    parser.add_argument(
        "--cx-import",
        action="store_true",
        help=(
            "Classify the single ZIP source as CX Import; a CSV containing the "
            "required two-table CX mapping signature also enables CX Import automatically."
        ),
    )
    parser.add_argument(
        "--approved-sha256",
        help="Deprecated compatibility option; explicit data-load initiation is the single submission approval.",
    )
    parser.add_argument(
        "--cx-import-object-code",
        help="CX Import ObjectCode for a CX ZIP without a mapping CSV; mapping CSV IMPORT OBJECT is authoritative.",
    )
    parser.add_argument(
        "--cx-import-high-volume-load",
        action="store_true",
        help="Internal flag for an explicitly requested high-volume CX Import.",
    )
    parser.add_argument(
        "--business-object",
        help=(
            "Exact Business Object for a single CSV or XLSX source, or one of the tied FBDI ZIP candidates."
        ),
    )
    parser.add_argument(
        "--mapping-edit", action="append", default=[],
        metavar="SECTION/SOURCE=ATTRIBUTE|exclude",
        help="Resolve one CSV/XLSX mapping review row without changing the source file.",
    )
    parser.add_argument(
        "--accept-mapping-review", action="store_true",
        help="Accept fuzzy mapping candidates and retain unmapped CSV/XLSX columns for validation output.",
    )
    parser.add_argument(
        "--skip-business-object",
        action="append",
        default=[],
        help="Exact failed business-object discriminator to omit after explicit user confirmation; repeat for every failed object.",
    )
    parser.add_argument(
        "--task-routed",
        action="store_true",
        help="Require Task Validator approval for this task-routed upload.",
    )
    parser.add_argument(
        "--task-validation-envelope",
        type=Path,
        help="Approved Task Validator envelope for a task-routed upload.",
    )
    parser.add_argument(
        "--inline-output",
        type=Path,
        help="Deprecated compatibility option; inline HTML rendering is disabled.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source_paths: tuple[Path, ...] = ()
    try:
        if args.confirm_upload and args.approve_upload:
            raise DataLoadError("approval", "Use only one upload authorization mode.")
        if args.confirm_upload and args.approved_preflight_envelope is None:
            raise DataLoadError(
                "approval",
                "--confirm-upload requires a retained approved preflight envelope.",
            )
        if args.approved_preflight_envelope is not None:
            if not (args.confirm_upload or args.approve_upload):
                raise DataLoadError(
                    "approval",
                    "--approved-preflight-envelope requires upload authorization.",
                )
            conflicting = (
                args.source_path
                or args.ide_file
                or args.preflight_envelope_output is not None
                or args.project_root is not None
                or args.review_output_dir is not None
                or args.cx_import
                or args.cx_import_high_volume_load
                or args.approved_sha256 is not None
                or args.cx_import_object_code is not None
                or args.business_object is not None
                or args.mapping_edit
                or args.accept_mapping_review
                or args.skip_business_object
                or args.task_routed
            )
            if conflicting:
                raise DataLoadError(
                    "source-selection",
                    "Approved preflight submission cannot include source, mapping, routing, or review arguments.",
                )
            result = upload_approved_preflight(
                args.approved_preflight_envelope,
                args.properties,
                run_config_path=args.run_config,
                auth_options=metadata.oauth_kwargs(args),
                task_validation_envelope=args.task_validation_envelope,
            )
            for internal_envelope in (
                args.task_validation_envelope,
                args.approved_preflight_envelope,
            ):
                if internal_envelope is None:
                    continue
                try:
                    internal_envelope.unlink()
                except OSError:
                    pass
            data_loader_report.emit_inline_or_markdown(
                result,
                "initiation",
                args.inline_output,
                data_loader_report.render_initiation_report,
                stream=sys.stdout,
            )
            return 0
        if args.preflight_envelope_output is not None and args.approve_upload:
            raise DataLoadError(
                "source-selection",
                "--preflight-envelope-output is only for validation before later approval.",
            )
        if args.project_root is not None and args.review_output_dir is not None:
            raise DataLoadError(
                "artifact-persistence",
                "Use either --project-root or --review-output-dir, not both.",
            )
        project_review_directory = (
            project_review_archive_directory(args.project_root)
            if args.project_root is not None
            else explicit_review_output_directory(args.review_output_dir)
            if args.review_output_dir is not None
            else None
        )
        source_paths = select_sources(args.source_path, args.ide_file, cx_import=args.cx_import)
        overrides: dict[tuple[str, str], str | None] = {}
        for edit in args.mapping_edit:
            if "=" not in edit or "/" not in edit.split("=", 1)[0]:
                raise DataLoadError("mapping", "Mapping edits must use SECTION/SOURCE=ATTRIBUTE or SECTION/SOURCE=exclude.")
            left, target = edit.split("=", 1)
            section, source = (part.strip() for part in left.split("/", 1))
            target = target.strip()
            if not section or not source or not target:
                raise DataLoadError("mapping", "Mapping edits must contain a section, source attribute, and target or exclude.")
            overrides[(section.casefold(), source.casefold())] = None if target.casefold() == "exclude" else target
        metadata.set_mapping_overrides(
            overrides,
            accept_fuzzy=args.accept_mapping_review,
            preserve_unmapped=args.accept_mapping_review,
        )
        xlsx_count = sum(
            1 for source_path in source_paths if source_path.suffix.lower() == ".xlsx"
        )
        progress = (
            cli_validation_progress_reporter(sys.stderr)
            if xlsx_count >= 2
            else None
        )
        upload_arguments: dict[str, Any] = {
            "business_object": args.business_object,
        }
        if args.cx_import:
            upload_arguments["cx_import"] = True
        if args.approved_sha256 is not None:
            upload_arguments["approved_sha256"] = args.approved_sha256
        if args.cx_import_object_code is not None:
            upload_arguments["cx_import_object_code"] = args.cx_import_object_code
        if args.cx_import_high_volume_load:
            upload_arguments["cx_import_high_volume_load"] = True
        if args.skip_business_object:
            upload_arguments["skip_business_objects"] = args.skip_business_object
        if args.task_routed:
            upload_arguments["task_routed"] = True
        if args.task_validation_envelope is not None:
            upload_arguments["task_validation_envelope"] = args.task_validation_envelope
        if progress is not None:
            upload_arguments["progress"] = progress
        upload_arguments["project_review_directory"] = project_review_directory
        if not args.approve_upload:
            upload_arguments["poster"] = _approval_required_after_preflight
        result = upload_and_initiate_sources(
            source_paths,
            args.properties,
            run_config_path=args.run_config,
            auth_options=metadata.oauth_kwargs(args),
            **upload_arguments,
        )
    except DataLoadError as exc:
        if exc.stage == "approval" and hasattr(exc, "prepared_archive"):
            prepared = exc.prepared_archive
            if isinstance(exc.response, dict):
                preflight = exc.response.get("preflight")
                if isinstance(preflight, dict):
                    if preflight.get("mappingComplete") is False:
                        pass
                    elif len(source_paths) == 1 and source_paths[0].suffix.lower() == ".zip":
                        source_path = source_paths[0]
                        preflight["archiveName"] = source_path.name
                        preflight["archivePath"] = str(source_path.resolve())
                        preflight["approvedArtifactPath"] = str(source_path.resolve())
                    else:
                        persisted_archive = prepared
                        upload_file_name = preflight.get("uploadFileName")
                        if (
                            preflight.get("sourceType") != CX_IMPORT_SOURCE_TYPE
                            and isinstance(upload_file_name, str)
                            and upload_file_name.strip()
                        ):
                            persisted_archive = PreparedArchive(
                                upload_file_name.strip(), prepared.content
                            )
                        output_path = persist_prepared_archive(
                            persisted_archive,
                            exc.archive_directory,
                            project_review_directory=project_review_directory,
                        )
                        preflight["archiveName"] = output_path.name
                        preflight["approvedArtifactPath"] = str(output_path)
                        if preflight.get("sourceType") == CX_IMPORT_SOURCE_TYPE:
                            preflight["archiveName"] = upload_file_name
                        else:
                            preflight["archivePath"] = str(output_path)
                    if (
                        args.preflight_envelope_output is not None
                        and preflight.get("mappingComplete") is not False
                        and preflight.get("approvedArtifactPath")
                    ):
                        persist_preflight_envelope(preflight, args.preflight_envelope_output)
        data_loader_report.emit_inline_or_markdown(
            exc,
            "error",
            args.inline_output,
            data_loader_report.render_error_report,
            stream=sys.stderr,
        )
        return 1

    if args.task_validation_envelope is not None:
        try:
            args.task_validation_envelope.unlink()
        except OSError:
            pass
    data_loader_report.emit_inline_or_markdown(
        result,
        "initiation",
        args.inline_output,
        data_loader_report.render_initiation_report,
        stream=sys.stdout,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
