# Standard Operations — Design Enforcement

## Release and evidence boundary

Reviewed 29 October 2026. The [Oracle SCM documentation hub](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/) identifies 26D as current. The 26D overview/setup topics were retrieved; detailed Standard Operations REST pages could be retrieved only in 26C, and the detailed creation guide in 26B. These are retrieval gaps, not proof that newer topics do not exist. Use the cited release for each rule and verify the deployed contract before execution.

Public contract, request-preparation policy and deployment-dependent behavior are distinguished below. Public citations establish only what the linked pages document. No live create/update tests were performed. Keep supplied intent separate from the persisted result; the owning core workflow controls reads, preparation, authorization, writes and result verification.

## Public references

- [26D: Manage Standard Operations](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/faumf/how-you-manage-standard-operations.html): reusable in-house and supplier operations.
- [26D: Outside-processing items](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/faims/how-items-are-set-up-for-outside-processing.html): service-item meaning; do not import finished-product/work-definition rules into an unbound standard operation.
- [26B: Create a Standard Operation](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26b/faumf/create-a-standard-operation.html): operational choices and UI behavior.
- [26C: Alternate resource contract](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/op-standardoperations-standardoperationid-child-standardoperationresource-standardoperationresourceid-child-standardoperationalternateresource-post.html): alternate input fields; it does not certify setter behavior in every deployment.

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Actual change selection | For update, compare supplied intended fields with resolved current values using their types; preserve text casing and omission/null distinctions. Remove equal fields from the proposed change; missing current data is not equality |
| 2 | Narrow intent safeguards | Handle conflicting defaults, ignored alternate rates and unproven clear semantics below; avoid reproducing proven server validators |
| 3 | Capability and extension scope | Require owning workflow support for requested child/feature operations; do not convert missing support into a direct API fallback |
| 4 | Complete intent handoff | Return permitted intended changes and applicable capability requirements; if any requested part is blocked, do not silently submit a subset. A reduced scope requires explicit choice or an established partial-execution policy |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Supplier header create or intended OSP-item change | Server validation | | No separate FSCR eligibility gate | Rely on server validation for OSP item eligibility and handle returned errors through error handling | No automatic item selection |
| Explicit alternate UsageRate or InverseUsageRate create/change | Mandatory | | Requested value is zero, negative or a null clear with unverified semantics | Stop and resolve intent because alternate setters can ignore nonpositive inputs. Use an intended positive rate and verify persisted result | No silent positive replacement |
| Explicit rate and inverse both supplied | Mandatory | | Intended authoritative rate is unresolved | Ask which representation is intended; never rely on setter ordering to choose | No automatic choice |
| Supplier create with DefaultforAutomaticWorkDefinition=Y | Mandatory | | Server would force N and discard explicit intent | Explain the forced value and request a corrected business choice; do not silently overwrite | No automatic change |
| Explicit completion controls or yield conflict with effective type/flags | Mandatory | | Known clearing/forcing behavior would discard requested intent, or feature/clearing semantics are unestablished | Explain expected persistence behavior; request correction or verified capability before handoff | No silent clear, force or rounding promise |
| Wholly new singleton resource sequence | FSCR preparation safeguard | | Explicit PrincipalFlag=true conflicts with a sequence containing only one resource | Explain that Principal applies to simultaneous resources; propose false while preserving the sequence. If omitted, use the singleton preparation policy. Keep the server authoritative for validation | Resolve an explicit true with the user; never silently change it or renumber resources |
| Wholly new simultaneous resource group | FSCR preparation safeguard | | Multiple supplied resources share a sequence but exactly one principal has not been selected | Collect one explicit principal choice for that group. Use supplied task grouping only; do not query unrelated resource graphs | No automatic principal selection or sequence change |
| Existing or partially persisted resource groups | Preparation | find_standard_operation_resource | Current group membership needed for an intended correction is unknown | Reconcile the actual parent and child records through the owning workflow before determining group membership; a singleton in a partial retry file does not prove a singleton in Fusion | No inference from retry rows alone |
| Existing global-linked header/resource/alternate, or requested global linkage/unlink | Scope gate | | Ordinary update would require a separate global-operation workflow | Preserve linked state and server protection; stop until an explicit supported global workflow is selected. Do not inject internal flags or clear links to bypass protection | No implicit unlink or synchronization |
| Requested campaign-resource behavior dependent on deployment changes | Capability gate | | Compatibility of the target deployment for the requested campaign/production-line scenario has not been established | Require focused deployment acceptance evidence; do not claim generic metadata proves the relevant guard is installed | No client workaround or speculative graph check |
| Requested DFF, attachment, yield or profile work | Capability gate | read_standard_operation_contract | Required deployed fields/extension contract or owning core support is missing | Stop only the requested unsupported scope, report missing requirements and preserve complete request intent; do not invent tenant values | No auto-enable or fabricated metadata |
| Update already matches supplied intent | Informational | | None after valid identity and comparison | Report no change and no write needed; do not apply create defaults or repair unrelated existing data | Omit equal values only |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| read_standard_operation_contract | Requested operation/extension needs deployment contract confirmation | Supported attributes, actions and child metadata | ora_reference_lookups.md |
| find_standard_operation_resource | Existing or partially persisted resource group needs reconciliation | Actual child identities, sequences and principal flags under the resolved parent | ora_reference_lookups.md |

## Server-owned Enforcement

These remain server validations, not new client lookup gates: organization security; organization-scoped code uniqueness; work-center validity and resource-protected changes; inactive-date boundaries; count-point/automatic-transact combinations; automatic-work-definition singleton; saved operation-type immutability; referenced code/count-point protections; supplier/site and lead-time/UOM rules; no supplier resource children; no in-house OSP fields; contract-manufacturing supplier restrictions; primary/alternate active association, quantities, capacity, UOM, ranking and uniqueness; simultaneous/principal-resource checks; feature/profile rules; and protected deletes.

Do not copy Work Definition Names policies or usage-flag contracts into this task. Header code usage covers work definitions or work orders; count-point protection has its own referenced-work-definition scope. Do not infer both from one generic usage flag. No display-name uniqueness or case-insensitive code rule is added. Do not precheck dates against the agent clock.

Supplier creation needs explicit count-point intent consistent with the server rule; do not silently change flags. Missing supplier/site is not universally invalid, though a site requires a supplier. Rely on server validation for OSP eligibility; no separate verification or disclosure requirement is added.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| STDOP.DESIGN | step | 50 | design_enforcement | passed->STDOP.HANDOFF_GATE;failed->STDOP.ERROR | STDOP.DEFAULTS | stop | Apply narrow intent guards and capability gates; rely on server validation for OSP eligibility and established business rules |
