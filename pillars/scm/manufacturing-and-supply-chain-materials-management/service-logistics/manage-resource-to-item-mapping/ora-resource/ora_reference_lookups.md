# Manage Resource to Item Mapping Reference Evidence

Current capability gate: the task SKILL.md permits metadata/sample and explicitly requested status only. Complete business/reference reads and create/update/delete preparation are unsupported. Return blocked (invalid at input validation) before external activity or source preparation; the remaining domain contracts do not enable those operations.

## Current Capability Gate

The task's Reference Read Workflow is unsupported in this checkout. No complete core Data Loader business/reference reader is implemented or selected. Stop business reads, identity resolution, verification and mutation preparation before external activity. The local resolver contracts below describe requirements for a future reviewed integration; they do not select live requests and cannot accept caller-provided or historical evidence as a substitute. Only a separately reviewed capability and task change can enable these contracts.

Require complete current-run, same-environment evidence and independently verified data visibility if that future integration is delivered. Until then return blocked; never mark an identity resolver resolved.

## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| resolve_resource_item_mapping | Read selection, update/delete and create duplicate checks | Original root mapping evidence selected by Reference Read Workflow | For existing selection match exact ResourceItemMapId and every supplied selector. Create requires zero existing rows with the verified InventoryItemId, OrganizationId and ResourceId tuple; update excludes only its selected mapping from that duplicate check | Current mapping and retained omitted values; verified absence/duplicate outcome | Zero selected row is a no-op only for delete after full scope verification; missing update or multiple matches blocks; duplicate create/update target tuple blocks |
| resolve_mapping_organization | Create or organization change | Original inventoryOrganizationsOpenLOV evidence | Match one exact supplied OrganizationId and every supplied code/name; require active organization | Verified OrganizationId | Zero, multiple, inactive or conflicting values blocks |
| resolve_mapping_resource | Create; resource or organization change | Original productionResources evidence and resolved OrganizationId | Match one ResourceId in the exact selected organization; require resource not inactivated as of observation. On organization change verify retained ResourceId too | Verified ResourceId and association | Missing, multiple, inactivated or wrong-organization resource blocks |
| resolve_mapping_item | Create; item or organization change | Original itemsV2 evidence and resolved OrganizationId | Match one ItemId/OrganizationId pair, comparing task InventoryItemId to ItemId exactly; supplied item number must agree. On organization change verify the retained item too | Verified InventoryItemId and organization association | Missing, multiple, wrong organization or conflicting item identifiers blocks |

## Capability Checks

| Situation | What Happens |
|---|---|
| Future reviewed integration supplies valid evidence | Require original passed complete current-run evidence for each applicable collection and independent required data visibility; then evaluate the exact local resolvers |
| Missing/denied/stale/partial evidence or target describe mismatch | Return blocked before preview or preparation with the failed core stage; never use earlier values, samples, caller lists or another executor |
| Selected values change during validation | Obtain fresh reference evidence and prepare a new immutable artifact before core approval |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| RIM.RESOLVE_IDENTITIES | decision | 2 | evaluate_result | resolved->RIM.CHECK_DEPENDENCIES;blocked->RIM.RETURN_REFUSAL | RIM.VALIDATE_INPUT | stop | Evaluate original complete current-run mapping and applicable organization/resource/item reader evidence through the local resolvers; require matching environment/host and verified data visibility; any failed contract, ambiguity or missing evidence blocks |
