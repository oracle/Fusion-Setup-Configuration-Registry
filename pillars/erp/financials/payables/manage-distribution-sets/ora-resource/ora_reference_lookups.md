# Reference lookups


## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| resolve_business_unit_context | Create context or changed BU selection | BuName; EnterpriseId from explicit row, current-run default or one distinct nonblank fresh export value | GET /fscmRestApi/resources/11.13.18.05/finBusinessUnitsLOV | BusinessUnitName, BusinessUnitId, ActiveFlag, PrimaryLedgerId | Exact active name; require one identity; zero or multiple matches block. The GET does not attest EnterpriseId. A conflicting explicit enterprise value is row-specific and makes later blank values ambiguous | BU identity and PrimaryLedgerId; EnterpriseId provenance recorded separately; FSM owns BuName + EnterpriseId to OrgId resolution | Block absent/inactive/ambiguous BU or unresolved enterprise; never create a BU or choose first match |
| validate_distribution_account | New line or effective ledger/account changes | SOBName and ordered DistCcidSegments slots; exact owning BU/line identity and fresh baseline | POST /fscmService/AccountCombinationService; validateAndCreateAccounts; DynamicInsertion=No through approved core transport | Status, CcId | Map newline slots positionally to Segment1..30 and exact ledger to LedgerName; require successful bounded SOAP response, Status=Valid and positive existing CcId for the existing path | Read-only account receipt bound to identity, ledger, segments and baseline; keep segments in CSV | Invalid/fault/unavailable/unclassified missing CCID blocks; do not infer absence. Authoritative confirmed-absence evidence uses the separate approved FSM-creation gate; no direct SOAP creation |
| find_ledger_by_exact_name | Optional preflight requested for SOBName | SOBName | GET /fscmRestApi/resources/11.13.18.05/ledgersLOV | Name, LedgerId, ChartOfAccountsId, LedgerTypeCode, LedgerCategoryCode | q Name exact-match; compare returned Name and ledger identity; exclude ledger sets and enforce BU/primary-ledger/COA coherence before candidate readiness. | SOBName -> Name; returned LedgerId -> SetOfBooksId and ChartOfAccountsId -> import account context. Package keeps SOBName; derived IDs are not customer-input columns. | Successful zero-match is a target-data issue requiring correction; never classify as endpoint unavailability. Read-only preflight requires exactly one exact code/name match across paginated results; multiple matches require clarification. This conservative preflight rule does not claim the import helper itself rejects duplicates. |
| find_active_income_tax_type | Newly supplied or effectively changed nonblank Type1099; skip omitted, cleared, blank or unchanged existing values | Explicit code or description with input intent | Bundled references/income-tax-types/income-tax-types.json first; GET /fscmRestApi/resources/11.13.18.05/payablesIncomeTaxTypes for unknown values or explicit live verification | incomeTaxType, inactiveDate, description | Apply Income tax resolution policy below: exact code first, then unique exact description; preserve canonical code spelling. REST uses exact escaped code/description query and complete pagination; evaluate date only against authoritative application date | Canonical Type1099 code and provenance: seed reference, live REST or unverified explicit code; never serialize a description | Successful zero-match/inactive result requires correction; multiple matches require selection. Availability/access/contract failure allows an explicit code with warning and governed FSM validation; unknown descriptions require the user to supply a code. Never create tax types |

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| Pagination and identity | Read all pages; compare exact returned keys; never select a partial-name or first match. Use authorized session reads only. |
| Unavailable optional preflight | Distinguish request/permission failure from a successful zero-match. Disclose unavailability. A confirmed FSM mechanism still requires governed application validation; no request retry or mutation is implied. |
| Tax active predicate | Require trunc(application database date) < trunc(nvl(inactive_date, application database date+1)); obtain authoritative application date before evaluating a date boundary. |
| BU context boundary | FSM import uses the BU name plus EnterpriseId. finBusinessUnitsLOV verifies the BU/ledger only. Configured explicit/current-run/fresh-export precedence supplies EnterpriseId; preserve its provenance. Block ambiguous preflight identities without claiming shared helper duplicate semantics. |
| Account import boundary | FSM resolves the 30 ordered segment slots and may create a missing account combination during import. This is a mutation inside import, never a read-only lookup. Existing ID/COA GET does not establish a newline-input mapping. The AccountCombinationService check provides a read-only existing-account preflight. Only the source-proven FSM import may create a missing combination after its explicit effect is approved. |


## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| DS.LOOKUPS | step | 30 | reference_lookup | resolved->DS.DEPENDENCIES;not_requested->DS.DEPENDENCIES;invalid->DS.ISSUES | DS.DEFAULT | stop | Automatically check new-line and changed account or ledger references; resolve new or changed nonblank income tax input repository-first; only additional optional preflight requires a request; disclosed unverified explicit tax codes may resolve with warnings |


## Account absence and creation choice

| Situation | What Happens |
|---|---|
| Valid existing combination | Require Status=Valid, positive existing CCID, matching exact ledger/segments and read-only receipt; proceed to normal candidate preparation. |
| Confirmed missing combination | Ask whether to create the exact combination in the identified ledger. Record the decision and disclose its intended effect in the normal immutable Data Loader preview. Declining creation blocks this account selection and allows a replacement account; no balancing or alternate account is invented. |
| Invalid segments or unclear response | Stop and show the validation issue. A missing CCID, Invalid status, fault or unavailable service alone does not prove a valid-but-missing combination. Creation consent cannot override proven-invalid input. |
| Creation approved in principle | This consent is business intent. The final Data Loader approval must bind the exact candidate, ledger, ordered segments and possible account creation. Changed inputs require a new preview/approval. |
| Governed execution | Use the existing Distribution Sets FSM import through Run Book/core.data-loader; its GL_BULK_COMBINATIONS transform may create the combination. No task script calls DynamicInsertion=Yes and no standalone creation endpoint is invented. |
| Post-import verification | Fresh task export verifies the requested distribution set and line account segments. Repeat the read-only account check to verify an existing positive CCID. Uncertain creation or import state requires reconciliation before any new decision; never automatically resubmit. |

Verify the requested account and distribution-set state after the approved import.

## Seeded income tax reference

The [income tax seed repository](../references/income-tax-types/README.md) and its [machine-readable data](../references/income-tax-types/income-tax-types.json) provide 51 income tax codes with their descriptions and inactive dates. This reference list does not replace a current environment lookup. Preserve exact code spelling; do not resolve the duplicate description “Overtime Compensation” without the user's code selection. The reference records two end-dated codes. A source match or miss does not establish current deployed availability. The repository-first policy below governs income tax resolution; all imports retain normal Run Book/Data Loader approval and Fusion validation.

## Income tax resolution policy

This policy applies to newly supplied or effectively changed `AP_DISTRIBUTION_SET_LINE.Type1099`. It uses the bundled [51-entry seed reference](../references/income-tax-types/income-tax-types.json) as a versioned mapping, not current environment validation. Do not add a separate mandatory REST-access prerequisite.

| Input or lookup result | Required action |
|---|---|
| Omitted on update or equal to existing exported code | Preserve the existing value; no income-tax lookup. Do not block an unrelated edit because an existing value is absent or inactive in the reference list. |
| Blank, omitted on create, or explicitly cleared on update | Keep the optional blank or requested clear; no income-tax lookup. |
| Exact repository code with no source inactive date | Retain its exact spelling and continue with seed-reference provenance. Do not call REST by default or claim live/active verification. A user-requested live check uses the REST branch. |
| Unique exact repository description | Resolve to the corresponding exact code, show the mapping in the business preview and apply the same date handling as for code input. Match descriptions after surrounding-whitespace trimming only; do not use fuzzy, partial or first-match mapping. |
| Multiple codes for a repository description | Ask the user to choose a code before candidate preparation. In particular, “Overtime Compensation” maps to both MISC16 and NEC1D; never choose one automatically. An explicit code resolves that ambiguity. |
| Repository code has an inactive date | Show the date and source; never silently present it as active. Ask for a valid replacement, or use explicit live verification if the user disputes the snapshot. Only authoritative target evidence that it is active can supersede the snapshot warning. REST unavailability alone cannot override known inactivity. MISC13 A and MISC13 EPP are end-dated 2001-04-10 in this snapshot. |
| No repository match | Determine whether the supplied value is a code or description from explicit user intent or ask if unclear. Try the supported standard REST lookup for that exact value; a repository miss alone is not invalidity. Deduplicate identical lookups within the current request only. |
| REST returns exactly one exact active match | Use returned incomeTaxType, retain the description/code mapping and live provenance. Apply the source-backed date predicate using authoritative application database date; if that date cannot be established, report active status as unverified rather than inventing a timezone/date. |
| REST successfully completes all pages with zero exact matches | Report invalid/not found in the target and ask for correction. Do not reclassify a zero-match as service unavailability or fall back to an unverified code. |
| REST returns multiple exact matches | Show distinguishing codes/descriptions and ask for selection. Do not take the first result. |
| REST confirms inactive code | Report inactive and ask for replacement; no unavailable-service override. |
| REST is unavailable | For 401/403 after the core client's supported authentication handling, 404 endpoint unavailable, network/TLS/timeout, 5xx or response-contract mismatch, disclose the failure and continue with an explicit user-supplied code. If only an unknown description was supplied, ask for the code first. Do not automatically retry task requests, create reference data or bypass application validation. |

For unknown descriptions, query the REST description field; for explicit codes, query incomeTaxType. Use the approved core REST client, exact filter literals with correct escaping, requested fields incomeTaxType/description/inactiveDate, and complete pagination. No task-owned authentication or direct HTTP implementation is introduced.

The unavailable branch is a warning, not another approval gate. Include this clear message in the normal business preview: **“Income tax code <code> could not be prevalidated because the lookup is unavailable. Fusion will validate it during import.”** Retain the exact code and source/failure provenance in the task's normal preparation evidence. `resolved` may mean an explicit code is ready with this disclosed warning; it must not be recorded as live validation passed. Final candidate-bound Data Loader approval is still required, and Fusion rejection is an import failure to report without automatic resubmission.

BOSS is not a required fallback for this policy. The reviewed income-tax BOSS view exposes code and audit fields, without Description or Inactive Date, and its deployed availability is unqualified. Do not infer availability or permission from a successful call to another BOSS object. Do not use a code-only response to claim description resolution or active status.


## Automatic account-check scope

Check every new line account and every effective account or ledger change before preparing the import, even when the natural-language request does not ask for a check. Preserve unchanged account references during unrelated updates. Numeric CCID is a lookup result, not a required customer input.

An Invalid SOAP result alone does not establish absence. Authoritative absence evidence must identify the exact ledger and COA, use confirmed target segment metadata and ordered slots, and account for complete pagination and exact matching. Partial, failed or ambiguous reads remain unresolved. Keep any complete account-list comparison in memory and retain only the selected-account receipt and completeness result. Do not assume that COA-specific segment attribute names are universal. Confirmed absence leads to a creation-intent question; approved creation still requires the separate candidate-bound Data Loader preview and post-import account plus set verification.
