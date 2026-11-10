# Meals encoding, identity and evidence boundaries

The executable scope and user fields are defined in
[ordinary execution](ordinary-meals-execution.md),
[the fixed intake schema](intake-fields.json) and
[the runtime contract](fsm-runtime-contract.json). The full 19-entity,
634-column export schema remains necessary for package validation and preservation;
it does not enable authoring other categories. Historical broader research and
qualification campaigns remain in Git/project history, outside the runtime package.

## Field encoding and managed values

[Boolean evidence](boolean-encoding-evidence.json) retains the nine Meals
field-specific mappings, including five user inputs and four hidden/managed
flags. Use the explicit Yes-to-Y and No-to-N mapping for each listed field. Do not infer a mapping for another field from a Flag suffix.

The intake contract maps the two enforcement labels to UPPER and VIOLATION.
[Date evidence](date-encoding-evidence.json) binds the observed Meals StartDate
representation YYYY/MM/DD to its original candidate/reconciliation/acceptance
hashes, retaining the original batch's mismatch classification. It establishes
encoding, not date changes, EndDate support or overlap behavior. The batch
extension uses the same date-only representation for EndDate as an explicitly
user-authorized engineering contract, not a new observed result. Its limits are
recorded in accepted-meals-profile.json#batch_extension.

SINGLE mode and DRAFT status are fixed consumer-owned values. Role/location
controls are disabled. Child currency/type stay blank. Hidden include flags
submitted blank exported N in the accepted CREATE; updates preserve actual N.
Generated audit values and that raw difference require explicit reconciliation.
Blank workbook cells preserve existing values and never request clearing or defaults.

## Resulting-state validation and identity

[Pinned source facts](product-contract-evidence.json) retain the Meals EO/service
identities, declared keys and nonnegative/ordered tolerance validators. Amounts
and tolerances use finite decimal arithmetic without rounding or float conversion.
Required values, control applicability, and inactive-value preservation are
validated against every complete resulting policy and its rates, including omitted baseline rows.

The parent uses exact PolicyName. The rate retains its full portable identity,
including hidden nullable currency, geography, role, end-date, type and zone
components. EndDate may now be supplied on create; the other hidden components
remain empty under the supported profile. Removing their
workbook inputs does not remove them from the FSM key. Reject ambiguous and
case-only matches. Keys, date, currency, status and determinants are immutable.

Batch admission preserves the full rate key and the alternate key excluding Start Date, and conservatively requires nonoverlapping inclusive effective periods, including retained rates. No existing rate is automatically closed or deleted. Multi-rate and EndDate generation remain pending live qualification. Local validation is not target acceptance.

## Qualification boundaries

Historical review does not establish target-release equivalence. The shipped
[profile evidence](accepted-meals-profile.json) preserves accepted basic
CREATE/UPDATE hashes and historical observation release. Private target identity
is omitted; every selected target retains the live-reconciliation warning. Runtime has no
release allowlist; admission requires the exact task schema and release provenance.
Other environments or releases need
fresh bound evidence and live reconciliation, not edits to the historical target.
Schema drift requires reviewed contract extension; no live equivalence is inferred. Cleanup does
not promote additional live combinations. Retain existing expanded-setting
qualification notices and per-run native approval/reconciliation requirements.

Keep baseline descriptor/nonCSV bytes exact. [Metadata handling](metadata-contract.md)
retains strict sequence drift as a finding; no arbitrary ordering equivalence,
package-wide atomicity, guaranteed rollback or cleanup is established.
