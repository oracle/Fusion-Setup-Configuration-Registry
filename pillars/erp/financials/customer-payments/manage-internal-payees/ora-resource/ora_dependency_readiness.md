# Dependency readiness

Dependency checks preserve business scope; prerequisite creation belongs to the relevant owning task.

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Payee identity | Establish exact root and parent/child scope |
| 2 | Referenced setup | Resolve required BU/account-type/payment-system/account/profile context through declared routes |
| 3 | Conditional reference | Establish criterion-specific raw identity and eligibility when changing condition Value |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| IP.DEP.ROOT | Parent payee | Yes | Child operation with exact parent already evidenced | Satisfied | Fresh exact-task export and import matching source |  | Child identity belongs to its payee | Select exact parent; do not attach by row position | Exact parent scope |
| IP.DEP.IMPORT | Import-resolved setup names | Conditional | A required BU/account-type/payment-system/account/profile key is missing | Blocked | Exact required key tuple from reviewed import source | | Import cannot invent prerequisite setup | Request the missing named input; approved FSM import performs its own resolution and validation | No value until resolved by the owning import |
| IP.DEP.PAYMENT-ACCOUNT | Payment-system/account membership | Conditional | New or changed Suffix/Key1 | Verify | Fresh complete Manage Payment Systems FSM export, Financials / Payments | resolve_payment_account_membership | The owning task exports exact root Suffix and ancestor-scoped account Key1 through the normal shared exporter. This establishes membership or absence without using an import as a probe; it does not establish Ownerid. | Require one exact parent and one exact account; zero or ambiguous matches stop the affected selection. Obtain owning-payee evidence separately; do not substitute or create a missing account. | Exact Suffix and Key1, existing Ownertype as evidence only |
| IP.DEP.COUNTRY | Country condition value | Conditional | New or changed Value: COUNTRY_PR or COUNTRY_PY excluding IN/NOT_IN; or BUCOUNTRY or PAYERCOUN | Verify | Exact criterion reference | resolve_condition_country | Source/public contract complete; current-pod availability and authorization require read-only qualification. | Resolve affected selection or preserve unchanged same-environment baseline | Exact code or identifier; no display-name import resolution |
| IP.DEP.ZONE | Country-set condition value | Conditional | New or changed Value: COUNTRY_PR or COUNTRY_PY with IN or NOT_IN | Verify | Exact criterion reference | resolve_condition_zone | Source/public contract complete; current-pod availability and authorization require read-only qualification. | Resolve affected selection or preserve unchanged same-environment baseline | Exact code or identifier; no display-name import resolution |
| IP.DEP.YESNO | Boolean condition value | Conditional | New or changed Value: FACTOR_FLAG or BR_SIGNED_FLAG or BR_DRAWEE_ISSUED_FLAG | Verify | Exact criterion reference | resolve_condition_yesno | Source/public contract complete; current-pod availability and authorization require read-only qualification. | Resolve affected selection or preserve unchanged same-environment baseline | Exact code or identifier; no display-name import resolution |
| IP.DEP.BU | Business-unit condition identity | Conditional | New or changed Value: ORG_ID | Verify | Exact criterion reference | resolve_condition_bu | Source/public contract complete; current-pod availability and authorization require read-only qualification. Identity preflight does not certify equivalence to the UI business-unit security scope. | Resolve affected selection or preserve unchanged same-environment baseline | Exact code or identifier; no display-name import resolution |
| IP.DEP.CARD | Card-brand condition value | Conditional | New or changed Value: CC_TYPE | Verify | Completed target card-brand FSM export | resolve_condition_card | Target export and candidate selection checks qualified; read-only resolution does not qualify every Internal Payees import variant. Runtime must reacquire or explicitly validate current target-bound evidence. | Resolve affected selection or preserve unchanged same-environment baseline | Exact code or identifier; no display-name import resolution |
| IP.DEP.APPLICATION | Source-product condition value | Conditional | New or changed Value: SOURCEPROD | Verify | Supported current-target GET | resolve_condition_application | Read-only positive target qualification, not Internal Payees import certification. Documentation and current target evidence are required; do not hard-code observed IDs. | Resolve affected selection or preserve unchanged same-environment baseline | Exact code or identifier; no display-name import resolution |
| IP.DEP.PAYER | Payer condition value | Conditional | New or changed Value: PAYER | Verify | Supported current-target GET | resolve_condition_payer | Qualified automatic resolution covers PERSON and ORGANIZATION. Other party types require a separately qualified identity path only for the affected selection; no blanket task prohibition. Preserve unchanged same-environment baseline Values without re-resolution. | Resolve affected selection or preserve unchanged same-environment baseline | Exact code or identifier; no display-name import resolution |
| IP.DEP.RECEIPT-ELIGIBILITY | Receipt-method eligibility | Conditional | New or changed Value: AR_RECEIPT_METHOD_ID new or changed | Verify | Completed target dependency export and supported reads | resolve_condition_receipt_eligibility | Composed contract and one target example qualified; read-only resolution does not qualify every Internal Payees import variant. No extra account-use AR flag or unattached criteria are imposed. | Resolve affected selection or preserve unchanged same-environment baseline | Exact code or identifier; no display-name import resolution |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Satisfied | Required identity and context are evidenced | Only declared read-only lookup in the active workflow; no prerequisite creation by this task |
| Missing | A required business value is absent | Request missing input |
| Evidence unresolved | A resolver or eligibility contract is incomplete | Retain exact unresolved scope; no fabricated lookup or broad create/update prohibition |


## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| IP.DEPENDENCIES | step | 30 | resolve_dependency | pass->IP.DEFAULTS;fail->IP.ERROR | IP.REFERENCES | stop | Selected Manage Internal Payees request; evaluate only applicable source rows |


## Routing account required independently of process profile

A new routing rule requires a resolved payment-system account for both PROCESSOR and GATEWAY systems. Supply the complete portable Suffix + Key1 reference so the approved import can resolve Bepid and BepAccountId. A gateway waives the process-profile requirement only; it does not waive the account requirement. For an existing rule, preserve its complete baseline account reference unless an explicit reviewed change is requested. When the resolved account has null Ownerid, the import assigns Ownerid to the payee and Ownertype=PAYEE; include this external-entity side effect in preview and post-import verification.
