# IDR Input Validation

<!-- fscr-supported-operations: update -->
<!-- fscr-update-fields: ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::BuDerivationBasisCode, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::CalcTaxDuringImportFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::EnforceIncompleteStatusFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::ImportFreightAmountFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::ImportLinesMatchedFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::ImportLinesUnmatchedFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::ImportPairedLinesOnlyFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::SingleLineAmountPoFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::SingleLineUtilityInvFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::UseTaxAmountAsControlFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::RequesterEmailDomain, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::ValidatePoLeFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::ConvertEmailIntoAttachFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTION_EXTENSIONS::EnabledFlag -->
**Normal update fields:** the annotation above lists normal allowlist support only. **Governed mapping update:** `ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::Mappings` is additionally available through its exact-field serialized-XML validation path. It is not included in the normal allowlist.


Validate an update request for the existing IDR setup. Task create is unsupported. Normal options updates support the 13 fields listed in SKILL.md. The additional UI mapping setting follows its separate governed validation path below. Status, IDR email, other internal mappings, reference keys, flexfield attributes and all other non-UI fields are protected and cannot be enabled by an override. Extension updates permit only EnabledFlag on the existing AP_PRORATE_FREIGHT_MISC row; reject every other extension field, including overrides. Mappings belongs to the editable mapping dialog and uses the governed exact-field path described in SKILL.md. Require an explicitly supplied serialized mapping payload and apply the validation rules below. Actual Image Attachment Formats changes are prohibited; explicitly unchanged values may proceed only after exact comparison with the fresh baseline.

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Existing IDR setup | Completed exact-task export from the target environment with exactly one options data row | Block; do not create or choose a row | Obtain a fresh target export; treat its sole options row as the singleton. Zero or multiple rows block the update. This row-count rule does not create a CSV key. | Every update | |
| Requested change | One or more explicitly named fields with desired values | Ask for the intended change | Map a unique UI phrase, database column, or CSV attribute through the reviewed IDR field map | Every update | |
| Permitted extension selector | OptionCode AP_PRORATE_FREIGHT_MISC | Reject another code | Select an existing AP_PRORATE_FREIGHT_MISC row only | Extension update | validate_idr_extension_option_code |

## Dependency-Aware Validation

| Applies When | Result | Next Action | Resolver |
|---|---|---|---|
| Override Default Business Unit is supplied | Accept RA, SE, RE, N, the exact named labels, or an explicitly empty selection; empty maps to N | Reject an unknown choice; preserve the existing value when the field is omitted | resolve_idr_override_business_unit |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Create request | Reject. IDR is update-only. | A new options or extension record is requested | |
| Options singleton cardinality | Count data rows in `ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS.csv`; require exactly one in the fresh target export. Select that row and preserve unrelated values. | Every options update | |
| Extension OptionCode | Accept only AP_PRORATE_FREIGHT_MISC as a selector, not a mutable new code. | An extension row is included | validate_idr_extension_option_code |
| Override Default Business Unit | Normalize Email Routing Attribute to RA, Sender's Email Address to SE, Recipient Email Address to RE, and an explicitly empty selection to N. | BuDerivationBasisCode is supplied | resolve_idr_override_business_unit |
| On/off options | For the six `Process*AttachmentFlag` fields, interpret supported `On`/`Off` labels as `Y`/`N` only to compare the request with the fresh baseline. Accept an exact match as a no-op and preserve the exported value unchanged; reject any requested change. Normalize supported case-insensitive `On`/`Off` labels or `Y`/`N` codes to canonical `Y`/`N` for other supported on/off fields and the allowed extension's `EnabledFlag`. `ConvertEmailIntoAttachFlag` also accepts an empty value to restore an existing empty export value. Reject ambiguous values such as `maybe` before candidate ZIP creation. | Any of these fields is supplied for update | |
| Other package field | Use declared types and value contracts for the 13 normal options fields and extension EnabledFlag. Route Mappings through its separate governed validation path. Reject Status in any activation state, every non-UI field, every other extension field and key/audit updates; no override may bypass protection. Preserve omitted values. | A remaining business field is requested | |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| IDR.INPUT.VALIDATE | step | 10 | validate_input | success->IDR.DEP.CHECK;failure->IDR.ERROR.BLOCK | none | stop | Every IDR update: validate only explicitly requested fields against the normal update allowlist; route Mappings through its separate governed field gate. Preserve omitted business fields. Reject actual image-format changes while accepting baseline-proven no-ops; block Status and other protected fields. |

## Email attachment flag and blank restoration

The existing task-specific semantic extension validates `ConvertEmailIntoAttachFlag` as `Y`, `N`, or an explicitly requested empty restoration value. Normalize On/Off/Empty exported value to those exact CSV values, including a genuinely empty CSV cell for restoration. Omission preserves the existing exported value; apply no default and do not convert blank to `N`. Reject other inputs before candidate creation. The preview and verification requirements must show the explicit blank, and prepared ZIP validation compares the same exact field value without rewriting the upload. The six Image Attachment Formats flags cannot change; explicitly identical values are no-ops proven against the fresh baseline. Other supported on/off flags and extension `EnabledFlag` normalize supported On/Off labels or Y/N codes to `Y` or `N`, and reject blank; Override Default Business Unit retains its separate explicit-empty-to-`N` rule.

## Mapping-dialog request

Accept `Mappings` as a complete list of rows with exactly `email` and `businessUnit` strings, or as a serialized XML string. Row lists are escaped and encoded deterministically; an empty list produces an empty mapping collection. Validate the XML root/items/attributes, unambiguous email inputs, explicit nonblank BU names and duplicate emails. Reject malformed XML, DTD/entity declarations, unexpected elements/attributes, over 1000 rows or an XML payload over 1 MiB. These are local supported-input limits. Do not rewrite uploaded ZIP cells. Preserve unrequested assignments and unrelated settings. Fusion validates BU existence during the approved import; disclose that local checks are structural, use the governed exact-field application-validation path and obtain informed acceptance. Preserve `BuEmailMapping` and `MappingUpdated`; neither is directly updateable.
