# Validation guidance and FAQ

Start here when answering questions about FSCR validation. The
[Validation FAQ](fscr-validation-faq.md) covers Prevalidation, Implementation
Review and transactional validation, with prompts and illustrative human/agent
conversations.

## Find an answer

| Topic | FAQ section |
| --- | --- |
| What each stage proves and current capabilities | [What validation means](fscr-validation-faq.md#1-what-validation-means) |
| Triggers and single-line prompts | [When validation starts](fscr-validation-faq.md#2-when-validation-starts-and-what-to-say) |
| Standalone readiness, projects, skipping and reruns | [Projects, skipping and repeated runs](fscr-validation-faq.md#3-projects-skipping-and-repeated-prevalidation-runs) |
| Data Loader API accessibility | [Data Loader readiness](fscr-validation-faq.md#4-how-data-loader-readiness-is-checked) |
| Implementation scope, OAuth scopes and privileges | [Scope identity and access](fscr-validation-faq.md#5-how-scope-identity-and-access-are-checked) |
| Correct tasks, completion status and timestamps | [Run Book tasks](fscr-validation-faq.md#6-run-book-task-correctness-and-completion) |
| Local evidence, live status and actual Fusion values | [Evidence and value checks](fscr-validation-faq.md#7-where-evidence-comes-from-and-how-values-are-checked) |
| Missing pillar skills, check discovery and handover | [Pillar skills and handover](fscr-validation-faq.md#8-missing-pillar-skills-and-the-handover) |
| Report contents, outcomes and gaps | [Reports and passing results](fscr-validation-faq.md#9-reports-and-the-meaning-of-a-pass) |
| Hallucination risk and unverified claims | [Evidence safeguards](fscr-validation-faq.md#10-hallucination-risk-and-evidence-safeguards) |
| Prevalidation conversation and fixing issues | [Prevalidation play story](fscr-validation-faq.md#11-play-story-for-prevalidation-and-a-corrected-issue) |
| Review, one transaction, approval and cleanup | [Implementation review play story](fscr-validation-faq.md#12-play-story-for-implementation-review-and-one-transaction) |
| Manual tests, skips, missing routes and uncertain outcomes | [Exception play stories](fscr-validation-faq.md#13-play-story-when-a-check-cannot-run-automatically) |
| Delivery responsibilities and remaining integration work | [Pilot ownership](fscr-validation-faq.md#14-what-teams-must-finish-before-a-live-pilot) |
| Executive report, historical counts, evidence conflicts and Data Loader boundaries | [Executive reports and evidence boundaries](fscr-validation-faq.md#15-executive-reports-and-evidence-boundaries) |

## How to use this guidance

Answer the question using the relevant FAQ section and link to it. The FAQ is
dated explanatory guidance, not an execution contract or proof that a live test
ran. Check current behavior in the owning skill, contract and script before
claiming that a capability is available. Explain any discrepancy and preserve
the distinction between implemented behavior, proposed work and examples.
In executive summaries, counts describe explicitly selected historical
reports; they are not a project success score. Preserve separate stages,
environments, scopes and requirement versions, and distinguish task completion,
load/job outcomes, row/object errors and actual-value verification.

A question does not start an assessment, create a project or authorize Fusion
calls. Route actual execution requests through the
[Implementation Router](../../router/implementation-router/SKILL.md) and its
selected workflows. Authentication diagnosis starts with
[Onboarding](../../core/getting-started/onboarding/SKILL.md).

## Owning skills and contracts

- [Prevalidation](../../shared/validation/prevalidation/SKILL.md): environment readiness and the run-or-skip gate.
- [Implementation Review](../../shared/validation/configuration-completeness-validator/SKILL.md): requirements, task outcomes, setup correctness and gaps.
- [Transactional Validation Coordinator](../../shared/validation/transactional-validation-coordinator/SKILL.md): one explicitly requested pillar check and its cleanup.
- [Implementation Summary and Evidence](../../shared/validation/implementation-summary-and-evidence/SKILL.md): reports from recorded evidence.
- [Common validation workflow](../../shared/validation/references/validation-workflow.md) and [pillar check contract](../../shared/validation/references/pillar-check-contract.md): execution boundaries, handover and check definitions.
- [Core Validation Reporting](../../core/validation/reporting/SKILL.md): local report validation and publication.
- [Functional and technical design](../../governance/designs/fscr-validation/fscr-validation-functional-technical-design.md): the fuller design and ownership model.

## Maintaining the FAQ

The FSCR Framework Team owns this guidance. Edit the structured
[FAQ source](../../governance/designs/fscr-validation/faq-content.json), then run:

```bash
python3 governance/designs/fscr-validation/build_faq.py --markdown-only --dry-run
python3 governance/designs/fscr-validation/build_faq.py --markdown-only
```

The builder publishes the same Markdown to this folder and the existing design
folder. Do not edit either generated FAQ independently. Use the builder's full
document workflow with the bundled document dependencies to refresh HTML and
Word for a document release; inspect those rendered outputs before sharing.

The executive index generation contract is maintained in [Core reporting: executive summary](../../core/validation/reporting/references/executive-summary-contract.md). Use it when assembling the report manifest, interpreting historical counts, or explaining why a summary does not establish current project readiness.
