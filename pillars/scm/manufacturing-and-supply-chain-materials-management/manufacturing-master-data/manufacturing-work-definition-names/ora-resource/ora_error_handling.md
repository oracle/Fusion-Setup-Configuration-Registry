# Work Definition Names — Errors and Handoff Gates

## Public references and compatibility

- [Oracle Fusion Cloud Manufacturing 26D: Work Definition Names](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/faumf/work-definition-names.html) explains the business fields and usage restrictions.
- [Oracle Fusion Cloud SCM 26D: WorkDefinitionName business object](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/fabsm/bo_oraScmCoreManufacturingWorkDefinition_WorkDefinitionName.html) lists the business type codes. This is a different API model; do not copy its field names, children or write contract into V2.

The public references support business terminology. They do not establish a public compatibility guarantee for workDefinitionNamesV2. Verify its availability, operations and schema in the selected environment through the owning workflow. The rules below distinguish service behavior, request preparation and adopted FSCR policy. They are not evidence of successful create/update testing.

## Execution boundary

Scope is create/update preparation through core.data-loader and its task validation, immutable preparation and approval gates. No direct product write is performed by these rule nodes. Do not select DELETE, a UI fallback, a legacy resource, or automatic upsert. Verify deployed capabilities and ID generation during separate acceptance testing; static contracts do not prove deployed behavior or privileges.

## Error Situations

| Situation | What Should Happen |
|---|---|
| Duplicate display name | Preserve WIS:::WIS_DUP_WDN_DISP_NM or process variant WIS:::WIS_DUP_WDN_DISP_NM_PM when returned. Ask whether reuse, update or a different new name was intended; never auto-rename |
| Duplicate internal code | Preserve WIS:::WIS_DUP_WDN_INT_NM or process variant WIS:::WIS_DUP_WDN_INT_NM_PM when returned. Do not treat the conflict as success or rely on a preflight existence query |
| Past end date | Preserve WIS:::WIS_WDN_ED or WIS:::WIS_WDN_ED_PM and useful returned details. Fusion evaluates its date context; do not recompute using the agent clock |
| End date before start date | Preserve FND:::FND_CMN_TOERLY_EQ_FRM_DTE_EF when returned. Equal start/end dates are not rejected by this comparison; do not infer stricter behavior from the identifier |
| Required, precision or key error | Return the backend field/message details; request only the necessary correction. Do not build a second validator from message wording |
| Read-only or unsupported field | Correct the field selection through the owning workflow; never resend a full GET response |
| Unknown error, authorization, concurrency or transport failure | Preserve redacted backend identifier, message and nested details. Exact HTTP-status/error-envelope mappings are deployment-dependent; do not hardcode an unverified mapping |
| Uncertain prior write | Stop blind retries; use the owning workflow's authorized reconciliation read before deciding whether a new submission is safe |
| Policy prohibits an actual change or required evidence is unavailable | Name each blocked field and the policy or missing fact. Reject the whole requested write; do not silently submit a permitted subset. A reduced request requires explicit user choice or an established partial-execution policy |
| All supplied values already match | Report already matching, with no PATCH required; do not claim a write occurred |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| input_validation | Business intent or safe request shape is missing | Ask for the missing choice/value |
| catalog_or_metadata_mismatch | Target capability or required usage evidence is inconsistent/incomplete | Resolve the contract before proceeding |
| auth_authz | Owning client reports access failure | Follow core authentication/privilege handling |
| transport_environment | Request transport fails | Preserve diagnostics and apply only permitted retries |
| fusion_api | Backend rejects the submitted operation | Surface actual field/message details for correction |
| approval_blocker | Normal execution approval is missing | Complete the owning workflow approval gate |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Authoring readiness | Separate compiled policy readiness from request-specific evidence, permissions and live acceptance testing |
| Execution handoff | Intended operation, selected target, applicable rule results and approved immutable source |
| Error | Redacted stage, returned backend message/identifier, partial outcome and safe next action |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Backend-owned uniqueness or date rule | Do not add database queries, client-clock checks, forced uppercase, automatic renaming or silent date changes |
| Unknown usage encoding | Do not infer a Boolean mapping for IsUsedInWorkDefinition; return a missing-fact blocker only for actual changes requiring usage |
| Unknown seeded status | Do not infer it from prefixes, name usage or a partial seed inventory |
| Blocked field in a mixed request | Do not silently drop the blocked change and report complete success; preserve the whole requested intent |
| Completed preparation graph | Do not claim a Fusion write or successful deployed test |

## Acceptance boundary

Before enabling writes in a target environment, separately verify minimal create/defaults/ID generation, Boolean handling, null/clearing behavior, duplicate case/whitespace behavior, equal and past-date boundaries, returned errors, policy enforcement and uncertain-outcome reconciliation. These are one-time integration acceptance checks, not per-request duplicate validations. This resource authoring does not authorize running them.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| WDNAME.HANDOFF_GATE | step | 60 | execution_gate | passed->WDNAME.RULES_COMPLETE;failed->WDNAME.ERROR | WDNAME.DESIGN | stop | Require applicable policy results and owning core workflow boundaries; carry a no-write result when already matching; writes still require deployed capability checks |
| WDNAME.RULES_COMPLETE | terminal | 70 | terminal | none | WDNAME.HANDOFF_GATE | stop | Return completed preparation results only, including explicit no-write status when already matching |
| WDNAME.ERROR | step | 90 | error_handler | reported->RETURN_ISSUES | none | stop | Reached failure or missing evidence |
| RETURN_ISSUES | terminal | 100 | terminal | none | none | stop | Return blockers and safe next action |
