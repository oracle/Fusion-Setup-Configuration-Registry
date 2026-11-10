# Manage Payment Codes — Reference Lookups

The user explicitly declared the reviewed Manage Payment Codes ora-resource tables as local authority for Type, length, key and seeded checks. The local Type resolver below evaluates only that reviewed table. Current-record facts come separately from a validated fresh exact-task current-data export acquired through the owning workflow. Country/language preflight uses the exact published Common Features 26D GET schemas below and fresh environment responses through core.fusion-api.rest-api-client. Reference preflight does not establish translation operation ownership, CSV language defaults or successful import. Remaining TBD contracts are execution blockers. Product sources were reviewed on FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64.

## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| resolve_payment_code_type | Root or translation PaymentCodeType is supplied | User-declared local authority: this file's Seeded Type Domain table; Canonical Code and Business Label, reviewed from SRC-CS-UIVO, SRC-CS-EO, SRC-CS-TYPESEED | Match an exact canonical code or one unique reviewed business label after trimming and case-insensitive label comparison; reject off-domain values and UI selection indices | Canonical PaymentCodeType for the owning entity | Zero matches: stop before candidate generation and request a reviewed code or label. Multiple matches: stop and request the exact canonical code; never select by row order |
| find_payment_code_by_key | Before each create/update/no-op preview and seeded restriction check | Full IBY_PAYMENT_CODE.csv from a fresh unfiltered shared.setup-export.task-level-export current-data export for IBY_MANAGE_PAYMENT_CODES. Require completed metadata, exact environment/task/submitted user, both declared CSV members, template-matched headers, unique root pairs and unique child triples with matching parent pairs; SRC-FSM-CURRENT-20261006, SRC-CS-AMIMPL, SRC-CS-VO | Scan every root record by exact canonical PaymentCodeType + PaymentCode; do not apply active-date or session-language filters. Bind the snapshot hash/time/user/environment to the preview and refresh for a later preview; reject incomplete or stale evidence | Existence and the full matching root baseline, including SeededFlag and dates/transients. Preserve nested translation records as read-only reconciliation evidence; exported languages do not prove allowed-language population or child write ownership | Zero matches in the validated complete snapshot: absent at snapshot time, eligible for create only after all other gates pass. One match: compare supported requested business fields for update/no-op. Multiple matches, missing/invalid manifest, export failure or wrong scope: stop; never treat an incomplete read as absence |

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| resolve_payment_code_country | TerritoryCode supplied or Country label needs resolution | Fresh current-environment territoriesLOV collection; SRC-PUBLIC-COMMON-OPENAPI-26D. Task UI TerritoryPVO/TerritoryVVO and TerritoryPEO association prove the owning Country code/name correspondence; SRC-CS-UIVO, SRC-CS-TERRVO, SRC-CS-TERRASSOC | GET /fscmRestApi/resources/11.13.18.05/territoriesLOV through core.fusion-api.rest-api-client. Request fields=TerritoryCode,TerritoryShortName,EnabledFlag,ObsoleteFlag, limit=500, offset=0, orderBy=TerritoryCode:asc; continue offset pages while hasMore is true. Follow returned self links if an item read is needed; never construct the opaque item key | items[].TerritoryCode, TerritoryShortName, EnabledFlag, ObsoleteFlag; count, hasMore, limit, offset, links. The complete official 26D OpenAPI supplies the business schema omitted from the rendered response page | Scan the fully acquired collection for one exact canonical code, or one exact trimmed business label in the response/session language. Require unique codes and a unique label match; never choose row order. Bind response time/environment/user to the preview; repeat for a later preview. Do not add an enabled/obsolete business restriction absent task evidence | Matching TerritoryCode maps to IBY_PAYMENT_CODE.TerritoryCode. Keep label and flags as read-only context; no master-data create or implicit normalization of unknown codes | Zero matches in a complete successful read: request a valid Country code/label and stop. Multiple matches: request the exact canonical code. HTTP/auth failure, bad schema, missing page or inconsistent pagination: disclose the preflight failure and stop; never report absence. Exact task FSM missing-reference error is not qualified by this public-preflight-only contract |
| resolve_payment_code_language | Root create needs complete installed-language inventory, or preserved child language context needs verification; never direct child writes | Fresh current-environment languagesLOV catalog and separate installed/active finder snapshots; SRC-PUBLIC-COMMON-OPENAPI-26D, SRC-CS-APPLCORE-LANGUAGES. Framework root-create languages use every installed I/B member without filtering by activation; preserve existing child language cells | GET /fscmRestApi/resources/11.13.18.05/languagesLOV through core.fusion-api.rest-api-client, with fields=LanguageCode,LanguageTag,Description,InstalledFlag,ActivationStatus, limit=500, offset=0, orderBy=LanguageCode:asc. Acquire the catalog and separate finder=InstalledLanguageFinder and finder=ActiveLanguageFinder collections without a languageCode bind; paginate each to hasMore=false | items[].LanguageCode, LanguageTag, Description, InstalledFlag, ActivationStatus; count, hasMore, limit, offset, links. Preserve exact finder names; do not substitute prefAllLanguagesLOV | Require complete successful snapshots and unique codes; keep installed and active membership separate. Root create uses the complete installed I/B set, including installed inactive languages. Do not infer this set from existing children, a bound finder or partial response. This lookup does not determine execution-session NLS language or translated-update effects | Installed codes identify expected framework-created child keys. Return description and separate installed/active facts. SourceLang is session-derived framework output, not a default supplied by this lookup or the base language. Existing child inputs are read-only; derive and verify exact session-dependent effects before translated-root updates or stop | Zero or duplicate installed keys, missing/partial snapshot or page, bad schema, HTTP/auth failure: disclose the blocker and stop. Never invent a default, assume no generated children, enable direct operations or infer import success |

## Seeded Type Domain

| Canonical Code | Business Label | Authority |
|---|---|---|
| BANK_INSTRUCTION | Bank instruction | SRC-CS-TYPESEED, SRC-CS-UIVO |
| DELIVERY_CHANNEL | Delivery channel | SRC-CS-TYPESEED, SRC-CS-UIVO |
| LOCAL_INSTRUMENT | Local instrument | SRC-CS-TYPESEED, SRC-CS-UIVO |
| PAYMENT_REASON | Payment reason | SRC-CS-TYPESEED, SRC-CS-UIVO |
| SERVICE_LEVEL | Service Level | SRC-CS-TYPESEED, SRC-CS-UIVO |

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| Type normalization | Use the user-declared local resolver for static checks of the reviewed labels/codes; UI values 0–4 are ADF selection indices. This system-level seeded enumeration has CustomizationLevel S, ViewApplicationId 0 and SetId 0; public preflight is not applicable. The source-proven FSM ListValidationBean remains the application validation boundary; the declaration is not live import proof. |
| Country or language resolution | Use only the defined published public-preflight contracts and fresh complete responses through the declared native client. They do not claim FSM import resolution or qualify translation operations/defaults; no generic endpoint substitution or expanded local authority. |
| Public Payment Codes LOV | Exact resource actions disable create/update/delete. SRC-CS-PC-REST-VO proves the current-date filter; future and ended records are outside the declared query. SRC-EDM-PC-VL-26D proves session-language scope. Eight root field mappings are proved; missing SeededFlag/translation/audit and filtered coverage prevent operation selection. Never synthesize the opaque hash key. |
| Public Territories LOV | SRC-PUBLIC-TERR-GET-26D and SRC-PUBLIC-TERR-ITEM-26D confirm collection/item paths. SRC-PUBLIC-COMMON-OPENAPI-26D supplies TerritoryCode, TerritoryShortName and flag fields omitted from the rendered page. The item parameter may be a hash; follow returned self links. The published contract is complete, while actual reference values and read privileges still require a successful current-environment read. |

## Public Operation Evidence

| Source | Exact Reviewed Oracle Operation | Proven Boundary |
|---|---|---|
| SRC-PUBLIC-PC-GET-26D | [Get all payment codes, 26D](https://docs.oracle.com/en/cloud/saas/financials/26d/farfa/op-paymentcodeslov-get.html) | GET path, queryable fields, paging and eight business response fields; no full FSM baseline |
| SRC-PUBLIC-PC-ITEM-26D | [Get a payment code, 26D](https://docs.oracle.com/en/cloud/saas/financials/26d/farfa/op-paymentcodeslov-paymentcodeslovuniqid-get.html) | Composite-key collection filter and returned self-link navigation |
| SRC-PUBLIC-TERR-GET-26D | [Get all territories, 26D](https://docs.oracle.com/en/cloud/saas/applications-common/26d/farca/op-servername-fscmrestapi-resources-11.13.18.05-territorieslov-get.html) | Collection path and standard paging/query controls |
| SRC-PUBLIC-TERR-ITEM-26D | [Get a territory, 26D](https://docs.oracle.com/en/cloud/saas/applications-common/26d/farca/op-servername-fscmrestapi-resources-11.13.18.05-territorieslov-territorycode-get.html) | Required TerritoryCode path parameter; corresponding business fields are supplied by the complete 26D OpenAPI source |
| SRC-PUBLIC-COMMON-OPENAPI-26D | [Common Features 26D OpenAPI, version 2026.09.28](https://docs.oracle.com/en/cloud/saas/applications-common/26d/farca/openapi.json) | Complete territoriesLOV-item and languagesLOV-item field schemas, queryable fields, paging and exact language finder contracts; published read-only preflight authority, not deployed-value or translation-write proof |

Documentation discovery does not select a live execution route. Runtime calls still require a complete resolver contract selected by the owning project workflow. A failed or incomplete read never proves absence.

The public paymentCodesLOV collection remains diagnostic evidence only. Its eight business fields, active-date predicate and session-language join cannot replace the full-task export used by find_payment_code_by_key. Do not call the public LOV to decide absence, SeededFlag or translation ownership.

## Public Field Mapping

SRC-CS-PC-REST-RESOURCE binds the public resource to the exact REST VO. SRC-CS-PC-REST-VO maps its fields to SRC-CS-PC-PEO; SRC-CS-PC-PEOJAVA getters return internal attribute values. The public entity and the FSM service entity share the named VL database columns. This proves read-only field correspondence, not imported date/null/default handling or complete baseline coverage.

| Public Field | Root FSM Model Field | Database Column |
|---|---|---|
| PaymentCode | PaymentCode | PAYMENT_CODE |
| PaymentCodeType | PaymentCodeType | PAYMENT_CODE_TYPE |
| PaymentCodeName | Meaning | MEANING |
| PaymentCodeDescription | Description | DESCRIPTION |
| PaymentCodeAlias | FormatValue | FORMAT_VALUE |
| Country | TerritoryCode | TERRITORY_CODE |
| FromDate | StartDate | START_DATE |
| EndDate | EndDate | END_DATE |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MPC_RESOLVE_REFERENCES | step | 30 | reference_lookup | resolved->MPC_DEFAULTS;missing->MPC_HANDLE_ISSUES;ambiguous->MPC_HANDLE_ISSUES;unavailable->MPC_HANDLE_ISSUES | MPC_DEPENDENCIES | stop | Applicable resolver must have a complete authorized contract |
