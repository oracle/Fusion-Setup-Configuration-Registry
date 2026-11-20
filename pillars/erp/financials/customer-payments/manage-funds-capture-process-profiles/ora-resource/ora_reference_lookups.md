# Funds capture profile reference resolution

Use the current authorized task context. These are functional matching requirements, not new API endpoints. Retain all pagination, identity and compatibility boundaries.

## PARENT-IDENTITY

Match the nine declared parent/child relationships by exact profile code. Translation identity also includes Language; names cannot replace keys.

Updates must prove exactly one existing primary-key match. No match can create; missing-parent rejection is not guaranteed.

Status: Partial. Resolution mode: fsm_import_validated. Public preflight policy: optional_when_fsm_import_confirmed.

For exact request/response keys and applicable fields see `references/resolver-contracts.json`.
## TRANSMISSION

Map each TransmitConfigurationName slot to its processing-type-specific identifier. Import selection is not guaranteed to filter by payment system; verify protocol/payment-system compatibility separately.

Joined configuration results can duplicate an identity. Retain actual 25071 multiple-match or 25072 no-match diagnostics only when surfaced; configured null-selection exceptions remain material.

Status: Confirmed. Resolution mode: fsm_import_resolved. Public preflight policy: optional_when_fsm_import_confirmed.

For exact request/response keys and applicable fields see `references/resolver-contracts.json`.
## PAYMENT-ACCOUNT

Resolve Suffix to the payment system, then its Key1 to BepAccountId. The mapped identifier may be changed through supported profile fields; account master keys do not themselves forbid reassignment.

No match may leave the identifier unset; multiple matches are not guaranteed to be rejected by import. Require explicit nonblank, coherent Suffix/Key1 for each selected child. Unchanged-ID/null consequences and live reassignment require qualification.

Status: Confirmed. Resolution mode: fsm_import_resolved. Public preflight policy: optional_when_fsm_import_confirmed.

For exact request/response keys and applicable fields see `references/resolver-contracts.json`.
## PAYMENT-SYSTEM

Resolve the explicit root Suffix to PaymentSystemId. Child Suffix participates in the account match; do not mutate the referenced payment-system master.

No match may leave the identifier unset; multiple matches are not guaranteed to be rejected by import. Preserve unless explicitly changed and verify target-bound existence and parent/account coherence.

Status: Confirmed. Resolution mode: fsm_import_resolved. Public preflight policy: optional_when_fsm_import_confirmed.

For exact request/response keys and applicable fields see `references/resolver-contracts.json`.
## LANGUAGE

Preserve Language and SourceLang in the owning translation rows. Language participates in translation identity.

An observed export language set is not the installed-language union. Obtain the complete current-target language evidence before adding a language; SourceLang/default translation creation require qualification.

Status: Partial. Resolution mode: fsm_import_validated. Public preflight policy: optional_when_fsm_import_confirmed.

For exact request/response keys and applicable fields see `references/resolver-contracts.json`.
## FORMAT

Thirteen fields store FormatCode directly. Resolve display names to the exact compatible format codes; retain CC authorization/settlement, DC online-debit and EFT transfer requiredness.

UI filters are not import enforcement and generic invalid-format rejection is not established. Notification format type matching may be prefix-based; verify the actual type and payment-system compatibility.

Status: Partial. Resolution mode: fsm_import_validated. Public preflight policy: optional_when_fsm_import_confirmed.

For exact request/response keys and applicable fields see `references/resolver-contracts.json`.
## PROTOCOL

Nine protocol fields store TransmitProtocolCode directly. Do not serialize a display label as a code.

Generic invalid-code rejection, enabled/date filtering and payment-system compatibility are not established for every import field. Verify the exact compatible target code.

Status: Partial. Resolution mode: fsm_import_validated. Public preflight policy: optional_when_fsm_import_confirmed.

For exact request/response keys and applicable fields see `references/resolver-contracts.json`.
## ACK-READER

Nine acknowledgement fields store reader codes. Apply the exact field mandatory/conditional rules and verify compatibility with the processing family.

Generic reader-existence rejection is not established for every field. The debit-card online reader path has unresolved validation evidence; retain that limitation and actual application diagnostics.

Status: Partial. Resolution mode: fsm_import_validated. Public preflight policy: optional_when_fsm_import_confirmed.

For exact request/response keys and applicable fields see `references/resolver-contracts.json`.
## YES-NO

Nine EFT fields enforce YES_NO membership with FND_CMN_INVALID_ATTRIB_Y_N. Other documented checkbox bindings serialize Y/N, which alone does not establish server rejection.

Keep those nine EFT validators distinct from CC/DC checkbox-only fields and ExternalSettlementFlag. Do not infer Boolean behavior, enabled/date filters, or other validators from a Flag suffix.

Status: Partial. Resolution mode: fsm_import_validated. Public preflight policy: optional_when_fsm_import_confirmed.

For exact request/response keys and applicable fields see `references/resolver-contracts.json`.
## CURRENCY

LimitByAmtCurr stores CurrencyCode. Resolve a displayed name to one unique exact code; a prefix name result is not an exact identity.

Current enabled domain and task-import invalid-code rejection require target verification. Currency sources are not interchangeable merely because their names are similar.

Status: Partial. Resolution mode: fsm_import_validated. Public preflight policy: optional_when_fsm_import_confirmed.

For exact request/response keys and applicable fields see `references/resolver-contracts.json`.
## RATE-TYPE

LimitByExchRateType stores ConversionType; the displayed UserConversionType is a label. Map it only through unique verified evidence.

The complete public lookup operation and generic invalid-code rejection remain unresolved. Do not invent a REST endpoint or treat UI name-finder behavior as import matching.

Status: Partial. Resolution mode: fsm_import_validated. Public preflight policy: optional_when_fsm_import_confirmed.

For exact request/response keys and applicable fields see `references/resolver-contracts.json`.
## DELIVERY

Resolve exact IBY_DELIVERY_METHODS LookupCode through the documented GET. Map a display label only when unique and never serialize Meaning.

Endpoint availability must be verified in the selected target. A successful preflight does not establish task-import membership enforcement or import success.

Status: Confirmed. Resolution mode: public_preflight_only. Public preflight policy: required.

For exact request/response keys and applicable fields see `references/resolver-contracts.json`.
## COMPLETE-POINT

SettlementCompletePoint is a persisted string with maximum declared length 50. No nonblank business enumeration is established.

Blank observations do not establish an allowed nonblank domain or make the field unsupported. Preserve baseline blanks; new nonblank values require the exact business contract.

Status: Partial. Resolution mode: fsm_import_validated. Public preflight policy: optional_when_fsm_import_confirmed.

For exact request/response keys and applicable fields see `references/resolver-contracts.json`.
## NOTIFY-CONDITION

Resolve exact IBY_PN_CONDITIONS LookupCode through the documented GET. Map a display label only when unique and never serialize Meaning.

Endpoint availability must be verified in the selected target. A successful preflight does not establish task-import membership enforcement or import success.

Status: Confirmed. Resolution mode: public_preflight_only. Public preflight policy: required.

For exact request/response keys and applicable fields see `references/resolver-contracts.json`.
## GROUPING

Use exact IBY_PMTGROUP_OPTIONS LookupCode. Resolve labels uniquely; retain FND_CMN_INVALID_ATTRB_API_SERV membership validation.

Do not add enabled/date filtering absent from the declared field contract. Verify the current target values; do not claim a successful live import from a static rule.

Status: Confirmed. Resolution mode: public_preflight_and_fsm_import. Public preflight policy: optional_when_fsm_import_confirmed.

For exact request/response keys and applicable fields see `references/resolver-contracts.json`.
## PAYMENT-CODE

ServiceLevel uses SERVICE_LEVEL and Localinstr uses LOCAL_INSTRUMENT. Serialize exact PaymentCode, never PaymentCodeAlias or an arbitrary same-name row; retain membership validation.

Verify exact type and code in the selected target; do not add unestablished enabled/date filters. Preserve FND_CMN_INVALID_ATTRB_API_SERV if actually returned.

Status: Confirmed. Resolution mode: public_preflight_and_fsm_import. Public preflight policy: optional_when_fsm_import_confirmed.

For exact request/response keys and applicable fields see `references/resolver-contracts.json`.
## PURPOSE

Use exact IBY_PURPOSE_CODE LookupCode. Resolve labels uniquely; retain FND_CMN_INVALID_ATTRB_API_SERV membership validation.

Do not add enabled/date filtering absent from the declared field contract. Verify the current target values; do not claim a successful live import from a static rule.

Status: Confirmed. Resolution mode: public_preflight_and_fsm_import. Public preflight policy: optional_when_fsm_import_confirmed.

For exact request/response keys and applicable fields see `references/resolver-contracts.json`.
