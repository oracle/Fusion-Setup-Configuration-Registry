# Dependency Readiness

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Exact task package | Confirm the selected task and AP_SYSTEM_PARAMETER package match the same-task exports |
| 2 | Business-unit scope | Confirm one target business unit without creating or selecting a record implicitly |
| 3 | Shared AP_SYSTEM_PARAMETER contract | Run the delegated Invoice Options read-only preflight, then load and validate the versioned Manage Invoice Options adapter before candidate preparation |
| 4 | Field evidence | Resolve any field-specific reference, allowed-value, or lifecycle contract before candidate preparation |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| PAYOPT-PACKAGE | Exact AP_SYSTEM_PARAMETER package | Yes | Always | Verify | Same-task current and template exports | | Prevents task/package substitution | Re-export if package identity differs | Exact header and metadata identity |
| PAYOPT-BU | Target business unit | Yes | Before candidate preparation | Verify | Fresh same-task export and approved request context | | Prevents an ambiguous setup target | Provide one target business unit | Target business-unit identity |
| PAYOPT-SHARED-AP-SYSTEM-PARAMETER | Manage Invoice Options shared-row contract | Yes | Every supported Payment operation | Verify | `scripts/resolve_lookup_prerequisites.py`, `../manage-invoice-options/e2e-adapter.json`, and `../manage-invoice-options/scripts/fsm_task_adapter.py` | | The delegated preflight records applicable read-only lookup receipts; Payment runtime then validates the complete resulting AP_SYSTEM_PARAMETER row through the sibling Invoice Options contract. Prevents a Payment Options setup request from creating or retaining an invalid Invoice Options-owned or shared value; Invoice Options updates reciprocally validate resulting Payment-owned values through this task | Run the delegated preflight before normalization; refresh task evidence when either task's AP_SYSTEM_PARAMETER header, key, audit, node, or lifecycle contract differs | Sibling adapter and runtime must be present and structurally compatible; their documented create defaults must be present in the actual CSV for a new row |
| PAYOPT-OPTIONAL-UPDATE-FIELD-CONTRACT | Optional Payment field update contract | Yes | Any optional Payment Options field is supplied for update | Verify or evidence-unresolved | Exact task export, task-local field contract, and field-specific update evidence | | All optional Payment fields use the same request-driven validation path. A field with incomplete update evidence is not a special product case or silently excluded; it requires the normal field-bound governed application-validation override. | Validate the supplied value, preserve unrelated fields, and bind an override exactly to each update field whose contract remains unresolved. | Current baseline and requested optional Payment fields |
| PAYOPT-UI-PAYMENT-FIELDS | Payment Options UI-field contract | Yes | Every Payment Options or Invoice Options setup-row create/update candidate that resolves AP_SYSTEM_PARAMETER | Verify | Exact Payment Options export plus the task-local `paymentOwnedFields` contract | | The shared row validates the Payment-owned controls—postdated payment permission, supplier-bank override, payment document-category override, third-party payee override, conversion-rate requirement, payment accounting, Bank Charge Deduction Type, and escheatment days—even when the request originates from Invoice Options. Bank Charge Deduction Type serializes as `Standard`, `Negotiated`, or `None` in the CSV, rather than the database codes `S`, `N`, or `X`. | Correct the applicable supplied value or refresh the exact baseline; do not treat task ownership as permission to skip sibling validation. | Complete resulting AP_SYSTEM_PARAMETER row |

## What These Statuses Mean

| Status | Plain Meaning | What Happens Next |
|---|---|---|
| Verify | Required source evidence, task identity, or a sibling contract must be present and consistent. | Obtain or correct the required evidence before candidate preparation. |
| Verify or evidence-unresolved | The field follows the normal validation path, but its update contract may still be incomplete. | Bind the governed field-specific override to each unresolved update field, or obtain evidence that resolves the contract. |
| Resolve | The user-facing value cannot safely be serialized until its exact package field and resolver are known. | Keep the value out of the candidate until the evidence gap is closed. |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Ready | Every mandatory dependency is verified | No; proceed only to governed preview |
| Blocked | Any package, scope, or field contract is incomplete | No |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| PAYOPT.CHECK_DEPENDENCIES | step | 20 | resolve_dependency | ready->PAYOPT.APPLY_DEFAULTS;blocked->PAYOPT.DEPENDENCY_BLOCKED | PAYOPT.LOOKUP_PREFLIGHT | stop | Always |
