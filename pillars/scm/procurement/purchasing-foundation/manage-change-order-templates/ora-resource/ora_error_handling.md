# Change Order Template Error Handling and Handoff

These nodes are local preparation only. They do not invoke Fusion, request
REST metadata, obtain a token, select POST or PATCH, or submit an import.

## Error Situations

| Situation | What Should Happen |
|---|---|
| Create input has a missing, null, whitespace-only, non-string, or overlength ChangeOrderTemplateName or ChangeOrderTemplateCode | Report the field issue and stop before Data Loader review |
| Edit input has a missing, null, whitespace-only, non-string, or overlength ChangeOrderTemplateName | Report the field issue and stop before Data Loader review |
| DocumentType is missing or not Purchase Order, Blanket Purchase Agreement, or Contract Purchase Agreement | Report the field issue and stop before Data Loader review; do not derive DocumentTypeCode locally |
| Description is supplied as a non-string non-null value or exceeds 240 characters | Report the field issue and stop before Data Loader review |
| Submitted batch contains a duplicate name or code | Report each duplicated value and its affected rows; do not issue a lookup or claim Fusion-wide uniqueness |
| An identifier, status, child attribute, or default is inferred to complete the request | Stop and require the downstream Data Loader workflow to obtain its own supported source and metadata contract |
| Data Loader later reports a validation, metadata, privilege, transport, Fusion API, timeout, process, artifact, or approval failure | Let core.data-loader classify and persist the prescribed sanitized diagnostic; do not retry or substitute a direct REST call |

## Error Classifications

| Result Category | When Used | Next Action |
|---|---|---|
| input validation | Create-required name/code, edit-required name, document type label, optional description, or create-batch uniqueness fails a local check | Correct the supplied row values and rerun local preparation |
| catalog mismatch | Task or business object differs from the generated skill manifest | Resolve the mapping before Data Loader review |
| approval blocker | An import is requested without the Data Loader workflow's current approval | Use the Data Loader approval workflow once the exact source and preview are ready |
| process failed | The selected Data Loader workflow reports a failed import | Preserve its diagnostics and follow its documented recovery path |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| COT.HANDOFF | Task code and name, the completed action-specific offline checks, no defaults applied, no live lookups or REST calls made, and readiness for Data Loader review only |
| COT.RETURN_ISSUES | Failure class, blocked Rule ID, sanitized issue list, verified side effects none, and a safe correction step |

## Data Loader Handoff

| Situation | What Happens |
|---|---|
| Create checks pass | Hand off the submitted name, code, DocumentType label, and Description when supplied to core.data-loader for purchasingChangeOrderTemplates. Data Loader derives DocumentTypeCode through its derivation query. This handoff does not create a REST payload or assert it is complete. |
| Edit checks pass | Hand off the submitted name, DocumentType label, Description when supplied, and any supplied editable attributes to core.data-loader. Data Loader owns target identification, DocumentTypeCode derivation, editability, payload shape, and backend validation. |
| Missing identifiers or child attributes | Do not request or derive IDs or child attribute values in this local contract. Data Loader owns its supported sample, metadata, source validation, and any required fields for a later approved import. |
| Import requested | core.data-loader owns immutable-source preparation, preview, approval binding, submission, verification, and diagnostics. |

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Name validation | Do not perform a live lookup, REST call, authentication action, token refresh, or direct API mutation |
| Client input | Do not invent an identifier, child attribute, status, Fusion-wide uniqueness result, or default value |
| Failed or uncertain import | Do not retry, POST, PATCH, or otherwise alter Fusion outside the selected Data Loader workflow |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| COT.HANDOFF | decision | 20 | execution_gate | ready->COT.READY;blocked->COT.HANDLE_ISSUES | COT.VALIDATE_INPUT | stop | Action-specific local checks passed; allow Data Loader review only, with no authorization for a write |
| COT.READY | terminal | 30 | terminal | none | COT.HANDOFF | stop | Return READY_FOR_DATALOADER_REVIEW with verified side effects none |
| COT.HANDLE_ISSUES | step | 90 | error_handler | reported->COT.RETURN_ISSUES | none | stop | Any reached local input or handoff failure |
| COT.RETURN_ISSUES | terminal | 100 | terminal | none | COT.HANDLE_ISSUES | stop | Return MISSING for an absent required field and FAILED for invalid input or handoff failure |
