# Customers source contract and readiness


The initial task covers all 87 input columns of the **Customers worksheet** in the simplified Upload Customers template. Contacts, Reference Accounts and Customer Bank Accounts are deferred. A worksheet boundary is not a creation-only rule. Do not substitute the larger CustomerImportTemplate flow.

## Evidence

| Source | Supports | Limit |
|---|---|---|
| Target-delivered 26D UploadCustomersTemplate; SHA-256 8869f28164ab9d7fee2bfd52ea47b35c28b5901293d04af5ed8576b9eef6e261 | Ordered worksheet labels/comments and Module1.GenCSV mechanics: ArUpdCustomers.csv, headerless 87 business values plus END, UTF-8 without BOM | VBA inspected without executing macros; no current loader run proved |
| [Oracle Upload Customers](https://docs.oracle.com/en/cloud/saas/financials/26b/oefbf/uploadcustomers-3123.html) | Simplified flow identity, published template/control reference, staging tables and UCM account | Published 26B control file does not prove deployed 26D behavior |
| Developer-supplied ADE ArUpdCustomers.ctl; SHA-256 c85f853f709c7adaec364476049c74f21f00ac5fc5bfdf97b6e2a96c89a548e4 | All 87 ordered inputs; source-reference fallbacks, generated party-site reference and date expressions | Supplied in response to the 26D source request; exact ADE label not supplied. Identical to the public control comparison copy. No live loader execution established |
| [Oracle upload guidelines](https://docs.oracle.com/en/cloud/saas/financials/26c/facsf/guidelines-for-uploading-customer-data-using-a-simplified.html) | Related setup, original column order and template input conventions | A documented profile update convention is not blanket field mutability |
| 26D AR customer interface source | Entity mappings at 13297–13714, account DFFs, profile default at 14571–14604, existing-profile I-to-U switch at 14615–14629, receipt-method default at 14646–14684 | Indexed source does not establish exact tenant patch or an authorized lookup endpoint |
| 26D CustomerUpload source | Five-argument ESSCREATE contract and request correlation | ESSCREATE is a batch/job mode, not a guarantee that existing business records remain unchanged |
| Developer deployment readback | Published customers registration and full adapter configuration were compared successfully in the selected test environment | Environment receipt remains outside this portable skill; each live run must re-resolve its actual registration and privileges |

## Operation and reconciliation ownership

The [87-field reconciliation matrix](../assets/customer-reconciliation-matrix.json) records reviewed input-to-interface mappings and source hashes. Every field still requires persisted-value verification; a mapped interface field is not a passed reconciliation check. `PAYMENT_METHOD_START_DATE` is generated staging data, not an additional worksheet input. The supplied ADE control derives it from account established date with a 1900/01/01 fallback. Record that as an expected loader effect, never an input value silently filled by the skill. The supplied file closes the control-content/layout gap; deployed behavior remains a live-test obligation.

Requested create/update/mixed intent is recorded by the offline tool. The interface has no generic per-row operation flag in these 87 fields. Actual effects depend on existing parties, accounts, sites, profiles and source references. Before a live run, complete the source-key matching contract, resolve ambiguous or conflicting existing targets, and preview actual expected effects. A valid loader update may be unintended. Do not introduce a blanket existing-customer rejection, and do not promise every field supports an update.

Reconcile requested party/account identities and relationships, site/location/site-use identities, account profile assignment, supplied receipt-method assignment and every supplied DFF value. Distinguish requested blank from product-owned default and observed canonicalization. Preserve the before/after state for updates. Select the supported central API collection and [business-outcome review](business-outcome-reconciliation.md) for the actual candidate. The supplied-evidence comparators are additional review tools; Publisher/SQL is developer-only and is never an implementor prerequisite. Requested unreadable values or an unqualified operation composition remain explicit review gaps, not successful reconciliation.

Track Data Loader run/dataset/request, interface LOAD_REQUEST_ID, scoped product UPLOAD_REQUEST_ID and BATCH_ID separately. AR_UPD_CUSTOMERS and linked AR_UPD_ERROR_DETAILS/AR_UPD_CUST_ERRORS support row diagnostics, not proof that every requested persisted value is correct. PARTIAL is not full success. Staging purge is not rollback of customer data.

The receipt-method mapping at source lines 14646–14684 propagates `CUST_SITE_ORIG_SYS_REF` and conditionally its source code. Lines 486–515 validate the site's active **BILL_TO** use; lines 10127–10210 insert `RA_CUST_RECEIPT_METHODS` using the resolved account, receipt method and optional BILL_TO site use with matching set. Reconcile the actual assignment scope, ownership, method, primary flag and dates. The INSERT truncates assignment dates and writes **negative BATCH_ID** to its `REQUEST_ID`; that marker is not the product ESS ID. Lines 629–720 validate overlapping same-method assignments separately at account and site level (T1/T2). Do not infer in-place receipt-assignment updates or harmless replay. These source expectations still require live verification, including the no-site-reference path where supported.

Lines 16408–16442 describe first-submission CREATE mode grouping by party reference into `FILE_RECORD_NUM` for HZ all-or-nothing processing within that party. This is not whole-batch atomicity and does not prove rollback of HZ objects when a later AR profile or payment-method stage fails. Test a failure among rows sharing one party separately from a failure across distinct parties. Verify each stage and persisted entity before planning recovery. Product RESUBMIT mode (16471 onward) is a distinct corrected-batch workflow; it does not authorize automatic retry of a Data Loader initiation request.

## Current status

Offline package tooling, known input checks, assisted existing-target evaluation and central handoff/readback contracts are implemented. The compiled graph is plannable; actual candidate evaluation and live qualification remain required. The former development checkout contained a central FBDI no-reinitiation extension. It is excluded from the task-only revision. The task instead delegates to the existing core approval/recovery workflow and obtains exact attempt evidence through task-selected core REST GETs; see [governed read routes](governed-read-routes.md). This skill implements no authentication or HTTP transport, direct ESS/UCM submission, or automatic import retry.

Eligible named business-rule uncertainties are separate from those hard gates. The remaining city-domain gap may be explicitly accepted for loader validation against exact preview bytes/context; evidence stays unresolved. Confirmed byte/character limits are hard checks. The acceptance helper never grants execution authority or authenticates an actor.

Controlled 26D direct-CSV testing closed the blank address-set uncertainty:
AR_UPD_CUSTOMERS.ACCT_ADDRESS_SET_CODE is NOT NULL, and a candidate preserving
the blank failed during SQL*Loader insertion with ORA-01400 before product loading.
The error log did not expose the column name; attribution combines the controlled
input difference, table nullability and template required marker. Require an
explicit set for this direct import route, including update/mixed input, and do
not offer AR-SET-REQUIRED as an override. This does not assert how spreadsheet
macros or other releases default values. Historical previews retain their original
contract and are not renewed under this changed contract.

Separate 26D scoped observations found the literal city-limit value `1` preserved
in both staging and the location, and a 1500-character ASCII address description
rejected by the interface. The reviewed CHAR(1000) control and that rejection
establish a 1000-character ceiling for ADDRESS_DESCRIPTION. A later controlled
1000-character/3000-byte rejection and the source-defined SQL*Loader semantics
resolved its byte limit. Enforce the [reviewed UTF-8 input byte ceilings](control-byte-limits.md)
independently of business character limits; do not offer AR-ADDRESS-LENGTH as an
uncertainty override or truncate values. The observations do not define every
city-limit domain value.

The target template documents PARTY_SITE_NUMBER as VARCHAR2(30), and reviewed
26D final HZ_PARTY_SITES metadata also limits it to 30 characters. AR_UPD_CUSTOMERS
permits 230 characters in staging; that wider staging capacity is not a supported
business-input limit. Enforce 30 characters for all candidate intents and remove
AR-SITE-LENGTH from eligible overrides. The source transfers PARTY_SITE_NUMBER
unchanged into HZ_IMP_PARTYSITES_T at lines 13345–13380. This metadata was a
developer qualification check, not a SQL prerequisite for implementors. Historical
previews retain their earlier contract and cannot authorize a new attempt under
these resolved rules.
