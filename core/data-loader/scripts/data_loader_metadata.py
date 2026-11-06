#!/usr/bin/env python3
"""Shared live metadata, DAT schema, and validation helpers for Fusion Data Loader."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, NamedTuple

BUSINESS_OBJECTS_PATH = "/hcmRestApi/resources/latest/dataLoaderBusinessObjects"
FSCR_BUSINESS_OBJECTS_PATH = "/hcmRestApi/resources/11.13.18.05/dataLoaderBusinessObjects"
FSCR_FINDER = "findBusinessObjectsForFSCR"
PAGE_LIMIT = 500
REST_FRAMEWORK_VERSION_HEADER = "REST-Framework-Version"
REST_FRAMEWORK_VERSION = "9"
ATTRIBUTE_FIELDS = (
    "AttrMapId,BusinessObjectId,HiddenAttr,AttributeName,AttributeType,"
    "AttributeDisplayType,AttributeDatatype,DataType,MandatoryStatus,"
    "UserKeyAttrNames,DataLength,NumberPrecision,AttributeLabel,"
    "AttributeMapKeyReferenceType,IntKeySupported,ReferenceIntObjName,"
    "UserKeyListCountNew,LookupName,Description,MandatoryStatusCode"
)
SOURCE_REFERENCE_ASSIGNMENT = re.compile(
    r"^(SourceRef(?:TableName|\d{3}))=.*$"
)
REFERENCE_KEY_HINT = re.compile(
    r"^([A-Za-z][A-Za-z0-9_]*)\((SourceSystemId|SourceSystemOwner|GUID)\)$"
)
REFERENCE_HEADER_SHAPE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*\s*[()]")
ADF_VO_HDL_PARAMETERS = frozenset({
    "ReplaceFirstEffectiveStartDate",
    "ReplaceLastEffectiveEndDate",
})


def _find_fdos_root() -> Path:
    configured_root = os.environ.get("FDOS_ROOT")
    starts = [
        Path(__file__).resolve(),
        Path.cwd().resolve(),
    ]
    if configured_root:
        starts.insert(0, Path(configured_root).expanduser().resolve())
    for start in starts:
        for candidate in (start, *start.parents):
            if (
                (candidate / "core" / "auth" / "fusionEnv.properties").is_file()
                and (
                    candidate
                    / "core"
                    / "auth"
                    / "fusion-oauth-authentication"
                    / "scripts"
                    / "fusion_auth.py"
                ).is_file()
            ):
                return candidate
    raise RuntimeError(
        "Could not locate the repository root. Set FDOS_ROOT or pass "
        "--properties and --run-config explicitly."
    )


FDOS_ROOT = _find_fdos_root()
AUTH_SCRIPTS_PATH = (
    FDOS_ROOT / "core" / "auth" / "fusion-oauth-authentication" / "scripts"
)
if str(AUTH_SCRIPTS_PATH) not in sys.path:
    sys.path.insert(0, str(AUTH_SCRIPTS_PATH))

from fusion_auth import (
    authorized_urlopen, request_context, require_authorized_rest_url, BoundAccessToken,  # noqa: E402
    DEFAULT_CALLBACK_TIMEOUT_SECONDS,
    get_access_token,
    read_properties,
    require_props,
)


DEFAULT_PROPERTIES = FDOS_ROOT / "core" / "auth" / "fusionEnv.properties"
DEFAULT_RUN_CONFIG = FDOS_ROOT / "core" / "data-loader" / "config" / "env.properties"
# Retain the old constant name for Python callers while changing its meaning to
# the central OAuth properties file.
DEFAULT_CONFIG = DEFAULT_PROPERTIES


class DataLoadError(Exception):
    def __init__(
        self,
        stage: str,
        message: str,
        *,
        http_status: int | None = None,
        response: Any = None,
        content_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.stage = stage
        self.message = message
        self.http_status = http_status
        self.response = response
        self.content_id = content_id

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"stage": self.stage, "error": self.message}
        if self.http_status is not None:
            result["httpStatus"] = self.http_status
        if self.content_id:
            result["ContentId"] = self.content_id
        if self.response is not None:
            result["response"] = self.response
        return result


@dataclass(frozen=True)
class TemplateAttribute:
    raw_name: str
    name: str


@dataclass(frozen=True)
class TemplateSection:
    discriminator: str
    attributes: tuple[TemplateAttribute, ...]

    @property
    def attribute_names(self) -> tuple[str, ...]:
        return tuple(attribute.name for attribute in self.attributes)

    def raw_name_for(self, name: str) -> str:
        for attribute in self.attributes:
            if attribute.name == name:
                return attribute.raw_name
        raise KeyError(name)


@dataclass(frozen=True)
class SourceSection:
    discriminator: str
    attributes: tuple[str, ...]


@dataclass(frozen=True)
class ColumnMapping:
    section: str
    source_column: str
    target_attribute: str | None
    match_rule: str | None = None
    reason: str | None = None
    confidence: float | None = None
    status: str | None = None


_MAPPING_OVERRIDES: dict[tuple[str, str], str | None] = {}
_MAPPING_ACCEPT_FUZZY = False
_MAPPING_PRESERVE_UNMAPPED = False
MAPPING_REVIEW_VERSION = 1
MAPPING_REVIEW_DIRECTORY = ".data-loader-mapping-reviews"


def schema_fingerprint(schema: "BusinessObjectSchema") -> str:
    payload = {"businessObject": schema.discriminator, "sections": [
        {"discriminator": section.discriminator, "attributes": list(section.attribute_names)}
        for section in schema.sections
    ]}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def set_mapping_overrides(
    overrides: dict[tuple[str, str], str | None], *, accept_fuzzy: bool = False,
    preserve_unmapped: bool = False,
) -> None:
    global _MAPPING_ACCEPT_FUZZY, _MAPPING_PRESERVE_UNMAPPED
    _MAPPING_OVERRIDES.clear()
    _MAPPING_OVERRIDES.update({(section.casefold(), source.casefold()): target for (section, source), target in overrides.items()})
    _MAPPING_ACCEPT_FUZZY = accept_fuzzy
    _MAPPING_PRESERVE_UNMAPPED = preserve_unmapped


def mapping_preserves_unmapped() -> bool:
    return _MAPPING_PRESERVE_UNMAPPED


def mapping_requires_review(mappings: Iterable[ColumnMapping]) -> bool:
    return any(
        mapping.status == "unmapped"
        or (
            mapping.status == "fuzzy"
            and (mapping.confidence is None or mapping.confidence < 1.0)
        )
        for mapping in mappings
    )


def mapping_review_path(source_path: Path, *, fallback_root: Path | None = None) -> Path:
    key = hashlib.sha256(str(source_path.resolve()).encode()).hexdigest()[:16]
    source_directory = source_path.parent / MAPPING_REVIEW_DIRECTORY
    try:
        source_directory.mkdir(mode=0o700, exist_ok=True)
        if os.access(source_directory, os.W_OK):
            return source_directory / f"{key}.json"
    except OSError:
        pass
    root = fallback_root or (FDOS_ROOT / MAPPING_REVIEW_DIRECTORY)
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    return root / f"{key}.json"


def save_mapping_review(
    source_path: Path, schema: "BusinessObjectSchema", *, fallback_root: Path | None = None,
) -> Path:
    path = mapping_review_path(source_path, fallback_root=fallback_root)
    payload = {
        "version": MAPPING_REVIEW_VERSION,
        "sourceSha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
        "schemaFingerprint": schema_fingerprint(schema),
        "mappings": [{"section": section, "source": source, "target": target} for (section, source), target in sorted(_MAPPING_OVERRIDES.items())],
        "acceptFuzzy": _MAPPING_ACCEPT_FUZZY,
        "preserveUnmapped": _MAPPING_PRESERVE_UNMAPPED,
    }
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.chmod(temporary, 0o600)
    os.replace(temporary, path)
    return path.resolve()


# Deliberately small, reusable aliases. A target is accepted only when it is a
# live attribute of the section currently being converted.
COLUMN_ATTRIBUTE_ALIASES: dict[str, tuple[str, ...]] = {
    "orgcode": ("OrganizationCode",),
    "code": ("UOMCode",),
    "orgname": ("OrganizationName",),
    "organization": ("OrganizationName",),
    "businessunit": ("ManagementBusinessUnitName",),
    "managementbu": ("ManagementBusinessUnitName",),
    "profitcenterbu": ("ProfitCenterBusinessUnitName",),
    "legalentity": ("LegalEntityName",),
    "action": ("RestAction",),
    "classfrom": ("UOMClassCode",),
    "baseto": ("BaseUnitFlag",),
    "unitofmeasure": ("BaseUnitOfMeasure",),
    "description": ("ClassDescription",),
}


@dataclass(frozen=True)
class BusinessObjectSchema:
    business_object_id: str
    discriminator: str
    ui_name: str
    ucm_content_id: str
    template_file_name: str
    sections: tuple[TemplateSection, ...]
    components: dict[str, dict[str, Any]]
    attributes: dict[str, tuple[dict[str, Any], ...]]
    schema_source: str = "UCM_TEMPLATE"
    object_type: str = ""

    @property
    def sections_by_discriminator(self) -> dict[str, TemplateSection]:
        return {section.discriminator: section for section in self.sections}


class SchemaProgressEvent(NamedTuple):
    event: str
    business_object: str


Getter = Callable[..., Any]
ByteGetter = Callable[..., bytes]
SchemaProgressCallback = Callable[[SchemaProgressEvent], None]


@dataclass
class OAuthSession:
    properties: dict[str, str]
    explicit_access_token: str | None = None
    auth_code: str | None = None
    redirect_url: str | None = None
    callback_timeout: int = DEFAULT_CALLBACK_TIMEOUT_SECONDS
    token_cache: str | None = None
    force_login: bool = False
    open_browser: bool = True
    _access_token: str | None = None

    def __post_init__(self) -> None:
        self.properties = dict(self.properties)
        self.context = request_context(self.properties)

    def token(self, *, refresh: bool = False) -> str:
        if request_context(self.properties) != self.context:
            raise ValueError("OAuth session service context changed")
        if self.explicit_access_token and not refresh:
            return BoundAccessToken(self.explicit_access_token, self.context)
        if self._access_token is not None and not refresh:
            return self._access_token
        self._access_token = get_access_token(
            self.properties,
            redirect_url=self.redirect_url,
            auth_code=self.auth_code,
            open_browser=self.open_browser,
            callback_timeout=self.callback_timeout,
            token_cache=self.token_cache,
            force_login=self.force_login or refresh,
        )
        return self._access_token

    def secrets(self) -> tuple[str, ...]:
        return tuple(
            value
            for value in (
                self.explicit_access_token,
                self._access_token,
                self.properties.get("clientSecret"),
            )
            if value
        )


def read_config(
    path: Path = DEFAULT_PROPERTIES,
    *,
    access_token: str | None = None,
    auth_code: str | None = None,
    redirect_url: str | None = None,
    callback_timeout: int = DEFAULT_CALLBACK_TIMEOUT_SECONDS,
    token_cache: str | None = None,
    force_login: bool = False,
    open_browser: bool = True,
) -> dict[str, Any]:
    try:
        values = read_properties(path)
        require_props(values, ["environment", "restBaseUrl"])
    except (OSError, ValueError) as exc:
        raise DataLoadError("configuration", f"Unable to read config: {path}: {exc}") from exc

    return {
        "environment": values["environment"].strip(),
        "host": values["restBaseUrl"].rstrip("/"),
        "auth": OAuthSession(
            values,
            explicit_access_token=access_token,
            auth_code=auth_code,
            redirect_url=redirect_url,
            callback_timeout=callback_timeout,
            token_cache=token_cache,
            force_login=force_login,
            open_browser=open_browser,
        ),
    }


def read_run_id(path: Path = DEFAULT_RUN_CONFIG) -> str | None:
    try:
        values = read_properties(path)
    except (OSError, ValueError) as exc:
        raise DataLoadError(
            "configuration", f"Unable to read run ID config: {path}: {exc}"
    ) from exc
    return values.get("runID", "").strip() or None


def add_oauth_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--properties",
        "--config",
        dest="properties",
        type=Path,
        default=DEFAULT_PROPERTIES,
        help=(
            "Fusion OAuth properties file (default: "
            "core/auth/fusionEnv.properties). --config is a compatibility alias."
        ),
    )
    parser.add_argument(
        "--access-token",
        help="Existing Fusion bearer token; never written to output.",
    )
    parser.add_argument("--auth-code", help="OAuth authorization code.")
    parser.add_argument("--redirect-url", help="OAuth redirect URL override.")
    parser.add_argument(
        "--callback-timeout",
        type=int,
        default=DEFAULT_CALLBACK_TIMEOUT_SECONDS,
        help="Seconds to wait for the OAuth callback.",
    )
    parser.add_argument(
        "--token-cache",
        help=(
            "Optional token-cache path. By default the core OAuth service uses "
            "macOS Keychain with a ~/.fusionaim fallback."
        ),
    )
    parser.add_argument(
        "--force-login",
        action="store_true",
        help="Ignore a cached token and perform OAuth login.",
    )
    parser.add_argument(
        "--open-browser",
        action="store_true",
        default=True,
        help="Open the OAuth login URL when authentication is required.",
    )
    parser.add_argument(
        "--no-open-browser",
        action="store_false",
        dest="open_browser",
        help="Print the OAuth login URL without opening a browser.",
    )


def oauth_kwargs(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "access_token": args.access_token,
        "auth_code": args.auth_code,
        "redirect_url": args.redirect_url,
        "callback_timeout": args.callback_timeout,
        "token_cache": args.token_cache,
        "force_login": args.force_login,
        "open_browser": args.open_browser,
    }


def redact_sensitive(value: Any, secrets: Iterable[str]) -> Any:
    active_secrets = [secret for secret in secrets if secret]
    if isinstance(value, str):
        redacted = value
        for secret in active_secrets:
            redacted = redacted.replace(secret, "<redacted>")
        return redacted
    if isinstance(value, list):
        return [redact_sensitive(item, active_secrets) for item in value]
    if isinstance(value, dict):
        return {
            key: redact_sensitive(item, active_secrets) for key, item in value.items()
        }
    return value


def _decode_json(body: bytes, stage: str, secrets: Iterable[str]) -> Any:
    text = body.decode("utf-8", errors="replace")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise DataLoadError(
            stage,
            "Server returned a malformed JSON response.",
            response=redact_sensitive(text, secrets),
        ) from exc


def _request_bytes(
    url: str,
    auth: OAuthSession,
    *,
    stage: str,
    accept: str,
    method: str = "GET",
    data: bytes | None = None,
    content_type: str | None = None,
    sensitive_values: Iterable[str] = (),
    refresh_http_statuses: frozenset[int] = frozenset({401, 403}),
) -> bytes:
    context = auth.context
    require_authorized_rest_url(context, url)
    extra_secrets = tuple(value for value in sensitive_values if value)
    for attempt in range(2):
        try:
            token = auth.token(refresh=attempt == 1)
        except Exception as exc:
            message = redact_sensitive(str(exc), auth.secrets())
            raise DataLoadError(
                "authentication", f"OAuth authentication failed: {message}"
            ) from exc
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": accept,
            REST_FRAMEWORK_VERSION_HEADER: REST_FRAMEWORK_VERSION,
        }
        if content_type:
            headers["Content-Type"] = content_type
        request = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers=headers,
        )
        try:
            with authorized_urlopen(context, request, timeout=120, access_token=token) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            response_body = exc.read()
            if exc.code in refresh_http_statuses and attempt == 0:
                continue
            secrets = auth.secrets() + extra_secrets
            try:
                parsed = _decode_json(response_body, stage, secrets)
            except DataLoadError:
                parsed = redact_sensitive(
                    response_body.decode("utf-8", errors="replace"),
                    secrets,
                )
            else:
                parsed = redact_sensitive(parsed, secrets)
            raise DataLoadError(
                stage,
                f"HTTP request failed with status {exc.code}.",
                http_status=exc.code,
                response=parsed,
            ) from exc
        except urllib.error.URLError as exc:
            raise DataLoadError(stage, f"HTTP request failed: {exc.reason}") from exc
        except TimeoutError as exc:
            raise DataLoadError(stage, "HTTP request timed out after 120 seconds.") from exc
    raise AssertionError("OAuth request retry loop did not terminate")


def request_json(
    url: str,
    auth: OAuthSession,
    *,
    stage: str,
    method: str = "GET",
    data: bytes | None = None,
    content_type: str | None = None,
    sensitive_values: Iterable[str] = (),
    refresh_http_statuses: frozenset[int] = frozenset({401, 403}),
) -> Any:
    body = _request_bytes(
        url,
        auth,
        stage=stage,
        accept="application/json",
        method=method,
        data=data,
        content_type=content_type,
        sensitive_values=sensitive_values,
        refresh_http_statuses=refresh_http_statuses,
    )
    return _decode_json(body, stage, auth.secrets() + tuple(sensitive_values))


def request_json_or_empty(
    url: str,
    auth: OAuthSession,
    *,
    stage: str,
    method: str = "GET",
    data: bytes | None = None,
    content_type: str | None = None,
    sensitive_values: Iterable[str] = (),
) -> Any:
    """Return a JSON response, accepting an empty successful action response."""
    body = _request_bytes(
        url,
        auth,
        stage=stage,
        accept="application/json",
        method=method,
        data=data,
        content_type=content_type,
        sensitive_values=sensitive_values,
    )
    if not body.strip():
        return {}
    return _decode_json(body, stage, auth.secrets() + tuple(sensitive_values))


def get_json(url: str, auth: OAuthSession, *, stage: str) -> Any:
    return request_json(url, auth, stage=stage)


def get_bytes(url: str, auth: OAuthSession, *, stage: str) -> bytes:
    return _request_bytes(url, auth, stage=stage, accept="*/*")


def discriminator_from_item(item: dict[str, Any]) -> str:
    """Return the registered parent discriminator from its REST attribute."""
    value = item.get("BusObjTopDiscriminator")
    return str(value).strip() if value not in (None, "") else ""


def component_discriminator_from_item(item: dict[str, Any]) -> str:
    """Return the component discriminator from its REST attribute."""
    value = item.get("BusObjFileDiscriminator")
    return str(value).strip() if value not in (None, "") else ""


def normalized_name(value: Any) -> str:
    return "".join(character.lower() for character in str(value or "") if character.isalnum())


def is_supported_reference_hint(section: str, header: str, schema: BusinessObjectSchema) -> bool:
    """Permit HDL key hints only on live ADF VO parent or foreign references."""
    match = REFERENCE_KEY_HINT.fullmatch(header)
    if match is None or schema.object_type != "ADF_VO":
        return False
    base_name = match.group(1)
    template = schema.sections_by_discriminator.get(section)
    if template is None or base_name not in template.attribute_names:
        return False
    details = next((item for item in schema.attributes.get(section, ())
                    if normalize_attribute_name(str(item.get("AttributeName") or "")) == base_name), None)
    if details is None:
        return False
    reference_type = str(details.get("AttributeMapKeyReferenceType") or "").upper()
    return (
        ("PARENT" in reference_type or "FOREIGN" in reference_type or "REFERENCE" in reference_type)
        and "LOCAL" not in reference_type
        and str(details.get("ReferenceIntObjName") or "").strip() != ""
        and str(details.get("IntKeySupported") or "").strip().lower() == "yes"
    )


def is_supported_source_attribute(section: str, header: str, schema: BusinessObjectSchema) -> bool:
    """Check UCM headers and supported virtual HDL parameters and references."""
    if normalized_name(header) == "dataloaderaction":
        return False
    template = schema.sections_by_discriminator.get(section)
    if template is None:
        return False
    if header in template.attribute_names and REFERENCE_KEY_HINT.fullmatch(header) is None:
        return True
    if header in ADF_VO_HDL_PARAMETERS:
        return schema.object_type == "ADF_VO"
    if REFERENCE_HEADER_SHAPE.match(header):
        return is_supported_reference_hint(section, header, schema)
    return False


def map_source_headers(
    section: str,
    headers: Iterable[str],
    schema: BusinessObjectSchema,
) -> tuple[tuple[str, ...], tuple[int, ...], tuple[ColumnMapping, ...]]:
    """Resolve headers and retain reviewable mappings until explicitly accepted."""
    header_values = tuple(str(header or "").strip() for header in headers)
    template = schema.sections_by_discriminator.get(section)
    if template is None:
        return header_values, tuple(range(len(header_values))), ()
    live = set(template.attribute_names)
    details = schema.attributes.get(section) or ()
    labels: dict[str, set[str]] = {}
    for item in details:
        name = normalize_attribute_name(str(item.get("AttributeName") or ""))
        label = normalized_name(item.get("AttributeLabel"))
        if name in live and label:
            labels.setdefault(label, set()).add(name)

    catalog = {normalize_attribute_name(str(item.get("AttributeName") or "")): item for item in details}
    resolved: list[tuple[int, str, str, str, float | None, str]] = []
    ignored: list[ColumnMapping] = []
    for index, header in enumerate(header_values, start=1):
        source = header or f"Column {index} (blank header)"
        normalized = normalize_attribute_name(header)
        if normalized_name(normalized) == "dataloaderaction":
            raise DataLoadError("file-validation", "DataLoaderAction is a workbook-only control column.")
        if normalized in ADF_VO_HDL_PARAMETERS and is_supported_source_attribute(section, normalized, schema):
            resolved.append((index - 1, source, normalized, "Exact HDL parameter", 1.0, "exact"))
            continue
        if normalized not in live and normalized_name(normalized).startswith(
            ("replacefirsteffective", "replacelasteffective")
        ):
            raise DataLoadError(
                "file-validation",
                f"Section {section} contains attribute(s) not present in the UCM template: {normalized}.",
            )
        if REFERENCE_HEADER_SHAPE.match(normalized) and (
            normalized not in live or REFERENCE_KEY_HINT.fullmatch(normalized) is not None
        ):
            if not is_supported_reference_hint(section, normalized, schema):
                raise DataLoadError(
                    "file-validation",
                    f"Section {section} contains attribute(s) not present in the UCM template: {normalized}.",
                )
            resolved.append((index - 1, source, normalized, "Exact HDL reference hint", 1.0, "exact"))
            continue
        target: str | None = None
        rule: str | None = None
        override = _MAPPING_OVERRIDES.get((section.casefold(), source.casefold()), "__missing__")
        confidence: float | None = None
        status = "exact"
        if override != "__missing__":
            if override is None:
                ignored.append(ColumnMapping(section, source, None, reason="User excluded source attribute", confidence=1.0, status="excluded"))
                continue
            if override not in live:
                raise DataLoadError("mapping", f"User mapping is not a live attribute: {override}")
            target, rule, confidence, status = override, "User mapping", 1.0, "manual"
        elif normalized in live:
            target, rule, confidence = normalized, "Exact attribute", 1.0
        else:
            technical = [name for name in live if normalized_name(name) == normalized_name(header)]
            if len(technical) == 1:
                target, rule, confidence = technical[0], "Normalized attribute", 1.0
            elif len(labels.get(normalized_name(header), set())) == 1:
                target, rule, confidence = next(iter(labels[normalized_name(header)])), "Attribute label", 1.0
            else:
                aliases = [name for name in COLUMN_ATTRIBUTE_ALIASES.get(normalized_name(header), ()) if name in live]
                if len(aliases) == 1:
                    target, rule, confidence, status = aliases[0], "Glossary alias", 0.89, "fuzzy"
                else:
                    header_tokens = set(re.findall(r"[a-z0-9]+", header.casefold()))
                    candidates: list[tuple[float, str]] = []
                    for name, item in catalog.items():
                        if name not in live:
                            continue
                        label = str(item.get("AttributeLabel") or "")
                        description = str(item.get("Description") or "")
                        base = max(difflib.SequenceMatcher(None, normalized_name(header), normalized_name(name)).ratio(), difflib.SequenceMatcher(None, normalized_name(header), normalized_name(label)).ratio())
                        description_tokens = set(re.findall(r"[a-z0-9]+", description.casefold()))
                        score = min(1.0, base * 0.86 + (len(header_tokens & description_tokens) / max(1, len(header_tokens))) * 0.14)
                        candidates.append((score, name))
                    candidates.sort(reverse=True)
                    if candidates and candidates[0][0] >= 0.68 and (len(candidates) == 1 or candidates[0][0] - candidates[1][0] >= 0.08):
                        target, rule, confidence, status = candidates[0][1], "Semantic match", candidates[0][0], "fuzzy"
        if target is None:
            if _MAPPING_PRESERVE_UNMAPPED:
                resolved.append((index - 1, source, header, "Unmapped", 0.0, "unmapped"))
            else:
                ignored.append(ColumnMapping(section, source, None, reason="No safe live attribute mapping", confidence=0.0, status="unmapped"))
        else:
            if status == "fuzzy" and not _MAPPING_ACCEPT_FUZZY:
                resolved.append((index - 1, source, target, rule or "", confidence, "fuzzy"))
            else:
                approved_status = "approved-fuzzy" if status == "fuzzy" else status
                resolved.append((index - 1, source, target, rule or "", confidence, approved_status))

    retained: list[tuple[int, str, str, str, float | None, str]] = []
    by_target: dict[str, list[tuple[int, str, str, str, float | None, str]]] = {}
    for item in resolved:
        by_target.setdefault(item[2], []).append(item)
    for target, matches in by_target.items():
        if target not in live:
            retained.extend(matches)
            continue
        exact = [item for item in matches if item[3] == "Exact attribute"]
        inferred = [item for item in matches if item[3] != "Exact attribute"]
        if exact and inferred:
            retained.extend(exact)
            ignored.extend(
                ColumnMapping(section, item[1], None, reason=f"Exact header already supplies {target}", confidence=0.0, status="unmapped")
                for item in inferred
            )
        elif len(matches) > 1:
            raise DataLoadError(
                "file-validation",
                f"Section {section} has multiple columns mapped to {target}: "
                + ", ".join(item[1] for item in matches),
            )
        else:
            retained.extend(matches)
    retained.sort(key=lambda item: item[0])
    mappings = [
        ColumnMapping(section, source, target if status != "unmapped" else None, rule, confidence=confidence, status=status)
        for _index, source, target, rule, confidence, status in retained
    ]
    return (
        tuple(target for _index, _source, target, _rule, _confidence, _status in retained),
        tuple(index for index, _source, _target, _rule, _confidence, _status in retained),
        tuple(mappings + ignored),
    )


def normalize_attribute_name(value: str) -> str:
    token = value.strip()
    match = SOURCE_REFERENCE_ASSIGNMENT.fullmatch(token)
    return match.group(1) if match else token


_STANDARD_WHO_COLUMNS = frozenset(
    {
        "createdby",
        "creationdate",
        "lastupdatedby",
        "lastupdatedate",
    }
)


def is_standard_who_column(name: str) -> bool:
    """Return whether *name* is one of the standard Fusion audit attributes."""
    return normalize_attribute_name(name).casefold() in _STANDARD_WHO_COLUMNS


def _validated_page(response: Any, *, offset: int, label: str) -> tuple[list[Any], bool]:
    if not isinstance(response, dict):
        raise DataLoadError(
            "business-object-validation", f"{label} returned a malformed response object."
        )
    items = response.get("items")
    has_more = response.get("hasMore")
    if not isinstance(items, list) or not isinstance(has_more, bool):
        raise DataLoadError(
            "business-object-validation",
            f"{label} response must contain an items array and boolean hasMore value.",
            response={"offset": offset},
        )
    return items, has_more


def _escape_like_value(value: str) -> str:
    """Escape string-literal quotes and LIKE wildcards for a Fusion q= filter."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_").replace("'", "''")


def _business_object_lookup_filter(lookup_value: str) -> str:
    escaped_value = _escape_like_value(lookup_value.strip())
    if not escaped_value:
        raise DataLoadError(
            "business-object-validation", "Business-object lookup value must not be blank."
        )
    pattern = f"'%{escaped_value}%' ESCAPE '\\'"
    return (
        "ProductAreaCode is not null AND ("
        f"BusObjTopDiscriminator LIKE {pattern} OR "
        f"TemplateFileName LIKE {pattern} OR "
        f"UIName LIKE {pattern}"
        ")"
    )


def find_business_objects(
    config: dict[str, str], lookup_value: str, *, getter: Getter = get_json,
    top_discriminator_prefix: bool = False,
    sample_attribute_lookup: bool = False,
) -> list[dict[str, Any]]:
    offset = 0
    results: list[dict[str, Any]] = []
    if top_discriminator_prefix or sample_attribute_lookup:
        escaped_value = _escape_like_value(lookup_value.strip())
        if not escaped_value:
            raise DataLoadError(
                "business-object-validation", "Business-object lookup value must not be blank."
            )
        lookup_filter = f"BusObjTopDiscriminator LIKE '{escaped_value}%'"
        if "\\" in escaped_value:
            lookup_filter += " ESCAPE '\\'"
        if sample_attribute_lookup:
            ui_filter = f"UIName LIKE '{escaped_value}%'"
            if "\\" in escaped_value:
                ui_filter += " ESCAPE '\\'"
            lookup_filter += " OR " + ui_filter
    else:
        lookup_filter = _business_object_lookup_filter(lookup_value)
    while True:
        query_params = {
            "onlyData": "true",
            "offset": str(offset),
            "q": lookup_filter,
        }
        if not top_discriminator_prefix and not sample_attribute_lookup:
            query_params["finder"] = "findDataLoaderBos"
        query = urllib.parse.urlencode(query_params)
        response = getter(
            config["host"] + BUSINESS_OBJECTS_PATH + "?" + query,
            config["auth"],
            stage="business-object-validation",
        )
        items, has_more = _validated_page(
            response, offset=offset, label="Business-object finder"
        )
        for item in items:
            if not isinstance(item, dict):
                raise DataLoadError(
                    "business-object-validation",
                    "Business-object finder returned a non-object item.",
                    response={"offset": offset},
                )
            if not discriminator_from_item(item):
                raise DataLoadError(
                    "business-object-validation",
                    "Business-object finder item did not contain BusObjTopDiscriminator.",
                    response={"offset": offset},
                )
            results.append(item)
        if not has_more:
            return results
        if not items:
            raise DataLoadError(
                "business-object-validation",
                "Business-object finder pagination did not advance.",
                response={"offset": offset},
            )
        offset += len(items)


def resolve_business_object(
    query_value: str,
    config: dict[str, str],
    *,
    allow_aliases: bool,
    getter: Getter = get_json,
    sample_attribute_lookup: bool = False,
) -> dict[str, Any]:
    items = find_business_objects(
        config, query_value, getter=getter, sample_attribute_lookup=sample_attribute_lookup
    )
    exact = [item for item in items if discriminator_from_item(item) == query_value]
    matches = exact
    if not matches and allow_aliases:
        normalized_query = normalized_name(query_value)
        matches = [
            item
            for item in items
            if normalized_query
            and normalized_query
            in {
                normalized_name(discriminator_from_item(item)),
                normalized_name(Path(str(item.get("TemplateFileName") or "")).stem),
                normalized_name(item.get("UIName")),
            }
        ]

    # The finder can repeat an unchanged business-object record across pages.
    # Treat identical registered identities as one candidate, while preserving
    # ambiguity when the registry genuinely identifies different objects.
    unique_matches: list[dict[str, Any]] = []
    seen_identities: set[tuple[str, str]] = set()
    for item in matches:
        business_object_id = str(item.get("BusinessObjectId") or "")
        identity = (business_object_id, discriminator_from_item(item))
        # An absent identity is not evidence that two finder records are the
        # same object, so leave it available for the normal ambiguity check.
        if not business_object_id or identity not in seen_identities:
            seen_identities.add(identity)
            unique_matches.append(item)
    matches = unique_matches

    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        candidates = [
            {
                "BusinessObjectId": item.get("BusinessObjectId"),
                "discriminator": discriminator_from_item(item),
                "UIName": item.get("UIName"),
            }
            for item in matches
        ]
        raise DataLoadError(
            "business-object-validation",
            (
                f"Business-object lookup returned multiple exact matches for {query_value}."
                if exact
                else f"Business-object lookup returned multiple matches for {query_value}."
            ),
            response={"candidates": candidates},
        )

    suggestions: set[str] = set()
    normalized_query = normalized_name(query_value)
    for item in items:
        template_stem = Path(str(item.get("TemplateFileName") or "")).stem
        if normalized_query and normalized_query in {
            normalized_name(template_stem),
            normalized_name(item.get("UIName")),
        }:
            suggestions.add(discriminator_from_item(item))
    message = f"No exact business-object file discriminator matched {query_value}."
    if suggestions:
        message += " Candidate discriminator(s): " + ", ".join(sorted(suggestions)) + "."
    raise DataLoadError("business-object-validation", message)


def refresh_fscr_business_object(
    match: dict[str, Any], config: dict[str, str], *, getter: Getter = get_json
) -> dict[str, Any]:
    """Update object attributes once and return refreshed metadata when advertised.

    An unavailable finder or empty result returns the original object unchanged.
    The finder has side effects even though its transport method is GET.
    """
    stage = "business-object-validation"
    describe = getter(
        config["host"] + FSCR_BUSINESS_OBJECTS_PATH + "/describe",
        config["auth"], stage=stage,
    )
    if not isinstance(describe, dict):
        raise DataLoadError(stage, "Business-object describe returned a malformed response.")
    resources = describe.get("Resources", describe.get("resources"))
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
        raise DataLoadError(stage, "Business-object describe did not identify dataLoaderBusinessObjects.")
    collection = resource.get("collection", {})
    if not isinstance(collection, dict):
        raise DataLoadError(stage, "Business-object describe returned malformed collection metadata.")
    finders = collection.get(
        "finders", collection.get("Finders", resource.get("finders", resource.get("Finders", [])))
    )
    if isinstance(finders, list):
        if any(not isinstance(item, dict) or not isinstance(item.get("name"), str) for item in finders):
            raise DataLoadError(stage, "Business-object describe returned malformed finder definitions.")
        available = any(item["name"] == FSCR_FINDER for item in finders)
    elif isinstance(finders, dict):
        available = FSCR_FINDER in finders
    else:
        raise DataLoadError(stage, "Business-object describe returned malformed finder definitions.")
    if not available:
        return match
    discriminator = discriminator_from_item(match)
    if any(character in discriminator for character in ('"', ';', '\\', '\n', '\r')):
        raise DataLoadError(stage, "Business-object discriminator cannot be safely used in the FSCR finder.")
    query = urllib.parse.urlencode({
        "finder": f'{FSCR_FINDER};BusObjTopDiscriminator="{discriminator}"',
    })
    url = config["host"] + FSCR_BUSINESS_OBJECTS_PATH + "?" + query
    # Production requests use the existing 120-second transport timeout without retries.
    try:
        response = (
            request_json(url, config["auth"], stage=stage, refresh_http_statuses=frozenset())
            if getter is get_json else getter(url, config["auth"], stage=stage)
        )
    except TimeoutError as exc:
        raise DataLoadError(stage, "FSCR business-object finder timed out; schema retrieval did not proceed.") from exc
    items, _has_more = _validated_page(response, offset=0, label="FSCR business-object finder")
    if not items and not _has_more:
        return match
    if _has_more or len(items) != 1:
        raise DataLoadError(stage, "FSCR business-object finder returned ambiguous results.")
    refreshed = items[0]
    if not isinstance(refreshed, dict) or discriminator_from_item(refreshed) != discriminator:
        raise DataLoadError(stage, "FSCR business-object finder returned a mismatched object.")
    return refreshed


def parse_template(
    content: bytes, *, allow_no_metadata: bool = False
) -> tuple[TemplateSection, ...]:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise DataLoadError(
            "business-object-validation", "UCM DAT template must contain valid UTF-8 text."
        ) from exc

    sections: list[TemplateSection] = []
    seen_sections: set[str] = set()
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if not raw_line.startswith("METADATA|"):
            continue
        parts = raw_line.split("|")
        if len(parts) < 3 or not parts[1].strip():
            raise DataLoadError(
                "business-object-validation",
                f"UCM DAT template contains a malformed METADATA line at line {line_number}.",
            )
        discriminator = parts[1].strip()
        if discriminator in seen_sections:
            raise DataLoadError(
                "business-object-validation",
                f"UCM DAT template contains duplicate METADATA section {discriminator}.",
            )
        attributes: list[TemplateAttribute] = []
        seen_attributes: set[str] = set()
        for raw_attribute in parts[2:]:
            if not raw_attribute.strip():
                raise DataLoadError(
                    "business-object-validation",
                    f"UCM DAT template section {discriminator} contains an empty attribute.",
                )
            name = normalize_attribute_name(raw_attribute)
            if name in seen_attributes:
                raise DataLoadError(
                    "business-object-validation",
                    f"UCM DAT template section {discriminator} contains duplicate attribute {name}.",
                )
            seen_attributes.add(name)
            attributes.append(TemplateAttribute(raw_attribute.strip(), name))
        seen_sections.add(discriminator)
        sections.append(TemplateSection(discriminator, tuple(attributes)))

    if not sections and not allow_no_metadata:
        raise DataLoadError(
            "business-object-validation", "UCM DAT template did not contain a METADATA section."
        )
    return tuple(sections)


def _ordered_component_discriminators(
    components: dict[str, dict[str, Any]], top_discriminator: str
) -> tuple[str, ...]:
    """Order components parent-before-child while preserving live response order."""
    if top_discriminator not in components:
        raise DataLoadError(
            "business-object-validation",
            f"Child business-object metadata did not contain top component {top_discriminator}.",
        )

    ordered = [top_discriminator]
    remaining = [name for name in components if name != top_discriminator]
    while remaining:
        advanced = False
        for name in tuple(remaining):
            item = components[name]
            if (
                "PARENT_BUS_OBJ_FILE_DISCRIMINATOR" in item
                and "ParentBusObjFileDiscriminator" not in item
            ):
                raise DataLoadError(
                    "business-object-validation",
                    "Child business-object item did not contain ParentBusObjFileDiscriminator as a REST attribute.",
                )
            parent = str(
                item.get("ParentBusObjFileDiscriminator") or ""
            ).strip()
            if not parent:
                parent = top_discriminator
            if parent in ordered:
                ordered.append(name)
                remaining.remove(name)
                advanced = True
        if not advanced:
            unresolved = [
                {
                    "discriminator": name,
                    "parent": components[name].get("ParentBusObjFileDiscriminator"),
                }
                for name in remaining
            ]
            raise DataLoadError(
                "business-object-validation",
                "Child business-object hierarchy contains an unresolved parent or cycle.",
                response={"components": unresolved},
            )
    return tuple(ordered)


def _synthesized_raw_attribute_name(name: str) -> str:
    if name == "SourceRefTableName":
        return "SourceRefTableName=<source-table-name>"
    if re.fullmatch(r"SourceRef\d{3}", name):
        return name + "=<source-column-" + name[-3:] + ">"
    return name


def parse_source_sections(content: bytes, *, source_name: str) -> tuple[SourceSection, ...]:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise DataLoadError(
            "file-validation", f"Source file must contain valid UTF-8 text: {source_name}"
        ) from exc

    sections: list[SourceSection] = []
    seen_sections: set[str] = set()
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if not raw_line.startswith("METADATA|"):
            continue
        parts = raw_line.split("|")
        if len(parts) < 3 or not parts[1].strip():
            raise DataLoadError(
                "file-validation", f"Malformed METADATA line {line_number}: {source_name}"
            )
        discriminator = parts[1].strip()
        if discriminator in seen_sections:
            raise DataLoadError(
                "file-validation",
                f"Duplicate METADATA section {discriminator}: {source_name}",
            )
        attributes = tuple(normalize_attribute_name(value) for value in parts[2:])
        if any(not value for value in attributes):
            raise DataLoadError(
                "file-validation",
                f"METADATA section {discriminator} contains an empty attribute: {source_name}",
            )
        seen_sections.add(discriminator)
        sections.append(SourceSection(discriminator, attributes))
    if not sections:
        raise DataLoadError(
            "file-validation", f"Source file did not contain a METADATA section: {source_name}"
        )
    return tuple(sections)


def _fetch_collection(
    path: str,
    config: dict[str, str],
    *,
    label: str,
    getter: Getter,
    fixed_query: dict[str, str] | None = None,
) -> list[Any]:
    offset = 0
    results: list[Any] = []
    while True:
        query_values = dict(fixed_query or {})
        query_values.update(
            {"onlyData": "true", "limit": str(PAGE_LIMIT), "offset": str(offset)}
        )
        response = getter(
            config["host"] + path + "?" + urllib.parse.urlencode(query_values),
            config["auth"],
            stage="business-object-validation",
        )
        items, has_more = _validated_page(response, offset=offset, label=label)
        results.extend(items)
        if not has_more:
            return results
        if not items:
            raise DataLoadError(
                "business-object-validation",
                f"{label} pagination did not advance.",
                response={"offset": offset},
            )
        offset += len(items)


def load_business_object_schema(
    query_value: str,
    config: dict[str, str],
    *,
    allow_aliases: bool,
    getter: Getter = get_json,
    byte_getter: ByteGetter = get_bytes,
    allow_attribute_schema_fallback: bool = False,
    progress: SchemaProgressCallback | None = None,
    sample_attribute_lookup: bool = False,
    fscr_business_object_lookup: bool = False,
) -> BusinessObjectSchema:
    match = resolve_business_object(
        query_value, config, allow_aliases=allow_aliases, getter=getter,
        sample_attribute_lookup=sample_attribute_lookup,
    )
    use_lookup_record = sample_attribute_lookup
    if sample_attribute_lookup or fscr_business_object_lookup:
        refreshed = refresh_fscr_business_object(match, config, getter=getter)
        # The helper preserves object identity only for absent/empty fallback.
        use_lookup_record = use_lookup_record or refreshed is not match
        match = refreshed
    business_object_id = match.get("BusinessObjectId")
    if business_object_id in (None, ""):
        raise DataLoadError(
            "business-object-validation",
            "Matched business object did not contain a BusinessObjectId.",
        )
    business_object_id = str(business_object_id)
    detail = match if use_lookup_record else getter(
        config["host"] + BUSINESS_OBJECTS_PATH + "/" + urllib.parse.quote(business_object_id),
        config["auth"],
        stage="business-object-validation",
    )
    if not isinstance(detail, dict):
        raise DataLoadError(
            "business-object-validation", "Business-object detail returned a malformed response."
        )
    discriminator = discriminator_from_item(detail) or discriminator_from_item(match)
    if discriminator != discriminator_from_item(match):
        raise DataLoadError(
            "business-object-validation",
            "Business-object detail discriminator did not match the finder result.",
        )
    if progress is not None:
        progress(SchemaProgressEvent("business_object_resolved", discriminator))
    ucm_content_id = detail.get("UcmContentId")
    if not isinstance(ucm_content_id, str) or not ucm_content_id.strip():
        raise DataLoadError(
            "business-object-validation",
            f"Business object {discriminator} did not contain a UcmContentId. Perform the Business Object Attribute Update, then retry.",
            response={"BusinessObjectId": business_object_id},
        )
    ucm_content_id = ucm_content_id.strip()
    template_content = byte_getter(
        config["host"]
        + "/documents/files/"
        + urllib.parse.quote(ucm_content_id)
        + "/data",
        config["auth"],
        stage="business-object-validation",
    )
    sections = parse_template(
        template_content, allow_no_metadata=allow_attribute_schema_fallback
    )
    if sections and sections[0].discriminator != discriminator:
        raise DataLoadError(
            "business-object-validation",
            "UCM DAT template top discriminator did not match the selected business object.",
            response={
                "selectedDiscriminator": discriminator,
                "templateDiscriminator": sections[0].discriminator,
            },
        )

    component_path = (
        BUSINESS_OBJECTS_PATH
        + "/"
        + urllib.parse.quote(business_object_id)
        + "/child/childBusinessObjects"
    )
    component_items = _fetch_collection(
        component_path,
        config,
        label="Child business objects",
        getter=getter,
    )
    components: dict[str, dict[str, Any]] = {}
    for item in component_items:
        if not isinstance(item, dict):
            raise DataLoadError(
                "business-object-validation", "Child business objects returned a non-object item."
            )
        if (
            "PARENT_BUS_OBJ_FILE_DISCRIMINATOR" in item
            and "ParentBusObjFileDiscriminator" not in item
        ):
            raise DataLoadError(
                "business-object-validation",
                "Child business-object item did not contain ParentBusObjFileDiscriminator as a REST attribute.",
            )
        component_discriminator = component_discriminator_from_item(item)
        component_id = item.get("BusinessObjectId")
        if not component_discriminator or component_id in (None, ""):
            raise DataLoadError(
                "business-object-validation",
                "Child business-object item did not contain BusObjFileDiscriminator and BusinessObjectId.",
            )
        if component_discriminator in components:
            raise DataLoadError(
                "business-object-validation",
                f"Child business objects returned duplicate discriminator {component_discriminator}.",
            )
        components[component_discriminator] = item
    if discriminator not in components:
        components[discriminator] = {
            "BusinessObjectId": business_object_id,
            "BusObjFileDiscriminator": discriminator,
            "UIName": detail.get("UIName") or match.get("UIName"),
        }

    schema_source = "UCM_TEMPLATE"
    section_discriminators = tuple(section.discriminator for section in sections)
    if not sections:
        schema_source = "ATTRIBUTE_METADATA"
        section_discriminators = _ordered_component_discriminators(
            components, discriminator
        )

    def fetch_attributes_for_section(
        section_discriminator: str,
    ) -> tuple[str, tuple[dict[str, Any], ...]]:
        component = components.get(section_discriminator)
        if component is None:
            return section_discriminator, ()
        component_id = str(component["BusinessObjectId"])
        attribute_path = (
            BUSINESS_OBJECTS_PATH
            + "/"
            + urllib.parse.quote(business_object_id)
            + "/child/childBusinessObjects/"
            + urllib.parse.quote(component_id)
            + "/child/attributes"
        )
        attribute_items = _fetch_collection(
            attribute_path,
            config,
            label=f"Attributes for {section_discriminator}",
            getter=getter,
            fixed_query={"fields": ATTRIBUTE_FIELDS},
        )
        validated_attributes: list[dict[str, Any]] = []
        seen_names: set[str] = set()
        for item in attribute_items:
            if not isinstance(item, dict) or not str(item.get("AttributeName") or "").strip():
                raise DataLoadError(
                    "business-object-validation",
                    f"Attributes for {section_discriminator} returned a malformed item.",
                )
            name = normalize_attribute_name(str(item["AttributeName"]))
            if name in seen_names:
                raise DataLoadError(
                    "business-object-validation",
                    f"Attributes for {section_discriminator} returned duplicate attribute {name}.",
                )
            seen_names.add(name)
            validated_attributes.append(item)
        return section_discriminator, tuple(validated_attributes)

    attribute_sets: dict[str, tuple[dict[str, Any], ...]] = {}
    sections_with_components = [
        section_discriminator
        for section_discriminator in section_discriminators
        if section_discriminator in components
    ]
    with ThreadPoolExecutor(max_workers=min(8, len(sections_with_components) or 1)) as executor:
        futures = {
            section_discriminator: executor.submit(
                fetch_attributes_for_section, section_discriminator
            )
            for section_discriminator in sections_with_components
        }
        for section_discriminator in sections_with_components:
            _name, attributes = futures[section_discriminator].result()
            attribute_sets[section_discriminator] = attributes

    if not sections:
        synthesized_sections: list[TemplateSection] = []
        for section_discriminator in section_discriminators:
            details = attribute_sets.get(section_discriminator, ())
            if not details:
                raise DataLoadError(
                    "business-object-validation",
                    f"Attributes for {section_discriminator} were empty; a sample schema could not be synthesized.",
                )
            synthesized_sections.append(
                TemplateSection(
                    section_discriminator,
                    tuple(
                        TemplateAttribute(
                            _synthesized_raw_attribute_name(
                                normalize_attribute_name(str(item["AttributeName"]))
                            ),
                            normalize_attribute_name(str(item["AttributeName"])),
                        )
                        for item in details
                    ),
                )
            )
        sections = tuple(synthesized_sections)

    return BusinessObjectSchema(
        business_object_id=business_object_id,
        discriminator=discriminator,
        ui_name=str(detail.get("UIName") or match.get("UIName") or discriminator),
        ucm_content_id=ucm_content_id,
        template_file_name=str(
            detail.get("TemplateFileName") or match.get("TemplateFileName") or discriminator + ".dat"
        ),
        sections=sections,
        components=components,
        attributes=attribute_sets,
        schema_source=schema_source,
        object_type=str(detail.get("ObjectType") or match.get("ObjectType") or "").strip(),
    )


def resolve_xlsx_root_business_object(
    sheet_discriminators: Iterable[str],
    config: dict[str, str],
    *,
    getter: Getter = get_json,
) -> str:
    """Resolve an exact root or an unambiguous generated 30-character prefix."""
    sheet_names = [str(value).strip() for value in sheet_discriminators if str(value).strip()]
    if not sheet_names:
        raise DataLoadError("business-object-validation", "XLSX workbook has no visible root worksheet.")
    root_sheet_name = sheet_names[0]
    unique_items: list[dict[str, Any]] = []
    seen_identities: set[tuple[str, str]] = set()
    for item in find_business_objects(
        config, root_sheet_name, getter=getter, top_discriminator_prefix=True
    ):
        discriminator = discriminator_from_item(item)
        identity = (str(item.get("BusinessObjectId") or ""), discriminator)
        if not identity[0] or identity not in seen_identities:
            seen_identities.add(identity)
            unique_items.append(item)

    exact_matches = [
        item for item in unique_items
        if discriminator_from_item(item) == root_sheet_name
    ]
    if len(exact_matches) == 1:
        return root_sheet_name
    if len(exact_matches) > 1:
        raise DataLoadError(
            "business-object-validation",
            "The first visible XLSX worksheet name matches multiple registered top-level business objects exactly.",
            response={
                "rootWorksheet": root_sheet_name,
                "candidates": [
                    {
                        "BusinessObjectId": item.get("BusinessObjectId"),
                        "discriminator": discriminator_from_item(item),
                    }
                    for item in exact_matches
                ],
            },
        )

    prefix_matches = [
        item for item in unique_items
        if len(root_sheet_name) == 30
        and len(discriminator_from_item(item)) > 30
        and discriminator_from_item(item)[:30] == root_sheet_name
    ]
    if len(prefix_matches) == 1:
        return discriminator_from_item(prefix_matches[0])
    if not prefix_matches:
        raise DataLoadError(
            "business-object-validation",
            "The first visible XLSX worksheet name does not match a registered top-level business object exactly and is not a 30-character prefix of one longer discriminator.",
            response={"rootWorksheet": root_sheet_name},
        )
    raise DataLoadError(
        "business-object-validation",
        "The 30-character first visible XLSX worksheet prefix matches multiple registered top-level business objects.",
        response={
            "rootWorksheet": root_sheet_name,
            "selectionRequired": True,
            "candidates": [
                {
                    "BusinessObjectId": item.get("BusinessObjectId"),
                    "discriminator": discriminator_from_item(item),
                }
                for item in prefix_matches
            ],
        },
    )


def validate_selected_xlsx_root_business_object(
    sheet_discriminators: Iterable[str], selected_discriminator: str
) -> str:
    """Validate an explicit exact discriminator against the visible root sheet."""
    sheet_names = [str(value).strip() for value in sheet_discriminators if str(value).strip()]
    if not sheet_names:
        raise DataLoadError("business-object-validation", "XLSX workbook has no visible root worksheet.")
    selected = str(selected_discriminator).strip()
    if not selected:
        raise DataLoadError(
            "source-selection", "--business-object must contain an exact registered discriminator."
        )
    root_sheet_name = sheet_names[0]
    if root_sheet_name == selected or (
        len(root_sheet_name) == 30
        and len(selected) > 30
        and selected[:30] == root_sheet_name
    ):
        return selected
    raise DataLoadError(
        "business-object-validation",
        "The selected Business Object does not match the first visible XLSX worksheet.",
        response={
            "rootWorksheet": root_sheet_name,
            "selectedDiscriminator": selected,
        },
    )


def is_mandatory(attribute: dict[str, Any]) -> bool:
    return str(attribute.get("MandatoryStatus") or "").strip().lower() == "yes" or str(
        attribute.get("MandatoryStatusCode") or ""
    ).strip() == "ORA_Y"


def is_required_for_create(attribute: dict[str, Any]) -> bool:
    """Return whether metadata marks an attribute as required for new records."""
    return str(attribute.get("MandatoryStatusCode") or "").strip() == "ORA_W" or str(
        attribute.get("MandatoryStatus") or ""
    ).strip().lower() == "for new records"


def mandatory_id_has_user_key_alternative(
    attribute_name: str,
    attribute: dict[str, Any] | None,
    present_attributes: set[str],
) -> bool:
    """Whether an omitted mandatory ID is covered by all declared user-key columns.

    This helper is used by sample-field selection. Upload validation deliberately
    does not use it because mandatory metadata is not a blanket DAT requirement.
    """
    if not attribute_name.lower().endswith("id"):
        return False
    alternatives = user_key_attribute_names(attribute)
    return bool(alternatives) and all(name in present_attributes for name in alternatives)


def is_key_attribute(attribute: dict[str, Any]) -> bool:
    return (
        "KEY" in str(attribute.get("AttributeType") or "").upper()
        or bool(attribute.get("UserKeyAttrNames"))
        or str(attribute.get("IntKeySupported") or "").strip().lower() == "yes"
    )


def user_key_attribute_names(attribute: dict[str, Any] | None) -> tuple[str, ...]:
    """Return normalized user-key alternatives declared for an identifier."""
    raw_value = (attribute or {}).get("UserKeyAttrNames")
    if isinstance(raw_value, (list, tuple, set)):
        values = [str(value) for value in raw_value]
    else:
        values = re.split(r"[,;|]", str(raw_value or ""))
    return tuple(
        normalized
        for value in values
        if (normalized := normalize_attribute_name(value.strip().strip("[]\"'")))
    )


def is_source_reference_attribute(name: str) -> bool:
    """Return whether a normalized template attribute is a SourceRef helper column."""
    return name == "SourceRefTableName" or re.fullmatch(r"SourceRef\d{3}", name) is not None


def is_surrogate_id_attribute(attribute: dict[str, Any] | None) -> bool:
    details = attribute or {}
    reference_type = str(details.get("AttributeMapKeyReferenceType") or "")
    attribute_type = str(details.get("AttributeType") or "")
    return "SURROGATE" in reference_type.upper() or "SURROGATE" in attribute_type.upper()


def is_foreign_key_attribute(attribute: dict[str, Any] | None) -> bool:
    details = attribute or {}
    if str(details.get("ReferenceIntObjName") or "").strip():
        return True
    reference_type = str(details.get("AttributeMapKeyReferenceType") or "").upper()
    return "FOREIGN" in reference_type or "REFERENCE" in reference_type


def generated_attribute_order(
    names: Iterable[str], details: dict[str, dict[str, Any]]
) -> tuple[str, ...]:
    """Prioritize creation keys while retaining template order within each group."""
    ordered: list[tuple[int, int, str]] = []
    for index, name in enumerate(names):
        if is_source_reference_attribute(name):
            continue
        attribute = details.get(name)
        if is_surrogate_id_attribute(attribute):
            group = 0
        elif attribute is not None and is_mandatory(attribute):
            group = 1
        elif attribute is not None and is_key_attribute(attribute):
            group = 2
        elif is_foreign_key_attribute(attribute):
            group = 3
        else:
            group = 4
        ordered.append((group, index, name))
    return tuple(name for _group, _index, name in sorted(ordered))


def validate_source_sections(
    source_sections: tuple[SourceSection, ...], schema: BusinessObjectSchema
) -> None:
    template_sections = schema.sections_by_discriminator
    validation_errors: list[dict[str, Any]] = []
    for source_section in source_sections:
        section_errors: dict[str, Any] = {"discriminator": source_section.discriminator}
        template_section = template_sections.get(source_section.discriminator)
        if template_section is None:
            section_errors["unknownSection"] = True
            validation_errors.append(section_errors)
            continue

        duplicates = sorted(
            {name for name in source_section.attributes if source_section.attributes.count(name) > 1}
        )
        allowed = set(template_section.attribute_names)
        unknown = sorted({name for name in source_section.attributes
                          if not is_supported_source_attribute(source_section.discriminator, name, schema)})
        if duplicates:
            section_errors["duplicateAttributes"] = duplicates
        if unknown:
            section_errors["unknownAttributes"] = unknown

        detailed_attributes = schema.attributes.get(source_section.discriminator)
        if detailed_attributes is not None:
            mandatory = {
                normalize_attribute_name(str(attribute["AttributeName"]))
                for attribute in detailed_attributes
                if is_mandatory(attribute)
            }
            template_missing = sorted(mandatory - allowed)
            if template_missing:
                response = {
                    "section": source_section.discriminator,
                    "mandatoryAttributesMissingFromTemplate": template_missing,
                }
                raise DataLoadError(
                    "business-object-validation",
                    validation_mismatch_message(response),
                    response=response,
                )
            # Live mandatory flags describe the complete Fusion operation
            # contract, not necessarily the selected DAT operation. For
            # example, PATCH and child-only rows may intentionally omit fields
            # that a create operation requires. Preserve strict section and
            # attribute-schema validation here; let Fusion validate the
            # operation-specific required values during import/load.

        if len(section_errors) > 1:
            validation_errors.append(section_errors)

    if validation_errors:
        response = {
            "BusinessObjectId": schema.business_object_id,
            "UcmContentId": schema.ucm_content_id,
            "sections": validation_errors,
        }
        raise DataLoadError(
            "business-object-validation",
            validation_mismatch_message(response),
            response=response,
        )


def _bounded_attribute_list(values: Iterable[Any], *, limit: int = 8) -> str:
    names = [str(value) for value in values if str(value)]
    visible = names[:limit]
    suffix = f" and {len(names) - limit} more" if len(names) > limit else ""
    return ", ".join(visible) + suffix


def validation_mismatch_details(response: Any) -> tuple[str, ...]:
    """Return safe, actionable source-versus-schema validation differences."""
    if not isinstance(response, dict):
        return ()

    details: list[str] = []
    section = str(response.get("section") or "")
    missing = response.get("mandatoryAttributesMissingFromTemplate")
    if isinstance(missing, list) and missing:
        label = f" in section {section}" if section else ""
        details.append(
            "Live metadata marks attribute(s) mandatory"
            f"{label}, but the UCM template does not include them: "
            f"{_bounded_attribute_list(missing)}."
        )

    sections = response.get("sections")
    if not isinstance(sections, list):
        return tuple(details)
    for item in sections:
        if not isinstance(item, dict):
            continue
        discriminator = str(item.get("discriminator") or "this section")
        if item.get("unknownSection"):
            details.append(
                f"Source section {discriminator} is not present in the UCM template."
            )
        duplicates = item.get("duplicateAttributes")
        if isinstance(duplicates, list) and duplicates:
            details.append(
                f"Section {discriminator} repeats attribute(s): "
                f"{_bounded_attribute_list(duplicates)}."
            )
        unknown = item.get("unknownAttributes")
        if isinstance(unknown, list) and unknown:
            details.append(
                f"Section {discriminator} contains attribute(s) not present in the UCM template: "
                f"{_bounded_attribute_list(unknown)}."
            )
    return tuple(details)


def validation_mismatch_message(response: Any) -> str:
    details = validation_mismatch_details(response)
    return " ".join(details) or "Source attributes do not match live business-object metadata."
