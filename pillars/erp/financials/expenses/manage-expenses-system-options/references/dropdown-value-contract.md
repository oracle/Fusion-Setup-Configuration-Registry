# System Options dropdown values

The five fixed option dropdowns below use source-defined lookup code/meaning
pairs, not values observed on configured Business Units. `observed_codes` is
not an allowed-value source. Every listed choice is supported for sparse
create and update, even if its code has never occurred in the task export.

| Field | Lookup type | Labels and ValueCode mappings |
| --- | --- | --- |
| Enable Attachments | EXM_ENABLE_ATTACHMENTS | Both Header and Lines=B; Header Only=H; Lines required=L; No=N |
| Enable Expense Location Level | ORA_EXM_ENABLE_LOCATION_LEVELS | All Locations=ORA_EXM_ALL; Country=ORA_EXM_ONE; Country and State or Province=ORA_EXM_TWO |
| Enable Payment Notification to Employee | EXM_ENABLE_PMT_NOTIFICATION | Card issuer and employee are paid=BOTH; Card issuer is paid=CARDPROVIDER; Employee is paid=EMPLOYEE; No=N |
| Expense Report Audit Approval | EXM_ENABLE_AUDIT_APPROVAL | After manager approval=AFTER_MGR_APPROVAL; In parallel with manager approval=BEFORE_MGR_APPROVAL |
| Pay Expense Reports Through | EXM_ENABLE_REIMB_OPTION | Payables=ORACLE_FUSION_PAYABLES; Third Party=THIRD_PARTY_APPLICATION |

The last field remains global-only. This changes supported value mappings,
not field scope, inheritance/removal, dynamic references or live-import gates.
Printable Expense Report Format is a dynamic report-template reference; its
existing unresolved mapping is not promoted to a fixed code by this table.

## Source evidence

CodeSearch MCP, maintainer-reviewed source snapshot, reviewed 2026-10-21:

- `fusionapps/fin/components/payables/exm/setup/options/model/src/oracle/apps/financials/expenses/setup/options/uiModel/view/SetupOptionMinus1VO.xml`:
  option-to-LOV selection at 48 and 853; lookup types at 269 (payment), 318
  (attachments), 344 (audit), 384 (reimbursement), and 444 (location).
  Sibling SetupOptionAttachmentVO, SetupOptionPmtNotificationVO,
  SetupOptionAuditApprovalVO and SetupOptionLocationVO bind the same types.
- `fusionapps/fin/exm/db/data/StandardLookupTypeSD.xml`: attachment L rowkey
  at 5965 and Meaning at 5968; audit AFTER/BEFORE rowkeys 6016/6032;
  reimbursement ORACLE_FUSION_PAYABLES/THIRD_PARTY_APPLICATION 6660/6676;
  location ALL/ONE/TWO 16721/16737/16753, Country and State or Province at 16756.
- `fusionapps/fin/exm/noship/cdrautoapply/db/data/StandardLookupTypeSD.xml`:
  attachment B/H/N at 3920/3936/3952; payment BOTH/CARDPROVIDER/EMPLOYEE/N
  at 4251/4267/4283/4299. The UI-bound lookup type, labels and exact code
  identities establish the mapping; unrelated setup-row usage does not.

These are source-backed mappings. Development-series source does not prove
successful persistence on a specific release or grant import approval.
