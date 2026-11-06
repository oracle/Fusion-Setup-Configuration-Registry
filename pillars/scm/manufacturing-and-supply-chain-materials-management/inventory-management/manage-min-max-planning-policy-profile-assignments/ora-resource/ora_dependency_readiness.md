# Manage Min-Max Planning Policy Profile Assignments Dependency Readiness

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Data Loader business-object metadata | Run a metadata preflight for minMaxPolicyAssignments in the selected target environment before each Data Loader handoff. |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| dataloader_metadata_preflight | minMaxPolicyAssignments Data Loader metadata | Yes | Every REST/Data Loader handoff | Verify | Per-run target-environment Data Loader metadata preflight | | External BO-registration completion is user-provided provenance only. A prior successful preflight is runtime evidence only and cannot be reused for a later load. | Verify the exact discriminator minMaxPolicyAssignments in the selected target environment before handoff. If unavailable, stop; do not use direct REST as a fallback. | Selected environment, minMaxPolicyAssignments discriminator, metadata-preflight result |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Satisfied | The current run's metadata preflight confirms minMaxPolicyAssignments in the selected target environment. | No |
| Blocked | The metadata preflight fails, is unavailable, or does not expose minMaxPolicyAssignments. | No |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MIN_MAX_POLICY_ASSIGNMENTS.PREFLIGHT_DATALOADER_METADATA | step | 20 | resolve_dependency | ready->RETURN_SUCCESS;blocked->RETURN_ISSUES | MIN_MAX_POLICY_ASSIGNMENTS.VALIDATE_INCLUDE_IN_CAL | stop | Before every REST/Data Loader handoff. |
