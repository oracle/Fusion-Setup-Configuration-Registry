# Design enforcement


## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Preserve identity | Enforce owning header/line keys and immutable update fields |
| 2 | Validate complete owning set | Require at least one child and exact aggregate equality |
| 3 | Preserve uncertainty | Reject unsupported behavior and disclose unresolved field-specific scope |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Create or update | Error |  | No child or sum of all owning PercentDistribution values differs from TotalPercentDistribution; header domain is 0/100 | Require at least one line and exact decimal aggregate. Valid examples include -10+110+0=100. Never silently rescale | No |
| Update | Error |  | Attempted change to BU, EnterpriseId identity context, distribution set name, SOBName, parent-link keys or line number | Preserve keys and ownership; do not relocate children | No |
| Delete request | Error |  | Persisted header delete requested | AP_NO_DELETE is source-proven; InactiveDate update is a distinct lifecycle action | No |
| Other unresolved project/transient changes | Error |  | No field-specific evidence disposition and governed application-validation decision | Keep known hard constraints; bind any allowed unresolved-field disposition to exact fields and operation, preview and reconciliation | No automatic fix |
| Account combination change | Error |  | Missing ledger/COA coherence, invalid or indeterminate account validation, or confirmed missing combination without exact creation consent and candidate approval | Require the documented existing-account receipt or governed missing-account creation choice; disclose creation in the immutable preview | No |
| InactiveDate supplied | Error |  | Create supplies an inactive date before today from the system clock | Reject before package generation under the agreed UI-based FSCR create policy. This is a local FSCR policy. Do not apply this guard to updates or hardcode a screenshot date | No |


## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| DS.DESIGN | decision | 50 | design_enforcement | passed->DS.GATE;blocked->DS.ISSUES | DS.DEPENDENCIES | stop | After required dependency validation |


<!-- fscr-supported-operations: create, update -->

<!-- fscr-create-fields: AP_DISTRIBUTION_SET::BuName, AP_DISTRIBUTION_SET::Description, AP_DISTRIBUTION_SET::DistributionSetName, AP_DISTRIBUTION_SET::EnterpriseId, AP_DISTRIBUTION_SET::InactiveDate, AP_DISTRIBUTION_SET::TotalPercentDistribution, AP_DISTRIBUTION_SET_LINE::AP_DISTRIBUTION_SET.BuName, AP_DISTRIBUTION_SET_LINE::AP_DISTRIBUTION_SET.DistributionSetName, AP_DISTRIBUTION_SET_LINE::Description, AP_DISTRIBUTION_SET_LINE::DistCcidSegments, AP_DISTRIBUTION_SET_LINE::DistributionSetLineNumber, AP_DISTRIBUTION_SET_LINE::PercentDistribution, AP_DISTRIBUTION_SET_LINE::SOBName, AP_DISTRIBUTION_SET_LINE::Type1099, AP_DISTRIBUTION_SET_LINE::ProjectAccountingContext, AP_DISTRIBUTION_SET_LINE::ExpenditureType, AP_DISTRIBUTION_SET_LINE::AccountDescription, AP_DISTRIBUTION_SET::AttributeCategory, AP_DISTRIBUTION_SET::Attribute1, AP_DISTRIBUTION_SET::Attribute2, AP_DISTRIBUTION_SET::Attribute3, AP_DISTRIBUTION_SET::Attribute4, AP_DISTRIBUTION_SET::Attribute5, AP_DISTRIBUTION_SET::Attribute6, AP_DISTRIBUTION_SET::Attribute7, AP_DISTRIBUTION_SET::Attribute8, AP_DISTRIBUTION_SET::Attribute9, AP_DISTRIBUTION_SET::Attribute10, AP_DISTRIBUTION_SET::Attribute11, AP_DISTRIBUTION_SET::Attribute12, AP_DISTRIBUTION_SET::Attribute13, AP_DISTRIBUTION_SET::Attribute14, AP_DISTRIBUTION_SET::Attribute15, AP_DISTRIBUTION_SET_LINE::AttributeCategory, AP_DISTRIBUTION_SET_LINE::Attribute1, AP_DISTRIBUTION_SET_LINE::Attribute2, AP_DISTRIBUTION_SET_LINE::Attribute3, AP_DISTRIBUTION_SET_LINE::Attribute4, AP_DISTRIBUTION_SET_LINE::Attribute5, AP_DISTRIBUTION_SET_LINE::Attribute6, AP_DISTRIBUTION_SET_LINE::Attribute7, AP_DISTRIBUTION_SET_LINE::Attribute8, AP_DISTRIBUTION_SET_LINE::Attribute9, AP_DISTRIBUTION_SET_LINE::Attribute10, AP_DISTRIBUTION_SET_LINE::Attribute11, AP_DISTRIBUTION_SET_LINE::Attribute12, AP_DISTRIBUTION_SET_LINE::Attribute13, AP_DISTRIBUTION_SET_LINE::Attribute14, AP_DISTRIBUTION_SET_LINE::Attribute15 -->

<!-- fscr-update-fields: AP_DISTRIBUTION_SET::Description, AP_DISTRIBUTION_SET::InactiveDate, AP_DISTRIBUTION_SET::TotalPercentDistribution, AP_DISTRIBUTION_SET_LINE::Description, AP_DISTRIBUTION_SET_LINE::DistCcidSegments, AP_DISTRIBUTION_SET_LINE::PercentDistribution, AP_DISTRIBUTION_SET_LINE::Type1099, AP_DISTRIBUTION_SET_LINE::ProjectAccountingContext, AP_DISTRIBUTION_SET_LINE::ExpenditureType, AP_DISTRIBUTION_SET_LINE::AccountDescription, AP_DISTRIBUTION_SET::AttributeCategory, AP_DISTRIBUTION_SET::Attribute1, AP_DISTRIBUTION_SET::Attribute2, AP_DISTRIBUTION_SET::Attribute3, AP_DISTRIBUTION_SET::Attribute4, AP_DISTRIBUTION_SET::Attribute5, AP_DISTRIBUTION_SET::Attribute6, AP_DISTRIBUTION_SET::Attribute7, AP_DISTRIBUTION_SET::Attribute8, AP_DISTRIBUTION_SET::Attribute9, AP_DISTRIBUTION_SET::Attribute10, AP_DISTRIBUTION_SET::Attribute11, AP_DISTRIBUTION_SET::Attribute12, AP_DISTRIBUTION_SET::Attribute13, AP_DISTRIBUTION_SET::Attribute14, AP_DISTRIBUTION_SET::Attribute15, AP_DISTRIBUTION_SET_LINE::AttributeCategory, AP_DISTRIBUTION_SET_LINE::Attribute1, AP_DISTRIBUTION_SET_LINE::Attribute2, AP_DISTRIBUTION_SET_LINE::Attribute3, AP_DISTRIBUTION_SET_LINE::Attribute4, AP_DISTRIBUTION_SET_LINE::Attribute5, AP_DISTRIBUTION_SET_LINE::Attribute6, AP_DISTRIBUTION_SET_LINE::Attribute7, AP_DISTRIBUTION_SET_LINE::Attribute8, AP_DISTRIBUTION_SET_LINE::Attribute9, AP_DISTRIBUTION_SET_LINE::Attribute10, AP_DISTRIBUTION_SET_LINE::Attribute11, AP_DISTRIBUTION_SET_LINE::Attribute12, AP_DISTRIBUTION_SET_LINE::Attribute13, AP_DISTRIBUTION_SET_LINE::Attribute14, AP_DISTRIBUTION_SET_LINE::Attribute15 -->

## Runtime enforcement

Validate the final state after all operations, grouped by exact owning BU and set name. Count retained children, reject orphan lines, require at least one line, positive integral line numbers, header domain 0/100 and exact decimal aggregate equality without rounding. Compare integral key aliases together for duplicates and existence. Never allow caller flags to disable preservation.

For child-only creates or updates under an existing header, include the matching fresh-baseline header unchanged except blank system audit fields. This is a package dependency, not an invented business change. For new headers require explicit creation and valid children. Uploaded packages must match this closure and may not introduce unrelated values.

The preview and blueprint list preserved non-audit values for each existing update target, derived from the validated current-data export. Requested fields are listed separately; creates have no existing target values to preserve. The per-operation preservation flags also cover unspecified records. Caller-supplied preservation descriptions do not replace baseline values.

ProjectAccountingContext is a normal optional create/update string field. It does not require the unresolved-field override, special warning or extra approval. Unchanged values remain preserved; all ordinary field and owning-set checks still apply.

AttributeCategory and Attribute1 through Attribute15 on headers and lines are supported for create and update. FSM validates configured DFF values during import. Pass each supplied value to FSM without changing its spelling, case or spacing. On update, a field that the requester does not supply keeps its existing value; omission does not clear it. Clear an existing value only when explicitly requested. Report Fusion validation errors without substituting values or retrying automatically. Normal type, identity, preservation, package and candidate-bound import approval rules still apply.

ExpenditureType is an optional create/update string field. Pass the supplied value unchanged without lookup or business-value validation, unresolved-field override, special warning or extra approval. Keep ordinary type, identity, preservation, package and import approval checks. Fusion validates the value during approved import; report rejection without substitution or automatic retry. Omission on update preserves the existing value; clear only when explicitly requested.

AccountDescription is optional nonpersistent context. Pass a supplied string unchanged for create or update, without lookup, business-value validation, unresolved-field override or a persistence-match requirement. Keep ordinary string-type, identity, package, preservation and import approval checks. Do not promise that it changes the UI Combination Description.
