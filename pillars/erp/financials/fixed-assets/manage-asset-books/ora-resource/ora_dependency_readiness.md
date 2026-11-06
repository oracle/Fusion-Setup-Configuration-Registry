# Dependency Readiness

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Import contract | Confirm the current CSV headers and structural metadata. |
| 2 | Automatic input recovery | Reprocess the complete current input set and eligible current-project artifacts before declaring a business requirement missing. |
| 3 | Asset accounting foundation | Resolve the required ledger, calendar, account, convention, and reference-data dependencies. |
| 4 | Tax relationship | For a Tax book, resolve the associated Corporate book. |
| 5 | Asset book | Confirm the existence state and prepare the proposal. |
| 6 | Execution approval | Use the parent/Data Loader approval for the exact reviewed immutable ZIP and target. Do not request a duplicate approval. |
| 7 | Parent handoff | After acceptance, report `accepted — pending parent verification`; the Fixed Assets parent owns monitoring and fresh read-back. |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| FSM_CONTRACT | Current task CSV headers and structural metadata XML | Yes | FSM import or update | Verify | Fresh header-only target export | resolve_fsm_asset_book_contract | Establishes CSV members, headers, and column structure before first import; it is not a source of configuration values or defaults | Export and inspect only the structural contract | CSV files; XML files; headers; required/defaultable columns |
| INPUT_RECOVERY | Current request, provided inputs, and current-project artifacts | Yes | Every request before a missing-input response | Lookup | Current request inputs, provided inputs, and refreshable project artifacts | resolve_asset_book_dependencies | Avoids asking users to restate visible or previously supplied business requirements while preventing stale evidence reuse | Reprocess current inputs first; prior artifacts are candidates that require current-target reconciliation | Normalized business values; source citations; refreshed candidate evidence; unresolved source gaps |
| ASSET_BOOK_FOUNDATION | Ledger, depreciation calendar, current period and immediately preceding period, accounts, conventions, and all eight selected reference-data-set assignments | Yes | Every request | Verify | Current input recovery plus supported read-only metadata | resolve_asset_book_dependencies | Books depend on valid accounting foundations and internal Initial Date depends on the preceding period start date | Resolve calendar periods and all technical assignments automatically. Do not ask the user for technical identifiers or generate a partial package. | Codes/identifiers; active/effective state; compatibility result; Reference Data Set assignment for every field; preceding-period start date; resolved Initial Date |
| LEDGER_BOOK_ACCOUNTS | Ledger COA structure, optional supplied Account Defaults, and book-level retirement/deferred accounts | Yes | Every request | Verify | Selected-ledger GL/COA read-only evidence for derived accounts, structural import-contract metadata, and, only when necessary, user-provided accounting-policy mapping | resolve_ledger_book_accounts | The selected ledger identifies the COA format and Natural Account values required by derived book controls | Preserve supplied Account Defaults under the supplied-input rule in ora_reference_lookups.md; no full-combination search or existence prerequisite. When omitted, derive one complete valid Account Defaults combination. Resolve one enabled, effective, non-summary Natural Account for each other required account purpose directly from the selected ledger; do not use export rows | Supplied or derived Account Defaults and its input/derivation source; valid Natural Account; NBV, proceeds, removal, and deferred-depreciation accounts |
| CORPORATE_BOOK | Associated Corporate book | Yes | Book class is Tax | Verify | Supported read-only target lookup | resolve_associated_corporate_book | Tax books must associate to a Corporate book | Supply a valid existing Corporate book | Corporate book code and compatible ledger evidence |
| ASSET_BOOK_EXISTENCE | Existing target book classification | Yes | Before create or update | Lookup | BOSS Asset Books evidence; when that route is unavailable, a user-authorized task-level setup-data export restricted to exact requested Asset Book Code matching | resolve_asset_book_existence | Prevents duplicate setup data and uncontrolled updates | Review identical/different classification before proceeding; never use exported rows for defaults or package values | Existing definition, complete BOSS no-data evidence, or a complete authorized data-export no-match result |
| LIVE_IMPORT_APPROVAL | Explicit approval for the reviewed package | Yes | Before live import or update | Pending | Parent `Execution Approval Preview` and authoritative `core.data-loader` approval | | Keeps mutations separate from discovery and preview without asking twice | Present the exact target, operation, immutable ZIP, and SHA-256 through the parent/Data Loader gate | Approval record |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Blocked | A required source, dependency, technical default, or compatibility result is absent or ambiguous | No |
| Existing-Identical | The requested definition matches one existing book | No |
| Existing-Different | The requested definition differs from one existing book | No |
| Pending Approval | All technical gates pass but live import has not been approved | No |
| Ready | All technical gates, package evidence, and approval are current | Yes |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| FA_BOOK.DEPENDENCIES_READY | decision | 4 | resolve_dependency | ready->FA_BOOK.DEFAULTS_RESOLVED;blocked->FA_BOOK.RETURN_ISSUES | FA_BOOK.TARGET_DEPENDENCIES_RESOLVED | stop | Required technical evidence has been resolved and must be assessed as a complete book definition. |


