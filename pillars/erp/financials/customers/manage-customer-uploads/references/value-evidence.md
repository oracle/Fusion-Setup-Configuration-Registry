# Selected persisted-value evidence


`scripts/customer_value_review.py:analyze` is an offline comparison function.
Pass the candidate ZIP bytes, declared create/update/mixed intent, environment,
identity evidence, after-phase ownership evidence and value evidence. It
recomputes identity/ownership review and checks candidate, environment, intent,
ownership fingerprint, capture ordering and query scope before comparing values.
It does not perform a Fusion call, approve an import or complete the Journey.

Value evidence version `ar-customer-value-evidence-v1` contains
`candidate_sha256`, `environment_url`, `operation_intent`,
`ownership_evidence_sha256`, timezone-qualified `captured_at`,
`evidence_reference` and `queries`. Each query contains `entity`,
`owner_table_id`, boolean `complete` and `records`. Record keys are the exact
persisted column names in the helper's `FIELDS` mapping; values are strings or
explicit null. Owner IDs must occur in the bound ownership evidence. Retain all
rows, duplicates and missing/null fields. Do not select the first result or
change a lookup's scope to expected parents/values.

The comparator covers 75 nonblank input fields: the original 15 party number/name;
account number/description/established date; party-site number/name/identifying
flag; address line 1/city/state/postal code/country; and site-use code/primary
flag fields, plus account ATTRIBUTE_CATEGORY and ATTRIBUTE1 through ATTRIBUTE30.
Six further comparisons are ACCOUNT_TYPE to account CUSTOMER_TYPE,
CUSTOMER_CLASS to account CUSTOMER_CLASS_CODE, MAIL_STOP to party-site MAILSTOP,
ACCT_SITE_LANGUAGE and TRANSLATED_CUSTOMER_NAME to their account-site columns,
and SITE_LOCATION to site-use LOCATION. These are stored code/value comparisons;
they do not resolve display names, lookup meanings or update mutability.
The remaining 20 location inputs are also compared: address lines 2–4,
floor/building, province/county, phonetic address, postal extension, both
descriptions, sales-tax geocode/city-limits flag, house type, timezone code and
address elements 1–5. FLOOR_NUMBER maps to FLOOR_NUMBER;
ADDRESS_DESCRIPTION and ADDR_SHORT_DESCRIPTION map to DESCRIPTION and
SHORT_DESCRIPTION. All 20 columns were verified as VARCHAR2 in the target 26D
FSCM schema; preserve leading zeros and compare strings exactly. Country-specific
address validation, geography standardization, timezone validity and loader
normalization remain product/business validations, not locally invented rules.
Three additional party comparisons map DUNS_NUMBER to DUNS_NUMBER_C,
TAXPAYER_ID_NUM to JGZZ_FISCAL_CODE, and GSA_INDICATOR_FLAG to its same-name
HZ_PARTIES column. All three were verified as VARCHAR2 in the target 26D schema.
Do not parse these identifiers as numbers or use site-use GSA/tax columns instead.
The 26D HZ_CIMP_PARTIES_PKG insert/update paths persist these values on parties
and organization profiles; null incoming values preserve existing values on
update. This comparator checks only the party projection. Organization-profile
history, effective-row selection, blank/sentinel behavior and actual loader
effects still require separate reconciliation. TAXPAYER_REGISTRATION_NUM is
distinct from taxpayer ID and uses the separate
[tax-profile comparator](tax-evidence.md); live callback/persistence remains unverified. See
[the downstream source findings](downstream-party-and-bill-to.md).
DFF checks compare exact stored account columns, preserving leading zeros,
Unicode, spaces and segment positions. They do not validate context definitions,
segment value sets or blank-clear/default/update semantics. A blank context is
not silently filled in. The description comparison uses ACCOUNT_NAME; the date uses full ISO
seconds after strict YYYY/MM/DD calendar validation. Other text is compared
exactly, including leading zeros, spaces and Unicode. Blank input does not imply
clear/no-change/default semantics; those require a separate effect contract.

`SELECTED_VALUES_MATCH` means only those selected supplied values match.
Other nonblank fields remain visible as `FIELD_NOT_COVERED` or
`SEPARATE_IDENTITY_REVIEW`. Incomplete ownership, missing/incomplete queries,
zero or multiple result rows, missing values and mismatches cannot pass selected
comparison. Per-row findings retain matches alongside failures, without echoing
customer values. Every result keeps full reconciliation, authorization and
Journey completion false.

Mapping evidence is the reviewed 26D Customer Interface package lines
13297–13714 and FSCM column/query validation; this is not proof of downstream
mutability or a successful live import. Source fingerprints remain in
`assets/customer-reconciliation-matrix.json`. Profile, requested set-code
resolution, receipt effects, DFF business semantics, defaults, before/after operation effects and
the rest of the Customers worksheet remain separate obligations.

File placement and test discovery are provisional pending the separately agreed
artifact-ownership contracts. This does not finalize customer/`noship` packaging.
