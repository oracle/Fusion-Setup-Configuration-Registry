# Manage Legal Addresses Defaulting Rules

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| ActualContentSource | USER_ENTERED | Every supported CREATE | No |  |
| InternalFlag | Y | Every supported legal-location CREATE | No |  |
| StatusFlag | A | New active legal location | No |  |
| ValidatedFlag | N | No approved address-validation result exists | No | record_address_validation_status |
| GeometryStatusCode | DIRTY | No approved geocoding result exists | No | record_address_validation_status |
| SalesTaxInsideCityLimits | 1 | Target metadata permits the observed address-framework default | No | verify_address_package_baseline |
| AddressStyle | Resolved StyleFormatCode | Country style resolves | No | resolve_address_style_layout |
| CreatedByModule | XLE_CREATE_LE | Every CSV CREATE | No |  |
| OrigSystemReference | New nonblank collision-checked FDoS-owned identifier | Every CSV CREATE | No | find_existing_legal_address |
| LeFormattedAddress | Nonblank value derived and comma-to-slash normalized by the contract below | Every CSV CREATE | Normalize commas; preserve other reviewed content |  |
| TimezoneCode | Null | User omits the optional time zone | No |  |
| Optional dates, phonetic fields, DFF and localization segments | Null | Not supplied and no active runtime context requires them | Yes |  |

FormattedAddress and FormattedMultilineAddress are Fusion-generated; leave them blank on CREATE. LeFormattedAddress is a required authored import value and must never be blank. Leave physical IDs, audit fields, ESS fields, object versions, and login values blank.

## LeFormattedAddress Construction

1. When the user gives the entire address on one comma-separated line, derive `LeFormattedAddress` by literal replacement of every comma with `/`: `full_address.replace(',', '/')`. Preserve existing spaces, case, country text, and other characters; do not replace only the first comma, drop the country, or silently remove spaces. For example, `Line 1, City, Region PostalCode, Country` becomes `Line 1/ City/ Region PostalCode/ Country`.
2. If no complete line is supplied, use an explicitly supplied nonblank `LeFormattedAddress`, or construct it deterministically from the reviewed nonblank address components in the resolved country-layout order, including the reviewed country name or resolved country code. Use `/` between component groups and replace any remaining commas with `/`. Do not copy an existing row's display, guess missing components, or apply a universal country-specific layout. Block ambiguous source/component mappings.
3. Apply normalization to an explicitly supplied value too. Require the resulting value to be nonblank after trimming and contain no commas. A blank supplied value may be derived only from complete reviewed inputs; otherwise stop for correction. Preserve the structured Address1, City, State, Province, County, PostalCode, and Country values in their own fields; the slash rule applies only to `LeFormattedAddress`.
4. Check exact equality between the derived value, preview, and reparsed final CSV value for every new row. Record the derivation source and transformation in the preview.

This contract describes the upload value. Fusion can regenerate formatted output from the stored components. Verify returned `LeFormattedAddress`, `FormattedAddress`, and `FormattedMultilineAddress` separately when asked; a generated display or successful load does not prove literal retention of the input string.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| LA.APPLY_DEFAULTS | step | 40 | apply_default | applied->LA.ENFORCE_DESIGN;blocked->LA.HANDLE_ERROR | LA.CHECK_DEPENDENCIES | stop | After dependencies are ready |
