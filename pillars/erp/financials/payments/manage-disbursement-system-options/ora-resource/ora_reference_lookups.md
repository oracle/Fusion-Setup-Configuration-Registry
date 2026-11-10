# Reference lookups

For create, bind current exact active BU evidence and current-task selection
eligibility to the same target/baseline. Use the resolved BU ID for verification,
not as a business override. Candidate blank audit/BU usage columns remain
service-owned. Fresh created-row BusinessUnitId1 must match the resolved BU and
ModuleKey the source-backed PAYABLES_PAYMENT_BF export join. A positive numeric
derived ModuleId is disclosed; no fixed numeric mapping is invented.

Scope: IBY_MANAGE_DISBURSEMENT_SYSTEM_OPTIONS.

Source: SRC-REST-FIN-BU-26C, SRC-GOLD-AM-SNIPPETS, SRC-GOLD-BU-PVO, SRC-GOLD-BU-PEO, SRC-GOLD-EO-SNIPPETS. Public BU existence is supplementary; import resolves Name plus current EnterpriseId into OrgId. Never copy a returned public ID into protected BusinessUnitId1. Lookup/format value populations and helper no/multiple-match internals remain evidence_unresolved. The local evidence checks below do not execute an unqualified private resolver or guess a value.

## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| match_baseline_identity | Select existing enterprise/BU update target | Captured fresh exact-task rows and explicit user scope | Enterprise requires one blank BuName row; BU requires one exact named row. No case folding or fallback | Selected row; preserve BuName exactly | Ask bounded scope/target question; no candidate |
| verify_option_value_evidence | Requested code/format needs verification | Source-bound current target lookup or format evidence with field, canonical code, label and applicability | Require one exact canonical value from applicable evidence; never close a code domain from sample exports. Report missing operation/normalization evidence and require a separate exact-candidate application-validation decision when eligible | Canonical code already confirmed; no invented mapping | Clarify or collect evidence; unresolved is not invalid. No automatic code substitution |

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| find_business_unit_by_exact_name | Explicit named BU requires independent existence verification; otherwise return not_applicable | Exact user BuName and approved target environment | GET /fscmRestApi/resources/11.13.18.05/finBusinessUnitsLOV; q filter BusinessUnitName; paginate limit and offset until hasMore=false | BusinessUnitName, BusinessUnitId, ActiveFlag | Require one exact visible name after complete pagination; query escaping/encoding belongs to the routed REST client. Active state is shown, not silently repaired | Verified BU name and context; do not rewrite CSV service-owned fields | Clarify zero/many exact matches. Never reinterpret missing BU as enterprise |

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| Missing configured code evidence | Do not fabricate an endpoint or derive a code from a label. The task EO validates four lookup domains and the PPR format; use applicable source/target evidence or an explicit eligible application-validation decision |
| Public BU match exists | Does not prove new task-row creation eligibility, payment function, import helper fallback behavior or a successful import |
| Read-only access fails | Report access failure; never use another environment or broader query scope silently |

## Payment-usage visibility evidence

The public finBusinessUnitsLOV response proves only its declared exact-name/active reference facts. It does not expose or prove PAYABLES_PAYMENT_BF usage. Task create-picker selection and this export's usage filter are distinct source predicates.

Review the exact BU in the supported Assign Business Unit Business Function workflow when payment-function visibility needs confirmation. This guidance declares no new REST resolver, private helper or SQL dependency. Missing access/evidence is unresolved, not proof of absence or an invalid BU.

BusinessUnitId1, ModuleId and ModuleKey are derived usage-join metadata in the export. Leaving these service-owned create cells blank does not create a business-function usage record. Preserve protected-field rules and never copy a guessed module ID/key into the candidate to bypass the join. Source: SRC-GOLD-VO-SNIPPETS, lines40–49.

## Observed update evidence and its limits

Observed enterprise automatic-report updates preserved PPR_STATUS_REPORT. Neither that observation nor the three subject contexts establishes a current lookup population, label-to-code mapping or permission to substitute another code. Keep lookup gaps explicit; verify the exact target value or obtain an eligible bounded application-validation decision. No new endpoint or resolver is declared. Sources: SRC-E2E-OBSERVED-AUTOPPR-164493-164510, SRC-E2E-OBSERVED-SUBJECT-164559-164580.

## Observed create and reviewed lookup source boundaries

Reviewed DEV StandardLookupTypeSD.xml records IBY_DOCUMENT_REJECTION_LEVELS DOCUMENT/NONE/PAYEE/REQUEST, IBY_PAYMENT_REJECTION_LEVELS NONE/PAYMENT/REQUEST, IBY_PSO_DEF_PAY_METHOD N/Y and IBY_BANK_CHARGE_BEARER BEN/OUR/PAYEE_PAYS_EXPRESS/SHA/SLEV, with source descriptions in references/task-contract.json. The first three have CustomizationLevel S; BankChargeBearer has E and its seed list is not exhaustive. Source enabled/date facts are not deployed checks. Document/payment EO accessors use IsActive/IsEnabled; BankChargeBearer IsActive is commented and must not be invented. No new endpoint or runtime domain/normalization check is introduced. PPR FormatVA filters IBY_FD_PPR_STATUS; actual current format codes remain unresolved. EOImpl565–575 confirms Y requires non-null/nonblank trimmed format. DEV-only AgentTeam fields are excluded; OrgType mutability and helper no/multiple-match internals remain unresolved. Sources: SRC-E2E-RETAINED-CREATE-55ROW-164877, SRC-DEV-LOOKUP-SEEDS-20260924, SRC-DEV-INTERNAL-PAYER-EO-LOOKUPS, SRC-DEV-INTERNAL-PAYER-EOIMPL-PPR.

## Task Nodes

DSO_BU_REFERENCE uses only find_business_unit_by_exact_name when its Runs When condition applies; otherwise return not_applicable. DSO_VALUE_EVIDENCE evaluates captured local evidence through match_baseline_identity and verify_option_value_evidence. It does not invoke an unqualified import helper or private lookup endpoint.

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| DSO_BU_REFERENCE | decision | 30 | reference_lookup | matched->DSO_VALUE_EVIDENCE;not_applicable->DSO_VALUE_EVIDENCE;missing->DSO_RETURN_MISSING;failed->DSO_RETURN_FAILED | DSO_DEPENDENCIES | stop | true |
| DSO_VALUE_EVIDENCE | decision | 35 | evaluate_result | satisfied->DSO_PRESERVATION;missing->DSO_RETURN_MISSING;invalid->DSO_RETURN_FAILED | DSO_BU_REFERENCE | stop | true |
