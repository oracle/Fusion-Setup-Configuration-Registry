# Change Order Template Input Validation

This local contract validates the user-provided change order template name,
code, and document type label. The requested action context determines whether
the row creates a template or edits an existing one. It performs no live lookup or REST request,
does not derive an identifier, and does not apply a default. The public 26D
REST schema identifies ChangeOrderTemplateName, ChangeOrderTemplateCode, and
DocumentTypeCode as required create fields. This task instead accepts the
business-facing DocumentType label; core.data-loader derives DocumentTypeCode
through its downstream derivation queries. The supplied acceptance criteria
also require nonblank, unique Name and Code values. This client can detect only
duplicates inside the submitted batch; Data Loader remains responsible for any
existing-record and server-side uniqueness behavior.

## UI Label Mapping

| UI Label Accepted in Input | Canonical Attribute Name |
|---|---|
| Name | ChangeOrderTemplateName |
| Code | ChangeOrderTemplateCode |
| Document Type | DocumentType |
| Description | Description |

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Create identity and type | ChangeOrderTemplateName or Name; ChangeOrderTemplateCode or Code; DocumentType or Document Type | MISSING | Provide a nonblank name, a nonblank code, and one allowed document type label | Create action | |
| Edit identity and type | ChangeOrderTemplateName or Name; DocumentType or Document Type | MISSING | Provide a nonblank name and one allowed document type label | Edit action | |
| Optional description | Description | Not applicable; omission is valid | Provide a null or a string up to 240 characters when a description is needed | Only when supplied | |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| ChangeOrderTemplateName or Name presence | Map Name to ChangeOrderTemplateName. Require a string with at least one non-whitespace character; reject null, omission, and whitespace-only values. Do not trim, normalize, or replace the supplied value. | Every submitted template row | |
| ChangeOrderTemplateName or Name length | Reject a name longer than 240 characters. Preserve Unicode, case, punctuation, and surrounding whitespace when the value is otherwise valid. | Every supplied name | |
| ChangeOrderTemplateCode or Code presence and length | Map Code to ChangeOrderTemplateCode. Require a string with at least one non-whitespace character and no more than 30 characters; reject null, omission, and whitespace-only values. Do not trim, normalize, or replace the supplied value. | Create action; optional and not locally validated for edit action | |
| DocumentType or Document Type | Map Document Type to DocumentType. Require exactly one of Purchase Order, Blanket Purchase Agreement, or Contract Purchase Agreement; reject null, omission, whitespace-only values, and any other value. Pass the supplied label unchanged to core.data-loader for its downstream DocumentTypeCode derivation query. | Every submitted template row | |
| Description | Accept omission or null. When a non-null value is supplied, require a string of no more than 240 characters. Preserve the value exactly; do not trim, normalize, replace, or default it. | Only when supplied | |
| Other editable attributes | Treat editable attributes supplied for an edit as optional changes. Preserve their values and field presence exactly; do not locally determine editability, resolve identifiers, or validate backend-only value rules. Data Loader and the backend own those checks. | Edit action; only when an editable attribute is supplied | |
| Batch uniqueness | Reject a submitted create batch containing duplicate ChangeOrderTemplateName or Name values, or duplicate ChangeOrderTemplateCode or Code values. Compare supplied values exactly; do not normalize case, whitespace, or Unicode. Do not claim that values are unique in Fusion. | Create action with two or more template rows | |
| Identifiers, REST codes, and child attributes | Do not require, synthesize, validate, resolve, or default ChangeOrderTemplateId, ChangeOrderSeededTemplateId, DocumentTypeCode, AttributeCode, or EntityType. DocumentTypeCode is derived only by core.data-loader's downstream derivation query. | Every submitted template row | |

## Dependency-Aware Validation

| Applies When | Result | Next Action | Resolver |
|---|---|---|---|
| A create row passes create checks and no submitted-batch duplicate name or code exists | FIELD_VALID; no existing-record, privilege, or server-acceptance claim | Continue directly to Data Loader review only | |
| An edit row passes name and document-type checks | FIELD_VALID; no record-existence, editable-attribute, privilege, or server-acceptance claim | Continue directly to Data Loader review only | |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| COT.VALIDATE_INPUT | decision | 10 | validate_input | valid->COT.HANDOFF;missing->COT.HANDLE_ISSUES;invalid->COT.HANDLE_ISSUES | none | stop | Create rows require ChangeOrderTemplateName, ChangeOrderTemplateCode, and DocumentType; edit rows require ChangeOrderTemplateName and DocumentType, with optional Description and editable attributes preserved without REST calls or defaulting |
