# Customers Input Validation


Source basis: target-delivered template and source register in ../references/source-contract.md.

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Reviewable business input | ar-customers-input-v1; operation create, update or mixed; provenance explicit-business-input or proposed-business-input; Customers rows | Stop normalization | Preserve supplied input. When the user has requested design or test-data generation, mark generated records proposed-business-input and disclose their origin and every proposed value in the exact-candidate preview; template example rows are not input | Every offline preview |  |
| Template-required identifiers and values | Fields marked required=true in ../assets/customer-contract.json | Return row and field error without echoing values | Supply the requested identifiers and business values | Each row |  |
| Account Address Set | ACCT_ADDRESS_SET_CODE | Reject blank before preview or acceptance; do not guess Common | Supply the intended configured set. Direct 26D CSV loading requires a value, corroborated by table nullability and controlled interface rejection | Every row, including update/mixed intent |  |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Worksheet boundary | Reject Contacts, Reference Accounts, Customer Bank Accounts, unknown sections/fields, and extra ZIP members as a whole request | All inputs |  |
| Positional contract | Emit exactly 87 ordered business fields and END; ArUpdCustomers.csv only, headerless UTF-8 without BOM; preserve blanks, leading zeros, Unicode and quoting | Package preview |  |
| Known constraints | Enforce template-required fields and nonconflicting documented lengths; supplied GSA, identifying-address, site-use-primary and payment-primary flags must be Y or N; supplied account date must be a valid YYYY/MM/DD | Values supplied |  |
| Input preservation | Accept strings/null; reject numeric/boolean coercion, duplicate JSON keys, unknown/system-owned fields and NUL; no trimming, guessed defaults, truncation or code translation | Normalization |  |
| Proposed input | Validate proposed rows normally; preserve input provenance/hash in finalData and require the normal explicit approval of the proposed data and load. Do not relabel a proposal as user-supplied or accepted input, reuse template examples automatically, infer business intent, or waive failed hard checks | User-authorized design or test-data preparation |  |
| Parent consistency | Allow repeated customers/accounts for multiple sites; conflicting nonblank party/account definitions under the same exact source/name-number key require correction | Repeated parent input |  |
| Operation intent | Create/update/mixed identifies requested effects, not blanket field mutability; no creation-only assumption or automatic existing-target rejection | Every preview |  |
| Business-rule gaps | Disclose remaining length/domain gaps in the contract; retain unresolved evidence and unchanged values; user acceptance cannot override known-invalid data | Named gap applies |  |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| ARCU.INPUT | step | 10 | validate_input | valid->ARCU.DEFAULTS;invalid->ARCU.ERROR | none | stop | Before offline preview or live planning |
