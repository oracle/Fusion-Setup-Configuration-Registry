# Resolve setup blockers in one pass

> Use [live setup workflow](live-setup-workflow.md) for service selection and
> approval. Package-only mode stops before external operations. A shared capability
> failure remains a dependency blocker, not permission for a pillar workaround.

Use this procedure when intake or authoring readiness prevents setup. It is an
assessment and repair procedure, not a substitute execution route. Run Book owns
customer inputs; core Data Loader and Task Hook own live validation and approval.

## Assess the request

Merge the original workbook with explicit customer corrections, preserving text
and leading zeros. Never overwrite a confirmed business choice with a guessed
value. Map labels to package codes only with evidence; unresolved mapping labels
remain a reference-resolution item, not a missing customer value.

For CREATE, assess the program, each company account and requested upload settings
before collecting further input. Require a program name, type and brand; company
account name and number, issuer/site and business unit. For non-Procurement require
payment terms, currency and payment option. Company Pay and Both Pay additionally
require the full expense clearing combination. Validate lengths against input
validation. Preserve text and leading zeros. Collect all missing business choices
in one question and keep unresolved technical references separate.

For upload settings, resolve or derive file format, and resolve supplied employee
matching, transaction source and mapping rule values through their named lookup
contracts. Do not treat a display label as a package code. Unused optional fields
do not cause customer questions, but their import blank/omission behavior still
requires qualification. This checklist is intake only: it does not replace the
compiled rule plan, validated candidate or approval. Developer assessment tooling
and tests are kept outside the distributed customer task.

## Resolution ownership

| Blocker | Skill action | Completion evidence | Customer question |
|---|---|---|---|
| Missing business choice | Collect all missing or invalid business values together; retain earlier answers | Customer provides the missing value | Ask only the unresolved business choices |
| Blank file format | Derive from exact brand only for CREATE; preserve explicit format | Derived value plus qualified target format validation | None when brand mapping exists |
| New-program duplicate check | Use a complete fresh exact-task export through the declared shared export route; compare exact and conservatively normalized names | Zero conflicts, same target/task, complete metadata and all program rows; recheck after stale state or changed input | None unless an existing/conflicting program is found; CREATE is never silently changed to UPDATE |
| Qualified BU, ledger or account reference | Run declared shared-client GETs when selected by the active workflow; complete pagination and cardinality checks | Exact matching active target identity in correct scope | Ask only after a successful zero/ambiguous match |
| Issuer name differs from export | Present exact candidate and preserve explicit customer correction | Exact approved target party identity | One spelling/identity confirmation, never repeat it |
| Issuer site | Run resolve_issuer_site against the complete party address collection, including inactive sites; require one matching address because importer selects first by party | Complete source-backed target site evidence or corrected supported importer contract | Ask only for business disambiguation; technical source gaps belong to the implementation owner |
| Missing public lookup with known importer resolver | Review AM call, actual resolver VO/EO, portable input key, scope and failure path; qualify FSM resolution only when established | Source-linked resolver contract plus required target evidence | Do not ask customer for internal IDs or helper code |
| No confirmed importer/lookup contract | Group all gaps by owning node and source component; perform available source discovery as authoring work | Reviewed evidence and source-authored rule changes, rebuilt registry and tests | Do not ask permission to bypass it as a routine fix |
| Optional field not supplied | Do not request it merely to exercise an unused lookup | Record lookup not needed for intake; independently qualify its blank/omission behavior in any candidate | None |
| Existing issuer/site during program CREATE | Resolve company references, retain both party CSV members header-only, and reject party data rows | Oracle FSM header-only contract plus independent company importer reference resolution | None after issuer/site selection is confirmed |
| Root/child field contract unresolved | Review task VO/EO and shared migration evidence; distinguish alternate-key matching from CSV blank behavior | Exact requested-field create/blank contract; relevant negative tests | Not a customer-data question |
| Authentication or transport failure | Use only the owning client's documented recovery; preserve actual error class | Successful required read or explicit unresolved error | Ask for sign-in/access only if needed |
| Immutable candidate changes | Revalidate through Data Loader and Task Hook | Current exact artifact and required approval | Present only the final validated approval report |

Do not confuse the number of compiler messages with the number of business
questions. Group every original compiler reason by node without removing it, and report
applicable intake resolutions separately. Never turn an authoring gap into passed validation. Customer-confirmed values do not
prove target existence, enabled status or privilege.

## Export submission cannot be confirmed

Use [export response recovery](export-response-recovery.md) for missing process
IDs and unexpected envelopes. Preserve the sanitized receipt, reconcile through
the shared client and retain customer decisions. An empty process collection
does not prove that submission failed or authorize another POST.

## Finish and resume

Complete every independent repair before reporting a source-access blocker. Keep
one consolidated project record containing resolved decisions, applicable reads,
remaining source contracts, exact source-discovery attempts and the next action.
Refresh the existing record on resume; do not re-ask answered questions or restart
with a generic blocker count. Source absence in one search is not proof that no
supported import exists; try the declared source channels and directly referenced
components. Do not invent source findings, submit a test import to discover an
unqualified contract, or use database/browser writes as an alternative route.

After authoring repairs, compile the registry and run the ordinary core planner.
An intake report cannot replace either. Use Builder staging, tests, packaging and
audit for repository changes. Then prepare the immutable candidate through Data
Loader, complete Task Hook validation, and request the exact candidate approval
required by the core contract. An explicit waiver, if separately requested, follows
core policy and retains the original findings; this assessment never creates one.

## Empty customer cells (CREATE)

Treat null, empty-string and whitespace-only cells as not supplied. For fields
that are optional in the selected program/company/upload context, skip their
value validation and reference lookup, and do not ask the customer to fill them.
Record skipped field names without inventing a value. Do not turn blank into
zero, N, a default choice or an instruction to clear an existing value. Preserve
explicit values, including text `0`, `N` and leading zeros, and validate them.

Check mandatory and conditional requirements first: an empty required cell still
blocks preparation. For Travel company accounts, Both Pay or Company Pay requires
the clearing account. Fields with a qualified derivation retain that rule: blank
file format derives from the resolved brand when upload rules are requested.
Unknown fields and invalid types remain errors, even when apparently empty.

Skip the business input, not the physical FSM column. Keep exact headers, row
widths, trailing empty cells and all CSV members. Never construct a row from only
nonempty cells. Populated rows still require the task's supported serialization
contract; this customer-input policy does not prove that Fusion ignores empty
CSV cells or authorize deleting XML nodes, changing metadata or clearing values.
The current request is CREATE; this policy does not qualify update semantics.
