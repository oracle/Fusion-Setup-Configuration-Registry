# Input validation


<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: AP_DISTRIBUTION_SET::BuName, AP_DISTRIBUTION_SET::Description, AP_DISTRIBUTION_SET::DistributionSetName, AP_DISTRIBUTION_SET::EnterpriseId, AP_DISTRIBUTION_SET::InactiveDate, AP_DISTRIBUTION_SET::TotalPercentDistribution, AP_DISTRIBUTION_SET_LINE::AP_DISTRIBUTION_SET.BuName, AP_DISTRIBUTION_SET_LINE::AP_DISTRIBUTION_SET.DistributionSetName, AP_DISTRIBUTION_SET_LINE::Description, AP_DISTRIBUTION_SET_LINE::DistCcidSegments, AP_DISTRIBUTION_SET_LINE::DistributionSetLineNumber, AP_DISTRIBUTION_SET_LINE::PercentDistribution, AP_DISTRIBUTION_SET_LINE::SOBName, AP_DISTRIBUTION_SET_LINE::Type1099, AP_DISTRIBUTION_SET_LINE::ProjectAccountingContext, AP_DISTRIBUTION_SET_LINE::ExpenditureType, AP_DISTRIBUTION_SET_LINE::AccountDescription, AP_DISTRIBUTION_SET::AttributeCategory, AP_DISTRIBUTION_SET::Attribute1, AP_DISTRIBUTION_SET::Attribute2, AP_DISTRIBUTION_SET::Attribute3, AP_DISTRIBUTION_SET::Attribute4, AP_DISTRIBUTION_SET::Attribute5, AP_DISTRIBUTION_SET::Attribute6, AP_DISTRIBUTION_SET::Attribute7, AP_DISTRIBUTION_SET::Attribute8, AP_DISTRIBUTION_SET::Attribute9, AP_DISTRIBUTION_SET::Attribute10, AP_DISTRIBUTION_SET::Attribute11, AP_DISTRIBUTION_SET::Attribute12, AP_DISTRIBUTION_SET::Attribute13, AP_DISTRIBUTION_SET::Attribute14, AP_DISTRIBUTION_SET::Attribute15, AP_DISTRIBUTION_SET_LINE::AttributeCategory, AP_DISTRIBUTION_SET_LINE::Attribute1, AP_DISTRIBUTION_SET_LINE::Attribute2, AP_DISTRIBUTION_SET_LINE::Attribute3, AP_DISTRIBUTION_SET_LINE::Attribute4, AP_DISTRIBUTION_SET_LINE::Attribute5, AP_DISTRIBUTION_SET_LINE::Attribute6, AP_DISTRIBUTION_SET_LINE::Attribute7, AP_DISTRIBUTION_SET_LINE::Attribute8, AP_DISTRIBUTION_SET_LINE::Attribute9, AP_DISTRIBUTION_SET_LINE::Attribute10, AP_DISTRIBUTION_SET_LINE::Attribute11, AP_DISTRIBUTION_SET_LINE::Attribute12, AP_DISTRIBUTION_SET_LINE::Attribute13, AP_DISTRIBUTION_SET_LINE::Attribute14, AP_DISTRIBUTION_SET_LINE::Attribute15 -->
<!-- fscr-update-fields: AP_DISTRIBUTION_SET::Description, AP_DISTRIBUTION_SET::InactiveDate, AP_DISTRIBUTION_SET::TotalPercentDistribution, AP_DISTRIBUTION_SET_LINE::Description, AP_DISTRIBUTION_SET_LINE::DistCcidSegments, AP_DISTRIBUTION_SET_LINE::PercentDistribution, AP_DISTRIBUTION_SET_LINE::Type1099, AP_DISTRIBUTION_SET_LINE::ProjectAccountingContext, AP_DISTRIBUTION_SET_LINE::ExpenditureType, AP_DISTRIBUTION_SET_LINE::AccountDescription, AP_DISTRIBUTION_SET::AttributeCategory, AP_DISTRIBUTION_SET::Attribute1, AP_DISTRIBUTION_SET::Attribute2, AP_DISTRIBUTION_SET::Attribute3, AP_DISTRIBUTION_SET::Attribute4, AP_DISTRIBUTION_SET::Attribute5, AP_DISTRIBUTION_SET::Attribute6, AP_DISTRIBUTION_SET::Attribute7, AP_DISTRIBUTION_SET::Attribute8, AP_DISTRIBUTION_SET::Attribute9, AP_DISTRIBUTION_SET::Attribute10, AP_DISTRIBUTION_SET::Attribute11, AP_DISTRIBUTION_SET::Attribute12, AP_DISTRIBUTION_SET::Attribute13, AP_DISTRIBUTION_SET::Attribute14, AP_DISTRIBUTION_SET::Attribute15, AP_DISTRIBUTION_SET_LINE::AttributeCategory, AP_DISTRIBUTION_SET_LINE::Attribute1, AP_DISTRIBUTION_SET_LINE::Attribute2, AP_DISTRIBUTION_SET_LINE::Attribute3, AP_DISTRIBUTION_SET_LINE::Attribute4, AP_DISTRIBUTION_SET_LINE::Attribute5, AP_DISTRIBUTION_SET_LINE::Attribute6, AP_DISTRIBUTION_SET_LINE::Attribute7, AP_DISTRIBUTION_SET_LINE::Attribute8, AP_DISTRIBUTION_SET_LINE::Attribute9, AP_DISTRIBUTION_SET_LINE::Attribute10, AP_DISTRIBUTION_SET_LINE::Attribute11, AP_DISTRIBUTION_SET_LINE::Attribute12, AP_DISTRIBUTION_SET_LINE::Attribute13, AP_DISTRIBUTION_SET_LINE::Attribute14, AP_DISTRIBUTION_SET_LINE::Attribute15 -->

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Package identity | AP_DISTRIBUTION_SET.csv; AP_DISTRIBUTION_SET_LINE.csv; ASM_SETUP_CSV_METADATA.xml; ObjectShortName AP_MANAGE_DISTRIBUTION_SETS | Block candidate | Use the exact supplied same-task template and metadata | Always |  |
| Header identity | BuName and DistributionSetName; resolve EnterpriseId using the documented row, current-run and fresh-export precedence and preserve existing context on update | Block affected target | Resolve owning enterprise and BU without guessing a match | Create or update selection |  |
| Owning header linkage | AP_DISTRIBUTION_SET.BuName and AP_DISTRIBUTION_SET.DistributionSetName on every child | Block affected target | Match exactly one owning header | Every child |  |
| Line identity and context | DistributionSetLineNumber >= 1, DistCcidSegments and PercentDistribution; establish coherent SOBName/ledger context without inferring unconditional serialized SOBName requiredness | Block candidate | Supply exact source-backed line identity and ledger/account context | Create line; update selection preserves keys |  |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Logical CSV shape | Require all exact ordered template headers: 27 header fields and 33 child fields. Parse quoted embedded newlines as one logical field; reject ragged rows and extra members. Serialize trailing blanks explicitly. | Every package |  |
| Percentage values | TotalPercentDistribution accepts only numeric 0 or 100. PercentDistribution is a signed decimal; reject expressions such as 20/2 and nonfinite values. Do not enforce a per-line 0..100 interval. | When supplied |  |
| Date contract | InactiveDate follows the exact metadata date type; no guessed date locale. FSCR create policy mirrors UI AP-810410: a supplied inactive date must be on or after today from the system clock. This is an FSCR policy, not a claimed FSM restriction. Use optional applicationTimeZone for a configured IANA application time zone, otherwise the runtime local system zone. No user date evidence is required. This create-only policy does not restrict updates. | InactiveDate supplied |  |
| Audit ownership | LastUpdateDate, LastUpdatedBy, LastUpdateLogin, CreationDate, CreatedBy on both entities are system owned; never accept requester edits. | Create and update |  |
| Field operation allowlists | Use the independently evidenced create/update markers above. Never broaden one field from task-level operation support. Unresolved fields require governed field-specific application validation; hard blockers cannot be overridden. | Create and update |  |
| DFF attributes | AttributeCategory and Attribute1 through Attribute15 on headers and lines are supported for create and update. FSM validates configured DFF values during import. Pass each supplied value to FSM without changing its spelling, case or spacing. On update, a field that the requester does not supply keeps its existing value; omission does not clear it. Clear an existing value only when explicitly requested. Report Fusion validation errors without substituting values or retrying automatically. Normal type, identity, preservation, package and candidate-bound import approval rules still apply. | Create and update |  |
| Project field boundary | CSV exposes ProjectAccountingContext, ExpenditureType and InstanceNumber. No named columns for Project Number, Task Number, Expenditure Organization, Contract Number or Funding Source. Never map InstanceNumber to Project Number. The UI Project Information Expenditure Type uses PJC_EXPENDITURE_TYPE_ID and is separate from the legacy CSV ExpenditureType string column. UI testing is outside this FSM skill’s scope and does not establish CSV import support; do not substitute the PJC identifier or require a UI test for the CSV column. Handle ProjectAccountingContext and ExpenditureType as ordinary optional string fields; pass supplied ExpenditureType values unchanged without lookup or business-value validation. Other project mappings retain their individual contracts and existing create/update restrictions. | Project request |  |
| Transient fields | InstanceNumber is a nonpersistent service attribute, not a stored Distribution Set line field. Leave it blank in new input and retain the column in the unchanged CSV schema; do not map it to Project Number or promise a stored value. AccountDescription is a nonpersistent service field. If supplied, pass it unchanged without lookup or business-value validation. Do not require the exported value to match or promise that it changes the UI Combination Description. Keep ordinary string-type and package checks. | When requested |  |
| String limits | Do not invent a byte or character length limit; use only an established field-length rule. | String changes |  |

## Field Contracts

| Entity | Field | Type | Create | Update |
| --- | --- | --- | --- | --- |
| AP_DISTRIBUTION_SET | BuName | string | supported | unsupported |
| AP_DISTRIBUTION_SET | DistributionSetName | string | supported | unsupported |
| AP_DISTRIBUTION_SET | LastUpdateDate | dateTime | unsupported | unsupported |
| AP_DISTRIBUTION_SET | LastUpdatedBy | string | unsupported | unsupported |
| AP_DISTRIBUTION_SET | Description | string | supported | supported |
| AP_DISTRIBUTION_SET | TotalPercentDistribution | decimal | supported | supported |
| AP_DISTRIBUTION_SET | InactiveDate | date | supported | supported |
| AP_DISTRIBUTION_SET | LastUpdateLogin | string | unsupported | unsupported |
| AP_DISTRIBUTION_SET | CreationDate | dateTime | unsupported | unsupported |
| AP_DISTRIBUTION_SET | CreatedBy | string | unsupported | unsupported |
| AP_DISTRIBUTION_SET | AttributeCategory | string | supported | supported |
| AP_DISTRIBUTION_SET | Attribute1 | string | supported | supported |
| AP_DISTRIBUTION_SET | Attribute2 | string | supported | supported |
| AP_DISTRIBUTION_SET | Attribute3 | string | supported | supported |
| AP_DISTRIBUTION_SET | Attribute4 | string | supported | supported |
| AP_DISTRIBUTION_SET | Attribute5 | string | supported | supported |
| AP_DISTRIBUTION_SET | Attribute6 | string | supported | supported |
| AP_DISTRIBUTION_SET | Attribute7 | string | supported | supported |
| AP_DISTRIBUTION_SET | Attribute8 | string | supported | supported |
| AP_DISTRIBUTION_SET | Attribute9 | string | supported | supported |
| AP_DISTRIBUTION_SET | Attribute10 | string | supported | supported |
| AP_DISTRIBUTION_SET | Attribute11 | string | supported | supported |
| AP_DISTRIBUTION_SET | Attribute12 | string | supported | supported |
| AP_DISTRIBUTION_SET | Attribute13 | string | supported | supported |
| AP_DISTRIBUTION_SET | Attribute14 | string | supported | supported |
| AP_DISTRIBUTION_SET | Attribute15 | string | supported | supported |
| AP_DISTRIBUTION_SET | EnterpriseId | long | supported | unsupported |
| AP_DISTRIBUTION_SET_LINE | AP_DISTRIBUTION_SET.BuName | string | supported | unsupported |
| AP_DISTRIBUTION_SET_LINE | AP_DISTRIBUTION_SET.DistributionSetName | string | supported | unsupported |
| AP_DISTRIBUTION_SET_LINE | SOBName | string | supported | unsupported |
| AP_DISTRIBUTION_SET_LINE | DistCcidSegments | string | supported | supported |
| AP_DISTRIBUTION_SET_LINE | DistributionSetLineNumber | long | supported | unsupported |
| AP_DISTRIBUTION_SET_LINE | LastUpdateDate | dateTime | unsupported | unsupported |
| AP_DISTRIBUTION_SET_LINE | LastUpdatedBy | string | unsupported | unsupported |
| AP_DISTRIBUTION_SET_LINE | PercentDistribution | decimal | supported | supported |
| AP_DISTRIBUTION_SET_LINE | Type1099 | string | supported | supported |
| AP_DISTRIBUTION_SET_LINE | Description | string | supported | supported |
| AP_DISTRIBUTION_SET_LINE | LastUpdateLogin | string | unsupported | unsupported |
| AP_DISTRIBUTION_SET_LINE | CreationDate | dateTime | unsupported | unsupported |
| AP_DISTRIBUTION_SET_LINE | CreatedBy | string | unsupported | unsupported |
| AP_DISTRIBUTION_SET_LINE | AttributeCategory | string | supported | supported |
| AP_DISTRIBUTION_SET_LINE | Attribute1 | string | supported | supported |
| AP_DISTRIBUTION_SET_LINE | Attribute2 | string | supported | supported |
| AP_DISTRIBUTION_SET_LINE | Attribute3 | string | supported | supported |
| AP_DISTRIBUTION_SET_LINE | Attribute4 | string | supported | supported |
| AP_DISTRIBUTION_SET_LINE | Attribute5 | string | supported | supported |
| AP_DISTRIBUTION_SET_LINE | Attribute6 | string | supported | supported |
| AP_DISTRIBUTION_SET_LINE | Attribute7 | string | supported | supported |
| AP_DISTRIBUTION_SET_LINE | Attribute8 | string | supported | supported |
| AP_DISTRIBUTION_SET_LINE | Attribute9 | string | supported | supported |
| AP_DISTRIBUTION_SET_LINE | Attribute10 | string | supported | supported |
| AP_DISTRIBUTION_SET_LINE | Attribute11 | string | supported | supported |
| AP_DISTRIBUTION_SET_LINE | Attribute12 | string | supported | supported |
| AP_DISTRIBUTION_SET_LINE | Attribute13 | string | supported | supported |
| AP_DISTRIBUTION_SET_LINE | Attribute14 | string | supported | supported |
| AP_DISTRIBUTION_SET_LINE | Attribute15 | string | supported | supported |
| AP_DISTRIBUTION_SET_LINE | ProjectAccountingContext | string | supported | supported |
| AP_DISTRIBUTION_SET_LINE | ExpenditureType | string | supported | supported |
| AP_DISTRIBUTION_SET_LINE | InstanceNumber | long | Nonpersistent service field; leave blank | Nonpersistent service field; no stored value to update |
| AP_DISTRIBUTION_SET_LINE | AccountDescription | string | Pass through if supplied; no business-value validation | Pass through if supplied; no business-value validation |


## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| DS.INPUT | step | 10 | validate_input | valid->DS.DEFAULT;invalid->DS.ISSUES | none | stop | Create or update request |


## Income tax input preparation

Follow [Income tax resolution policy](ora_reference_lookups.md#income-tax-resolution-policy) before constructing the blueprint. Use the seed reference first for new/changed nonblank input, resolving unique descriptions to exact codes. Never put a description into the CSV Type1099 column. Preserve significant spaces, slashes and mixed case in codes. Unknown values use standard REST; unavailable access is a warning and allows an explicit code to proceed to governed import, whereas successful no-match/inactive results and unresolved description ambiguity require correction. Omitted/blank/cleared values and unchanged existing codes require no tax lookup. Existing account, BU, shape and approval checks retain their own requirements.

## Project accounting context input

Preserve supplied ProjectAccountingContext strings through normal create/update processing. Do not add a field-specific warning, closed Yes/No domain, lookup or uncertainty gate. Apply the ordinary string-type check and all existing package/business validations; Fusion performs normal application validation during the approved import. Do not infer that the separate project attributes share this contract.

## Expenditure type input

Pass supplied ExpenditureType strings unchanged for create and update. Do not perform a lookup or business-value validation, substitute a PJC identifier, or require a field-specific warning or unresolved-field override. Keep the ordinary string-type, identity, preservation, package and import approval checks. Fusion performs application validation during the approved import. Omitted update values preserve existing values; clear only when explicitly requested. Report Fusion errors without substituting values or retrying automatically.
