# FSCR Validation Frequently Asked Questions

*Triggers evidence ownership and worked conversations*

**Version:** 1.1

**Date:** 20 October 2026

**Owner:** FSCR Framework Team

## Contents

- [1. What validation means](#1-what-validation-means)
- [2. When validation starts and what to say](#2-when-validation-starts-and-what-to-say)
- [3. Projects skipping and repeated prevalidation runs](#3-projects-skipping-and-repeated-prevalidation-runs)
- [4. How Data Loader readiness is checked](#4-how-data-loader-readiness-is-checked)
- [5. How scope identity and access are checked](#5-how-scope-identity-and-access-are-checked)
- [6. Run Book task correctness and completion](#6-run-book-task-correctness-and-completion)
- [7. Where evidence comes from and how values are checked](#7-where-evidence-comes-from-and-how-values-are-checked)
- [8. Missing pillar skills and the handover](#8-missing-pillar-skills-and-the-handover)
- [9. Reports and the meaning of a pass](#9-reports-and-the-meaning-of-a-pass)
- [10. Hallucination risk and evidence safeguards](#10-hallucination-risk-and-evidence-safeguards)
- [11. Play story for prevalidation and a corrected issue](#11-play-story-for-prevalidation-and-a-corrected-issue)
- [12. Play story for implementation review and one transaction](#12-play-story-for-implementation-review-and-one-transaction)
- [13. Play story when a check cannot run automatically](#13-play-story-when-a-check-cannot-run-automatically)
- [14. What teams must finish before a live pilot](#14-what-teams-must-finish-before-a-live-pilot)
- [15. Executive reports and evidence boundaries](#15-executive-reports-and-evidence-boundaries)

## 1. What validation means

### Q1 What are the three validation stages

| Stage | Question it answers | What it does not prove |
| --- | --- | --- |
| Prevalidation | Can the selected environment support the planned implementation workflow? | That customer setup is correct or that tasks are complete. |
| Implementation Review | Do requirements, task and load outcomes, and observed setup agree? | That every possible business transaction works. |
| Transactional validation | Does one selected basic business scenario work with the existing setup? | Bulk readiness, exhaustive testing or production release approval. |

Task completion, successful loading and correct business values are separate facts. A successful task can still create the wrong association. A successful API response can still fail a business assertion. Reports keep these facts separate.

### Q2 What is implemented today

The repository supplies assisted review and coordination skills, a hybrid prevalidation workflow, reusable core clients and executable local report tools. It does not contain a universal live evidence collector, generic transaction runner, bundled pillar tests or a Playwright or SVF adapter. Some steps are skill instructions that select existing services; they are not one executable end-to-end validation program.

The reporting tools check the consistency of supplied sanitized evidence and calculate readiness. They make no Fusion calls. A live result must come from an executed supported route or attributed manual evidence. A report file by itself is not proof that a live check ran.

This FAQ describes the validation design and its scoped reporting update reviewed on 20 October 2026. Check the owning skills in the branch you are using before assuming a capability is installed; validation development and core service contracts may have different release histories. Proposed behavior and current integration gaps are called out explicitly. The example conversations are illustrative; no Fusion operations were performed to produce them.

## 2. When validation starts and what to say

### Q3 How is prevalidation triggered and when

For a new implementation created from a requirements document, the Implementation Router selects Prevalidation. The workflow first reads the requirements, resolves catalog-backed scope and task mapping, and prepares the local project with Oracle Run Book creation deferred. It then honors an explicit Run or Skip choice, asking only if that choice is missing. Silence is not a skip.

A standalone environment-readiness request can also select Prevalidation. It is not a background monitor and does not run automatically after every setup task.

### Q4 When are post implementation checks triggered

A request to review completeness, correctness or gaps selects Implementation Review. It can run during implementation; unfinished work becomes a finding. A transaction check requires a separate explicit request. Completion of a Run Book or review may suggest a check but does not authorize its execution. A standalone transaction need not wait for unrelated tasks, but its prerequisites and project mutation gates still apply.

### Q5 What natural language prompts can a human use

| Intent | Sample single line prompt |
| --- | --- |
| Prevalidation before creation | Create project Atlas from this requirements document and run prevalidation before creating its Oracle Run Book. |
| Standalone assessment | Check TEST readiness for SCM Order Management; create a local evidence workspace if needed, but do not create an implementation Run Book. |
| Review with live refresh | Review Atlas against its approved requirements, refresh its Run Book and Data Loader status in TEST, verify setup where supported, and report gaps. |
| One transaction | Run one applicable transactional validation for Atlas in TEST and show the exact action before creating anything. |
| Report only | Generate the validation report for Atlas from existing evidence without refreshing live state. |
| Executive report only | Create an executive validation summary for Atlas from these existing report artifacts; keep stages and scopes separate and do not refresh live state or run tests. |

These are intent prompts, not special command syntax. Codex resolves the project and environment and asks for genuinely missing inputs. A request to generate a report alone does not implicitly refresh live state.

## 3. Projects skipping and repeated prevalidation runs

### Q6 Can prevalidation run without a project

Yes, without a previously existing implementation project or Oracle Run Book. No, without any local evidence workspace. The workflow initializes a local project to preserve scope, reports and audit history, with Oracle Run Book creation deferred. It needs a real offering and catalog-resolved task mapping; it must not invent tasks merely to make a connectivity test work.

If no name is supplied, it uses the repository draft-project convention and reports the corresponding folder ID. If the user forbids even a local workspace, or the scope cannot be mapped, the skill stops with that prerequisite. A general setup explanation can still be given without running an assessment.

### Q7 Is a standalone environment assessment fully available

Yes, subject to project, scope, identity and supported read-route prerequisites. Both pre\_runbook and standalone full\_readiness are read-only assessments. Run Book write verification has been removed from new prevalidation runs, so an unavailable isolated test-create route no longer prevents readiness. Run Book listing/detail-read evidence and all other applicable checks are still required.

New reports contain seven required categories and no Run Book write-check row, including no placeholder NOT APPLICABLE row. READY applies to the selected read-only assessment scope and does not verify write privileges or setup correctness. Actual implementation Run Book creation remains a separate core.runbook operation. Historical eight-category reports preserve their original write findings and readiness; use a new assessment run for the current rules.

### Q8 Can I skip prevalidation and continue

Yes. Say: “Skip prevalidation for Atlas, record readiness as unverified, and continue with normal Run Book planning and creation checks.” The workflow saves SKIPPED and readiness unverified, then resumes the original request through core.runbook. It still needs valid inputs, authentication, privileges, catalog/payload checks and the owning approval gates. Data Loader submissions still require the appropriate active Run Book. Skipping is not PASS or a guarantee that creation will succeed. After every executed assessment, the user is also offered fix and rerun, override selected results and continue, or override all results and continue. Each FAIL or REVIEW NEEDED includes a recommended solution. An override is recorded separately with the exact run, environment, scope, original findings, accepted risks and user instruction. It preserves the original assessment; it does not turn NOT READY into READY. Continuation requires acceptance of every outstanding required finding and still follows mandatory execution prerequisites and approvals. Silence is not an override.

### Q9 Can I rerun it after fixing an issue

Yes. Say: “I fixed the Data Loader access issue; rerun prevalidation for Atlas in TEST with the same scope and assessment stage and preserve the previous report.” Each run gets a new ID and report directory. Earlier failures remain visible. Rerunning read assessment is different from resending an uncertain create request; a lost mutation response requires read reconciliation, not blind recreation.

## 4. How Data Loader readiness is checked

### Q10 How does it determine whether Data Loader is available

Prevalidation checks Data Loader API accessibility only. It does not assess individual business objects or their metadata.

- Through the declared standard-service core REST client, make one authenticated GET to the dataLoaderBusinessObjects collection path defined by BUSINESS\_OBJECTS\_PATH, with onlyData=true, limit=1 and offset=0.
- Require HTTP 200 and the expected JSON collection envelope containing an items array. An empty array passes. Do not follow pagination, even when hasMore is true.
- Do not collect required business-object declarations, match discriminators, check individual-object registration, or retrieve BO details, UCM templates, components, attributes or schemas.
- Record sanitized endpoint/service, check time, HTTP status, response-envelope validation and safe diagnostic identifiers; exclude returned BO rows from evidence.
- Unavailable access, malformed responses, timeouts or missing routes produce REVIEW NEEDED with a recommended solution. Offer fix and rerun, override selected results and continue, or override all results and continue.

### Q11 Does a pass prove a future data load will succeed

No. PASS proves access to the tested collection API only. It does not prove individual-object availability, template access, schema compatibility, load/write privileges or successful future loads. Those checks belong to the separately selected implementation/load workflow. Prevalidation does not refresh metadata, generate a sample, validate or upload a file, or submit a job. Historical reports retain their original broader coverage and findings.

| Illustrative finding | Meaning |
| --- | --- |
| PASS: HTTP 200 and valid items array | The tested Data Loader collection API is accessible, including when items is empty. |
| REVIEW NEEDED: HTTP 401/403 | Access is unverified. Follow the owning authentication/access workflow; a status alone does not identify a missing role. |
| REVIEW NEEDED: timeout or malformed response | Connectivity or response evidence is insufficient. Diagnose the recorded failure, then rerun or explicitly accept the finding. |
| Individual BOs and schemas not assessed | No claim is made about object registration, metadata compatibility or load readiness. |

## 5. How scope identity and access are checked

### Q12 Does scope mean implementation scope or OAuth scope

Both matter, and they are checked separately. Implementation scope means the selected pillar, offering, areas, features, tasks and dependencies. OAuth scope means the service access requested during authentication.

### Q13 How is implementation scope validated

The workflow compares approved requirements and catalog-resolved identities against the complete effective repository catalogs and supported live catalog relationships. It preserves dependencies and repeated task occurrences. It checks actual enabled or opted-in state separately from catalog availability. A visible offering row does not prove that the required feature is enabled. Missing state fields or the absence of a supported read route become REVIEW NEEDED.

### Q14 How does it check OAuth scopes and privileges

| Check | What is verified |
| --- | --- |
| Service selection | Select the exact configured scope for the requested service: scope for standard, boss\_scope for BOSS, and fusion\_common\_scope for Fusion Common. Missing or blank values block the selected service. |
| Target and trust | Reconcile the selected project/environment, HTTPS base URL and trusted authentication profile. Bind cached access to the approved client, issuer, target and requested scope. |
| Authentication | Use the owning authentication workflow for the selected service. Never substitute another service scope to force login. |
| Observed access | Record the results of the specific supported service operations actually attempted, along with safe status and diagnostic references. |

Successful login does not prove that the user has all business roles, data access or write permissions. A 403 alone does not identify a particular missing role. The current implementation does not universally inspect all IAM grants or compare returned token scope with every business privilege. Report confirmed failures and unverified access separately; do not claim that all scopes and roles are automatically certified.

Passwords, tokens, private trust contents and credential configuration must not appear in the FAQ, evidence report or project artifacts. Authentication diagnosis begins with FSCR Onboarding and delegates execution to the owning auth workflow.

Prevalidation reports address implementation users. All confirmed issues, incomplete checks and FSCR limitations use REVIEW NEEDED, while diagnostics preserve which applies. A supplemental/custom FSCR offering absent from the returned catalog does not prove a missing environment capability. Ask the user to confirm whether the capability is required for the phase; if required, their Fusion application administrator can verify availability and access. FSCR support owns catalog mapping and unexpected-response investigation. Keep technical codes, endpoint details and parser errors in expandable diagnostics, rather than asking implementers to repair FSCR. The user may fix and rerun, override selected findings or override all findings and continue; readiness evidence is preserved.

## 6. Run Book task correctness and completion

### Q15 How does it know that the right tasks were created

Three comparisons are needed: approved requirements against the task mapping; the mapping against the canonical Run Book plan; and the intended plan/payload against the actual created task instances. Compare identity, occurrence, offering context, ordering and dependencies. Matching task counts alone is insufficient.

Prevalidation before Run Book creation checks planned identities and relationships against live catalogs. It cannot check a Run Book that does not exist yet. Core creation builds from the canonical plan, reports skipped-task warnings and reads back the dashboard. A complete deterministic plan-versus-live task reconciliation is still a framework pilot integration item; current create success must not be presented as proof of that full comparison.

### Q16 How does it check whether all tasks are complete

For a requested live refresh, core Run Book reads retrieve all task pages and individual task details using explicit journey/task identities. Preserve repeated catalog tasks as separate Run Book occurrences. Evaluate each status, exceptions and coverage, rather than trusting a single completed count.

| Current raw status | Meaning | Review treatment |
| --- | --- | --- |
| COM | Completed | Execution status only; still verify relevant setup. |
| CWE | Completed with Exceptions | Preserve exceptions; never flatten into clean success. |
| REJ | Not Applicable | Keep separate from successful completion. |
| Unknown | Unknown or unrecognized status | Keep unknown and investigate; do not infer completed. |

The current dashboard completedCount includes COM, CWE and REJ. “Ten completed” can therefore include exceptions and not-applicable tasks. The validation adapter must explicitly map source statuses to its result vocabulary.

### Q17 Where does the completion time come from

The raw Run Book client requests CompletionDate, but current sanitized dashboard/task models omit it. The framework must complete the supported normalization into completed\_at and preserve the source timezone and task occurrence identity. If the supplied evidence has no valid completion time, show Not recorded. Never substitute capture, last-update or report-generation time.

## 7. Where evidence comes from and how values are checked

### Q18 Does validation read folders or call live APIs

It can use both, with an explicit distinction. Existing-evidence review reads the approved requirement baseline, task/load evidence and previous observations in the project. A requested live refresh delegates to supported Run Book and Data Loader read operations. Every finding must show its source, environment, observation time and freshness. An old local report is not proof of current Fusion state.

| Question | Evidence source |
| --- | --- |
| What should exist | Approved requirements, design decisions and pillar assertions. |
| What was planned | Catalog-resolved task mapping and canonical Run Book plan. |
| Did a task finish | Live Run Book status/details when refresh is requested, or clearly dated saved evidence. |
| Did a load finish cleanly | Linked Data Loader dataset and error details; applicable object/failed-line evidence and ESS logs. |
| Are actual business values right | Pillar-defined read-back through a supported route, or attributed manual evidence. |

Data Loader status checks use dataLoaderDataSets and dataSetErrors even when a top-level status says success. Non-FSM loads also inspect failed lines and object results; FBDI checks include the ESS job hierarchy and available logs. Missing dataset evidence means unavailable or pending, not success. A request ID alone does not establish completion. Prevalidation checks only Data Loader collection API accessibility and does not perform this post-load assessment. Status refresh must be explicitly requested and routed through the owning core service; report generation does not automatically monitor a newly initiated load.

### Q19 Does it go into Fusion to check actual values

Yes, where the pillar supplies the correctness rule and a declared supported read-only route. For example, compare an observed business-unit association with the approved expected association. Keep expected value, observed value, assertion result and evidence together. Valid input files and successful loads cannot substitute for this read-back.

If the route is missing, report BLOCKED. If an authored application-only procedure exists, offer it to the implementer and record the performer and evidence, or identify attestation explicitly. Do not invent an endpoint, infer a correct value from the live environment, or silently control the application through a browser.

## 8. Missing pillar skills and the handover

### Q20 What if no pillar implementation skill exists

| Missing item | What happens |
| --- | --- |
| Implementation task skill | For an identified catalog task, core.runbook can route to shared.common.manual-tasks for human guidance from supplied documentation or valid product guidance. The missing skill is not proof that the live task is absent. |
| Setup correctness check | Review still reports available requirements, task and load evidence. The missing business verification remains a gap owned by the pillar; it cannot become PASS. |
| Transactional check or supported route | The requested automated test is BLOCKED. An explicitly authored applicable manual alternative may be selected; the framework must not invent one. |

Generic manual task guidance does not create a transaction-validation definition, business assertion or cleanup contract. If source guidance is insufficient, the responsible administrator or pillar must supply it.

### Q21 How does the framework hand over to the pillar

At runtime this is a skill and contract handover, not an automatic email, chat or Jira assignment. The framework resolves the project, offering and requirement version, discovers reviewed checks under pillars/\<pillar\>/\<existing-offering-slug\>/implementation-validation/, selects one, and checks its definition and execution prerequisites.

The handover carries the check ID/version, project/environment, requirement and task references, safe input references, expected assertions, declared route, limits and cleanup policy. The pillar procedure or supported core adapter performs the business-specific work. Its result returns to the shared run contract with observed assertions, evidence, safe record/request identifiers, side effects and cleanup status. The framework publishes the common report.

### Q22 Who builds what

The framework team owns routing, contracts, normalization, common limits, report assembly and history. Core service owners own supported adapters, authentication and their execution/approval gates. Pillar teams own product correctness, test definitions, applicability, API/manual procedures and cleanup. Implementers select, approve and supply manual evidence; project owners accept documented gaps and decide progression.

## 9. Reports and the meaning of a pass

### Q23 What does the overall output contain

There are separate prevalidation, implementation-review and transactional report families. The two post-implementation stages each produce HTML and JSON for a fresh run. The executive report uses an explicit manifest of selected existing project artifacts and recalculates source assessments locally. It keeps stage, environment, scope and requirement version visible, links detailed reports, and performs no live refresh or test execution.

- Project, environment, run identity and time, followed immediately by the Run Book task list: task ID, name, status and actual completion time.
- Scope, approved requirement version, requirement-to-task-to-check mapping and evidence coverage.
- Task/load outcomes, errors, evidence source, capture time, freshness and owners.
- Each check result, expected versus observed assertions, evidence references, gaps and manual checks.
- For a transaction: selected check/version, method, safe record/request identity, actual creation count or uncertainty, effects and separate cleanup outcome.
- Decisions, recommended next actions, accountable owners, limitations and diagnostics.
- For the executive index: the selected source reports and their recalculated outcomes, historical run/check counts, unresolved findings, owners and next actions. Counts are not a project success score.

| Illustrative task | Status | Completed at |
| --- | --- | --- |
| T001 Configure demo organization | completed | 2026-10-16T09:30:00+01:00 |
| T002 Associate business unit | completed | Not recorded |
| T003 Verify effective access | pending | Not completed |

Prevalidation reports instead lead with stage, environment and scoped area/task counts, then the seven assessment categories, evidence, findings needing review, recommended solutions and handoff decision. In pre\_runbook there may be no created Run Book to list. A skipped prevalidation produces a decision record with readiness unverified, not a passing assessment. New prevalidation reports use REVIEW NEEDED for incomplete evidence or unavailable routes/access; legacy FAIL, BLOCKED and POTENTIAL BLOCKER rows are accepted and displayed as REVIEW NEEDED. User overrides are separate continuation decisions and do not alter check counts or readiness.

### Q24 Does PASS mean the project is ready for production

No. PASS belongs to a specific evidenced check. Post-implementation readiness is BLOCKED, NEEDS\_REVIEW or READY\_WITHIN\_VERIFIED\_SCOPE. The last means only the stated scope was verified. Prevalidation has its own READY, READY WITH WARNINGS and NOT READY decisions. Project acceptance and production release remain separate human decisions. A transaction can pass while unresolved cleanup still requires review.

## 10. Hallucination risk and evidence safeguards

### Q25 Can hallucinations or incorrect conclusions happen

Yes. An absolute zero-hallucination guarantee would be misleading. Language-model interpretation can misread a requirement, propose a wrong mapping or misunderstand evidence. The design aims to constrain those errors and make them visible rather than assume they cannot occur.

- Use approved expectations and exact catalog/check identities. Never copy observed values into the expected values merely to produce a match.
- Use reviewed pillar procedures and declared supported execution routes. Missing guidance or routes remain explicit gaps.
- Keep environment, source/version, observation time, freshness, performer and evidence references with results.
- Require observed passing assertions and evidence references for PASS. Preserve BLOCKED, NOT\_RUN, SKIPPED, NOT\_APPLICABLE and INDETERMINATE honestly.
- Use deterministic schema/consistency checks and readiness calculation. Keep human acceptance separate from recorded failures.
- Review the pilot against known good and known bad examples, including false success, incomplete pagination, exceptions and unknown mutation outcomes.
- Keep accepted requests, Run Book status, terminal load/job results, row/object outcomes and actual-value assertions separate; partial or conflicting evidence never becomes PASS through aggregation.

### Q26 What can the report tool not protect against

A well-formed JSON record can still contain a wrong or fabricated observation. The renderer validates internal consistency; it does not independently call Fusion, open every evidence reference, verify that approval truly occurred, or certify business correctness. It is also not a secret scanner. Evidence collection, execution controls, redaction and reviewer judgment remain necessary.

A report should say “verified by a supported live read at this time,” “reviewed from saved evidence,” “reported by the user,” or “not verified,” as applicable. If the only evidence is an old project file or an unsupported inference, Codex must not describe the current Fusion environment as verified.

No live checks were run for this FAQ. The conversations below show expected interaction patterns and require the stated routes and pillar definitions to exist before the successful paths can execute.

## 11. Play story for prevalidation and a corrected issue

Illustrative scenario: Atlas is a new SCM project in TEST. Names, object identities, findings and outcomes below are examples, not observations from a live system.

Human: “Create Atlas from this requirements document and run prevalidation before creating its Oracle Run Book.”

Codex: “I have resolved the requirements and task mapping and prepared the local workspace with Oracle Run Book creation deferred. Your prompt already chooses Run, so I will assess pre\_runbook for the selected TEST environment and scope through its supported read routes.”

Codex after the hypothetical reads: “Prevalidation is NOT READY. Data Loader API accessibility is REVIEW NEEDED because the bounded authenticated collection request returned HTTP 403. Individual BOs, templates and schemas were not assessed. The report includes the failed read, safe diagnostics and the owning action. Run Book creation is on hold pending your choice: fix and rerun, override selected results and continue, or override all results and continue. The recommended solution is for the Data Loader owner to review standard-service API access using the recorded status and request ID, then rerun the check. An override preserves this finding and does not waive core creation prerequisites. Run Book writes are outside prevalidation and have no check row.”

Human: “The administrator has fixed that access issue. Rerun the same prevalidation.”

Codex: “I will create a new assessment run and preserve the first report. I will refresh the applicable evidence for the same environment and scope. I will not assume the fix worked because it was reported.”

Codex after the hypothetical successful reassessment: “The applicable read checks now pass and pre\_runbook readiness is READY. This does not verify write permission or business setup correctness. I will resume the original Run Book workflow and its required planning and approval gates.”

Codex: “I will now resume the original authorized Run Book creation through core.runbook, applying its prerequisites and operation-specific permission. The initial-creation workflow does not add a second payload-preview confirmation.”

Codex after the hypothetical creation: “The core workflow returned the Run Book identifier and task evidence. I will retain any skipped-task or creation warnings. Full plan-to-created-task reconciliation must be supplied by the supported integration before I claim the entire created task set is verified.”

### Alternative if the human skips

Human: “Skip prevalidation and continue.” Codex: “I have recorded SKIPPED and readiness unverified, preserving any earlier failures. I will resume normal Run Book planning and creation checks. The skip does not waive authentication, payload validity or approval.”

## 12. Play story for implementation review and one transaction

Illustrative success path: a reviewed pillar setup check and one executable transaction check already exist, with supported routes and valid project prerequisites. The example is not a ready-made product API specification.

Human: “Review Atlas in TEST, refresh task and load status, verify setup where supported, and report gaps.”

Codex: “I will use the approved requirements as the expectation. I will refresh Run Book and linked Data Loader evidence through the selected read routes and keep task completion separate from setup correctness.”

Codex after the hypothetical checks: “The association task is completed, but the observed association differs from the approved requirement. That required blocking assertion is FAIL, so review readiness is BLOCKED. The report shows the expected value, observed value, source and corrective owner. I have not changed the configuration.”

Human: “We corrected the association through the implementation workflow. Review it again.”

Codex after a new hypothetical read: “The current observation now matches the approved expectation. The new report preserves the earlier failure in history. This result applies to the stated verified scope.”

Human: “Run one basic transaction check for this offering.”

Codex: “The reviewed Demo Contact Check version 1 applies. Its existing reference is available. It permits at most one marked test contact and defines read-back assertions and cleanup. I will now show the exact TEST target, operation, payload, generated values, side effects and evidence plan before mutation.”

At this point the real workflow must show the complete concrete approval preview from the selected route. The example name is illustrative; no endpoint, payload or privilege is invented here.

Human: “Approve the displayed single-record action.”

Codex after the hypothetical execution: “One record was created and its read-back assertions passed. I captured evidence before cleanup. Here is the supported cleanup operation for that exact record; approve it or choose an allowed documented retention option.”

Human: “Approve the displayed cleanup.”

Codex after the hypothetical verification: “Removal is verified. The transactional HTML and JSON record the check result, observed values, evidence and cleanup separately, with the Run Book task table at the top. This does not automatically close other review gaps or approve the project for release.”

## 13. Play story when a check cannot run automatically

### No pillar check exists

Human: “Run a transaction check for this offering.”

Codex: “No reviewed matching check is available in the offering’s implementation-validation folder. Transactional execution is BLOCKED. The pillar needs to provide the scenario, assertions, supported API or manual procedure, bounds and cleanup. I can still produce the available implementation evidence report and identify this missing coverage.”

### A manual alternative exists

Codex: “The automated route is unavailable, but the pillar has supplied an applicable reviewed manual procedure. You can select it or skip the optional test.”

Human: “Use the manual procedure.”

Codex: “Here are the exact authored steps, input limits, expected result and evidence requirements. Perform them in TEST, capture evidence before cleanup, and provide the safe record identifier, performer and observed result.” In a real run, the selected pillar procedure must supply the actual product steps.

Human: “I completed it; here is the redacted evidence and the record reference.”

Codex: “I will record the result as manual-evidence and identify you as the performer. If only a statement is supplied, it will be user-attestation, not live API verification. Required attestation-only coverage still needs review. Cleanup remains a separate recorded action.”

### The user bypasses an optional check

Human: “Skip this test and continue.” Codex: “I will record SKIPPED and your reason if supplied. It will not be counted as a pass. The project owner can decide whether the unverified scope is acceptable; other execution gates still apply.”

### An API response is lost

Codex: “The creation outcome is INDETERMINATE. The record count is unknown. I have preserved the safe request reference and known effects. The next step is read reconciliation by the stable test key through the declared route. I will not blindly send the create again.”

### Cleanup is unavailable or fails

Codex: “The business assertions passed, but cleanup is unresolved. The report preserves PASS for the transaction, records the residual record and cleanup owner, and keeps overall readiness at NEEDS\_REVIEW. It does not claim removal.”

## 14. What teams must finish before a live pilot

Use the FAQ and design document as a handoff specification. The following work must be verified in a pilot before teams describe the entire process as automatic.

| Deliverable | Owner |
| --- | --- |
| Reviewed business assertions and one bounded API or manual transaction check per pilot scenario | Pillar lead and developer |
| Supported routes and enforcement of identity privileges payload limits approvals and reconciliation | Core service owner with pillar developer |
| Plan versus created Run Book task reconciliation, preserving repeated task instances and dependencies | Framework and Run Book service owners |
| Source status normalization, exception handling and CompletionDate to completed\_at mapping | Framework and Run Book service owners |
| Evidence collection, freshness, linked load identifiers and reviewed check-version binding | Framework engineering with pillar reviewer |
| Supported Run Book listing/detail reads; implementation creation remains a separate core.runbook operation | Core Run Book owner |
| Known-good and known-bad cases, manual/skip/timeout/cleanup behavior, and reviewer sign-off | QA with framework and pillar leads |

### Repository references

- router/implementation-router/SKILL.md and router/next-action-planner/SKILL.md
- shared/validation/prevalidation/SKILL.md and its references/execution-contract.md and report-contract.md
- shared/validation/configuration-completeness-validator/SKILL.md and transactional-validation-coordinator/SKILL.md
- shared/validation/references/pillar-check-contract.md and validation-workflow.md
- core/validation/reporting/SKILL.md, references/report-contract.md and scripts/validation\_report.py
- core/runbook/scripts/runbook\_client.py, runbook\_service.py, runbook\_workflows.py and status\_catalog.py
- core/data-loader/SKILL.md and scripts/data\_loader\_metadata.py
- core/getting-started/onboarding/SKILL.md and core/auth/fusion-oauth-authentication/SKILL.md
- shared/common/manual-tasks/SKILL.md
- core/validation/reporting executive-summary contract and local helper, as declared by its current SKILL.md

These sources define the current repository behavior. Product endpoint and release details must be checked through the declared workflow before live execution. The accompanying functional and technical design provides the fuller contracts, persistence layout and acceptance criteria.

## 15. Executive reports and evidence boundaries

### Q27 Can the framework produce a report similar to implementation-partner feedback

Yes. The common report should make each gap actionable: affected requirement and task, expected result, actual observation, dated evidence, impact, owner and next action. Separate observed implementation defects from missing framework routes and missing pillar checks. Reuse existing core status and validation services; a readable report does not require a new testing platform or a duplicate loader.

For a summary of existing work, the executive-report route accepts an explicit list of existing project artifacts, recalculates their assessments and produces a local index with source references. It does not discover arbitrary customer files, collect new evidence, execute checks or silently select the newest report as the whole-project truth.

### Q28 What do the executive counts and readiness labels mean

Counts describe the historical reports and checks selected in the manifest. They are not a percentage of project success or unique requirement coverage across unrelated scopes. Prevalidation, Implementation Review and each single-check transactional invocation keep their own outcomes. Environment, requirement version, scope and evidence time remain visible. A later passing transaction does not clear an earlier blocked implementation review.

Example: a 10:00 review finds an inactive supplier site and an unfinished prerequisite. A separate 12:00 transaction can run only after the needed corrections are evidenced. Its single check may pass while the earlier report remains BLOCKED in history. The summary shows both; it does not average them into project readiness.

### Q29 What happens when task load and actual-value results disagree

| Signal | Report treatment |
| --- | --- |
| Task completed but no terminal load result | Keep task completion; load completion remains unverified. |
| Request accepted but no dataset yet | Keep accepted request evidence; do not invent a completed job or zero errors. |
| Top-level success with failed rows or downstream job errors | Retain the reported status and contradictory error evidence; flag the affected scope for review. |
| Clean job but wrong or ignored business value | The actual-value assertion fails or remains unverified, even if the job passed. |
| Manual check or user bypass | Attribute supplied evidence or attestation; record a skip/waiver explicitly without converting it into PASS. |

A supported core route owns each lookup. Data Loader metadata and Task Hook rules can supply declared source/reference checks, but their available coverage must be stated. Metadata cannot prove a referenced record exists. Pillar definitions supply supported read-back and operation-specific business expectations; missing routes or rules remain gaps with owners.

### Q30 Does reporting save Data Loader previews or approve cleanup

No. Follow the selected core Data Loader contract without changing its execution, preview, approval or persistence rules. Reporting must not copy or reconstruct internal payloads, hashes, execution plans, previews or approval objects as validation artifacts, restore workflows retired by the selected core version, or automatically poll after initiation. A report request authorizes sanitized report artifacts, not export of internal loader state. Use supported safe summaries and explicitly requested diagnostics; disclose missing durable evidence.

Transactional reports still cover exactly one selected pillar check per invocation and at most one new primary transaction with bounded intrinsic children. Capture authorized evidence before cleanup. Deletion or cancellation requires its own supported route and applicable immediate authorization; a cleanup recommendation is not approval. Show test outcome and cleanup outcome separately. An executive index never batches or dispatches these tests.
