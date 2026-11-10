# Manage Transaction Sources Design Enforcement


<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: ORA_AR_TXN_BATCH_SOURCE::AutoTrxNumberingFlag, ORA_AR_TXN_BATCH_SOURCE::BatchSourceType, ORA_AR_TXN_BATCH_SOURCE::Description, ORA_AR_TXN_BATCH_SOURCE::InvalidLinesRule, ORA_AR_TXN_BATCH_SOURCE::LastBatchNum, ORA_AR_TXN_BATCH_SOURCE::Name, ORA_AR_TXN_BATCH_SOURCE::SetCode, ORA_AR_TXN_BATCH_SOURCE::StartDate, ORA_AR_TXN_BATCH_SOURCE::Status -->
<!-- fscr-update-fields: ORA_AR_TXN_BATCH_SOURCE::Description -->

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Confirm portable identity | Name and SetCode identify the intended source without numeric IDs |
| 2 | Confirm entity-operation ownership | Create targets ORA_AR_TXN_BATCH_SOURCE. Update targets the one package entity containing the exact Name plus SetCode key in the fresh export; stop if absent, duplicated, or present in both entities |
| 3 | Confirm source type boundary | Manual and Imported fields are not mixed |
| 4 | Confirm reference closure | Every supplied business key has the required set or identifier context |
| 5 | Confirm field disposition | Supported, unsupported, and explicitly unresolved update fields retain separate behavior |
| 6 | Preserve ordered self-reference | Credit transaction source resolution remains in the second FSM import pass |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Creating a customer-defined source | Error | | Name begins with ORA_ | Choose a non-reserved name | Yes, before preview |
| Creating or matching a source | Error | | Name plus SetCode is absent or ambiguous | Supply the exact portable key pair | Yes, before preview |
| BatchSourceType is INV | Error | | An Imported-only AutoInvoice field other than evidenced InvalidLinesRule is supplied | Remove the unsupported Imported-only field or select Imported intentionally; InvalidLinesRule=Reject remains valid for the evidenced Manual create path | Yes, before preview |
| An operation targets the wrong package entity | Error | | Create does not target ORA_AR_TXN_BATCH_SOURCE, or update does not target the one entity containing the exact Name plus SetCode key in the fresh export | Route create to ORA_AR_TXN_BATCH_SOURCE; route update to the exact export-owning entity and preserve the other member | No |
| Description is requested for update | Error | | Any deterministic field or resolver validation fails | Correct the exact failure; otherwise continue as a source-backed supported update field | Yes, before preview |
| An eligible unresolved field on the exact export-owning update entity is requested | Error | | A deterministic check fails, the evidence gap was not disclosed, or exact implementor approval for governed application validation is absent | Correct deterministic failures or obtain exact operation-, entity-, field-, environment-, and candidate-bound approval; never label the field supported merely because a trial is approved | Yes only through the governed application-validation choice |
| A completion-control, usage-category, or sales-territory value is requested for update | Error | | The value is known invalid or cannot be mapped to an exact package value using current Partial evidence | Correct the value; if an exact package value passes deterministic checks, retain the field as unresolved and use the governed application-validation decision path | Yes only for an exact deterministically valid value and explicit governed approval |
| A key, audit/identity, source-proven unsupported, package-integrity, authorization, or non-target field is requested for update | Error | | The field is non-overrideable or any deterministic validation fails | Remove the blocked field; do not offer application validation as a bypass | No |
| A credit transaction source is supplied | Error | resolve_credit_transaction_source_by_name_and_set | BatchSourceName lacks CmBatchSrcSetCode, the match is not unique, or second-pass ordering is lost | Supply both keys and retain AR_CM_TRX_BATCH_SOURCE before AR_TRX_BATCH_SOURCE | Yes, before preview |
| Normal create input includes audit or derived numeric identifier fields | Error | | Audit or derived identifiers would be serialized from user input | Remove system-managed values and use portable alternate keys | Yes, before preview |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| resolve_credit_transaction_source_by_name_and_set | A credit transaction source is supplied | BatchSourceName, CmBatchSrcSetCode, CmBatchSourceSeqId | ora_reference_lookups.md |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MTS.ENFORCE_DESIGN | decision | 5 | design_enforcement | pass->MTS.HANDOFF_GATE;blocked->MTS.RETURN_ISSUES | MTS.APPLY_DEFAULTS | stop | Every candidate before package handoff |

## Source Anchors

| Source IDs | Use |
|---|---|
| SRC-CS-EO; SRC-DOC-EDM-26A | Reserved-name, persistence, and unique-key constraints |
| SRC-CS-AMIMPL; SRC-CS-CMVO; SRC-FSM-TEMPLATE | Ordered two-file import and second-pass self-reference |
| SRC-UI-MTS; SRC-DOC-COMPLETION-26C; SRC-FSM-CURRENT | Surfaced completion choices versus package boolean boundary |
| SRC-CS-CREATE-VO; SRC-DOC-BO-26C | Manual/Imported conditional rules and system-owned field boundary |
| SRC-CS-CREATE-VO; SRC-CS-EDIT-VO; SRC-CS-VO; SRC-CS-CMVO; SRC-CS-AMIMPL; SRC-E2E-MTS-CREATE-20260906; SRC-E2E-MTS-UPDATE-20260905; SRC-E2E-MTS-AR-UPDATE-ROUTING-20260910 | Complete relationship-partition ownership matrix, export-owned update routing, supported ORA Description update, and same-entity update reconciliation |
