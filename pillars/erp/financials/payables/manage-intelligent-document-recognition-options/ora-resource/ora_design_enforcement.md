# IDR Design Enforcement

<!-- fscr-supported-operations: update -->
<!-- fscr-update-fields: ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::BuDerivationBasisCode, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::CalcTaxDuringImportFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::EnforceIncompleteStatusFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::ImportFreightAmountFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::ImportLinesMatchedFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::ImportLinesUnmatchedFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::ImportPairedLinesOnlyFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::SingleLineAmountPoFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::SingleLineUtilityInvFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::UseTaxAmountAsControlFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::RequesterEmailDomain, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::ValidatePoLeFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::ConvertEmailIntoAttachFlag, ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTION_EXTENSIONS::EnabledFlag -->
**Normal update fields:** the annotation above lists normal allowlist support only. **Governed mapping update:** `ORA_INTELLIGENT_DOCUMENT_RECOGNITION_OPTIONS::Mappings` is additionally available through its exact-field serialized-XML validation path. It is not included in the normal allowlist.


Apply the task rules before any preview. Validate the requested fields and values against the current target configuration; block when required target evidence is unavailable.

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Lifecycle | Reject create; require exactly one options data row in the fresh target export and select it as the existing singleton. |
| 2 | Extension selector | If an extension change is requested, accept only existing OptionCode AP_PRORATE_FREIGHT_MISC. |
| 3 | Preview | Show the exact canonical codes and planned field changes; do not infer writeability from a UI/database mapping alone. |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Any IDR create request | Block | | Create is unsupported | Use an existing subscribed IDR setup for an update | No |
| Any IDR update | Block | | Fresh target export has zero or multiple options data rows, or keyless singleton reconciliation is unavailable | Require exactly one row; use it as the singleton and preserve unrelated values. Do not synthesize a row or a CSV key. | No |
| Extension update | Block | validate_idr_extension_option_code | OptionCode is not AP_PRORATE_FREIGHT_MISC, no existing selected row is confirmed, or any field other than EnabledFlag is requested | Select only the existing allowed row and update EnabledFlag only; no override may bypass field protection | No |
| Override Default Business Unit change | Block | resolve_idr_override_business_unit | Supplied value is not RA, SE, RE, N, a named choice, or an explicitly empty selection | Ask for a supported value; leaving the selection empty means N | Yes - requester chooses a valid value |
| Image Attachment Formats change | Block actual change | | A requested image-format value differs from the fresh baseline, or no baseline proves equality | Preserve exported values. An explicitly identical value is a no-op and may accompany a valid update; no override may authorize a change | No actual change |
| Other business field change | Validate | | Invalid declared type, value or constraint, or a key/audit field is requested | Validate a normal editable options field or extension EnabledFlag. Apply the separate Mappings gate below; reject protected fields without override and retain normal preview/import approval | Requester supplies a valid value |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| validate_idr_extension_option_code | Extension update | Exact allowed OptionCode and existing-row evidence | ora_reference_lookups.md |
| resolve_idr_override_business_unit | Override Default Business Unit change | Canonical code N, RA, SE, or RE | ora_reference_lookups.md |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| IDR.DESIGN.ENFORCE | step | 40 | design_enforcement | success->IDR.DONE;failure->IDR.ERROR.BLOCK | IDR.DEP.CHECK | stop | Every IDR update. Enforce update-only, existing-row, extension-code, and choice rules before preview. |

## Metadata Object Identity

Identify the IDR options and extensions CSV objects by exact BusinessObjectShortName
and declared XmlNodePath. Their two XML roots do not establish a parent/child
hierarchy or prove separate XML-file grouping. Do not infer groups from CSV names
or paths. NodeSequence is positive package-local ordering metadata, not object
identity: accept either 1/2 or 2/1 without rewriting Oracle exports.

The task's metadataIdentityPolicy retains exact task/object inventory, paths,
CSV member/header/type, target and release checks. Reject missing, duplicate or
unexpected metadata objects, malformed sequences and duplicate sequence numbers
at the same XML hierarchy level. This collision check is conservative until
authoritative XML-file grouping is reviewed; do not claim every positive-number
combination is valid. Descriptor sequence numbers do not define business-object identity.

Keep uploaded/source ZIPs immutable. Generated candidates preserve current-data
baseline metadata byte for byte; templates and independent readbacks may use a
different valid sequence profile while retaining the same object/path/header/type
schema. Update-only, singleton matching, allowed extension selection, input rules
and Data Loader approval remain unchanged. This metadata compatibility rule does
not establish live import or persistence success.

## Mapping-dialog evidence gate

Apply deterministic row/XML validation to `Mappings` before its governed exact-field application-validation gate. Accept only complete intended assignments, reject ambiguous duplicate emails and preserve unrequested rows and unrelated fields. Fusion validates BU existence during the approved import; do not report an offline reference lookup as completed. Preserve `BuEmailMapping` and `MappingUpdated`. For restoration, require an explicitly requested new governed restore design bound to the calculated original values and separate exact-ZIP approval; never carry forward import approval or execute restoration automatically.
