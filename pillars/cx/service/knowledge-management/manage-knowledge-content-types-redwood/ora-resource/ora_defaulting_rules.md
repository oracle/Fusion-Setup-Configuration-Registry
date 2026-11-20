# Content Type Defaulting Rules

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| Reference Key | Approved unique referenceKey supplied for this request; no generated replacement | Creating a content type; stop if the approved key is missing | No | |
| Title field | Caller-approved title field; required must be true | Creating a content type; reject a missing title or false required setting | No | |
| articleGroup | ARTICLE | Creating a new content type and the value is omitted | No | |
| contentSourceType | INTERNAL | Creating a new content type when the exported value is missing and the value is omitted | No | |
| enableIndexing | TRUE | The same-task export does not provide a value for the content type and the value is omitted | No | |
| indexStatus | blank (empty CSV cell) | The same-task export does not provide a value for the content type and the value is omitted | No | |
| allowCheckOut | TRUE | Creating a new content type and the value is omitted | No | |
| hasProducts | TRUE | Creating a new content type and the value is omitted | No | |
| hasCategories | TRUE | Creating a new content type and the value is omitted | No | |
| hasUserGroups | TRUE | Creating a new content type and the value is omitted | No | |
| categoriesRequireWorkflowApproval | TRUE | Creating a new content type and the value is omitted | No | |
| userGroupRequireWorkflowApproval | TRUE | Creating a new content type and the value is omitted | No | |
| viewsRequireWorkflowApproval | TRUE | Creating a new content type and the value is omitted | No | |
| displayDatesRequireWorkflowApproval | TRUE | Creating a new content type and the value is omitted | No | |
| eventDatesRequireWorkflowApproval | TRUE | Creating a new content type and the value is omitted | No | |
| restrictAuthoringToWorkflowUser | TRUE | Creating a new content type and the value is omitted | No | |
| hasPriority, hasRelatedContent, hasTalkBack, isEvent, isModerated, requireAtLeastOneProduct, requireAtLeastOneCategory, requireAtLeastOneUserGroup, restrictToOneUserGroupSelection, notifyOnWorkflowApproval, notifyOnWorkflowRejection, notifyGroupOnWorkflowRejection, removeVersions, validateHtml, allowUnsafeHTMLAndJS | FALSE | Creating a new content type and the value is omitted | No | |
| requireWorkflowApproval, allowPreselectedUserGroupChange, enableFullTextSearch, includeInMasterIdentifier, isRequired | TRUE | Creating a new schema attribute and the value is omitted | No | |
| counter | 0 | Creating a new schema attribute and the value is omitted | No | |
| counterPrefix | blank | Creating a new schema attribute and the value is omitted | No | |
| isNode, allowMultipleNodes, readOnly, enableAttributeLevelSearch | FALSE | Creating a new schema attribute and the value is omitted | No | |
| wysiwygType | FULL | Creating or changing an attribute whose schemaAttrType is WYSIWYG_EDIT and the value is omitted | No | |

## Value Precedence

Preserve approved explicit values. For existing rows, retain exported values unless an approved change targets them. Use the documented defaults above only for omitted values supported by the task contract and same-task evidence. Required constraints are validation gates: reject conflicting inputs instead of silently replacing them. Use the approved root referenceKey unchanged for every child linkage; do not derive a replacement from the display name.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CONTENT_TYPES_REDWOOD.DEFAULTS | step | 11 | apply_default | applied->CONTENT_TYPES_REDWOOD.DESIGN;invalid->CONTENT_TYPES_REDWOOD.BLOCKED | CONTENT_TYPES_REDWOOD.DEPENDENCIES | stop | Apply Standard Defaults and Value Precedence only to omitted values in their create/attribute scope after checking source evidence. Preserve explicit values and all unchanged exported update values; never derive a replacement root key or override mandatory title validation. |
