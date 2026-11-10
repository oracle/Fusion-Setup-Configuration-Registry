# Taxpayer-registration evidence


The Customers input `TAXPAYER_REGISTRATION_NUM` maps to
`HZ_IMP_PARTIES_T.TAX_REFERENCE`. In the reviewed 26D source,
`ZX_NEW_SERVICES_PKG.zx_tca_ptp_callback` (lines 3185–3335) merges the nonnull
value into `ZX_PARTY_TAX_PROFILE.REP_REGISTRATION_NUMBER`, keyed by party ID
and `PARTY_TYPE_CODE='THIRD_PARTY'`. It selects the supplied batch, successful
interface rows, I/U action flags and PERSON/ORGANIZATION party types.
Existing matched profiles update the representative number only. Inserted
profiles use SITE_FLAG=N and usage-derived customer/supplier flags. This is
not a `ZX_REGISTRATIONS` row or a site-level tax registration.

The FinTaxConfigPartyImportComposite subscribes to ImportPartyData and
ImportPartyData_FIN. Its mediator invokes processPTPForTCAImportAsync; the XSL
passes the event batch ID. The service wrapper calls the PL/SQL function.
This source mapping does not prove that the event was emitted or the callback
committed for a specific Upload Customers run in the target environment.
The PL/SQL callback returns zero on exceptions. Loader terminal success alone
is therefore insufficient tax-value evidence. Do not automatically retry an
import when this asynchronous result is missing or delayed.

Sources, all under the indexed `FUSIONAPPS_11.13.26.10.0_LINUX.X64` series:

- Tax callback
- Service wrapper
- Event subscription
- Mediator
- Batch mapping

`scripts/customer_tax_review.py:analyze` consumes candidate-bound after-state
identity and ownership evidence plus `ar-customer-tax-evidence-v1`. The envelope
contains candidate_sha256, environment_url, operation_intent,
ownership_evidence_sha256, timezone-qualified captured_at, evidence_reference
and profile_queries. Each query contains party_id, complete and records.
Each record has party_tax_profile_id, party_id, party_type_code,
rep_registration_number, site_flag, customer_flag and supplier_flag. IDs and
numbers are strings; preserve nulls, exact text, duplicates and all profile
types returned for the bound party. Query the actual party ID without filtering
to the expected number or flags. Retain query completeness evidence.

The reviewer selects exactly one THIRD_PARTY profile, preserves other profile
types, rejects numeric coercion and compares the exact supplied value without
trimming or case folding. It reports only row/field/status and counts, never tax
identifiers. Blank input is not a request to clear a value. Even matching
evidence leaves callback completion, before/after effects, request correlation
and overall reconciliation unverified. Missing/duplicate/incomplete evidence
must not supply a false match. Reobserve the same attempt through the governed
readback plan when callback completion is pending.
