# Destination references and Expense Type Account

Use the baseline only to resolve existing identities, verify exact CSV schema,
and preserve values. Existing template/type usage never defines the full valid
category, business-unit, or ledger population.

The workflow selects these read-only operations through
`core/fusion-api/rest-api-client/scripts/fusion_rest_client.py`, with the exact
destination properties, core OAuth, and `REST-Framework-Version: 9`:

1. GET `/fscmRestApi/resources/11.13.18.05/standardLookups/EXM_EXPENSE_TYPE_CATEGORY/child/lookupCodes`.
   Read LookupCode, Meaning, EnabledFlag, StartDateActive and EndDateActive.
   Retrieve all pages until hasMore=false. Accept only enabled, currently
   effective codes. Effective dates must be null or strict, valid YYYY-MM-DD
   strings; malformed types, malformed dates and reversed intervals make the
   evidence unverified, even for disabled rows. Both boundary days are inclusive.
   Resolve a supplied code exactly or a business label by one
   case-insensitive Meaning match. Do not invent aliases or infer codes from
   expense type names. A valid unused category is accepted.
2. GET `/fscmRestApi/resources/11.13.18.05/finBusinessUnitsLOV`.
   Resolve one exact active BusinessUnitName with BusinessUnitId. An exact-name
   filter is permitted using core's escaped query contract; retrieve all pages
   of that filtered result. The BU need not occur in the task export.
3. When account_number is supplied, take PrimaryLedgerId from that BU and GET
   `/fscmRestApi/resources/11.13.18.05/ledgersLOV` filtered by that LedgerId.
   Require one LedgerId match and its Name. Serialize Name as LedgerName and
   the caller's account number as Segment1, preserving leading zeros. Never ask
   for a ledger name, select the first ledger, or use another type's ledger.
   Account value-set validation remains with the source-backed Fusion import;
   a ledger lookup alone does not certify account validity.

Before building, retain core-captured results as `--reference-evidence FILE`.
The JSON object contains categories, business_units and, when needed, ledgers.
Each batch has environment (exact normalized design environment),
baseline_sha256, captured_at (offset-aware ISO time within 24 hours), path
(the exact collection path above), http_status=200, complete=true and items.
Set complete only after verified pagination; request identity and raw responses
belong in the private project evidence. The helper `scripts/reference_values.py`
only evaluates captured evidence and makes no network calls.

Zero matches is a reference issue; multiple matches is ambiguity. An unavailable
endpoint, 401/403, transport failure, malformed response or incomplete pages
is unverified evidence, never proof that a business value is invalid. Stop
before preview, preserve diagnostics, and use core's bounded auth recovery.
No lookup grants import approval. A changed baseline requires new evidence.

Itemization references are candidate-local relationship identities: validate
against final type rows, including types created in the same candidate. This
is not an external reference domain and must not be replaced with an unrelated
LOV. Project mappings, tax, cards and policies retain their current scope gates.

## Reviewed evidence

- Category binding: `fusionapps/fin/components/payables/exm/setup/shared/model/src/oracle/apps/financials/expenses/setup/shared/model/entity/ExpenseTypeEO.xml`,
  lookup expression EXM_EXPENSE_TYPE_CATEGORY at line 77; Segment1 at 1152–1154.
- Import mapping: the sibling `expenseTemplateService/view/ExpenseTypeVO.xml`,
  Segment1 at 221–225; `applicationModule/ExpenseTemplateServiceAMImpl.java`,
  LedgerName/BindByLedgerName at 396–415 and 656–675, assigning ChartOfAccountsId.
- CodeSearch series: FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64. Development-source
  evidence must be qualified with the selected destination release; it is not
  by itself a claim of successful 26.10 import.
- [Lookup codes, Oracle 26D](https://docs.oracle.com/en/cloud/saas/applications-common/26d/farca/op-http-servername-fscmrestapi-resources-11.13.18.05-standardlookups-lookuptype-child-lookupcodes-get.html).
- [Financials BU LOV, Oracle 26C](https://docs.oracle.com/en/cloud/saas/financials/26c/farfa/op-finbusinessunitslov-get.html).
  The corresponding 26D short operation URL was unavailable on 2026-10-21;
  the BU and ledger response attributes were checked on the selected test pod.

These are source and read-only resolver contracts. Persisted create/update
behavior must still be verified through the governed Data Loader workflow.
