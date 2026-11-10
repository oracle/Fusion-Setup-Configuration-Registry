# Synthetic AVS fixture provenance

These four masked scenarios originated in the standalone generator. They are
synthetic validation seeds, not live captures or provider specifications.
On 2026-10-06 Pacific, they were reconciled against the reviewed source identifiers
and line references in `references/oracle-avs-payloads.md` (relative to this engine):
AccountSettings was renamed to AccountOption; CountryCode was supplied from each
scenario's existing APPLICABLE_COUNTRIES value after BankAccountNumberElectronic;
empty OwnerTaxId was inserted before PrimaryFlag to model the TEMP view. Account,
owner, scenario IDs and other values were retained. These are explicit source-shape
corrections, not evidence of a deployed change or working provider integration.
Original bytes/failure evidence remain in the development project's synthetic-avs-v1
run; do not replace historical test evidence with corrected fixtures.

The empty OwnerTaxId deliberately does not assert that p_tax_id populates the view.
Tests must exercise both main/TEMP contracts for features that depend on their differences.
