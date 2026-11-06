# FACPQ Sales Integration Design Enforcement

Enforce one embedded FACPQ design. Fail closed when a request mixes Fusion
hosts, standalone BM CPQ values, SAML URLs, or identifiers from another process.

## Submission and Status Boundary

After an accepted initiation, return Core's accepted-initiation report and stop.
Do not retrieve status, ProcessLog, errors, or post-import verification as an
automatic follow-up. Resume those steps only on a later explicit user request
for load status, progress, results, or errors. A ProcessId followed by a local
artifact write failure must be retained for that later request; never resubmit
or poll automatically. This boundary also applies to a separately approved FSM
fallback. Report initiation and confirmed successful completion distinctly.

## Enforcement Order

| Sequence | Gate | Pass Condition | On Failure |
|---|---|---|---|
| 1 | Required offering opt-ins | Fresh same-target GETs to the exact 11.13.18.05 Features item paths for Sales and Configure Price Quote return HTTP 200, exact FeatureCode, FeatureType OFFERING, and EnabledFlag Y | Stop before integration creation and return Configure Offerings remediation or the applicable REST/authentication correction |
| 2 | Platform | The request explicitly targets FACPQ and `bm_cpq_supported` is false | Return missing/invalid design |
| 3 | Host and endpoint | One non-placeholder HTTPS Fusion origin maps unchanged to EndPointUrl as exactly `<FA_HOST>` with no path | Stop before package generation |
| 4 | Authentication chain | Target-matching OAuth properties contain a non-empty `cpq_scope`; its complete value is used directly for one forced fresh login; the returned Fusion OAuth token authenticates documents and actionDefs directly, proving effective client-scope access | Stop before metadata discovery |
| 5 | Metadata provenance | Document, Copy action, and Version action values come from the same `/cpq/rest` process and the same fresh OAuth bearer | Recollect the direct OAuth metadata flow |
| 6 | Action family | All five values match the supplied FACPQ OpenID Connect expressions | Regenerate the contract |
| 7 | Secret boundary | The Fusion OAuth response may be cached only in the authentication service's managed private cache outside the repository; no credential, cookie, or Authorization header is persisted | Remove and rotate any improperly stored secret |
| 8 | Mutation approval | The immutable Fusion package has explicit approval | Stop before import |
| 9 | Post-import result separation | Fusion ProcessLog status, local artifact persistence, and FSM export portability substitution are reported independently | Do not turn a successful Fusion process into a failure because of a later local write error or exported endpoint sentinel |

## Design Rules

| Rule | Required Design | Block When |
|---|---|---|
| Offering prerequisite | Require two fresh same-target results from core.fusion-api.rest-api-client using GET /fscmRestApi/resources/11.13.18.05/features/ORA_MIDSIZE_SALES and GET /fscmRestApi/resources/11.13.18.05/features/ORA_CONFIGURE_PRICE_QUOTE; require HTTP 200, exact FeatureCode, FeatureType OFFERING, and EnabledFlag Y for both | Either result is missing, disabled, mismatched, cross-environment, UI-only, BOSS-derived, repository-derived, unauthorized, or not from the exact versioned item path |
| Platform boundary | FACPQ only | A standalone BM CPQ site, direct login, or BM browser session is proposed |
| Authentication route | Require OAuth properties restBaseUrl to equal `<FA_HOST>`, require a non-empty `cpq_scope`, pass its complete value directly to the core OAuth helper's runtime `scope` field in memory for one forced fresh login, and use the returned bearer directly for documents and actionDefs as effective client-scope verification | `cpq_scope` is missing or blank, the fresh OAuth or metadata read is rejected, metadata authentication scope is derived from the standard `scope` property, properties and request hosts differ, another bearer or route is introduced, browser cookies are used, or the OAuth cache is under project/ |
| Metadata base | `<FA_HOST>/cpq/rest/{version}` | The host is a CPQ tenant or the path omits `/cpq` |
| Sales endpoint before import and in live FSM | EndPointUrl exactly equals `<FA_HOST>` with no path; `/cpq` is added only by metadata and fixed action paths | A proposed package, immutable import artifact, or live FSM value is a placeholder such as `https://ThisURLMustBeChanged.com`, uses another host, contains `/cpq`, `/rest`, another path, a query, or a fragment |
| Sales endpoint in post-import task export | Treat the exact `https://ThisURLMustBeChanged.com` value as Oracle FSM export portability substitution when the successful import's reference code and non-endpoint fields match | Do not treat the exported sentinel as the live endpoint, fail the Fusion process, or build a corrective package solely because of it |
| Create/Edit family | `/cpq/sso/openid_connect_request.jsp` with Redwood `cx-cpq/.../quotes-detail` RelayState | SAML, legacy buy-side Create/Edit, or missing Redwood path is used |
| Version/Duplicate/Proposal family | `/sso/openid_connect_request.jsp` with RelayState beginning `/cpq/` | The RelayState omits `/cpq` |
| Duplicate version field | `version_id` equals Version Action ID | Commerce Process Version ID is substituted |
| Fixed Create values | `currency=USD`, `mode=live`, `id=100106915720776`, `inAppId=groupNode_RedwoodSales` | Any fixed value changes without a new approved contract |
| Input minimization | Require Document ID, Copy Action ID, and Version Action ID only | Edit Action ID or Commerce Process Version ID is made mandatory |

## Design Lookup Requirements

| Needed Value | Source | Resolver | Required Before |
|---|---|---|---|
| Sales and Configure Price Quote offering states | Fresh sanitized response evidence from both exact versioned Fusion Features item GETs in the target environment | verify_required_offering_opt_ins | Integration creation or package generation |
| Fusion host and FACPQ endpoint | Target environment context | resolve_cpq_integration_parameters | Metadata preview |
| IDCS OAuth-client CPQ scope | Target IDCS client configuration | resolve_cpq_integration_parameters | Fresh OAuth login |
| Main Document and Document ID | FACPQ documents GET | resolve_cpq_integration_parameters | ActionDefs GET and URL construction |
| Copy and Version Action IDs | FACPQ actionDefs GET | resolve_cpq_integration_parameters | Duplicate and Version URL construction |
| Five action expressions | Fixed FACPQ contract | resolve_cpq_action_url_contract | Fusion package preview |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CPQ.INT.DESIGN | decision | 5 | design_enforcement | pass->CPQ.INT.EXECUTION_GATE;blocked->CPQ.INT.RETURN_MISSING | CPQ.INT.DEPENDENCIES | stop | Before the Fusion import handoff |
