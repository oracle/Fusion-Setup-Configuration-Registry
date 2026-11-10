# Manage Transaction Sources Reference Lookups


Public lookups are optional read-only preflight. The exact-task FSM import resolver remains authoritative for application. Transport or authorization unavailability does not convert a valid import resolver into an unsupported path; zero or multiple business matches remain blocking data outcomes.

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| resolve_legal_entity_by_identifier | LegalEntityIdentifier is supplied | LegalEntityIdentifier | GET /fscmRestApi/resources/11.13.18.05/legalEntitiesLOV | LegalEntityId, LegalEntityIdentifier, LegalEntityName | Require exactly one exact identifier match | LegalEntityId from the matching item | Block zero matches; block multiple matches and request a precise identifier |
| resolve_transaction_type_by_name_and_set | TrxTypeName or InvTrxTypeSetCode is supplied | TrxTypeName, InvTrxTypeSetCode | GET /fscmRestApi/resources/11.13.18.05/transactionTypesLOV | TransactionTypeId, Name, SetName | Require exactly one exact Name plus SetName match | DefaultInvTrxTypeSeqId from the matching transaction type after FSM alternate-key resolution | Block zero matches; block multiple matches and require both portable keys |
| resolve_credit_transaction_source_by_name_and_set | BatchSourceName or CmBatchSrcSetCode is supplied | BatchSourceName, CmBatchSrcSetCode | GET /fscmRestApi/resources/11.13.18.05/transactionSourcesLOV with SetName filter and client-side exact Name comparison | TransactionSourceId, Name, SetName | Follow collection paging and require exactly one exact Name plus SetName match | CmBatchSourceSeqId from the matching source after FSM second-pass resolution | Block zero matches; block multiple matches and require both portable keys |

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| Public lookup succeeds with one exact match | Retain sanitized match evidence and continue; do not serialize the public identifier when the FSM package uses a portable alternate key |
| Public lookup returns zero rows | Block the affected record and report the missing business key |
| Public lookup returns multiple rows | Block the affected record and request the missing set or identifier context |
| Public lookup is unavailable because of 401, 403, TLS, timeout, or 5xx | Record optional preflight as unavailable and continue only to offline candidate build; exact-task FSM validation remains required before any approved import |
| Resolver has no supported public operation | Do not invent an endpoint; preserve the portable key for the reviewed FSM import resolver |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MTS.LOOKUP_REFERENCES | decision | 3 | reference_lookup | resolved->MTS.APPLY_DEFAULTS;not_applicable->MTS.APPLY_DEFAULTS;optional_unavailable->MTS.APPLY_DEFAULTS;blocked->MTS.RETURN_ISSUES | MTS.RESOLVE_DEPENDENCIES | stop | One or more supported public-preflight reference keys are supplied |

## Source Anchors

| Source IDs | Use |
|---|---|
| SRC-REST-LEGAL-26C | Supported read-only legal-entity resource |
| SRC-REST-TRXTYPE-26A | Supported read-only Receivables transaction-type resource; newer exact-topic attempts are recorded in the Source Register |
| SRC-REST-TRXSOURCE-26A | Supported read-only Receivables transaction-source resource; newer exact-topic attempts are recorded in the Source Register |
| SRC-CS-AMIMPL | Authoritative FSM import mappings and failure boundary |
