# Manage Transaction Sources Input Validation


<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: ORA_AR_TXN_BATCH_SOURCE::AutoTrxNumberingFlag, ORA_AR_TXN_BATCH_SOURCE::BatchSourceType, ORA_AR_TXN_BATCH_SOURCE::Description, ORA_AR_TXN_BATCH_SOURCE::InvalidLinesRule, ORA_AR_TXN_BATCH_SOURCE::LastBatchNum, ORA_AR_TXN_BATCH_SOURCE::Name, ORA_AR_TXN_BATCH_SOURCE::SetCode, ORA_AR_TXN_BATCH_SOURCE::StartDate, ORA_AR_TXN_BATCH_SOURCE::Status -->
<!-- fscr-update-fields: ORA_AR_TXN_BATCH_SOURCE::Description -->

This contract validates portable create and update input for `AR_MANAGE_TRANSACTION_SOURCES`. It does not authorize a Fusion import. Package assembly and any later write remain owned by Run Book and `core.data-loader`.

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Transaction source identity | Name, SetCode | Block the record | Supply a nonblank name and an exact reference-data-set code | Every create request | |
| Existing transaction source identity | Name, SetCode | Block the request | Supply the exact portable key pair for one current record | Every update request | |
| Core create information | Description, BatchSourceType, StartDate | Block the record | Supply Description, Manual or Imported type, and the active-from date | Every create request | |
| Automatic numbering state | LastBatchNum | Block the record | Supply an explicit integer of at least 1; the new sequence uses it directly as its start | Creating a source with explicit or defaulted AutoTrxNumberingFlag Y | |
| Default transaction type reference | TrxTypeName, InvTrxTypeSetCode | Block only the unresolved default | Supply both portable keys or omit both | A standard transaction type is requested | resolve_transaction_type_by_name_and_set |
| Credit transaction source reference | BatchSourceName, CmBatchSrcSetCode | Block only the unresolved credit source | Supply both portable keys or omit both | A credit transaction source is requested | resolve_credit_transaction_source_by_name_and_set |

## Dependency-Aware Validation

| Applies When | Result | Next Action | Resolver |
|---|---|---|---|
| LegalEntityIdentifier is supplied | Lookup | Resolve exactly one legal entity before preview when the public service is available; otherwise retain the key for FSM validation | resolve_legal_entity_by_identifier |
| GroupName is supplied for an Imported source | Verify during FSM validation | Preserve the portable grouping-rule name; do not invent an identifier | |
| DocumentTypeCode is supplied | Verify during FSM validation | Preserve the source-document-type code; do not invent an identifier | |
| BatchSourceName is supplied | Lookup | Resolve the set context first and retain second-pass self-reference ordering | resolve_credit_transaction_source_by_name_and_set |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Name must not begin with ORA_ for a new customer-defined source | Reject the record before package build | Creating a non-seeded source | |
| LastBatchNum must be at least 1 for a new automatic-numbering sequence | Reject zero or negative input before package build; never substitute another number | Creating a source with explicit or defaulted AutoTrxNumberingFlag Y, for either Manual or Imported type | |
| BatchSourceType normalization | Accept Manual or INV as INV; accept Imported or FOREIGN as FOREIGN; reject other values | Every create request | |
| Status normalization | Accept Active or A as A; accept Inactive or I as I | Status is supplied | |
| Fixed rule normalization | Convert reviewed business labels case-insensitively to the exact package codes in the Attributes Workbook | Any fixed-choice field is supplied | |
| Audit and derived identifiers | Exclude LastUpdateDate, LastUpdatedBy, CreationDate, CreatedBy, LastUpdateLogin, DefaultInvTrxType, and LegalEntityName from normal create input | Every create request | |
| Imported-only rule fields other than evidenced InvalidLinesRule | Reject unsupported Imported-only fields on a Manual source; preserve InvalidLinesRule when supplied or defaulted to Reject | BatchSourceType is INV | |
| Flexfield values | Preserve only explicitly supplied configured context and segment values; never infer deployment-specific segments | Any DFF or GDF attribute is supplied | |
| Supported update field | Accept `Description` after normal deterministic validation | Updating `ORA_AR_TXN_BATCH_SOURCE.Description` | |
| Evidence-unresolved update field | Run all known deterministic checks, then stop with an evidence-gap disclosure unless the implementor explicitly approves the exact operation-, entity-, field-, environment-, and candidate-bound FSM application-validation path | Updating an eligible non-key, non-audit field on the one package entity containing the exact Name plus SetCode key in the fresh export | |
| Entity ownership | Require exactly one Name plus SetCode match across the fresh package and target the entity containing it for update; reject absent, duplicated, cross-entity, or mismatched ownership | Create targets `ORA_AR_TXN_BATCH_SOURCE`; update targets the exact export-owning entity | |
| Non-overrideable update field | Reject the request before preview | The field is a key, audit/identity control, source-proven unsupported field, package-integrity requirement, authorization control, or has a deterministic validation failure | |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MTS.VALIDATE_INPUT | decision | 1 | validate_input | valid->MTS.RESOLVE_DEPENDENCIES;invalid->MTS.RETURN_ISSUES | none | stop | Every normalized create, update, or validation request |

## Source Anchors

| Source IDs | Use |
|---|---|
| SRC-FSM-TEMPLATE; SRC-CS-VO; SRC-CS-EO | Exact package fields, alternate keys, requiredness, persistence, and custom-name rule |
| SRC-UI-MTS; SRC-CS-CREATE-VO; SRC-DOC-COMPLETION-26C | Create requiredness, labels, defaults, and conditional UI behavior |
| SRC-DOC-BO-26C; SRC-FSM-CURRENT | Published enumerations and exact observed package codes |
| SRC-CS-CREATE-VO; SRC-CS-EDIT-VO; SRC-CS-VO; SRC-CS-CMVO; SRC-CS-AMIMPL; SRC-E2E-MTS-CREATE-20260906; SRC-E2E-MTS-UPDATE-20260905; SRC-E2E-MTS-AR-UPDATE-ROUTING-20260910 | Relationship-partition ownership, supported-field boundary, export-owned update routing, and reconciliation targets |
| SRC-CS-EO-NUMBERING-2610 | TransactionBatchSourceEOImpl.validateEntity, lines 40–64: when numbering is Y and the sequence does not yet exist, MINVALUE is 1 and START WITH uses LastBatchNum directly. This establishes the create lower bound; it does not establish an update-field range or a business default. |
