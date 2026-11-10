# Manage Payment Codes — Design Enforcement

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: IBY_PAYMENT_CODE::PaymentCodeType, IBY_PAYMENT_CODE::PaymentCode, IBY_PAYMENT_CODE::TerritoryCode, IBY_PAYMENT_CODE::FormatValue, IBY_PAYMENT_CODE::Meaning, IBY_PAYMENT_CODE::StartDate, IBY_PAYMENT_CODE::Description, IBY_PAYMENT_CODE::EndDate, IBY_PAYMENT_CODE::EndDateDsp, IBY_PAYMENT_CODE::Code -->
<!-- fscr-update-fields: IBY_PAYMENT_CODE::TerritoryCode, IBY_PAYMENT_CODE::FormatValue, IBY_PAYMENT_CODE::Meaning, IBY_PAYMENT_CODE::StartDate, IBY_PAYMENT_CODE::Description, IBY_PAYMENT_CODE::EndDate, IBY_PAYMENT_CODE::EndDateDsp -->

Create/update scope is source-backed for the root model. Direct translation operations remain excluded; framework-generated effects require operation-specific qualification. The user declared the reviewed task ora-resource tables as local authority for static Type, length, key and seeded checks. Input Validation owns Type/length checks; this file owns key and seeded restriction rules. Baseline-dependent enforcement still requires verified resolver outputs and complete coverage. These gates must pass before handing facts to Run Book/Data Loader. No direct write or payload action belongs here.

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Identity and existence | Resolve exact root key, baseline and requested business effect |
| 2 | Product restrictions | Respect identity immutability, reserved namespace and seeded-field restrictions |
| 3 | Lifecycle/readiness | Close operation-specific serialization and translation handling before preview |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Root update | Error | find_payment_code_by_key | PaymentCodeType/PaymentCode rename or Code setter changes identity; while-insert keys; SRC-CS-VO, SRC-CS-EO, SRC-CS-EOJAVA | Use the unchanged composite key and source-supported nonkey update fields | No automatic key rewrite |
| SeededFlag Y baseline | Error | find_payment_code_by_key | Changing TerritoryCode, Meaning or Description; SRC-CS-EOJAVA 474–488 | Preserve these values; do not generalize restriction to other fields without evidence | No |
| Create PaymentCode | Error | | Case-insensitive ORA_ prefix reserved except application seed CreatedBy; SRC-CS-EO | Use customer namespace; do not spoof framework CreatedBy | Correct business code after review |
| Unsupported history/flag input | Error | | Audit or SeededFlag supplied as implementor-controlled operation; SRC-CS-VO, SRC-CS-TLVO | Retain read-only dispositions and structural columns; use empty cells on create and preserved export cells on update. Documented readXML ignore behavior applies only to non-updateable service attributes; SRC-INTERNAL-FSM-FAQ | No audit mutation |
| Direct translation request or root operation with framework translation effects | Error | resolve_payment_code_language | Direct child authoring is outside declared ownership. Block a root operation if exact parent-child identity, preserved package inputs, installed-language inventory for create, applicable session-language effects or expected child reconciliation is unqualified; SRC-CS-TLEO, SRC-CS-TLASSOC, SRC-CS-AMIMPL, SRC-CS-APPLCORE-TL-CREATE, SRC-CS-APPLCORE-TL-UPDATE | Reject direct child inputs. Preserve exported child input rows. Before preview disclose expected generated keys and qualify the exact expected propagation and reconciliation contract. Verify actual effects after import with a fresh export. Country-only preservation evidence does not qualify Name/Description propagation | No inferred direct ownership or implementor-authored language rewrite; qualified framework propagation remains applicable |
| Static Type/length/key/seeded evaluation | Error | | A check uses rules outside the user-declared reviewed task tables, or baseline-dependent key/seeded enforcement lacks verified find_payment_code_by_key outputs | Use the owning validation/design tables and verified baseline facts; the local rule authority does not establish current record values or completeness | No inferred baseline or expanded local authority |
| Root create/update serialization | Error | find_payment_code_by_key | Candidate changes template shape, omits an explicit updateable required value, supplies inconsistent date/identity transients, or treats audit/flag fields as writable | Apply Input Validation and Standard Defaults to the exact template and fresh baseline: explicit business values, create-only Code pairing, preserved update Code, source-derived sentinel/finite date display, empty create history/flag cells, preserved update history/flag cells; metadata-bound converter and task readXML are the source-backed evaluator chain. Translation business serialization remains a separate blocker; SRC-FSM-PACKAGE, SRC-CS-AMIMPL, SRC-CS-FSM-MIGRATOR, SRC-CS-FSCORE-CSVXML, SRC-INTERNAL-FSM-FAQ | No readiness bypass |
| Source-backed field maxima | Error | | Any authored operation value exceeds its input-resource entity/field bound; SRC-CS-EO, SRC-CS-TLEO | Report field, actual size, maximum and characters; request corrected business text | No truncation or silent rewrite |
| End-date request | Error | | EndDate before StartDate, or request represented as physical delete; SRC-CS-EO, SRC-CS-EOJAVA | Preserve effective-dating semantics; CSV physical deletion remains unproven | No invented deletion |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| find_payment_code_by_key | Existence/update/seeded checks | Exact identity, complete root baseline and SeededFlag from the validated fresh full-task current-data export; compare only supported requested business fields and retain snapshot/task/user provenance | ora_reference_lookups.md |
| resolve_payment_code_language | Qualified root create or translated-root update; never direct child authoring | Complete installed I/B language inventory for root create; active membership kept separately. SourceLang comes from execution-session behavior, not this lookup. Stop if the applicable generated or propagated effects cannot be qualified | ora_reference_lookups.md |

An unresolved update field is not automatically a product prohibition. A governed application-validation choice is available only after exact entity-operation ownership is evidenced and the exact operation/fields/warning are bound to a preview. It cannot bypass keys, audits, malformed packages, missing identity, proven-invalid values, unsupported operations, or mutation authority. Independent translation ownership remains unqualified and outside this task scope; framework side effects do not grant it. Sources: approved generation prompt and repository Run Book/Data Loader governance.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MPC_DESIGN | step | 50 | design_enforcement | create->MPC_CREATE_GATE;update->MPC_UPDATE_GATE;blocked->MPC_HANDLE_ISSUES | MPC_DEFAULTS | stop | Before preview; retain source-supported operations and explicit blockers |
