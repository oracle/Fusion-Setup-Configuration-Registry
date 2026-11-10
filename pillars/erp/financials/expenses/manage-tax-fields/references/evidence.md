# Reviewed evidence and execution boundaries

## Portable contract

This task owns `EXM_MANAGE_TAX_FIELDS`. Preserve the exact same-target task
metadata, all CSV members, header sets, formats and current baseline evidence.
Tax switches use `ENABLE_TAX` with explicit Y/N values. The supported behavior
codes are REQUIRED (Required), ENABLED (Optional), and DISABLED (Hidden).
Keep the six controls distinct and validate target applicability. Literal OTHER
uses the task's explicit exception policy; do not look it up as an ISO country.

Resolve business-unit identity through the declared core preflight and require
an active, unique exact match with complete results. Resolve ordinary territories
through their declared validation route. Do not substitute a generic lookup
endpoint merely because its fields look similar. The approved import remains
responsible for field-domain validation; it is not a reference-data discovery API.

The candidate convention retains audit headers with empty cells and leaves audit
generation to Fusion. It does not establish blank business-field clearing or
column omission. Preserve the task's exact key and business-unit scope, reject
ambiguous identity, and never copy source-environment numeric keys into the input.
UI initialization is not an FSM default contract.

## Package ownership and preservation

Task exports can include both EXM_SETUP_OPTION and
EXM_CASH_ADV_SETUP_AND_POLICY members. Retain both original members and metadata.
The supported task contract populates only EXM_SETUP_OPTION for tax switches and
keeps the cash-advance alias header-only. Do not edit cash-advance settings, drop
an alias, infer populated-alias merging, or broaden scope to global settings.
Verify target acceptance and unrelated-data preservation after every approved
import. Omission of a row is not a deletion command.

## Validation coverage — 2026-10-07

The historical nonproduction campaign recorded 57 live setup passes, covering
selected creates, updates, all 18 field/value combinations and 30 directed
transitions. BU and territory preflight, terminal results and fresh-export
reconciliation were exercised. UI01 (hidden) and UI02 (optional blank) passed;
UI03 is partial: required-field validation was observed but supplied-value
persistence was not verified. Remaining transition/setup cases and live cleanup
are not certified. These are bounded historical observations, not a current
target's qualification or import approval.

The offline harness checks local contracts and mocked core behavior. It does
not prove live success. Current target identity, privileges, complete baseline,
references, exact-artifact approval and fresh-export reconciliation remain
mandatory. Runtime uses the co-shipped task contracts and core services; no
private source browser, campaign page or maintainer project is required.

## Provenance IDs

- `SRC-CS-LOOKUP-PVO` — maintainer source review; not an execution endpoint.
- `SRC-CS-LOOKUP-VIEW` — maintainer source review; not an execution endpoint.
- `SRC-CS-TASK` — maintainer source review; not an execution endpoint.
- `SRC-CS-TASK-BO` — maintainer source review; not an execution endpoint.
- `SRC-CS-UI-AM` — maintainer source review; not an execution endpoint.
- `SRC-CS-UI-AM-XML` — maintainer source review; not an execution endpoint.
- `SRC-CS-UI-VO` — maintainer source review; not an execution endpoint.
- `SRC-CS-EO` — maintainer source review; not an execution endpoint.
- `SRC-CS-FSM-AM` — maintainer source review; not an execution endpoint.
- `SRC-CS-FSM-VO` — maintainer source review; not an execution endpoint.
- `SRC-CS-EO-IMPL` — maintainer source review; not an execution endpoint.
- `SRC-CS-CASH-BO` — maintainer source review; not an execution endpoint.
- `SRC-CS-SETUP-FSM-AM` — maintainer source review; not an execution endpoint.
- `SRC-CS-TAX-SETUP-VO` — maintainer source review; not an execution endpoint.
- `SRC-CS-SETUP-EO` — maintainer source review; not an execution endpoint.
- `SRC-CS-BEHAVIOR-BOOTSTRAP` — maintainer source review; not an execution endpoint.
- `SRC-CS-MAPPING-MIGRATION` — maintainer source review; not an execution endpoint.
