# Manage Invoice Holds and Releases — Dependency Readiness

This file owns package and execution
prerequisites. Resolver behavior belongs to [Reference Lookups](ora_reference_lookups.md).
No prerequisite master-data creation or alternate execution route is defined here.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AP_HOLD.DEPENDENCIES | step | 30 | resolve_dependency | success->AP_HOLD.DEFAULTS;failure->AP_HOLD.ERRORS | AP_HOLD.LOOKUPS | stop | Setup-definition create/update/end-date request |

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Task and package identity | Qualify the package under Package and Runtime Prerequisites below. |
| 2 | Record and supporting lookup context | Apply the named resolvers in Reference Lookups. |
| 3 | Candidate and execution readiness | Apply the input, defaulting and design owners before the declared workflow's live gates. |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| hold_identity | Exact hold/release definition identity | Yes | Create or match existing setup definition | Verify | Fresh exact-task export and declared public identity preflight | find_hold_code_identity | Imported rows must refer to the intended task record. | Apply Record Identity in Reference Lookups. | Exact HoldLookupCode. |
| hold_type | Explicit type code | Yes (local input only) | Create; preserve baseline on update | Local validation | Requested canonical code or preserved baseline | | Type input and import membership have separate owners. | Apply the HoldType field contract in Input Validation and verify_hold_type in Reference Lookups. | Canonical HoldType. |
| hold_description | Lookup-backed business description | Yes | Create or update; preserve baseline when omitted | Local validation | Explicit requested description or preserved update baseline | resolve_hold_description | Fusion maintains the supporting lookup during ordinary import. | Apply the DspDescription field contract in Input Validation and this resolver in Reference Lookups. | Nonblank DspDescription. |
| import_contract | FSM matching and serialization | Yes | Create or supported update | Verify | Exact task template/current schema and selected workflow | | Matching and serialization govern imported rows. | Qualify the package/runtime below; use the candidate assembly contract in Input Validation. | Qualified package and declared execution prerequisites. |

## Package and Runtime Prerequisites

Establish exact AP_MANAGE_INVOICE_HOLDS_AND_RELEASES identity and matching
template/current schema through the selected export workflow. Retain package
metadata and actual process results. Keep environment identity, privileges,
capability checks and transport/runtime prerequisites in the declared workflow;
a catalog CSV-support flag alone does not establish import support. This file
adds no deployment or setter-order proof requirement to accepted input values.

For the local manifest, match the explicitly selected Fusion environment to
the package's ProcessEnv exactly. Keep an authentication-profile label separate;
do not derive an environment by stripping a profile suffix. The base URL must
be a credential-free HTTPS origin with a valid host and optional port, without
a path (including /), query or fragment. The owning workflow verifies that
the origin belongs to the selected environment. template_only must be a
Boolean: true requires no data rows, while false permits an empty data export.
An empty archive alone does not establish the export mode.

Before publishing outputs or returning a no-op, validate archive identity,
metadata coverage, ordered headers, record widths, portable keys, schema
fingerprints and compatibility with the task package. Reject unsafe or
nonregular archive members and enforce the runtime's archive size/ratio limits.
Apply the output-path and publication rules in
[Local artifact protection](ora_error_handling.md#local-artifact-protection).

## Importer Contract

The importer matches rows by their task primary key, rejects multiple matches,
and uses the matched row or creates an absent row. Apply the requested-operation
identity checks in [Reference Lookups](ora_reference_lookups.md#record-identity)
before relying on that behavior.

Ordinary empty and quoted-empty CSV fields serialize as explicit null. Omitted
XML fields make no direct assignment. The full-row candidate's preservation
rules, accepted clears and required fields are owned by
[Input Validation](ora_input_validation.md).
The importer skips read-only audit fields and insert-only key/type fields on
existing rows.

The reader queues values before the multi-setter. Equal persistent nonmutable
values skip unless a backward dependency is already queued; null/null persistent
values skip. HoldInstruction, WaitBeforeNotifyDays and ReminderDays depend on
InitiateWorkflowFlag; these four fields store their supplied values directly.
Pre-import field-combination rules and import processing are owned by Design Enforcement. Optional reconciliation,
conditional accounting diagnostics, import failure and recovery are owned by
[Error Handling](ora_error_handling.md).

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Satisfied | The complete task contract and selected-runtime evidence agree | Only the declared owner may continue; no implicit mutation |
| Verify | A read-only contract exists and workflow prerequisites pass | Declared read-only lookup only |
| Blocked | Contract, identity or target reference remains unresolved | No mutation; retain exact gap and closure action |
| Unavailable | Auth/transport/service preflight did not yield a valid answer | No invented zero-match or reference value; preserve failure |
