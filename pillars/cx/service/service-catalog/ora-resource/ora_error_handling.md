# Error Handling

This resource owns safe failure disclosure and the mutation gate. It does not authorize a Fusion write.

## Error Situations

| Task Code | Task Name | Situation | What Should Happen |
|---|---|---|---|
| QSC_MANAGE_PRODUCT_GROUPS | Manage Product Groups | The request lacks a required name or exact existing-product-group identifier | Stop before preview and request the missing field. |
| QSC_MANAGE_PRODUCT_GROUPS | Manage Product Groups | Identity lookup returns zero or multiple records | Stop as an identity blocker; do not select an arbitrary product group. |
| QSC_MANAGE_PRODUCT_GROUPS | Manage Product Groups | Product-relationship lookup returns zero or multiple records, or the client attempts to generate ProdGroupItemsId | Stop as an identity blocker. Use a documented collection finder and the server-returned identifier; do not generate an item-path key. |
| QSC_MANAGE_PRODUCT_GROUPS | Manage Product Groups | Parent product group cannot resolve to exactly one record for a subgroup read | Stop before the child request; do not substitute an arbitrary parent identifier. |
| QSC_MANAGE_PRODUCT_GROUPS | Manage Product Groups | Parent product group cannot resolve to exactly one record for subgroup creation | Stop before preview; do not create a subgroup below an arbitrary parent identifier. |
| QSC_MANAGE_PRODUCT_GROUPS | Manage Product Groups | Parent product group cannot resolve to exactly one record for filter-attribute creation | Stop before preview; do not add an attribute below an arbitrary parent identifier. |
| QSC_MANAGE_PRODUCT_GROUPS | Manage Product Groups | FSM import is requested | Stop as unsupported; the effective setup-task catalog marks export/import unsupported. |
| QSC_MANAGE_PRODUCT_GROUPS | Manage Product Groups | A lock, release, publish, create, update, or delete operation is pending | Wait for its response before performing another operation on the same product group. |
| QSC_MANAGE_PRODUCT_GROUPS | Manage Product Groups | A Fusion API failure or indeterminate mutation result occurs | Preserve sanitized diagnostics, verify with the documented read operation, and do not retry the mutation without a new exact approval. |
| QSC_MANAGE_PRODUCT_GROUP_USAGE | Manage Product Group Usage | UsageCode is missing, exceeds 30 characters, or the usage item cannot resolve | Stop before the usage or child read and request a valid documented UsageCode. |
| QSC_MANAGE_PRODUCT_GROUP_USAGE | Manage Product Group Usage | A usage-engine, mode, preference, or root child identifier is missing | Stop before the child-item read and request the identifier documented for that selected subcategory. |
| QSC_MANAGE_PRODUCT_GROUP_USAGE | Manage Product Group Usage | A Product Group Usage GET fails or a page cannot be retrieved | Preserve sanitized diagnostics and stop. Do not substitute cached or browser data and do not retry beyond the selected REST client policy. |

## Refusal Rules

| Task Code | Task Name | Situation | What Must Not Happen |
|---|---|---|---|
| QSC_MANAGE_PRODUCT_GROUPS | Manage Product Groups | Preview or approval is missing or stale | Do not submit a REST mutation. |
| QSC_MANAGE_PRODUCT_GROUPS | Manage Product Groups | The lock-before-publish dependency is unsatisfied | Do not publish the product group. |
| QSC_MANAGE_PRODUCT_GROUP_USAGE | Manage Product Group Usage | A caller requests REST create, update, delete, or import through the documented Product Group Usages REST endpoints | Do not submit it. The supplied Oracle REST source documents GET endpoints only; use the catalog-supported FSM task route only through the task metadata and its selected Data Loader workflow. |
| QSC_MANAGE_PRODUCT_GROUPS | Manage Product Groups | The selected Product Groups create command, contract or required core client/guards are unavailable | Stop with an execution-route blocker; retain sanitized diagnostics and the missing commands. Do not invoke REST directly, browser actions, CSV import, or an alternative adapter. Restore and test the exact selected task capability before retrying its preflight. |

## Task Nodes

| Task Code | Task Name | Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|---|---|
| QSC_MANAGE_PRODUCT_GROUPS | Manage Product Groups | MPG.EXECUTION_GATE | decision | 53 | execution_gate | ready->MPG.READY;blocked->MPG.BLOCKED | MPG.VALIDATE_REQUEST | stop | A mutation is requested. Require an implemented task-specific execution route before preview or approval. For create-product-group require scripts/product_group_rest.py and its enabled exact-task contract; its preview/verify/create commands own Product Groups validation and delegate HTTP/auth to core. The registry grants no POST permission; return to that selected workflow for exact immediate approval and one verified attempt. Missing commands or changed/expired evidence block. Other mutations require their own implemented contract; generic REST is not a fallback. |
| QSC_MANAGE_PRODUCT_GROUPS | Manage Product Groups | MPG.COLLECTION_COMPLETE | terminal | 54 | terminal | none | MPG.LOOKUP_PRODUCT_GROUPS | continue | The requested product-group collection pages have been returned. |
| QSC_MANAGE_PRODUCT_GROUPS | Manage Product Groups | MPG.READY | terminal | 55 | terminal | none | MPG.EXECUTION_GATE | continue | A task-specific execution route, immutable preview, and current explicit approval are present; hand off the unchanged request to that route. |
| QSC_MANAGE_PRODUCT_GROUPS | Manage Product Groups | MPG.FSM_IMPORT_BLOCKED | terminal | 56 | terminal | none | MPG.GATE_FSM_IMPORT | continue | FSM import is blocked because no supported catalog or authoritative import contract exists. |
| QSC_MANAGE_PRODUCT_GROUPS | Manage Product Groups | MPG.PRODUCT_RELATIONSHIPS_COMPLETE | terminal | 57 | terminal | none | MPG.LOOKUP_PRODUCT_RELATIONSHIPS | continue | The requested product-relationship collection pages have been returned. |
| QSC_MANAGE_PRODUCT_GROUPS | Manage Product Groups | MPG.SUBGROUPS_COMPLETE | terminal | 58 | terminal | none | MPG.LOOKUP_PRODUCT_GROUP_SUBGROUPS | continue | The requested parent-scoped subgroup collection pages have been returned. |
| QSC_MANAGE_PRODUCT_GROUPS | Manage Product Groups | MPG.BLOCKED | terminal | 59 | terminal | none | none | continue | A documented validation, identity, dependency, route, or approval gate blocks the request. |
| QSC_MANAGE_PRODUCT_GROUPS | Manage Product Groups | MPG.FAILED | terminal | 60 | terminal | none | none | continue | A documented read, dependency, or validation operation failed. |
| QSC_MANAGE_PRODUCT_GROUP_USAGE | Manage Product Group Usage | PGU.USAGES_COMPLETE | terminal | 52 | terminal | none | PGU.LIST_USAGES | continue | The Product Group Usage collection pages have been returned. |
| QSC_MANAGE_PRODUCT_GROUP_USAGE | Manage Product Group Usage | PGU.USAGE_COMPLETE | terminal | 53 | terminal | none | PGU.RESOLVE_USAGE | continue | The requested Product Group Usage item has been returned. |
| QSC_MANAGE_PRODUCT_GROUP_USAGE | Manage Product Group Usage | PGU.ENGINES_COMPLETE | terminal | 54 | terminal | none | PGU.LIST_USAGE_ENGINES | continue | The usage-engine collection pages have been returned. |
| QSC_MANAGE_PRODUCT_GROUP_USAGE | Manage Product Group Usage | PGU.MODES_COMPLETE | terminal | 55 | terminal | none | PGU.LIST_USAGE_MODES | continue | The usage-mode collection pages have been returned. |
| QSC_MANAGE_PRODUCT_GROUP_USAGE | Manage Product Group Usage | PGU.PREFERENCES_COMPLETE | terminal | 56 | terminal | none | PGU.LIST_USAGE_PREFERENCES | continue | The usage-preference collection pages have been returned. |
| QSC_MANAGE_PRODUCT_GROUP_USAGE | Manage Product Group Usage | PGU.ROOTS_COMPLETE | terminal | 57 | terminal | none | PGU.LIST_USAGE_ROOTS | continue | The usage-root collection pages have been returned. |
| QSC_MANAGE_PRODUCT_GROUP_USAGE | Manage Product Group Usage | PGU.BLOCKED | terminal | 58 | terminal | none | none | continue | A required usage identifier or documented child identifier is missing or unresolved. |
| QSC_MANAGE_PRODUCT_GROUP_USAGE | Manage Product Group Usage | PGU.FAILED | terminal | 59 | terminal | none | none | continue | A documented Product Group Usage lookup failed. |
| QSC_MANAGE_PRODUCT_GROUPS | Manage Product Groups | MPG.RELATIONSHIP_READ_COMPLETE | terminal | 70 | terminal | none | MPG.RESOLVE_PRODUCT_RELATIONSHIP_READ | stop | The requested relationship GET result is returned without a mutation preview, approval, or write handoff. |
| QSC_MANAGE_PRODUCT_GROUPS | Manage Product Groups | MPG.FILTER_ATTRIBUTES_COMPLETE | terminal | 71 | terminal | none | MPG.LOOKUP_FILTER_ATTRIBUTES | stop | The requested filter-attribute collection pages are returned; no write is authorized. |
| QSC_MANAGE_PRODUCT_GROUP_USAGE | Manage Product Group Usage | PGU.ENGINE_ITEM_COMPLETE | terminal | 70 | terminal | none | PGU.READ_ENGINE_ITEM | stop | The requested engine child item is returned; no mutation preview or approval is required. |
| QSC_MANAGE_PRODUCT_GROUP_USAGE | Manage Product Group Usage | PGU.MODE_ITEM_COMPLETE | terminal | 71 | terminal | none | PGU.READ_MODE_ITEM | stop | The requested mode child item is returned; no mutation preview or approval is required. |
| QSC_MANAGE_PRODUCT_GROUP_USAGE | Manage Product Group Usage | PGU.PREFERENCE_ITEM_COMPLETE | terminal | 72 | terminal | none | PGU.READ_PREFERENCE_ITEM | stop | The requested preference child item is returned; no mutation preview or approval is required. |
| QSC_MANAGE_PRODUCT_GROUP_USAGE | Manage Product Group Usage | PGU.ROOT_ITEM_COMPLETE | terminal | 73 | terminal | none | PGU.READ_ROOT_ITEM | stop | The requested root child item is returned; no mutation preview or approval is required. |
| QSC_MANAGE_PRODUCT_GROUP_USAGE | Manage Product Group Usage | PGU.FSM_HANDOFF_GATE | decision | 30 | execution_gate | ready->PGU.FSM_HANDOFF_READY;blocked->PGU.BLOCKED | PGU.VALIDATE_FSM_HANDOFF | stop | Return validated business intent only when the active Run Book and core.data-loader FSM preflight identify this exact task and immutable source. Missing or ambiguous ownership blocks; task validation does not request load approval. |
| QSC_MANAGE_PRODUCT_GROUP_USAGE | Manage Product Group Usage | PGU.FSM_HANDOFF_READY | terminal | 74 | terminal | none | PGU.FSM_HANDOFF_GATE | stop | Return validation results to the owning Run Book/core.data-loader FSM workflow, which owns mapping, exact-artifact preview, approval, import, polling and verification. This terminal authorizes no direct POST, PATCH, or import. |
