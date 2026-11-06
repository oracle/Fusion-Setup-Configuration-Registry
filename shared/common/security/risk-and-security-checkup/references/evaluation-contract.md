# Evaluation contract

Normalize caller input into an object with `requestId`, `environment`, and `roleSets`. Each set contains `roleSetId` and `roles`; each role has `roleCode`, `roleName`, and `accessPoints` containing exact `code` strings. Optional fields remain `subjectUser`, `roleType`, and access-point `name`. Missing request IDs are generated once. Environment is injected from the selected FSCR profile and is retained only as provenance. The caller supplies role evidence and optional request ID, not an environment or login username. Preserve role values and independent grouping; see input validation.

Before evaluation, consolidate all supplied files and source locations using the
[use-case-aware input contract](input-validation.md#use-case-aware-consolidation).
Within each explicit scope, merge by exact role code, including the specified
user in the key when present. Preserve independent personas/users/scenarios as
separate `roleSets`; file boundaries do not define assessment boundaries. Treat
the submitted evidence as final without requiring completeness confirmation.
Record consolidation provenance and supplied-access limitations alongside the
normalized JSON; this does not change the evaluator schema or expand access.

The evaluator returns `requestId`, `environment`, `rulesName`, `rulesSchemaVersion`, `evaluationScope`, `roleHierarchyExpansion`, `noRiskMeaning`, `roleSetsEvaluated`, `totalChecksEvaluated`, and `roleSetResults`. Counts reflect all checks generated from metadata freshly fetched for this assessment, not a fixed 167.

Each set returns `roleSetId`, `overallResult`, `recommendationStatus`, `checksEvaluated`, `rolesEvaluated`, `uniqueInputAccessPoints`, `accessPointsOutsideCatalog`, `sensitiveAccessFindings`, `toxicCombinationFindings`, and `findings`. Preserve `subjectUser` when supplied. Include the exact configured coverage message only for sets with unmatched codes.

The coverage message is independent of the risk result and must not assert that no risks were identified. Its exact configured text is:

> Some submitted access points are outside the runtime catalog coverage. Review the reported findings and run Risk Management analysis for a complete security analysis at regular intervals before going live.

Each finding returns `ruleId`, `ruleName`, `riskCategory`, `severity`, `sourceAlgorithm` (reference code, ID, exact runtime name), `offendingRoles`, `offendingAccessPoints` with entitlement references and contributors, `rationale`, and `recommendation`. Use actual runtime names in explanations. Preserve `risk_found` despite unmatched codes. No findings means no match within current runtime catalog coverage, not approval of the change. Preserve these established field names.


## Review artifacts

The orchestrator adds `catalogSource`, `generatedChecks`, `treeSummary`, and `evaluationArtifacts` to the assessment without renaming existing fields. Save `sensitive_access_rules.json`, `toxic_combination_rules.json`, `generation_summary.json`, and `runtime_tree.json` beside it. The tree export preserves the exact validated UTF-8 bytes used for rule generation, retaining the ordered algorithm/entitlement/access-point hierarchy. `evaluationArtifacts.runtimeTree` points to it. `treeSummary` in both assessment and generation summary reports `algorithms`, `entitlements` (dimension occurrences), `uniqueEntitlements` (distinct IDs), `accessPointOccurrences` (all hierarchy occurrences), `uniqueAccessPoints` (distinct exact codes), and per-algorithm counts. Link this raw tree to the request via the assessment/generation summary and verify its byte SHA-256 equals `catalogSource.treeSha256`; the tree array itself has no request wrapper. Never reuse an exported tree for a new assessment. Each rule export includes request ID, source provenance, rule type/count, evaluation policy, and all exact generated rules with access-point/entitlement evidence, source algorithm, match predicate, severity, rationale, and recommendation. No credentials or authentication responses are exported. Use runtime counts in link labels; 41 and 126 are observed counts, not required constants. Publish exports only after successful evaluation; verify they correspond to the same request/catalog as the assessment.

## Final presentation

The first completion response must contain the detailed results in chat. Writing
them to a report does not satisfy this requirement: do not replace findings with
aggregate counts, a report link, or an offer to provide details later. Before
sending, check that Rule-1 and Rule-2 cover every affected role and exact privilege,
identify source algorithms, reconcile conflict counts, and provide complete
remediation and documented-retention guidance. Include coverage limitations and
verified artifact links under the established numbering below. Group repeated
pairs through explicitly defined privilege dimensions when useful; preserve all
role mappings and matched conflicts. An explicit user request for summary-only
or file-only delivery takes precedence.

Use a numbered list with blank lines between points and indented content, following the caller's requested result layout:

1. Keep the main evaluation result as numbered point #1 in bold: **RESULT — [precise recommendation based on all identified risks].** Under #1, always present all evaluation findings in detailed tables, grouped by Rule-1 and Rule-2, using the requirements below. Keep the evaluation summary in normal font: runtime environment, sensitive/toxic checks, independent role-set count, total checks, finding counts, and toxic-match status. State that `high` is an implementation default when reporting severity. Use this run's values, never fixed example counts. All tables and explanations remain within #1; do not create new top-level numbered results. A clarification of one finding must retain the other findings rather than replace them with “as previously listed.” Preserve established numbering on follow-up revisions; leave #2 and #3 unchanged unless the caller requests changes to them.

   **Rule-1 sensitive-access table:** Include every affected role code, exact offending privilege code and runtime privilege name, source algorithm reference and exact runtime name, and the proposed privilege removal/restriction for that role. One row per role/privilege finding is suitable. Do not replace the role mappings with an aggregate count or an artifact link. If Rule-1 has no findings, state that in its table; do not invent removal recommendations.

   **Rule-2 conflict and resolution table:** Identify each affected role set (and subject user when supplied), source algorithm reference/name, the exact conflicting privilege groups, how the matched-pair count is obtained, and the proposed resolution. Show which role contributes each privilege using `contributingRoles`; for conflicts spanning roles, name each contributor and specify which role's privilege would need removal. Include the exact codes and runtime names for every matched privilege, using additional detailed tables when necessary. Shared group labels are acceptable only when their exact privileges and role associations are explicitly defined in #1.

   **Explain the arithmetic:** For each role set and algorithm, count the distinct matched privileges in each entitlement dimension. When all cross-pairs are present, explain in plain language that each privilege on the first side conflicts with every privilege on the second side, and show `m × n = matched pairs`. Count actual finding rule IDs and reconcile the equation with those findings. Distinguish pairs from distinct privileges; codes can overlap across dimensions. An illustrative synthetic example is 13 entry privileges paired with 2 posting privileges: 13 pairs with the first posting privilege plus 13 with the second, or 26 pairs, involving 15 distinct privileges only if the dimensions are disjoint. Never copy these numbers into a live result without deriving them from that run. If a complete Cartesian grouping is not supported by the findings, enumerate the actual pairs or supported subgroups instead of asserting a product.

   **Make the resolution complete and actionable:** For every finding/group, explain the conflict identified and the proposed resolution. For Rule-2, specify every exact privilege and role to remove/reassign on one complete conflicting dimension, or another change that breaks every matched pair. Give the alternative dimension when useful. Explain remaining conflicts after partial removal when this helps the caller understand the choice. Splitting responsibilities across roles assigned to the same user does not resolve a conflict; separate incompatible responsibilities between different users. For Rule-1, remove unnecessary sensitive privileges from the named roles and restrict justified retained access.

   **Documented-retention option:** Include a table explaining the alternative if the caller retains sensitive access or a known SoD violation: document the affected roles, exact privileges, algorithm reference, business justification, accountable owner, risk approver/acceptance, compensating controls, and review/expiry date. Suggest relevant controls as proposals, not verified safeguards. Explain that acceptance documents the decision but does not remove the finding. The caller decides remediation and risk acceptance; do not modify roles or approve access.

2. Only when `accessPointsOutsideCatalog` is nonempty, make point #2 **Access points outside catalog coverage**. List every exact unmatched code, deduplicating repeated codes across sets for presentation while preserving per-set associations in the assessment. An indented text code block is suitable for long code lists. Explain that the coverage message does not negate recognized findings or certify unmatched privileges. Follow with a separate paragraph containing the exact `securityCheckupMessage`. Preserve `risk_found`. Omit both this point and the coverage message when no codes are outside coverage, even if no toxic combinations matched. Never write “Outside catalog coverage: None.”
3. Finish with **Verified assessment artifacts** as the next numbered point (#3 when coverage is present, #2 otherwise). State verification only after checking request IDs, FSCR-derived environment, source digest, generated counts, and finding rule IDs against the exports. Link **Input JSON** and **Assessment result JSON**, then link both complete rule exports using their actual runtime counts. Also link **Generated JSON tree — A algorithms, E entitlement occurrences, P access-point occurrences (U unique codes)**, substituting this run’s actual counts; state unique entitlement IDs when different from occurrences. Compute the counts from the exported tree and reconcile them with `treeSummary` in the assessment and generation summary. Include a per-algorithm count table when useful. Verify the exact tree digest against the shared source provenance. Never substitute rule counts for tree counts or hard-code prior totals. Keep this information within the existing artifacts point (#3 when coverage is present); do not change Result #1/#2 or add a fourth top-level result. The user must be able to inspect what was evaluated, the exact source tree, and every rule used.

For no findings, say no removal is recommended by the generated checks rather than approving the role. Explain an algorithm's nonmatch only if supported by this run's rule evidence; never invent a finding reference. All privileges on one toxic entitlement dimension alone are not a toxic-combination match. `high` is an implementation default, not an API-derived severity; make this clear when stating severity.

For extraction/authentication failure, start with a bold failure result and the concrete action needed. Link the validated input and a sanitized failure report if available. Do not link stale assessments as this run's output, infer coverage, or emit the clean-result message.
