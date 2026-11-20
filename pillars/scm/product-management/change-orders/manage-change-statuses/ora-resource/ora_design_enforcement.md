# Design Enforcement

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Purpose and naming | Keep stable descriptive status identity; use a clear operational purpose when one is supplied |
| 2 | Scope and update behavior | Keep status setup separate from item lifecycle, item status, and workflow assignment; resolve every selector, including Existing Internal Name, against a fresh populated export before preparing the update. When Existing Status is the only selector and has multiple matches, show and obtain approval for every matching row before preparing the update. |
| 3 | Impact and approval boundary | Require reviewed impact and test plan before preview; submit only through Data Loader approval |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| New status | Error |  | Temporary project, release, or organization-specific identity without a stable operational definition | Confirm naming purpose; a numeric suffix alone is not evidence of a temporary identity | User correction only |
| Before preview | Error |  | Unreviewed impact or missing test plan | Keep this operation to the standalone status definition; review later workflow assignment separately | Documented assessment only |
| Before import | Error |  | No immutable Data Loader preview with later explicit approval | Use core.data-loader; never infer import approval from execution or authoring requests | No |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MCS.DESIGN | step | 40 | design_enforcement | passed->MCS.RETURN_SUCCESS;blocked->RETURN_ISSUES | MCS.DEFAULTS | stop | Required input, lookup, and defaulting rules passed; evaluate pre-preview rules now and retain the import approval requirement for the Data Loader submission gate |
