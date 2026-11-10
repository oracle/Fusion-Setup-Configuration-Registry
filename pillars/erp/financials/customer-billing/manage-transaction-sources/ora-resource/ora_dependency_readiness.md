# Manage Transaction Sources Dependency Readiness


## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Reference data set | Resolve SetCode to the target SetId context during FSM import |
| 2 | Legal entity | Resolve LegalEntityIdentifier when supplied |
| 3 | Standard transaction type | Resolve InvTrxTypeSetCode first, then TrxTypeName in that set |
| 4 | AutoInvoice grouping rule | Resolve GroupName for an Imported source when supplied |
| 5 | Revenue Management source document type | Resolve DocumentTypeCode when supplied |
| 6 | Credit transaction source | Resolve CmBatchSrcSetCode first, then BatchSourceName in the second import pass |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| transaction_source_set | Reference data set | Yes | Every source | Satisfied when portable key is present; FSM validates | SetCode from the request | | Name uniqueness and all dependent references are set-scoped | Supply an exact reference-data-set code | SetId from SetIdSetPVO.SetIdSetCodeKey |
| legal_entity | Legal entity | Conditional | LegalEntityIdentifier is supplied | Lookup | LegalEntityIdentifier from the request | resolve_legal_entity_by_identifier | Legal ownership is optional but must resolve unambiguously when supplied | Supply an exact legal entity identifier | LegalEntityId |
| standard_transaction_type | Receivables transaction type | Conditional | TrxTypeName or InvTrxTypeSetCode is supplied | Lookup | TrxTypeName and InvTrxTypeSetCode from the request | resolve_transaction_type_by_name_and_set | The transaction type is reference-data-set scoped | Supply both name and set code | DefaultInvTrxTypeSeqId |
| autoinvoice_grouping_rule | AutoInvoice grouping rule | Conditional | GroupName is supplied and BatchSourceType is FOREIGN | Satisfied when portable key is present; FSM validates | GroupName from the request | | The import hook resolves the alternate key; no supported public preflight was confirmed | Supply the exact grouping-rule name | GroupingRuleId during FSM import |
| source_document_type | Revenue Management source document type | Conditional | DocumentTypeCode is supplied | Satisfied when portable key is present; FSM validates | DocumentTypeCode from the request | | The import hook resolves AltKeyDocType; no supported public preflight was confirmed | Supply the exact source-document-type code | DocumentTypeId during FSM import |
| credit_transaction_source | Receivables transaction source | Conditional | BatchSourceName or CmBatchSrcSetCode is supplied | Lookup | BatchSourceName and CmBatchSrcSetCode from the request | resolve_credit_transaction_source_by_name_and_set | The self-reference requires set context and second-pass resolution | Supply both source name and set code | CmBatchSourceSeqId |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Satisfied | Required portable key is present and no early lookup is required | Continue to package preview; FSM validation remains authoritative |
| Lookup | A supported read-only public resource can validate the key early | Run lookup only; never create related setup |
| Blocked | A required key is missing, has zero matches, or is ambiguous | No; return issues and do not build an approvable candidate |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MTS.RESOLVE_DEPENDENCIES | decision | 2 | resolve_dependency | ready->MTS.LOOKUP_REFERENCES;blocked->MTS.RETURN_ISSUES | MTS.VALIDATE_INPUT | stop | After input validation |

## Source Anchors

| Source IDs | Use |
|---|---|
| SRC-CS-AMIMPL; SRC-CS-AM; SRC-CS-VO; SRC-CS-CMVO | Ordered alternate-key resolution and second-pass self-reference |
| SRC-FSM-TEMPLATE; SRC-CS-TASK-BO | Two-object import sequence and portable key fields |
| SRC-DOC-PREREQ-26C; SRC-DOC-BO-26C | Functional prerequisite boundaries |
