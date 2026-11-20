"""Activity Types adapter for the shared Field Service workflow."""
from __future__ import annotations
import importlib.util, sys
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[2] / "scripts"))
from task_orchestration import resolve_execution_route
def _load(name: str) -> Any:
    spec=importlib.util.spec_from_file_location(name,ROOT/f"{name}.py"); module=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(module); return module
PAYLOADS=_load("build_activity_types_preview"); PREVIEWS=_load("build_activity_types_execution_preview")


def _active_english_is_available(languages: object) -> bool:
    """Check the OFSC metadata language collection for an active English locale."""
    if not isinstance(languages, dict):
        return False
    items = languages.get("items")
    if not isinstance(items, list):
        return False
    return any(
        isinstance(item, dict)
        and isinstance(item.get("label"), str)
        and (item["label"].casefold() == "en" or item["label"].casefold().startswith("en-"))
        and item.get("active") in (True, "true", "TRUE")
        for item in items
    )


class ActivityTypesAdapter:
    task_code="ORA_FFS_TS_ACTIVITY_TYPES"
    def resolve_route(self,direction: str|None)->dict[str,str]: return resolve_execution_route(ROOT.parent/"ora-resource"/"ora_rest_execution.md",self.task_code,direction)
    def preflight(self,workbook: Path,get: Any,temp: Path)->tuple[dict[str,Any],dict[str,dict[str,Any]]]:
        # Validate locally before resolving the canonical Customer group remotely.
        payload=PAYLOADS.build_preview_data(workbook,"customer")
        languages=get("/rest/ofscMetadata/v1/languages",temp/"languages.json")
        if not _active_english_is_available(languages): raise RuntimeError("Target environment does not expose an active English language.")
        group=get("/rest/ofscMetadata/v1/activityTypeGroups/customer",temp/"group.json")
        if not group or group.get("label")!="customer": raise RuntimeError("Canonical Customer Activity Type Group could not be verified.")
        baselines={}
        for sequence,request in enumerate(payload["requests"],1):
            label=request["body"]["label"]; baselines[label]=get(request["path"],temp/f"baseline-{sequence}.json") or {"label":label,"state":"not_found"}
        return payload,baselines
    def build_preview(self,payload: dict[str,Any],environment: str,baselines: dict[str,dict[str,Any]])->dict[str,Any]: return PREVIEWS.build_execution_preview(payload,"ora_rest_execution",environment,baselines)
    def mismatches(self,expected: dict[str,Any],actual: dict[str,Any])->list[str]:
        result=[key for key in ("label","active","groupLabel","defaultDuration") if actual.get(key)!=expected.get(key)]
        if [{k:x.get(k) for k in ("language","name")} for x in actual.get("translations",[])]!=expected.get("translations"): result.append("translations")
        return result+[f"features.{k}" for k,v in expected.get("features",{}).items() if actual.get("features",{}).get(k)!=v]
