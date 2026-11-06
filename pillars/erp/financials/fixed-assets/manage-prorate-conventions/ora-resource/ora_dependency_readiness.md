# Manage Prorate Conventions: Dependency Readiness

## Required Dependency Order

Create/update follows these parent workflow stages.

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Validate prorate data | Apply [Input Validation](ora_input_validation.md), then the applicable Reference Lookups, Defaulting Rules, and Design Enforcement through the compiled task graph. Validation and its export require no approval. Failures follow [Error Situations](ora_error_handling.md#error-situations); retained state follows Conversation State and Resume. |
| 2 | Explain and correct missing or invalid data, only when needed | Use the Correction Question Contract in ora_input_validation.md for missing or proven invalid business values. Resume through Conversation State and Resume. If validation succeeds, skip this question and proceed directly to step 3. |
| 3 | Show preview and ask for ZIP approval | Continue Parent Workflow Continuation with verified data and Business Review Mapping. Ask: Please approve creation of the ZIP package. A reply of approved is sufficient. |
| 4 | Create/review the approved ZIP and ask for submission approval | The parent prepares and validates the ZIP and presents its actual contents. Ask for approval to submit that exact immutable ZIP to the exact target. A reply of approved is sufficient. |
| 5 | Submit the approved ZIP and hand off accepted request | Use Core Data Loader for the exact approved ZIP. After accepted initiation, report `accepted — pending parent verification` and hand off the archive identity, target, and request ID to the parent Fixed Assets workflow. The parent owns terminal status, ProcessLog review, and fresh target read-back. |

A standalone submission retains Core's accepted-initiation response. A
status-only request goes directly to the owning parent/Core status operation.

An existing-ZIP request enters parent/Core archive review after task validation,
without a ZIP-creation gate. Export-only follows its owner in [SKILL.md](../SKILL.md).
A read-only fiscal-year inquiry runs only resolve_prorate_fiscal_year_range under
Lookup Execution Rules and Fiscal-Year Lookup Freshness; it returns the requested
finding without convention checks, export, generation, or approvals.

## Parent Workflow Continuation

After create/update or existing-ZIP task validation succeeds, immediately read and follow the parent's
[Shared Fixed Assets Preview and Approval Gates](../../SKILL.md#shared-fixed-assets-preview-and-approval-gates)
and [CSV Encoding Fidelity](../../SKILL.md#csv-encoding-fidelity).
Supply verified values, defaults, dates, target, current-state evidence, and
export-backed mappings. Execute the parent's package preparation in the same run
using available local file/archive tools; no separate package-builder skill or
service is required. Its approval gates remain authoritative, with no additional
task-local upload or status approval. Export/import owners are indexed in
[SKILL.md](../SKILL.md).

## Conversation State and Resume

Use [Fiscal-Year Lookup Freshness](ora_reference_lookups.md#fiscal-year-lookup-freshness)
for evidence reuse, fresh requests, and target changes.

| Situation | What Happens |
|---|---|
| Missing/invalid input correction | Replace only changed fields, retain valid input and the selected operation, and automatically revalidate affected facts. Do not ask whether the correction is complete or verification may resume. |
| Pending parent workflow | Retain its step, exact data/ZIP under review, and accepted submission reference. Interpret replies at that step; a helper returning control does not restart intake or create another approval. |
| Unchanged affirmative reply | Advance only the pending approval through Required Dependency Order. After accepted submission, report the retained `accepted — pending parent verification` handoff state; never upload/submit again. If acceptance is uncertain, use the owner's read-only recovery before considering retry. |
| Changed business values or revalidation results | Revalidate affected facts and use the parent's existing review/approval gates for changed package data. Old approval cannot authorize changed data. Immutable artifact handling belongs to Design Rules. |
| Basis source | Keep each convention's normalized basis and explicit/Name source. A changed Name invalidates only a name-derived basis and its dates; rerun input validation. Preserve explicit basis across Name changes. A later explicit basis replaces inference; unrelated corrections retain the basis. |
| Fiscal-year selector | Retain selector, cycle constraint, and resolved exact name separately. A changed cycle invalidates that convention's resolution and dates. A later explicit name replaces the selection while retaining the cycle constraint. Reuse and revalidation follow the pending-workflow rule in [Fiscal-Year Lookup Freshness](ora_reference_lookups.md#fiscal-year-lookup-freshness). |
| Inquiry during pending work | Keep its fresh result separate from the pending inputs, selection, evidence, reviewed data, and approval stage. A newer name alone is not authorization to replace the selection. Applying a changed name or restarting validation follows the changed-data rule; correcting the inquiry selector stays in the inquiry. A later approval still belongs to the retained gate, subject to freshness and parent revalidation. |

## Parent Workflow Handoff

Use [Parent Import Handoff](ora_error_handling.md#parent-import-handoff)
for execution ownership. Task validation alone is not import completion.

| Terminal | Parent Workflow Continuation |
|---|---|
| PRC.IMPORT_GATE | Submit only the exact immutable ZIP approved by the parent/Core gate, then hand off the accepted request. |
| PRC.HANDED_OFF_TO_PARENT | Report `accepted — pending parent verification`; parent/Core owns status, ProcessLog, and fresh target read-back. |
| PRC.DONE_EXISTS | Report Convention name already exists and ask only for a different Name. Creation stops; no equivalence claim, package, or approval. |
| PRC.DONE_FISCAL_YEARS | Complete the read-only inquiry route from Required Dependency Order, using Disclosure Rules for the requested finding. |
| PRC.ISSUES | Use Error Situations and Conversation State and Resume. |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| operation_route | Requested operation | Yes | Before task-specific work | Satisfied | Completed input-validation result | | Select the applicable workflow without collecting unrelated inputs | Complete operation intake | operation route |
| existing_import_archive | Existing immutable FSM ZIP | Conditional | Existing-ZIP import | Satisfied | Completed import-artifact intake and validated immutable-archive context returned by the existing import-validation flow | | Preserve the supplied artifact and provide task-local comparison context | Use the input-validation import contract | archive reference, fingerprint, ProrateConventionCode or Name, SetCode, FiscalYearName, every archive date row, and the optional basis hint |
| fiscal_year_range | Fiscal-year selection or inquiry result | Yes | Create/update, existing-ZIP date validation, or read-only fiscal-year inquiry | Lookup | Current result under Fiscal-Year Lookup Freshness | resolve_prorate_fiscal_year_range | Supply the applicable finding or per-year generation context | Use the resolver's result or owning failure response | Resolved exact name and fiscal_year_date_rows for generation, or the requested inquiry finding |
| reference_data_set | Reference Data Set identity and code | Yes | Create/update | Lookup | One complete live result | validate_reference_data_set_name | Verify the selected dropdown name and resolve its exact code together | Use the resolver's invalid-name or mapping-gap result | Verified name and SetCode |
| import_metadata | Manage Prorate Conventions FSM export contract | Yes | Create or update after Reference Data Set and Fiscal Year verification, before the first preview | Lookup | Fresh same-target task export acquired through shared.setup-export.task-level-export | resolve_prorate_export_metadata | Package shape and technical mapping must match the target export contract | Resolve during the automatic verification phase above | resolved current export contract |
| convention_info_mapping | Convention Info DFF values | Conditional | Before the first preview when Convention Info is supplied | Lookup | Local lookup result | resolve_convention_info_mapping | Every supplied optional value needs a proven target column | Resolve automatically during verification | resolved Convention Info mapping |
| existing_parent | Existing parent row | Yes | Before defaults and the first preview | Lookup | BOSS `assetProrateConventionsView` | resolve_existing_prorate_parent | Defaults and create/update behavior must use the exact current parent state | Resolve automatically. For an explicit create whose exact Name is already used, state that the Name already exists and ask only for a different Name. | resolved parent-state result |
| existing_date_rows | Complete existing parent-owned dates | Conditional | Update only, before same-parent comparison and audit preservation | Lookup | Fresh same-target populated task export | resolve_existing_prorate_dates | Compare existing date tuples and preserve exact existing audit values | Acquire the declared export directly; stop if it fails or is incomplete | Complete parent-owned date inventory and source evidence |
| existing_convention | Completed create-name check or update definition comparison | Yes | After generation, before the first preview | Lookup | Resolved name check; update also requires parent-owned date rows | resolve_existing_prorate_convention | For create, check name availability only; for update, compare existing definition rows | Resolve automatically; do not create a duplicate convention or ask a generic create-versus-update question | completed comparison and package decision |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Verified create configuration | Create was selected and required values, Reference Data Set, resolved exact Fiscal Year Name, SetCode, normalized supported basis variant, defaults, and generated dates have passed their owning generation-integrity checks | Continue to parent Final ZIP Preview and `PRC.IMPORT_GATE`; no import approval is implied until the exact ZIP is shown |
| Verified update configuration | Update was selected and required values, Reference Data Set, resolved exact Fiscal Year Name, SetCode, normalized supported basis variant, defaults, and generated dates have passed their owning generation-integrity checks | Continue to parent Final ZIP Preview and `PRC.IMPORT_GATE`; no import approval is implied until the exact ZIP is shown |
| Existing-ZIP validated | The immutable archive passed the applicable lookup, generated-row, and exact-comparison requirements | Continue to `PRC.IMPORT_GATE` for the validated archive; no import approval is implied until that exact archive is shown |
| Already exists | The exact parent and generated selected-basis rows already exist | Lookup yes; create no |
| Fiscal-year names listed | An explicit listing-only request has a complete nonempty matching-name result | Return the read-only answer; create, package, and approval no |
| Missing required input | Input validation is incomplete | Lookup no; create no |
| Invalid Fiscal Year Name | resolve_prorate_fiscal_year_range returns invalid | Lookup no; create no |
| Fiscal-year selection unresolved | resolve_prorate_fiscal_year_range reports no matching cycle or a name/cycle conflict | Generation and package creation no; ask only the period or fiscal-year correction owned by ora_error_handling.md |
| Invalid Reference Data Set | validate_reference_data_set_name returns invalid | Lookup no; create no |
| Lookup gap | An applicable resolver fails or remains incomplete | Do not generate dates or prepare a package |
| Technical package gap | Export metadata, Convention Info mapping, current-state evidence, or safe technical-field handling is unavailable | Package creation no; show one concise action without an approval prompt |
| Create name conflict | An explicit create uses a Name already assigned to a different convention definition | Lookup yes; package creation no; state that the Name is invalid for a new convention and ask only for a different Name |

## Business Review Mapping

Populate this mapping from verified values before ZIP creation and from actual
contents for an existing/prepared ZIP. The parent owns review timing, defaults,
and child-row summarization. Response wording belongs to
[Disclosure Rules](ora_error_handling.md#disclosure-rules).

### Manage Prorate Conventions

| Field | Value |
|---|---|
| Prorate convention name | ProrateConventionCode |
| Reference data set | SetCode |
| Description | Description |
| Fiscal year name | FiscalYearName |
| Depreciate when placed in service | DeprWhenAcquiredFlag |
| Prorate basis | Resolved Prorate basis variant for this convention, not a list of choices |
| Convention Info | Supplied or changed Convention Info values with their business labels |

### Prorated Dates

| Start Date | End Date | Prorate Date |
|---|---|---|
| MM/DD/YYYY | MM/DD/YYYY | MM/DD/YYYY |

Use the table's date format and a separate copy ordered by descending StartDate;
never sort import rows in place for preview. Keep every date row available.
Show supplied or changed Convention Info values in the business review. Keep
unmapped DFF column names and omitted blank Convention Info columns internal.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| PRC.RESOLVE_PACKAGE | decision | 30 | resolve_dependency | create_verified->PRC.IMPORT_GATE;update_verified->PRC.IMPORT_GATE;existing_zip_validated->PRC.IMPORT_GATE;blocked->PRC.HANDLE_PACKAGE | PRC.ENFORCE_DESIGN | stop | Consume the applicable Dependency Rules and Design Enforcement result, then resolve_existing_prorate_convention for create/update. Any technical package gap selects blocked. Successful package-required outcomes proceed to the parent Final ZIP Preview and import gate. |
