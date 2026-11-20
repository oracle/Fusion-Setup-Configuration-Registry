"""Resource Types adapter for the shared Field Service task workflow."""
from __future__ import annotations

import importlib.util
import hashlib
import json
from pathlib import Path
import sys
from typing import Any
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[2] / "scripts"))
from task_orchestration import WorkflowBlocked, resolve_execution_route

TASK_CODE = "ORA_FFS_TS_RESOURCE_TYPES"
LANGUAGES_PATH = "/rest/ofscMetadata/v1/languages"
# The OFSC Metadata aliases are documentation identifiers.  The shared Core
# client does not rewrite them, so execute the supplied actual API paths.
RESOURCE_TYPES_PATH = "/api/field-service/configuration/v1/resourceTypes"
OPTIONAL_CAPABILITIES = (
    "allowTeamwork",
    "allowResourceLocationSharing",
    "supportOfSharedInventory",
    "supportOfWorkSkills",
    "supportOfWorkZones",
    "supportOfTimeSlots",
    "enableRoutingAssignment",
    "enableQuotaManagement",
    "enableRoutingIntoSubBuckets",
    "enableDurationLearning",
)
OPTIONAL_CAPABILITY_SOURCES = {
    "allowTeamwork": "resource can participate in team",
    "allowResourceLocationSharing": "share geolocation in teamwork",
    "supportOfSharedInventory": "share inventory in teamwork",
    "supportOfWorkSkills": "share workskills in teamwork (team-member only)",
    "enableRoutingAssignment": "routing can assign activities",
    "enableQuotaManagement": "used for quota management",
}
MUTABLE_BODY_FIELDS = (
    "active",
    "name",
    "role",
    "translations",
)
FEATURE_COLUMNS = {
    "routing can assign activities": ("features", "routingAssign", "routing rationale"),
    "used for quota management": ("features", "quota", "quota rationale"),
    "team participation": ("features", "participate", "teamwork rationale"),
    "resource location sharing": ("features", "geolocaionTeam", "privacy / regulatory rationale"),
    "shared inventory": ("features", "inventoryTeam", "inventory rationale"),
    "work skills": ("features", "skillsTeam", None),
}
DETAIL_FEATURE_COLUMNS = {
    "duration learning enabled": ("statistic", "usePersonalProfileForCalc"),
    "duration contribution enabled": ("statistic", "durationAffectsAvg"),
}
CREATE_FEATURE_DEFAULTS = {
    "allowChildProviders": False,
    "allowUsers": False,
    "bucket": False,
    "contingentWorkers": False,
    "geolocaionTeam": False,
    "includeFinalTravel": False,
    "includeFirstTravel": False,
    "inventoryTeam": False,
    "maintenanceResource": False,
    "notActivatedAlert": False,
    "participate": False,
    "queueOwner": False,
    "quota": False,
    "routingAssign": False,
    "skillsTeam": False,
    "teamholder": False,
    "trackLocation": False,
    "warehouse": False,
}
ROLE_FEATURE_DEFAULTS = {
    # `bucket` is a role invariant, not an optional capability. Every other
    # feature remains false until the workbook explicitly enables it.
    "bucket": {"bucket": True},
}


def _load_workbook_reader() -> Any:
    path = ROOT / "workbook_intake.py"
    spec = importlib.util.spec_from_file_location("resource_types_workbook_intake", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


WORKBOOK = _load_workbook_reader()


def _active_english_is_available(languages: object) -> bool:
    if not isinstance(languages, dict) or not isinstance(languages.get("items"), list):
        return False
    return any(
        isinstance(item, dict)
        and isinstance(item.get("label"), str)
        and (item["label"].casefold() == "en" or item["label"].casefold().startswith("en-"))
        and item.get("active") in (True, "true", "TRUE")
        for item in languages["items"]
    )


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _normal(value: object) -> str:
    return " ".join(str(value or "").replace("*", "").strip().split()).casefold()


def _boolean(value: object, field: str) -> bool:
    value = _normal(value)
    if value in {"true", "yes", "y", "1", "active", "enabled"}:
        return True
    if value in {"false", "no", "n", "0", "inactive", "disabled"}:
        return False
    raise WorkflowBlocked(f"{field} must be an unambiguous boolean.")


def _number(value: object, field: str) -> int:
    try:
        number = int(str(value).strip())
    except (TypeError, ValueError) as error:
        raise WorkflowBlocked(f"{field} must be an integer.") from error
    if number < 0:
        raise WorkflowBlocked(f"{field} must not be negative.")
    return number


class ResourceTypesAdapter:
    task_code = TASK_CODE

    def __init__(
        self,
        rationale_file: Path | None = None,
        english_names_file: Path | None = None,
        test_payload_file: Path | None = None,
    ) -> None:
        self.rationales = self._load_rationales(rationale_file)
        self.english_names = self._load_english_names(english_names_file)
        self.test_payload_file = test_payload_file

    @staticmethod
    def _load_rationales(path: Path | None) -> dict[str, dict[str, str]]:
        if path is None:
            return {}
        try:
            source = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise WorkflowBlocked("Rationale input could not be read as JSON.") from error
        if not isinstance(source, dict):
            raise WorkflowBlocked("Rationale input must be an object keyed by Resource Type label.")
        result: dict[str, dict[str, str]] = {}
        for label, entries in source.items():
            if not isinstance(label, str) or not isinstance(entries, dict):
                raise WorkflowBlocked("Each rationale entry must contain a Resource Type label and capability map.")
            result[label.casefold()] = {
                key.casefold(): value.strip()
                for key, value in entries.items()
                if isinstance(key, str) and isinstance(value, str) and value.strip()
            }
        return result

    @staticmethod
    def _load_english_names(path: Path | None) -> dict[str, str]:
        if path is None:
            return {}
        try:
            source = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise WorkflowBlocked("English display-name input could not be read as JSON.") from error
        if not isinstance(source, dict):
            raise WorkflowBlocked("English display-name input must be an object keyed by Resource Type label.")
        result = {key.casefold(): value.strip() for key, value in source.items() if isinstance(key, str) and isinstance(value, str) and value.strip()}
        if not result:
            raise WorkflowBlocked("English display-name input has no usable values.")
        return result

    def resolve_route(self, direction: str | None) -> dict[str, str]:
        return resolve_execution_route(ROOT.parent / "ora-resource" / "ora_rest_execution.md", self.task_code, direction)

    def validate_design_rules(self, workbook: Path) -> None:
        """Execute the compiled, task-local RT gates before a preview exists."""
        registry_path = ROOT.parent / "ora-resource" / "ora_rule_registry.json"
        try:
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise WorkflowBlocked("Resource Types rule registry could not be read.") from error
        task = next(
            (item for item in registry.get("tasks", []) if item.get("task_code") == self.task_code),
            None,
        )
        expected = [
            "RT.VALIDATE_WORKBOOK", "RT.CHECK_OPERATING_MODEL",
            "RT.CHECK_ORGANIZATION_AND_BUCKET_BOUNDARY", "RT.CHECK_ROUTING_AND_QUOTA_ENABLEMENT",
            "RT.CHECK_BUCKET_CAPACITY_SCOPE", "RT.CHECK_COST_POLICY", "RT.CHECK_TEAM_AND_SHARING",
            "RT.CHECK_LOAD_THRESHOLDS", "RT.CHECK_DURATION_LEARNING", "RT.CHECK_CHANGE_IMPACT",
            "RT.CHECK_CONTRACTOR_SEPARATION", "RT.RETURN_SUCCESS", "RT.RETURN_ISSUES",
        ]
        nodes = task.get("nodes") if isinstance(task, dict) else None
        if not isinstance(nodes, list) or [node.get("id") for node in nodes] != expected:
            raise WorkflowBlocked("Resource Types rule registry is incomplete or has an unsafe execution order.")
        records = WORKBOOK._resource_types_rows(workbook)
        details = self._details_by_label(workbook)
        for record in records:
            label = str(record["label"])
            values = record["values"]
            assert isinstance(values, dict)
            detail = details.get(label.casefold())
            if detail is None:
                raise WorkflowBlocked(f"{label}: RT.VALIDATE_WORKBOOK requires a Resource Type Details row.")
            role = WORKBOOK._role(values, label)
            self._validate_record_rules(label, bool(record["active"]), role, values, detail)

    @staticmethod
    def _value(values: dict[str, object], field: str) -> object:
        return values.get(_normal(field))

    @staticmethod
    def _required_text(label: str, values: dict[str, object], field: str, rule: str) -> str:
        value = str(ResourceTypesAdapter._value(values, field) or "").strip()
        if not value:
            raise WorkflowBlocked(f"{label}: {rule} requires {field}.")
        return value

    @staticmethod
    def _enabled(values: dict[str, object], field: str, label: str) -> bool:
        value = ResourceTypesAdapter._value(values, field)
        return value not in (None, "") and _boolean(value, f"{label}: {field}")

    def _validate_record_rules(
        self, label: str, active: bool, role: str, values: dict[str, object], details: dict[str, object]
    ) -> None:
        self._required_text(label, values, "operating model rationale", "RT.OPERATING_MODEL")
        if role == "bucket":
            self._required_text(label, values, "bucket operational rationale", "RT.ORGANIZATION_AND_BUCKET_BOUNDARY")
            self._required_text(label, values, "capacity scope rationale", "RT.BUCKET_CAPACITY_SCOPE")
        elif role == "organization_unit":
            self._required_text(label, values, "organization unit rationale", "RT.ORGANIZATION_AND_BUCKET_BOUNDARY")

        if role == "field_resource" and active:
            routing = self._value(values, "routing can assign activities")
            quota = self._value(values, "used for quota management")
            if routing in (None, "") or quota in (None, ""):
                raise WorkflowBlocked(f"{label}: RT.ROUTING_AND_QUOTA_ENABLEMENT requires routing and quota selections.")
            if not (self._enabled(values, "routing can assign activities", label) and self._enabled(values, "used for quota management", label)):
                self._required_text(label, values, "routing/quota exception rationale", "RT.ROUTING_AND_QUOTA_ENABLEMENT")

        teamwork_fields = (
            ("team participation", "teamwork rationale"),
            ("resource location sharing", "privacy / regulatory rationale"),
            ("shared inventory", "inventory rationale"),
            ("work skills", "teamwork rationale"),
        )
        if any(self._enabled(values, field, label) for field, _ in teamwork_fields):
            for field, rationale in teamwork_fields:
                if self._enabled(values, field, label):
                    self._required_text(label, values, rationale, "RT.TEAM_AND_SHARING")
            employment = _normal(self._value(values, "employment model"))
            if "contractor" in employment and self._enabled(values, "resource location sharing", label):
                self._required_text(label, values, "privacy / regulatory rationale", "RT.TEAM_AND_SHARING")

        cost_fields = ("working time cost", "travel cost", "start travel allowance", "end travel allowance")
        if any(details.get(_normal(field)) not in (None, "", 0, "0") for field in cost_fields):
            self._required_text(label, values, "cost policy rationale", "RT.COST_POLICY")
        if any(details.get(_normal(field)) not in (None, "", "not applicable") for field in ("load metric", "full load threshold", "empty load threshold")):
            self._required_text(label, values, "load threshold rationale", "RT.LOAD_THRESHOLDS")
        if any(self._enabled(details, field, label) for field in ("duration learning enabled", "duration contribution enabled")):
            self._required_text(label, values, "duration learning rationale", "RT.DURATION_LEARNING")
        if self._enabled(values, "existing resource type", label):
            self._required_text(label, values, "change impact assessment", "RT.CHANGE_IMPACT")
        if _normal(self._value(values, "employment model")) == "mixed":
            self._required_text(label, values, "contractor separation rationale", "RT.CONTRACTOR_SEPARATION")

    def preflight(
        self, workbook: Path, get: Any, temp: Path
    ) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
        if self.test_payload_file:
            payload = self._load_synthetic_test_payload(self.test_payload_file)
        else:
            payload = {"operation": "update-existing-resource-types", "requests": []}
        languages = get(LANGUAGES_PATH, temp / "languages.json")
        if not _active_english_is_available(languages):
            raise WorkflowBlocked("Target environment does not expose an active English language.")
        # The collection read proves that this is the Resource Types metadata scope;
        # label reads below provide the immutable baseline for each requested PUT.
        if get(RESOURCE_TYPES_PATH, temp / "resource-types.json") is None:
            raise WorkflowBlocked("Resource Types collection endpoint returned HTTP 404.")
        baselines: dict[str, dict[str, Any]] = {}
        if self.test_payload_file:
            for sequence, request in enumerate(payload["requests"], 1):
                label = request["identity"]
                current = get(request["path"], temp / f"baseline-{sequence}.json")
                baselines[label] = current or {"label": label, "state": "not_found"}
        else:
            details = self._details_by_label(workbook)
            for sequence, record in enumerate(WORKBOOK._resource_types_rows(workbook), 1):
                label = str(record["label"])
                path = f"{RESOURCE_TYPES_PATH}/{quote(label, safe='')}"
                current = get(path, temp / f"baseline-{sequence}.json")
                if current is None:
                    values = record["values"]
                    assert isinstance(values, dict)
                    current = self._new_resource_type_baseline(label, WORKBOOK._role(values, label))
                    baseline = {"label": label, "state": "not_found"}
                elif not isinstance(current, dict) or current.get("label") != label:
                    raise WorkflowBlocked(f"{label}: matching current-state baseline is required.")
                else:
                    baseline = current
                baselines[label] = baseline
                body = self._merge_existing(label, record, details.get(label.casefold()), current)
                if baseline.get("state") != "not_found" and not self.mismatches(body, current):
                    continue
                payload["requests"].append(
                    {
                        "operationId": "put-resource-type",
                        "method": "PUT",
                        "path": path,
                        "identity": label,
                        "expectedStatuses": [200],
                        "body": body,
                        # OFSC documents this precondition for the 404 create
                        # candidate.  Existing resource types are updated
                        # without it.
                        **({"headers": {"If-None-Match": label}} if baseline.get("state") == "not_found" else {}),
                    }
                )
        return payload, baselines

    @staticmethod
    def _new_resource_type_baseline(label: str, role: str = "field_resource") -> dict[str, Any]:
        """Build a v1 create baseline with the documented role-dependent defaults."""
        features = dict(CREATE_FEATURE_DEFAULTS)
        features.update(ROLE_FEATURE_DEFAULTS.get(role, {}))
        return {
            "active": False,
            "name": label,
            "role": role,
            "translations": [],
            "features": features,
            "loadThreshold": {"units": "activity_count", "load": 0, "empty": 0},
            "costOfTime": {"workingHoursCost": 0, "overtimeSoftCost": 0, "overtimeLimit": 0, "overtimeHardCost": 0, "travelCost": 0},
            "travelAllowance": {"startTravel": 0, "finalTravel": 0},
            "statistic": {"usePersonalProfileForCalc": False, "durationAffectsAvg": False, "skipDaysForStats": 0},
        }

    @staticmethod
    def _details_by_label(workbook: Path) -> dict[str, dict[str, object]]:
        sheets = WORKBOOK._read_xlsx(workbook)
        rows = next((value for title, value in sheets.items() if _normal(title) == "resource type details"), None)
        if not rows:
            raise WorkflowBlocked("Resource Type Details worksheet is required for full-fidelity updates.")
        header_index = next((index for index, row in enumerate(rows) if row and _normal(row[0]) == "resource type label"), None)
        if header_index is None:
            raise WorkflowBlocked("Resource Type Details worksheet requires a Resource Type Label column.")
        headers = [_normal(value) for value in rows[header_index]]
        result: dict[str, dict[str, object]] = {}
        for row in rows[header_index + 1:]:
            if not any(value not in (None, "") for value in row):
                continue
            label = str(row[0] if row else "").strip()
            if not label:
                raise WorkflowBlocked("Resource Type Details has an empty Resource Type Label.")
            if label.casefold() in result:
                raise WorkflowBlocked(f"{label}: Resource Type Details label is duplicated.")
            result[label.casefold()] = {
                header: row[index] if index < len(row) else None
                for index, header in enumerate(headers)
                if header
            }
        return result

    def _merge_existing(
        self,
        label: str,
        record: dict[str, object],
        details: dict[str, object] | None,
        baseline: dict[str, Any],
    ) -> dict[str, Any]:
        if details is None:
            raise WorkflowBlocked(f"{label}: Resource Type Details row is required.")
        body = {field: json.loads(json.dumps(baseline[field])) for field in MUTABLE_BODY_FIELDS if field in baseline}
        missing = [field for field in MUTABLE_BODY_FIELDS if field not in body]
        if missing:
            raise WorkflowBlocked(f"{label}: baseline lacks mutable fields: {', '.join(missing)}.")
        values = record["values"]
        assert isinstance(values, dict)
        body["active"] = bool(record["active"])
        body["role"] = WORKBOOK._role(values, label)
        name = (self.english_names.get(label.casefold()) or str(values.get("english display name") or "").strip())
        if not name:
            raise WorkflowBlocked(f"{label}: English Display Name is required.")
        body["name"] = name
        body["translations"] = self._merge_english_translation(body["translations"], name)

        self._block_unsupported_put_changes(label, values, details, baseline)
        return body

    @staticmethod
    def _block_unsupported_put_changes(
        label: str, values: dict[str, object], details: dict[str, object], baseline: dict[str, Any]
    ) -> None:
        """Fail closed when a workbook asks this endpoint to change non-public fields."""
        features = baseline.get("features") if isinstance(baseline.get("features"), dict) else {}
        statistic = baseline.get("statistic") if isinstance(baseline.get("statistic"), dict) else {}
        load_threshold = baseline.get("loadThreshold") if isinstance(baseline.get("loadThreshold"), dict) else {}

        for column, (section, key, _) in FEATURE_COLUMNS.items():
            source = values.get(column)
            if source in (None, ""):
                continue
            requested = _boolean(source, f"{label}: {column}")
            if requested != bool(features.get(key, False)):
                raise WorkflowBlocked(
                    f"{label}: {column} differs from the current state, but Resource Types PUT has no confirmed public mapping for {section}.{key}."
                )

        source = values.get("route into sub-buckets")
        if source not in (None, "") and _boolean(source, f"{label}: route into sub-buckets"):
            raise WorkflowBlocked(f"{label}: Route into Sub-Buckets has no confirmed OFSC field mapping.")

        for column, (_, key) in DETAIL_FEATURE_COLUMNS.items():
            source = details.get(column)
            if source in (None, ""):
                continue
            requested = _boolean(source, f"{label}: {column}")
            if requested != bool(statistic.get(key, False)):
                raise WorkflowBlocked(
                    f"{label}: {column} differs from the current state, but Resource Types PUT has no confirmed public mapping for statistic.{key}."
                )

        metric = _normal(details.get("load metric"))
        metric_values = {"number of activities": "activity_count", "work hours": "work_hours", "workday percentage": "workday_percentage"}
        if metric in metric_values and metric_values[metric] != load_threshold.get("units"):
            raise WorkflowBlocked(f"{label}: Load Metric differs from the current state, but Resource Types PUT has no confirmed public mapping for loadThreshold.units.")
        if metric and metric not in (*metric_values, "not applicable"):
            raise WorkflowBlocked(f"{label}: unsupported Load Metric.")
        for column, key in (("full load threshold", "load"), ("empty load threshold", "empty")):
            source = details.get(column)
            if source not in (None, "") and _number(source, f"{label}: {column}") != load_threshold.get(key, 0):
                raise WorkflowBlocked(f"{label}: {column} differs from the current state, but Resource Types PUT has no confirmed public mapping for loadThreshold.{key}.")

        source = details.get("duration exclusion period (days)")
        if source not in (None, "") and _number(source, f"{label}: Duration Exclusion Period") != statistic.get("skipDaysForStats", 0):
            raise WorkflowBlocked(f"{label}: Duration Exclusion Period differs from the current state, but Resource Types PUT has no confirmed public mapping for statistic.skipDaysForStats.")

        cost_of_time = baseline.get("costOfTime") if isinstance(baseline.get("costOfTime"), dict) else {}
        for column, key in (("working time cost", "workingHoursCost"), ("travel cost", "travelCost")):
            source = details.get(column)
            if source not in (None, "") and _number(source, f"{label}: {column}") != cost_of_time.get(key, 0):
                raise WorkflowBlocked(f"{label}: {column} differs from the current state, but Resource Types PUT has no confirmed public mapping for costOfTime.{key}.")

        for column, key in (("start travel policy", "includeFirstTravel"), ("end travel policy", "includeFinalTravel")):
            source = _normal(details.get(column))
            if not source or source == "not specified in source":
                continue
            if "included" in source:
                requested = True
            elif "excluded" in source:
                requested = False
            else:
                raise WorkflowBlocked(f"{label}: unsupported {column}.")
            if requested != bool(features.get(key, False)):
                raise WorkflowBlocked(f"{label}: {column} differs from the current state, but Resource Types PUT has no confirmed public mapping for features.{key}.")

    @staticmethod
    def _merge_english_translation(translations: Any, name: str) -> list[dict[str, Any]]:
        if not isinstance(translations, list):
            raise WorkflowBlocked("Baseline translations must be a list.")
        result = json.loads(json.dumps(translations))
        for translation in result:
            if isinstance(translation, dict) and isinstance(translation.get("language"), str) and (
                translation["language"].casefold() == "en" or translation["language"].casefold().startswith("en-")
            ):
                translation["name"] = name
                return result
        result.append({"language": "en", "languageISO": "en-US", "name": name})
        return result

    @staticmethod
    def _apply_travel_policy(label: str, body: dict[str, Any], details: dict[str, object]) -> None:
        policies = {
            "start travel policy": "includeFirstTravel",
            "end travel policy": "includeFinalTravel",
        }
        for column, feature in policies.items():
            value = _normal(details.get(column))
            if not value or value == "not specified in source":
                continue
            if "included" in value:
                body["features"][feature] = True
            elif "excluded" in value:
                body["features"][feature] = False
            else:
                raise WorkflowBlocked(f"{label}: unsupported {column}.")

    @staticmethod
    def _load_synthetic_test_payload(path: Path) -> dict[str, Any]:
        """Load a deliberately narrow, non-customer PUT fixture for API testing."""
        try:
            source = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise WorkflowBlocked("Synthetic test payload could not be read as JSON.") from error
        requests = source.get("requests") if isinstance(source, dict) else None
        if not isinstance(requests, list) or len(requests) != 1:
            raise WorkflowBlocked("Synthetic test payload must contain exactly one request.")
        request = requests[0]
        if not isinstance(request, dict) or request.get("method") != "PUT":
            raise WorkflowBlocked("Synthetic test payload request must use PUT.")
        path_value = request.get("path")
        prefix = f"{RESOURCE_TYPES_PATH}/fscr_test_"
        if not isinstance(path_value, str) or not path_value.startswith(prefix):
            raise WorkflowBlocked("Synthetic test payload path must target an fscr_test_ Resource Type.")
        label = path_value.rsplit("/", 1)[-1]
        body = request.get("body")
        if not isinstance(body, dict) or set(body) != {"name", "active", "role", "translations"}:
            raise WorkflowBlocked(
                "Synthetic test body must contain exactly name, active, role, and translations."
            )
        if not isinstance(body["name"], str) or not body["name"].strip() or not isinstance(body["active"], bool) or not isinstance(body["role"], str):
            raise WorkflowBlocked("Synthetic test body has invalid name, active, or role.")
        translations = body["translations"]
        if not isinstance(translations, list) or not translations or not all(
            isinstance(item, dict)
            and set(item).issubset({"language", "languageISO", "name"})
            and isinstance(item.get("language"), str)
            and isinstance(item.get("name"), str)
            for item in translations
        ):
            raise WorkflowBlocked("Synthetic test body requires valid translation entries.")
        return {
            "operation": "synthetic-upsert-test-only",
            "requests": [{
                "operationId": "put-resource-type-synthetic-test",
                "method": "PUT",
                "path": path_value,
                "identity": label,
                "expectedStatuses": [200, 201],
                "body": body,
            }],
        }

    def build_preview(
        self, payload: dict[str, Any], environment: str, baselines: dict[str, dict[str, Any]]
    ) -> dict[str, Any]:
        requests = []
        for request in payload.get("requests", []):
            label = request.get("identity")
            baseline = baselines.get(label)
            if not isinstance(baseline, dict) or (
                baseline.get("state") != "not_found" and baseline.get("label") != label
            ):
                raise WorkflowBlocked(f"{label}: matching current-state baseline is required.")
            requests.append({**request, "baseline": baseline})
        draft = {
            "schemaVersion": "1.0",
            "taskCode": self.task_code,
            "executionDirection": "ora_rest_execution",
            "environment": environment.strip(),
            "requests": requests,
        }
        if not draft["environment"] or not requests:
            raise WorkflowBlocked("A non-empty environment and at least one Resource Type are required.")
        return {
            **draft,
            "sha256": hashlib.sha256(_canonical_json(draft)).hexdigest(),
            "approvalRequired": True,
            "retryPolicy": "never",
        }

    def mismatches(self, expected: dict[str, Any], actual: dict[str, Any]) -> list[str]:
        return [field for field in MUTABLE_BODY_FIELDS if actual.get(field) != expected.get(field)]
