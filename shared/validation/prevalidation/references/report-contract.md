# Readiness report contract

Write sanitized `readiness.json` and its rendered `readiness.html` in a fresh `project/{project_id}/artifacts/shared/validation/prevalidation/{run_id}/` directory. Register both, preserve sanitized evidence in that run directory, and register any full catalog exports separately under `project/{project_id}/exports/`. Use relative artifact references; never link secret storage. Record durable execution metadata separately using `schemas/skill-run.schema.json` and the project artifact/state schemas.

New runs use the Prevalidation skill ID and locations above. Existing project
reports and durable run records retain their original identifiers and paths;
do not rename historical evidence or rewrite its provenance.

JSON fields:

- `assessment_stage`: `pre_runbook` for every new implementation project or `full_readiness` for standalone assessment. Omission is treated as `full_readiness` for existing reports. Render this stage prominently: READY in `pre_runbook` applies only to the checks before creation, not verified Run Book write access or setup readiness.
- `run_id`, `generated_at`: nonempty run identity and ISO-8601 timestamp.
- `target_environment`: object with `name`, `base_url`, `release` (use `unknown` if not observed).
- `selected_scope`: object with `pillar`, `offering`, `functional_areas` (array), `planned_setup_tasks` (array); empty optional arrays mean full offering coverage, not an empty assessment. Explain resolved coverage in findings.
- `selected_scope.task_details`: for new-project reports from plain-language or artifact requirements, one structured row per `planned_setup_tasks` occurrence, copied from the resolved mapping. Each row contains positive unique integer `sequence` (the resolver sequence), `functional_area_code`, `functional_area_name`, `task_code`, `task_name` and `phase` (nonempty strings; use `Unspecified` only when the source phase is unknown). Codes must belong to the selected functional areas when that array is populated. Preserve repeated task codes in different catalog occurrences; never deduplicate by task code or name. The legacy text arrays remain supported.
- `checks`: nonempty array of the rows below. Include every category: `environment_authentication`, `catalog_readiness`, `offering_functional_area_readiness`, `setup_task_readiness`, `data_loader_readiness`, `runbook_read_readiness`, `privilege_connectivity`. Expand categories into per-entity checks rather than collapsing failures.
- `overall_decision`: computed using the rules below. The renderer rejects a conflicting supplied decision.

New reports use `PASS`, `REVIEW NEEDED` and `NOT APPLICABLE`.
Historical `FAIL`, `BLOCKED` and `POTENTIAL BLOCKER` rows remain valid inputs;
the renderer displays/counts all three as `REVIEW NEEDED` without rewriting
source JSON or changing the calculated readiness/continuation decision.

Every check has these fields:

| Field | Content |
| --- | --- |
| `check_name` | Specific check and entity identity |
| `category` | One of the seven categories above |
| `status` | `PASS`, `REVIEW NEEDED`, `NOT APPLICABLE` |
| `required` | Boolean; false only for a documented advisory check, never to downgrade a required prerequisite |
| `repository_evidence` | Array of sanitized file/key, requirement, and scope provenance strings |
| `live_environment_evidence` | Array of sanitized observations: endpoint/service/method, retrieved time, HTTP result, identity/state fields, pagination counts/completeness, external identifiers as relevant |
| `failure_classification` | Null on PASS/NOT APPLICABLE; exact governance taxonomy on REVIEW NEEDED |
| `review_reason` | Required for new REVIEW NEEDED rows: `confirmed_issue`, `verification_incomplete`, or `framework_limitation`; preserves the basis for review without a FAIL label |
| `implementation_message` | Required for new REVIEW NEEDED rows. Plain-language finding using the business capability name; avoid catalog codes and API jargon |
| `support_action` | Required for new REVIEW NEEDED rows. Separate investigation for FSCR support or the appropriate technical team; displayed within expandable diagnostics |
| `recommended_remediation` | Plain-language action for the implementation user for every REVIEW NEEDED; technical investigation belongs in `support_action`; `None required` only for PASS/NOT APPLICABLE |
| `artifact_references` | Array of relative sanitized artifact paths |
| `external_identifiers` | Array of relevant BusinessObjectId, journey/task IDs, request IDs or ECIDs; no tokens |
| `notes` | Limitations, applicability rationale, Data Loader API-only coverage limitation, source/documentation release gaps, unproven privilege hypotheses or timing |

Semantics:

- PASS: supported by recorded evidence for the stated scope. No inferred enablement or unverified schemas.
- REVIEW NEEDED: an observed prerequisite is unmet, verification is incomplete, or a framework limitation needs investigation. Preserve the distinction in `review_reason`, evidence and failure classification. Dependent checks needing evidence also use REVIEW NEEDED; never infer PASS. Supplemental/custom catalog absence alone is an uncertain mapping, not a confirmed environment defect.
- NOT APPLICABLE: a proven scope or declared stage exclusion with rationale, never an access failure or missing workflow. Successful empty Run Book listing may exclude existing-book detail reads in `pre_runbook`; listing failures remain REVIEW NEEDED. Run Book writes have no check row in new reports, in either stage.
- READY: all required applicable checks PASS, at least one required check passed, no checks needing review anywhere.
- READY WITH WARNINGS: all required applicable checks PASS; only optional advisory checks REVIEW NEEDED. Document each warning.
- NOT READY: any required REVIEW NEEDED, any category lacks a required result, or no required check passed.

## Audience and recommended actions

The primary findings table shows the implementation message, REVIEW NEEDED
status, and recommended action for the user. Use business capability names and
clear implementation impact. The user confirms phase scope or asks their Fusion
application administrator to verify availability/access. Catalog mapping,
response parsing and adapter investigations belong to FSCR support, with
prepared technical details collapsed by default. Do not tell implementation
users to reconcile catalogs, diagnose assessment identities or repair FSCR.

## Run Book write-check removal and historical evidence

New reports contain seven categories and omit `runbook_write_verification`.
Both stages assess read readiness only; neither requests test-create approval
nor creates a Run Book. PASS/READY does not establish write privileges.

Historical reports containing `runbook_write_verification` remain readable with
their original eight-category coverage and decision semantics. Their write
findings remain historical evidence; do not silently drop them or recalculate
an old NOT READY as READY. Rerun the current read-only assessment in a new run
when an updated readiness decision is needed.

## Data Loader category scope

New assessments record one required `data_loader_readiness` check named
`Data Loader API accessibility`. Its PASS evidence is an authenticated HTTP 200
from the declared bounded collection GET plus a valid JSON `items` array;
empty results are valid. No complete pagination or individual BO, template,
component, attribute or schema evidence is required or collected. Record those
items and load/write privileges as **not assessed** in `notes`, rather than
implying object-level readiness. Unavailable/unverified API access is
REVIEW NEEDED with a recommended solution. Preserve historical reports
that assessed a broader Data Loader scope; do not rewrite their findings.

## Calculated overview and findings

The standalone HTML begins with the recorded decision, assessment stage,
environment, scope and report-generation timestamp. It then calculates these
metrics from the validated JSON without introducing new input fields:

| Metric | Calculation and limit |
| --- | --- |
| Recorded checks | Number of check rows, including advisory and excluded rows; not tasks executed. |
| Passed / review needed / not applicable | Exact count of each supplied check status. Excluded checks are not passes. |
| Required categories | Distinct categories with at least one required row, out of the seven required categories; not a pass rate. |
| Required applicable checks passed | Required PASS rows over required rows whose status is not NOT APPLICABLE. A zero denominator does not establish readiness. |
| Planned task occurrences | Length of `planned_setup_tasks`, preserving repeated occurrences. An empty list means all applicable tasks with the count **Not enumerated**, not zero tasks. |
| Functional areas | Length of the selected area list; an empty list means full offering scope with the count **Not enumerated**. |

No overall implementation percentage is inferred. Planned task counts do not
establish creation, execution or completion. The readiness decision retains its
existing rules; counts do not weaken required checks or the distinction between
`pre_runbook` and `full_readiness`.

The findings table lists missing required category results, then recorded
required REVIEW NEEDED rows, then advisory REVIEW NEEDED rows. It includes the
recorded remediation, limitation and evidence. Missing required results remain
missing evidence; the renderer does not manufacture REVIEW NEEDED input rows or add
them to the recorded review-needed count. A category represented only by
advisory rows is still missing its required result. Excluded checks retain their
rationale. Where no required applicable check passed, explain that condition
even if no check explicitly failed.

The per-category detail remains available below the overview, including source
observations, references, external IDs and classifications. Report generation
time is not task completion time or proof that every observation was retrieved
then. Evidence references remain inert text. The renderer validates structure
and decision consistency; it does not call Fusion, verify the observation
against its source, scan secrets, or certify a claim merely because it is
well-formed.

A requested project summary can consume this saved report through
`shared.validation.implementation-summary-and-evidence`, together with
explicitly selected implementation-review and transactional reports. That
local assembly preserves each source's identity, environment, scope, stage and
timestamp; it does not imply that all source scopes match or refresh any
evidence. Follow the summary skill's input and persistence contract.

## HTML scope navigation

The summary shows **Functional areas: count — View table** and **Planned setup
tasks: count — View table** as internal fragment links. Each reveals a hidden
table within the same standalone HTML file. Include a close/return-to-summary
link; hide the table again when the user returns. Use static fragment IDs and
CSS `:target`, without scripts or network requests. Keep readiness results
visible independently of which scope table is open. Print both tables.

The functional-area table contains **Code**, **Functional area** and **Planned
tasks**. Resolve names and task counts from the structured task details. The task
table contains **Sequence**, **Functional area**, **Task**, **Task code** and
**Phase**, ordered by resolver sequence. Escape every source value as text;
never turn source-supplied strings into link destinations or executable content.

For legacy reports without `task_details`, display every original task string
in a table and label missing context/fields **Not recorded**. Do not parse display
strings to guess ownership, task codes or phases. Empty scope arrays retain their
full-offering/all-applicable meaning: link to a table panel explaining that
individual entries were not enumerated, rather than displaying zero coverage.

## Result overrides and continuation

Every assessment presentation and rendered HTML must offer fix-and-rerun,
override-selected-and-continue, and override-all-and-continue. Passing assessments
may continue normally. HTML is informational: it does not grant an override,
perform writes, or collect approval. The agent obtains the explicit user choice.

Keep the calculated `overall_decision` independent of continuation authorization.
An override never changes a check to PASS or NOT APPLICABLE, removes a finding,
or changes NOT READY to READY. Missing evidence remains missing.

Write a new append-only `decisions/prevalidation-override-{decision_id}.json`
with:

- `decision_id`, `recorded_at` (timezone-aware timestamp), `project_id`;
- `decision: OVERRIDE_AND_CONTINUE`, `user_instruction_reference`, and optional user reason;
- `run_id`, `assessment_stage`, `target_environment`, and `selected_scope` matching the assessment;
- immutable report/diagnostic references and checksums, plus `original_overall_decision` (or `unverified` if no valid report could be produced);
- `override_scope: selected` or `all`; for selected results, exact check indices/names/categories and any specifically accepted missing categories;
- `accepted_findings`: original statuses, limitations, recommended solutions and implementation risks, including missing evidence;
- `remaining_required_findings` and `handoff: continue` only when every outstanding required finding is accepted; otherwise `handoff: hold`;
- `readiness: unverified_for_overridden_results` and the next authorized implementation route, or `awaiting_implementation_request` for an assessment-only request.

Register the decision and link it from the durable run and token log. Preserve
previous decisions/reports; changed findings, target or scope require a new
review and explicit decision. A decision cannot waive mandatory prerequisites or
approval gates of the next execution step. If the assessment failed before a
report existed, reference the persisted diagnostics and disclosed missing
coverage; never manufacture a passing report. Overrides are distinct from
`SKIPPED`, which records an assessment intentionally not performed.

## Skip evidence

Skipping the assessment is a decision, not a readiness report status. Persist
`decisions/prevalidation-{run_id}.json` with `prevalidation_status: SKIPPED`,
`readiness: unverified`, timestamp, user instruction reference, project and source
request reference (plus artifact references/checksum when files exist), selected scope, task mapping reference, optional
user-supplied reason and any prior assessment report/blocker references. Register
the decision and reference it in the skill run and token log. Do not render an
all-PASS or all-NOT-APPLICABLE readiness report for skipped checks. Preserve any
prior failed/partial assessment and state that only prevalidation was skipped;
core Run Book prerequisites and approvals remain mandatory.

Sanitize before persistence. Allowlist identity/metadata fields; exclude credentials, client secrets, codes, cookies, bearer headers, token/cache contents, private keys, private trust policy, raw response dumps, actual business setup rows and sensitive template values. Persist only the required target label/base origin, never properties-file copies or URL query strings carrying session state. The renderer escapes all input as text, uses no third-party resources, and does not automatically turn evidence into executable HTML or arbitrary links. It is not a secret scanner. Verify the HTML visually before handoff; ensure long evidence wraps, all checks/statuses and the decision are legible, and JSON/HTML agree.
