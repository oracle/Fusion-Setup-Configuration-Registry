---
skill_id: "cx.field-service"
name: "Field Service"
description: "Coordinates CX implementation guidance for the Field Service offering."
layer: "pillar"
pillar: "CX"
offering: "Field Service"
source_catalog: "knowledge/setup-task-catalog/effective/Offerings_catalog.json"
type: "orchestration"
execution_mode: "assisted"
owner_team: "CX Field Service pillar team"
version: "0.1.0"
inputs:
  - "implementation_objective"
  - "project_context"
  - "field_service_requirements"
outputs:
  - "offering_scope"
  - "functional_area_skill_plan"
  - "token_usage_record"
depends_on:
  - "shared.project-intake.scope-definition"
  - "shared.implementation-planning.offering-task-map-builder"
uses_core:
  - "core.project-mgmt.project-state-manager"
persists_project_state: true
token_usage_tracking:
  enabled: true
  granularity: "per_skill_run"
  artifact_type: "token_usage_record"
  default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
  estimation_method: "chars/4 estimate unless exact tokenizer or API accounting is available"
  required_fields:
    - "activity_start_time"
    - "skill_id"
    - "task"
    - "trigger"
    - "artifacts_written"
    - "files_read"
    - "estimated_input_tokens"
    - "estimated_output_tokens"
    - "estimated_total_tokens"
    - "estimation_method"
    - "notes"
state_updates:
  - "scope"
  - "skill_path"
  - "token_usage_records"
workspace_outputs:
  - artifact_type: "scope"
    default_location: "project/{project_id}/artifacts/pillars/cx/field-service/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
    versioning_policy: "append-only"
applicability:
  industries:
    - "All"
  countries:
    - "All"
  fusion_releases:
    - "Current Oracle Fusion Cloud release"
side_effects: []
required_privileges: []
---

# Field Service

## Purpose

Coordinates implementation work for offering `Field Service` (`ORA_FIELD_SERVICE`) under the `CX` pillar.

## Routing Responsibility

Resolve the requested functional area against the effective catalog and route to
its existing child `SKILL.md`. If the catalog entry has no packaged child skill,
report the missing route and stop before execution.

## Functional Areas From Effective Catalog

Source: `knowledge/setup-task-catalog/effective/offering-functional-area-task-catalog.json`
Offering code: `ORA_FIELD_SERVICE`
Functional area count: `4`
Setup task count: `32`

- `ORA_SVC_COMPANY_PROFILE`: Company Profile
- `ORA_ASK_USERS_AND_SECURITY`: Users and Security
- `ORA_FFS_FA_MOBILE_EXPERIENCE`: Mobile Experience
- `ORA_FFS_FA_SCHEDULING_AND_DISPATCH`: Scheduling and Dispatch

### Field Service guarded workbook intake

`pillars/cx/field-service/scripts/guarded_xlsx.py` provides the Field Service `GuardedWorkbook`,
`column_index`, and `shared_string` Python interfaces for local XLSX intake.
It bounds ZIP inflation, XML structure, worksheet allocation, string sizes,
and elapsed parsing time before callers construct task-specific Field Service records.
Callers use a context manager and handle `ValueError` as an input-validation
failure. Limits are cumulative for one open workbook. Field mappings and
business validation remain with the caller. The primitive reads local files
only and performs no network requests, archive extraction, or writes. Using
this primitive does not initiate a load or grant approval for execution.

Architecture exception `FFS-LAYER-001` is accepted by the user for this helper
and its six Field Service consumers. The bounded reader remains owned and
maintained inside Field Service. This exception concerns placement only; it
does not waive input limits, adversarial tests, approval checks, or other
security findings.

### Typed REST read failures

`scripts/rest_client_status.py` delegates to the existing Core REST client and
returns a small JSON error envelope based on its typed HTTP exception. The
shared task runner treats only an authoritative numeric HTTP 404 as absence.
Response-body text and authentication diagnostics cannot establish a creation
baseline. The adapter adds no authentication, transport, or retry mechanism.
