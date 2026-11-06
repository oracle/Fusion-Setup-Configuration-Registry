# FSCR complete validation — sample output pack

**Synthetic review material. No Fusion system was accessed; no real transaction, approval or cleanup occurred.**

Unzip the full folder and open `index.html` in a browser. Share the ZIP to preserve all report links. The HTML is self-contained, script-free and uses no external assets. It can be printed from a browser. JSON and Markdown can be read in any text editor.

## Start with all three stages

The main `index.html` directly displays the Run Book tasks, calculated executive counts and three clearly labeled stage summaries:

| Stage | Recorded outcome | Check results |
| --- | --- | --- |
| Prevalidation | READY before Run Book creation; write access remains unverified | 7 PASS, 1 NOT_APPLICABLE |
| Implementation review | BLOCKED at the original review | 2 PASS, 1 FAIL, 1 NOT_RUN |
| Transactional validation | READY_WITHIN_VERIFIED_SCOPE for one later draft check; cleanup verified | 1 PASS |

Each stage has a direct link to its detailed HTML report and JSON. These are one coherent fictional history: 3 reports and 13 recorded results. Later prerequisite corrections permit the selected transaction; they do not turn the original implementation review into PASS. No newer full implementation review is included, and overall current project readiness is not assessed.

## Additional independent transaction examples

Open `transaction-examples.html` for the six alternative outcomes below.

The six transaction cases are independent alternatives, each with a separate fictional project. They are not a batch execution or a sequence of successful/failed attempts in one project. Each contains exactly one selected check and at most one known new primary transaction; an uncertain outcome retains a null count.

| Example | Check result | Readiness | Cleanup |
| --- | --- | --- | --- |
| [Passed · cleanup verified](cases/01-pass-cleanup-verified/transactional-validation.html) | PASS | READY_WITHIN_VERIFIED_SCOPE | removed-verified |
| [Passed · cleanup pending](cases/02-pass-cleanup-pending/transactional-validation.html) | PASS | NEEDS_REVIEW | pending |
| [Blocked before execution](cases/03-blocked-prerequisite/transactional-validation.html) | BLOCKED | BLOCKED | not-needed |
| [Created · business assertion failed](cases/04-business-assertion-failed/transactional-validation.html) | FAIL | BLOCKED | removed-verified |
| [User skipped the check](cases/05-user-skipped/transactional-validation.html) | SKIPPED | NEEDS_REVIEW | not-needed |
| [Unknown creation outcome](cases/06-unknown-outcome/transactional-validation.html) | INDETERMINATE | BLOCKED | unknown |

The `executive-story/` files back the main three-stage dashboard and the full evidence index. Do not combine their counts with the independent transaction examples.

## Files in each case

- `transactional-validation.html`: user-facing report from the updated framework renderer, with an added sample banner/navigation.
- `transactional-validation.input.json`: fictional sanitized run envelope supplied to the renderer.
- `transactional-validation.json`: the run and its calculated assessment.
- `evidence.html`: matching fictional observation, decision and cleanup notes. No real screenshots or server responses are included.

`executive-story/` contains the separate report hierarchy and source manifest. Its relative paths match the production index layout. These sample files are not a registered/live implementation project: no real project-state update, artifact-registry publication or execution audit is claimed.

## Responsibilities

Pillars define the bounded scenario, prerequisites, supported API or reviewed manual route, business assertions and cleanup. The framework coordinates selection and controls, validates the result envelope, and generates common reports. A real execution route, current product documentation and required permissions must be supplied separately; none is implied by these examples.

One transaction may have several assertions. A completed Run Book task, successful request or successful cleanup cannot manufacture a passing business assertion. User skips remain unverified; timeout outcomes must be reconciled before another create attempt. Keep sensitive payloads/session objects out of report artifacts.

## Rebuild

From a checkout containing the updated validation reporting helpers:

```sh
python3 build_samples.py --renderer-root /path/to/validation-framework-checkout --dry-run
python3 build_samples.py --renderer-root /path/to/validation-framework-checkout
```

This builder uses pure local assessment/rendering functions and an ephemeral synthetic context. It never contacts Fusion or runs pillar tests. The source fixture story is included under `fixtures/`. `manifest.json` records package checksums and renderer source hashes for review; hashes cover report/code files only, not Data Loader payloads.
