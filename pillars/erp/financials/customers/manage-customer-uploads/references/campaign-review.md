# FBDI campaign evidence review


`scripts/customer_campaign_review.py` joins the existing evidence reviewers for
one exact candidate. It is the offline reconciliation stage of the campaign
adapter. It does not submit, monitor, approve, mark a Journey complete or supply
passed runtime checks merely because the registry is plannable.

Generate a candidate-specific readback plan:

```text
python <task-folder>/scripts/customer_campaign_review.py --zip candidate.zip plan --operation mixed --environment-url https://<approved-host>
```

Every one of the 87 columns has exactly one identity/value reviewer. The plan
lists each nonblank row/field, required evidence and separate effect obligations.
It contains no input values. Blank inputs still require default/effect review;
absence from the requested-field list never means no effect. Profile/default,
receipt inventory and tax callback work may remain necessary without explicit
input. The plan is not a database query or an approval record.

`omitted_field_effect_checks` lists every blank row/field explicitly. Together
with `requested_checks`, it covers each row's 87 columns exactly once. The
`collection_contract` separates before-preview, after-submission and additional
manual review responsibilities. Follow [the verification plan](verification-plan.md)
for collection scope, partial outcomes and recovery. This adds no requirement to
obtain post-import evidence before preview and claims no automated collection.

Review raw evidence:

```text
python <task-folder>/scripts/customer_campaign_review.py --zip candidate.zip review --bundle campaign-evidence.json
```

The exact envelope has `schema_version: ar-customer-campaign-evidence-v1`,
`environment_url`, `operation_intent` and an `evidence` object. Populate only
actual captured evidence, using these keys and the existing contracts:

| Key | Evidence contract / role |
|---|---|
| identity, ownership | After-state [identity](identity-evidence.md) and [ownership](ownership-evidence.md) |
| values | [Selected values](value-evidence.md) |
| profile_set | [Profile and requested set](profile-set-evidence.md), including reviewed profile defaults |
| receipt, bill_to, tax | [Receipt](receipt-evidence.md), [bill-to](bill-to-evidence.md), [tax](tax-evidence.md) comparisons |
| before_identity, before_ownership | Candidate-bound before-state identity and ownership |
| target_plan | [Before-state target intent and number observations](target-evidence.md) |
| before_values, after_values, effect_plan | [Before/after effect evidence](effect-evidence.md) |
| before_supporting, after_supporting | [Profile and sibling-site inventories](supporting-effects.md) |
| runtime_binding, core_status | [Actual core attempt association](attempt-association.md) |
| staging | [Staging scope evidence](request-evidence.md), bound to the attempt derived from the actual core observation |

Each reviewer recomputes its candidate/environment/evidence bindings. The bundle
does not accept a previously generated pass report in place of raw evidence.
Unknown keys are rejected. Missing, malformed and failed components remain
visible alongside successful observations. The staging bridge cannot be supplied
with a separately invented product request ID.

`requested_fields_match` describes only explicit input observations. It can be
true with missing default/effect or attempt evidence; inspect the component
findings and open obligations. No result certifies full reconciliation, physical
creation, callback completion, process success, retry authority or Journey sync.
Review exits with code 2 while these separate campaign obligations remain open;
plan exits with code 0 only to indicate that the plan was generated. The CLI
writes no files and makes no external calls. Preserve its output in the authorized
project/campaign evidence location, never in the reusable task tree.

The execution adapter must still bind the actual Run Book/Task Hook preview and
delegate submission and later status phases to core Data Loader. Do not use this
review helper as a readiness override or replace the FSM-only tester with it.
Final artifact ownership/test discovery remains subject to the parallel contract.
