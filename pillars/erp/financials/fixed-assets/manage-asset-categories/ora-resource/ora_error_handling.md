# Error Handling

## Failure Handling

| Failure | Message direction | Next action |
|---|---|---|
| System Controls row or matching enabled CAT# structure is unavailable | Stop and report the Asset Category structure setup dependency. | Resolve the exact selected System Controls and CAT# evidence before authoring. |
| Invalid category input | Identify the supplied category field or combination that failed validation and state the accepted target format. | Follow `ora_input_validation.md` and ask only for the corrected value. Do not create a package row. |
| Invalid category delimiter | State the supplied separator and the resolved CAT# delimiter. | Stop before splitting the category or looking up component values. Ask for labelled components or one concatenated category value using the resolved delimiter. |
| Missing CAT# prerequisite | Identify whether the current Key Flexfields export, the `CatStructureInstanceCode` match, the component-to-KFF-segment mapping, a value set, a component value, or a dependent parent value is unresolved. | Follow `ora_dependency_readiness.md`; obtain the approved prerequisite action, then resume after fresh target verification. |
| Existing category differs materially | State the exact existing category identity and show each requested-versus-target material field delta. | Stop package generation. For category-header work, request an explicit update-existing or preserve/create-new decision. Do not treat Create as Update. |
| Ambiguous or failed category state | State whether multiple exact matches, conflicting target evidence, incomplete pagination, or a failed lookup prevents one exact result. | Stop package generation. Do not request an update-or-preserve decision until exact target evidence exists. |
| Cross-structure category collision | Show the exact requested components and the existing category/structure identity; label the conservative create-policy hold separately from selected-structure existence. | Hold the affected header and all its book/default children. Do not claim the import's failed row IDs map to this combination unless target or batch evidence proves the mapping. An explicitly requested remaining subset may proceed only after fresh reconciliation, full subset validation, and a new approval preview. |
| Incomplete or rejected BOSS category filter | Identify the failed filter or missing continuation/visibility evidence. | Use the governed complete category export fallback. A 500-row page, unsupported `in` predicate, or incomplete structure mapping cannot prove absence. |
| Missing or ambiguous asset book | State that the assignment needs one exact active book. When an exact lookup returns no active row, retrieve and label up to three nearest active `BookTypeCode` matches, including match reason, class, currency, and depreciation calendar. | Require the customer to select or provide one exact book code, then rerun `resolve_asset_book_for_category`. Do not auto-select, map, or import a nearest candidate. |
| Account resolution blocked | Return the Account Review Disclosure below, including resolved and unresolved roles for the selected category, book, and ledger. | First complete the automatic `resolve_category_book_accounts` path for every required role that lacks a complete customer selection. Ask for a full combination or candidate selection only for roles with unresolved Natural Account derivation, skeleton, or required input. Do not use donor values or category-book mappings. |
| Impairment accounts missing | State that the selected book has `AllowImpairmentFlag` enabled and identify whether Impairment Expense, Impairment Reserve, or both are unresolved. | Obtain the missing complete, ledger-valid account combination or resolve its lookup evidence. Do not create, update, or import the category-book mapping until both roles are resolved. |
| Book fiscal-year calendar start blocked | State the selected book and missing/invalid fiscal-year calendar start. | Resolve the selected book fiscal year and its earliest available calendar start through `resolve_book_fiscal_year_start`. Stop until coverage is proven. |
| Depreciation setup blocked | Name only the required method, life, convention, or compatible setup that is unresolved. | Follow `ora_defaulting_rules.md` and `ora_reference_lookups.md`; obtain the required customer value or compatible selected-book evidence. Do not derive a business value from a donor row. |
| Default-rule reference-set mismatch | Name the supplied depreciation method, prorate convention, or retirement convention and its resolved reference set without exposing unrelated setup data. | Stop the package. Ask for a value whose reference set satisfies the documented book-level or Common Set rule; do not substitute another setup value. |
| Duplicate package data | Name the duplicate business key and member scope: category, category-book, default-rule date range, or translation language. | Follow `ora_design_enforcement.md`; remove or reconcile duplicate rows before preview. Ask the customer to identify the authoritative row when they conflict. |
| Malformed or incompatible package shape | Report the member, expected versus actual shape, and first malformed field when available. | Rebuild from the current task export and validate locally before preview. Do not treat a header-only template as sufficient evidence. |
| Invalid category-book account serialization | Identify every affected account role and any changed value/order, missing blank position, missing terminator, or malformed multiline CSV cell. | Do not submit or retry the ZIP. Rebuild only the affected account cells using Category-Book Account Format in ora_reference_lookups.md; repeat package validation, immutable preview, and approval. |
| Invalid Default depreciation expense combination | State that the UI value must be Yes or No and `DefaultExpenseCcidFlag` must serialize as `Y` or `N`. | Rebuild the ZIP with Yes → `Y` or No → `N`; reject `YES`, `NO`, selected, and cleared. Repeat package validation, immutable preview, and approval. |
| Missing category parent row or orphan child row | Identify the affected `FA_ASSET_CATEGORY_BOOK` or default-row member and the category combination whose `FA_ASSET_CATEGORY` parent is absent. | Do not submit or retry the ZIP. Rebuild it with the required matching parent row, repeat package validation and immutable preview, then obtain fresh approval. |
| Cross-environment or donor-value use | State that source and target environments differ, or that donor business values were detected. | Regenerate the affected preview using approved customer values and target-derived accounts/defaults. A same-book donor may provide formatting evidence only. |
| Preview or approval gate missing or stale | State that no unapproved ZIP creation or Fusion import has occurred. | Follow the parent Fixed Assets shared preview and immutable-artifact approval gates before the next task action. |
| Preview quantity or rendering issue | State the calculated category count, selected preview mode, and whether the complete detailed artifact was produced. | Use the preview-mode rule in `ora_design_enforcement.md`. Do not omit any applicable category, account role, or default rule from the complete inline preview or approval-bound artifact. Summaries and artifact links supplement the complete inline preview; they never replace it. |
| Import failure or post-import mismatch | Report the process/request identifier, terminal status when known, per-member loaded counts, and mismatched requested scope. | Do not claim completion or retry. When Fusion reports zero rows because a category parent alternate key cannot resolve, classify it as an orphan-child package failure; preserve the ProcessLog, rebuild the parent-child-complete ZIP, and obtain fresh approval before a new submission. |

## Account Review Disclosure

Show this review even when a dependency or lookup stops before normal package
preview. Use the same account-evidence section in a successful pre-creation
preview; do not maintain a separate duplicate success report.

| Gate | What Must Be Shown |
|---|---|
| Category-book account review | Identify category, book, ledger, and COA. Include one row for every required or supplied role, with account field/role, natural-account value and description, complete supplied or derived segment vector, category/role match basis, validation/result status, and customer action. Do not request or imply a verified CCID/full-combination match. Keep successful rows alongside unresolved rows; do not invent missing evidence. |
| Candidate disclosure | For ambiguous Natural Account derivation, list candidates and descriptions. Distinguish customer-supplied accounts from uniquely derived accounts; do not claim full-combination existence verification. |
| Blocked review | Label the review Blocked and identify the unresolved roles. State that package generation/import cannot proceed. Do not request ZIP/import approval while blockers remain. Ask only for the account decisions needed to resume. |

| Result Category | When Used | Next Action |
|---|---|---|
| Resolved | A complete customer selection has valid format, or a unique Natural Account and selected-book skeleton yield a complete vector. | Retain the account and source; apply CSV format checks and normal package approvals. |
| Unable to derive | Natural Account derivation or the selected-book skeleton cannot resolve the required account. | Ask only for missing input or derivation decisions; a nonexistent full combination is not a blocker. |
| Multiple matching accounts | More than one Natural Account candidate remains for an omitted/incomplete role. | List candidates and ask for selection, then assemble and check the chosen vector without full-combination search. |
| Lookup failed or incomplete | Authentication, authorization, API, transport, pagination, or required metadata prevented a complete search. | State the actual failure and safe next check. Do not claim that no matching account exists or repeatedly retry a failed operation. |
| Account format or derivation unresolved | Required COA metadata, selected-book skeleton, Natural Account derivation, or supplied segment format is missing, invalid, or ambiguous. | Resolve the specific gap under Category-Book Account Preparation. Do not search full combinations, require a waiver, or propose GL combination creation solely for nonexistence. |
| Not required | An optional role is outside scope and was not supplied, or the customer approved omitting a supplied optional role. | Leave blank; do not label it Unable to derive or ask for an unnecessary account. |

Example customer request: Unable to derive the Asset Cost account for the
selected Furniture category and book. Please provide the full account combination
or information needed to resolve the selected-book ledger lookup.

## Ownership Boundary

This file owns failure wording, stop conditions, and safe next actions. Input
constraints belong to `ora_input_validation.md`; prerequisite readiness belongs
to `ora_dependency_readiness.md`; lookup mechanics belong to
`ora_reference_lookups.md`; defaults belong to `ora_defaulting_rules.md`; and
package-design rules belong to `ora_design_enforcement.md`.

## Category Existence Lookup Continuation

Follow Category Existence Evidence Routes in ora_reference_lookups.md: prefer
the metadata-grounded BOSS `assetAllSegmentsCategoriesView` collection, then
use a governed complete current category export when BOSS is unavailable,
the selected structure cannot be bound to its numeric instance, or required
fields, visibility, or pagination are incomplete. Do not classify incomplete retrieval
as absence, substitute another structure, or infer a deployment requirement.
Ambiguous or contradictory state remains a blocker.

## Prerequisite Continuation

After a prerequisite change is verified by its owning workflow, obtain fresh
System Controls, CAT# structure, category-component value, and existing-category
evidence for the retained parent request. A prerequisite approval does not
approve the later Asset Categories artifact or import.

This skill ends at `validated_for_import`. The calling workflow follows the
parent Fixed Assets approval gates and uses `core.data-loader` for submission.
After acceptance, hand the request ID, target, immutable archive identity, and
child-supplied target-state criteria to the Fixed Assets parent and report
`accepted — pending parent verification`. The parent routes status and
ProcessLog retrieval through `core.data-loader`, verifies fresh target state,
shows the Post-Execution Verification Preview, and controls dependent-task
progression. This child must not poll, claim import completion, or start
dependent work from the accepted state.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---:|---|---|---|---|---|
| MAC.IMPORT_GATE | decision | 60 | execution_gate | ready->MAC.VALIDATED;incomplete->MAC.HANDLE_APPROVAL | MAC.ENFORCE_DESIGN | stop | Read-only design validation and immutable package preparation are complete. Approval is owned by the surrounding Data Loader workflow. |
| MAC.HANDLE_INPUT | step | 70 | error_handler | handled->MAC.ISSUES | MAC.VALIDATE_INPUT | stop | Input is invalid. |
| MAC.HANDLE_DEPENDENCY | step | 80 | error_handler | handled->MAC.ISSUES | MAC.CHECK_DEPENDENCIES | stop | Dependency is blocked; include Account Review Disclosure when account evidence is incomplete. |
| MAC.HANDLE_LOOKUP | step | 90 | error_handler | handled->MAC.ISSUES | MAC.RESOLVE_REFERENCES | stop | Lookup or export baseline is blocked, ambiguous, or failed; include Account Review Disclosure for unresolved accounts. |
| MAC.HANDLE_EXISTING_DIFFERENT | step | 95 | error_handler | decision_required->MAC.ISSUES | MAC.RESOLVE_REFERENCES | stop | One exact category exists but differs materially; show the delta and request an explicit category-header update-existing or preserve/create-new decision. |
| MAC.HANDLE_DESIGN | step | 100 | error_handler | handled->MAC.ISSUES | MAC.ENFORCE_DESIGN | stop | Design rule blocks the package; include Account Review Disclosure for non-unique or invalid ledger-derived account combinations. |
| MAC.HANDLE_APPROVAL | step | 110 | error_handler | handled->MAC.ISSUES | MAC.IMPORT_GATE | stop | A required parent Fixed Assets preview or approval gate is absent or stale. |
| MAC.VALIDATED | terminal | 120 | terminal | none | MAC.IMPORT_GATE | stop | Return validated_for_import for the current validation scope; no approval, submission, or Fusion completion is implied. |
| MAC.DONE_MATCH | terminal | 125 | terminal | none | MAC.RESOLVE_REFERENCES | stop | Existing category/category-book/default state already matches the requested material scope; no package row or import is needed. |
| MAC.ISSUES | terminal | 130 | terminal | none | none | stop | A blocker is handled and disclosed with the safe next action. |
## Validation and Execution Boundary

This graph returns read-only validation findings to the calling workflow.
VALIDATED means validated_for_import for the current stage, never a successful
Fusion import. Subsequent approval, submission, and accepted-import handoff
follow the parent-owned continuation defined in Prerequisite Continuation above.
