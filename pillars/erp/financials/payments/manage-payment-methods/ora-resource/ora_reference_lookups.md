# Manage Payment Methods reference lookups

Only confirmed GET operations are executable preflights. They do not establish FSM import acceptance. Match against the selected environment immediately before a candidate build; do not cache customer values. Sources: SRC-ORACLE-PMT-METHOD-LOV-26C, SRC-ORACLE-FIN-BU-LOV-26C, SRC-REVIEW-LE-REST-26D.

## Setup-parent identity resolution

`resolve_setup_payment_method_by_code` uses the fresh same-environment export
for this FSM task. Match exactly one `ORA_IBY_FD_PARENT_PAY_MET.PaymentMethodCode`,
or one explicit same-candidate parent create with no baseline collision.
Require exact child ancestor addressing and the full validation-assignment
context. Reject missing or duplicate parents, conflicting candidate identities,
and stale or wrong-task/environment evidence. A carried dependency row is not
an explicit parent create. Preserve existing seeded-parent and import-side-effect
gates. No new network operation is introduced by this resolver.

The transactional REST LOV is not an exhaustive setup-parent registry. Reviewed
source routes its no-finder request through AllPaymentMethod, whose SQL requires
an IBY_APPLICABLE_PMT_MTHDS row with type PAY_PROC_TRXN_TYPE. A setup method with
only domestic applicability can therefore be absent. Do not add usage rows just
to make the LOV return it. Source: SRC-REVIEW-PM-LOV-SCOPE, validated against a
fresh setup export and contrasting live LOV results.

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| find_payment_method_by_code | Optional transactional LOV corroboration; never a setup-parent existence gate | PaymentMethodCode | /fscmRestApi/resources/11.13.18.05/disbursementPaymentMethodsLOV | PaymentMethodCode, PaymentMethodName | Require one exact context-appropriate match when interpreting a returned row; paginate if needed. | Corroborating code only; cannot replace setup-export identity resolution. | Zero does not establish missing setup: the no-finder source query requires PAY_PROC_TRXN_TYPE usage. Multiple rows remain ambiguous for this lookup. Access failures remain unavailable evidence. |
| find_business_unit_by_name | IBY_FD_PAYMENT_METHOD.BuName | IBY_FD_PAYMENT_METHOD.BuName | /fscmRestApi/resources/11.13.18.05/finBusinessUnitsLOV | BusinessUnitName, BusinessUnitId, ActiveFlag | Filter on BusinessUnitName and require one exact context-appropriate match; paginate if needed. | Return BusinessUnitId only after exact matching; do not invent a value. | Zero: Block this candidate with a missing-reference result. Multiple: Block this candidate as ambiguous; do not choose a row. Failure: Treat authentication, transport or response-contract errors as preflight unavailable; no mutation follows automatically. |
| find_legal_entity_by_identifier | IBY_FD_PAYMENT_METHOD.LEName | IBY_FD_PAYMENT_METHOD.LEName | /fscmRestApi/resources/11.13.18.05/legalEntitiesLOV | LegalEntityIdentifier, Name, LegalEntityId, EffectiveFrom, EffectiveTo | Match CSV LEName to LegalEntityIdentifier, not display Name; require one exact context-appropriate match and paginate if needed. | Retain the exact LegalEntityIdentifier in LEName and record LegalEntityId as reference evidence; do not invent a value. | Zero: Block this candidate with a missing-reference result. Multiple: Block this candidate as ambiguous; do not choose a row. Failure: Treat authentication, transport or response-contract errors as preflight unavailable; no mutation follows automatically. |

## Unresolved Reference Contracts

| Requirement | Attributes | Source Kind | Evidence | Gap and next gate |
|---|---|---|---|---|
| RESOLVER-PM-APP | IBY_FD_PAYMENT_METHOD.ApplicationShortName | table_or_view | SRC-CODE-IBY-SVC-AM-IMPL, SRC-CODE-IBY-SVC-AM-XML | Import writes ApplicationId only when an ApplicationPVO row is found; surfaced no-match and duplicate behavior remain unproved. |
| RESOLVER-PM-TYPE | IBY_FD_PAYMENT_METHOD.ApplicableTypeCode | fixed_enumeration | SRC-CODE-IBY-SVC-AM-IMPL, SRC-CODE-IBY-SVC-CHILD-VOS | Code proves branch values but not an exhaustive allowed set or type-specific value mapping. |
| RESOLVER-PM-DOC-CAT | ORA_IBY_FD_PARENT_PAY_MET.DocumentCategoryCode | table_or_view | SRC-CODE-IBY-SVC-PARENT-VO, SRC-CODE-IBY-PMT-EO-XML | EDM documents the column but does not prove this task's import resolver or current configured categories. |
| RESOLVER-PM-MODE | ORA_IBY_FD_PARENT_PAY_MET.PaymentModeCode | lookup_type | SRC-CODE-IBY-PMT-VO-XML, SRC-CODE-IBY-SVC-PARENT-VO | UI lookup binding is confirmed; complete allowed package codes and import validation are not. |
| RESOLVER-PM-VAL-SET | ORA_PMT_METHOD_VALIDATION_ASSIGNMENT.ValidationSetCode, ORA_PAYMENT_METHOD_VALIDATION_VALUE.ValidationSetCode | table_or_view | SRC-CODE-IBY-SVC-ASSIGN-VO, SRC-CODE-IBY-SVC-VALUE-VO, SRC-CODE-IBY-SVC-AM-IMPL | Validation-set existence, context and surfaced import failure remain unverified. |
| RESOLVER-PM-TERRITORY | ORA_PMT_METHOD_VALIDATION_ASSIGNMENT.TerritoryCode | table_or_view | SRC-CODE-IBY-SVC-ASSIGN-VO | The territory code may be seeded, but the assignment import's accepted values and failure surface are unproved. |
| RESOLVER-PM-FIELD | ORA_PMT_METHOD_VALIDATION_ASSIGNMENT.FieldNameCode | unspecified | SRC-CODE-IBY-SVC-ASSIGN-VO, SRC-CODE-IBY-VALIDATION-EOS | Code and configured validation-set dependency need to be traced before a code list is generated. |
| RESOLVER-PM-PARAM | ORA_PAYMENT_METHOD_VALIDATION_VALUE.ValidationParameterCode | table_or_view | SRC-CODE-IBY-SVC-VALUE-VO, SRC-CODE-IBY-VALIDATION-EOS | Parameter choice must be tied to the selected validation set and parameter type; import failure remains unverified. |
| RESOLVER-PM-PARENT-FSM | IBY_FD_PAYMENT_METHOD.PaymentMethodCode | table_or_view | SRC-CODE-IBY-BO-REF-SEED, SRC-CODE-IBY-SVC-AM-IMPL | Seeded parent suppression and existing custom parent behavior are confirmed; preflight context and collision handling need a candidate check. |
| RESOLVER-PM-BU-FSM | IBY_FD_PAYMENT_METHOD.BuName | table_or_view | SRC-CODE-IBY-SVC-AM-IMPL, SRC-CODE-IBY-SVC-AM-XML | FSM no-match writes empty ApplicableValueTo; exact surfaced failure and duplicate-name behavior need controlled verification. |
| RESOLVER-PM-LE-FSM | IBY_FD_PAYMENT_METHOD.LEName | table_or_view | SRC-CODE-IBY-SVC-AM-IMPL, SRC-CODE-IBY-SVC-AM-XML | FSM no-match writes empty ApplicableValueTo; exact surfaced failure and duplicate-name behavior need controlled verification. |

## Lookup Execution Rules

These blocking rules apply to required reference lookups. The optional
transactional payment-method LOV cannot veto a uniquely resolved setup parent.

| Situation | What Happens |
|---|---|
| No exact match | Block candidate and report missing reference |
| Several matches | Block candidate as ambiguous; never select arbitrarily |
| Endpoint unavailable | Report preflight unavailable; do not infer existence or submit |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| PM.LOOKUP | step | 30 | reference_lookup | ok->PM.DEFAULTS;blocked->PM.RETURN_ISSUES | PM.DEPENDENCIES | stop | When a confirmed preflight applies |


## Reference mapping and qualification boundaries

Source confirmation does not satisfy a live resolver. ApplicationShortName mapping, tenant-scoped BU resolution, LE resolution and intentional null all-BU/all-LE scopes have reviewed contracts. No-match name resolution writes blank and must be stopped by the declared preflight. Duplicate/no-match surfaced error contracts remain unqualified.

Assignment source confirms ValidationSetVO/TerritoryPVO membership validators, IBY_VALIDATION_ASSIGN_ENTITIES and nullable FieldNameCode. Value source confirms parameter association, IBY_VALIDATION_FIELDS and NUMBER/DATE/VARCHAR2 value dispatch. Current configured values and complete context-specific selection paths remain per-request evidence gates. Sources: SRC-DEBUG-IMPORT; SRC-REVIEW-ASSIGN-EO; SRC-REVIEW-VALUE-EO; SRC-REVIEW-VALUE-IMPL.

## Legal-entity identifier correction

Despite its label, the FSM CSV LEName column contains LegalEntityIdentifier. A user-supplied display name must first resolve exactly once to an identifier, which is explicitly confirmed before serialization. Never compare a CSV identifier to display Name or silently substitute one. The published 26D legalEntitiesLOV GET returns both Name and LegalEntityIdentifier. Sources: SRC-DEBUG-CHILD-VO, SRC-REVIEW-LE-VO, SRC-REVIEW-LE-PEO, SRC-REVIEW-LE-REST-26D. Environment privileges, context, duplicate handling and actual import acceptance remain governed preflight/qualification gates.

## Reviewed reference boundaries

Alias/FormatValue needs no lookup. PaymentModeCode uses ORA_IBY_PAYMENT_MODE only for nonblank create input. Its supported read-only lookup-code collection is `/fscmRestApi/resources/11.13.18.05/standardLookups/ORA_IBY_PAYMENT_MODE/child/lookupCodes`. Use it only through the active declared preflight adapter after identity/access/input checks. Retain exact code, enabled/effective dates and pagination. Access failure is not an invalid code. Sources: SRC-REVIEW-MODE-LOOKUP, SRC-REST-STANDARD-LOOKUPS-26D.

IBY_VALIDATION_FIELDS, IBY_PARAMETER_TYPES and IBY_PMT_MTHD_USAGES have source-backed identities. Selected configured set/parameter/type, territory and flexfield context still require request-specific evidence. Preserve qualified AP six-type creates; an incomplete exhaustive catalog does not negate that subset. Keep named-BU enterprise/name and LE identifier preflights. Do not substitute transaction REST or transaction DFF metadata for setup evidence.

DocumentCategoryCode has a persistent scalar mapping and no category resolver in the reviewed FSM/EO chain. Check the chosen category and sequencing applicability when relevant; do not invent mandatory ID/name conversion or claim arbitrary codes valid. Existing candidate-specific evidence and explicit validation choice remain available. Source sufficiency and live qualification are distinct.
