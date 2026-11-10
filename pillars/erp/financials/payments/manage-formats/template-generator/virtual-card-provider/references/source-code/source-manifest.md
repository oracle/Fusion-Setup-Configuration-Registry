# Oracle Virtual Card Source Manifest

This manifest records the Oracle implementation evidence used to maintain the bundled virtual-card contracts. The bundled extracts are the local contract evidence for template generation. Source names and revisions below record provenance only; they are not customer execution steps.

## Retrieval Baseline

- Retrieved: 2026-08-20
- Local evidence: [outbound-contract-source.md](outbound-contract-source.md), [inbound-contract-source.md](inbound-contract-source.md), and [contract-elements.json](contract-elements.json)

| Profile | Source path | Revision observed |
| --- | --- | --- |
| Outbound view assembly | `fusionapps/fin/components/payables/iby/fundsDisbursement/payments/dbSchema/database/fusionDB/FUSION/IBY_XML_FD_PMT_1_0_V.view` | `/st_fusionapps_pt-v2mibfphdev/13`, 2024-10-01 |
| Outbound virtual-card constructors | `fusionapps/fin/iby/db/plsql/iby_fd_extract_gen_pvt.pkb` | `/st_fusionapps_pt-v2mibfphdev/62`, 2026-08-11 |
| Acknowledgment parser | `fusionapps/fin/components/payables/iby/sharedSetup/formats/publicModel/src/oracle/apps/financials/payments/sharedSetup/formats/publicModel/util/ack/FDBatchAckParser.java` | `/st_fusionapps_pt-v2mibfphdev/6`, 2025-09-29 |
| Payment-response parser | `fusionapps/fin/components/financialsEss/iby/shared/runFormat/ess/src/oracle/apps/financials/payments/shared/runFormat/ess/program/FDAckProcessing.java` | `/st_fusionapps_pt-v2mibfphdev/44`, 2026-06-30 |
| Reconciliation parser | `fusionapps/fin/components/financialsEss/iby/shared/commonUtil/ess/src/oracle/apps/financials/payments/shared/util/ess/program/common/util/VirtualCardPaymentReconciliation.java` | `/st_fusionapps_pt-v2mibfphdev/4`, 2026-03-01 |

## Use in FSCR

Use the bundled contract references during generation. No Oracle internal source browser or repository access is required or requested in the customer workflow.

If a provider requirement or the target environment conflicts with a bundled contract, record the affected field, observed evidence and unresolved mapping. Request the applicable supported contract or an updated skill package. Continue only within the existing candidate-generation and handoff rules; do not infer that an unverified mapping is deployable.
