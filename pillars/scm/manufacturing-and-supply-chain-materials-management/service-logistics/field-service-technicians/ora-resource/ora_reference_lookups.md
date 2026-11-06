# Field Service Technicians Reference Evidence

Current capability gate: the task SKILL.md permits metadata/sample and explicitly requested status only. Complete business/reference reads and create/update/delete preparation are unsupported. Return blocked (invalid at input validation) before external activity or source preparation; the remaining domain contracts do not enable those operations.

## Current Capability Gate

The task's Reference Read Workflow is unsupported in this checkout. No complete core Data Loader business/reference reader is implemented or selected. Stop business reads, identity resolution, verification and mutation preparation before external activity. The local resolver contracts below describe requirements for a future reviewed integration; they do not select live requests and cannot accept caller-provided or historical evidence as a substitute. Only a separately reviewed capability and task change can enable these contracts.

Require complete current-run, same-environment evidence and independently verified data visibility if that future integration is delivered. Until then return blocked; never mark an identity resolver resolved.

## Local Lookups

The future reviewed reader supplies three separate evidence sets; caller-provided lists, earlier observations and samples cannot satisfy this gate.

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| resolve_technician_stock_location | Before create, EnabledFlag update, default usable repair or selected deletion preview | Original current-run Data Loader root assignment evidence plus serviceLogisticsPersonsLOV and stockingLocations reference evidence from the task Reference Read Workflow; verified required data visibility | Require all evidence complete and bound to the same exact BO, environment and host. Match exact technician PartyName to one PartyId in persons LOV, independently of assignments. Match exact OrganizationCode and Subinventory to one StockLocationId in stockingLocations; compare supplied names/IDs and requested condition to ConditionMeaning. Then match the PartyId/StockLocationId pair in assignments. Create requires zero assignments; update/repair/delete require one selected existing row and its surrogate. Compare existing assignment organization, subinventory and condition with reference evidence; conflicts block | Verified PartyId, StockLocationId, organization identities; selected existing TechSubinventoryId, baseline flags/condition and independently resolved stock-location ConditionMeaning | Zero/multiple technician or stock-location matches, duplicates, mismatched/stale/partial/denied evidence or unverified visibility blocks. Verified zero assignment is a delete no-op only; it never establishes absent reference objects |

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| Reader or complete evidence unavailable | Record catalog mismatch or the owning Data Loader failure; follow blocked to FST.RETURN_REFUSAL before preview, approval or submission; no alternate reader is authorized |
| Evidence evaluation | Classify prior-node and Data Loader evidence locally; no request is authorized by this node, including by generic execution-guide instructions |
| Default usable prerequisite evidence | Use the complete unfiltered rows for the resolved PartyId, Condition and DefaultFlag to report existing default usable assignments to input validation. Zero matches means the proposed create must supply the explicitly requested usable default or remain blocked. Do not change defaults during reference resolution |
| Default usable repair evidence | Identify the explicitly selected existing usable row and its baseline; reject competing default usable rows for the same PartyId. Fill only the returned surrogate and baseline evidence; changing the two requested flags belongs to the separately approved Data Loader repair import |
| Sample enrichment or load status used as reference evidence | Reject; a first-record sample or job counters do not prove current complete assignment values |
| Unspecified flags | Keep optional flag columns absent; do not invent defaults or change other assignments |
| Customer reference evidence | Keep values in memory or private local ignored files; persist only redacted project diagnostics |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| FST.RESOLVE_IDENTITIES | step | 2 | evaluate_result | resolved->FST.EXECUTION_GATE;blocked->FST.RETURN_REFUSAL | FST.VALIDATE_INPUT | stop | Locally evaluate original complete same-environment Data Loader assignment, technician and stock-location evidence and separately verified required data visibility; missing, partial, ambiguous or mismatched evidence returns blocked |
