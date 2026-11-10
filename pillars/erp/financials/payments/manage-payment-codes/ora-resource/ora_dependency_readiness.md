# Manage Payment Codes — Dependency Readiness

Dependencies are source-bounded; reference seed foreign BO IDs are null and do not prove an alternate master-data resolver. Do not create prerequisite master data as a shortcut. SRC-CS-REFSEED, SRC-CS-TASKSEED, SRC-CS-BOSEED.

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Selected root identity and baseline | Confirm exact task and complete existence/baseline coverage before selecting create/update/no-op |
| 2 | Applicable references | Resolve Type and supplied Country. Root create requires complete installed I/B inventory; activation is separate. Translated-root updates require exact session-dependent effect qualification before preview or stop |
| 3 | Translation parent | Match existing child inputs and expected framework-generated child identities to both root keys. Direct child operations remain excluded; entity-bound NodeSequence remains 1 for each observed entity |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| payment_code_baseline | Exact root identity/existence | Yes | Before preview | Verify | Fresh unfiltered exact-task current-data CSV export, validated completed task/environment/submitted-user manifest; SRC-FSM-CURRENT-20261006, SRC-CS-AMIMPL, SRC-CS-VO | find_payment_code_by_key | Avoid duplicate or unintended update | Use the owning export workflow and validate both member/header shapes. Refresh before each operation preview; reject stale, partial, template-only or wrong-scope evidence | Exact root pair, all root baseline fields and SeededFlag; retain child rows by their triple key for reconciliation evidence without granting translation write ownership |
| payment_code_type | Type domain | Yes | Root/translation type present | Verify | User-declared reviewed local Type table; resolver definition owns source and match mechanics; SRC-CS-TYPESEED, SRC-CS-UIVO, SRC-CS-EO | resolve_payment_code_type | Stored value is canonical code | Supply exact code or supported business label | Owning entity PaymentCodeType |
| payment_code_country | Country reference | Conditional | TerritoryCode supplied | Verify | Exact published GET contract and fresh environment response; SRC-PUBLIC-COMMON-OPENAPI-26D, SRC-CS-TERRVO, SRC-CS-TERRASSOC | resolve_payment_code_country | Optional field still needs a valid reference when supplied | Use the owning resolver and successful current-environment response; do not infer a stored code from an unchecked label | Verified canonical TerritoryCode and response provenance; read failure stops preview |
| translation_parent | Owning root and child relationship | Yes | Translation rows present | Verify | SRC-CS-TLLINK, SRC-CS-TLASSOC, SRC-CS-TLEO, SRC-CS-AMIMPL, SRC-CS-FSM-MIGRATOR, SRC-CS-FSCORE-CSVXML; the task reads the nested XML tree and the converter requires the declared parent row | | 1-to-many owned relation on both keys; missing parent produces ASK_CSV_MISSING_PARENT_ROW | Match both parent-link keys and retain the child triple key. This verifies relationship integrity only; direct translation operation ownership remains unresolved | Parent/root/child PaymentCode and PaymentCodeType |
| translation_language | Framework language/effect context | Yes | Root create, translated-root update or preserved child context verification, including when no new child input rows are submitted | Verify | Published languagesLOV finder contracts and qualified framework source; fresh environment inventory for create; SRC-PUBLIC-COMMON-OPENAPI-26D, SRC-CS-TLEO, SRC-CS-APPLCORE-TL-CREATE, SRC-CS-APPLCORE-TL-UPDATE, SRC-CS-APPLCORE-LANGUAGES | resolve_payment_code_language | Framework-generated effects are not direct child operations; catalog membership does not establish execution-session NLS language | Before preview qualify all generated root-create keys or exact translated-update effects and their reconciliation contract; otherwise stop. Preserve existing child inputs and verify actual effects with the fresh post-import export. Never infer SourceLang from base/active language or invent independent child ownership | Complete installed I/B inventory and separate active facts for create; qualified session relationship/effect contract where applicable; preserved input identities and expected child effects, with no direct writes |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Verify | Complete source-backed verifier can establish identity/reference | Read-only lookup only after workflow authorization; no prerequisite create |
| Blocked | Required source, current reference authority or lifecycle is unresolved | No; retain gap and stop |
| Satisfied | Authoritative verification proves applicable requirement | No additional operation needed |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MPC_DEPENDENCIES | step | 20 | resolve_dependency | applicable->MPC_RESOLVE_REFERENCES;blocked->MPC_HANDLE_ISSUES | MPC_VALIDATE_INPUT | stop | After input checks |
