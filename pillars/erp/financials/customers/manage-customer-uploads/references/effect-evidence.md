# Before/after scoped effect observations


This is the detailed supplied-evidence comparator contract. Its exhaustive
column shape remains unchanged for developer or otherwise complete evidence.
It is not an unconditional runtime prerequisite. For the functional journey use
[business-outcome reconciliation](business-outcome-reconciliation.md), including
all supplied DFF values and source-backed relevant effects. Do not fabricate
missing columns to pass this deeper comparator.

`scripts/customer_effect_review.py:analyze` compares the candidate's source-key,
ownership and selected-value snapshots against declared entity-level intent.
It recomputes the existing identity/ownership reviews in both phases. A new
reference is not proof of a new entity: it may link a customer that already
existed through another key. Missing references likewise do not prove deletion.
Creation causality and full reconciliation remain false in every result.

## Inputs and completeness

Supply the candidate ZIP, operation, environment, before/after identity and
ownership evidence, before/after value snapshots and an intent plan.
Ownership phases must be before and after respectively. Each snapshot follows
its bound ownership capture; after identity capture must follow the before-value
capture. Exported database dates cannot move backwards. These checks establish
supplied ordering, not transaction isolation, freshness or authentication.

The intent plan version is `ar-customer-effect-plan-v1`. It contains
candidate_sha256, environment_url, operation_intent, review_reference and
expectations. Each expectation is `{row, entity, intent}` with one-based row,
one of the seven identity entities and create/update/reuse intent. Every row/entity
needs an entry. Shared source targets must have consistent intent. This is a
reviewed business-effect declaration, not import approval or permission to add
support for unknown update semantics.

Value snapshots use `ar-customer-effect-values-v1`, with candidate_sha256,
environment_url, operation_intent, ownership_evidence_sha256, phase, captured_at,
evidence_reference and queries. Each query has entity, owner_table_id, boolean
complete and records. It must be scoped to IDs in that phase's bound ownership
evidence. Each record requires **every** mapped persisted column for that entity
from `customer_value_review.FIELDS`, with string or explicit-null values.
This includes the account DFF context and all 30 segments, even if the candidate
omits them. Otherwise changes to omitted fields could disappear from comparison.
The projection still covers only 75 fields, not all columns on all seven entities.
Party snapshots also require DUNS_NUMBER_C, JGZZ_FISCAL_CODE and
GSA_INDICATOR_FLAG even when omitted from input. Organization-profile history
and effects are not part of these seven entity snapshots. Party-site-use has
ownership checks but no direct values in this projection; its primary flag,
dates, status and sibling effects require the supporting inventory review.
It includes account-site language/translated name, account type/class, party-site
mail stop and site-use location even when omitted from the candidate. Older
snapshots lacking these columns must be recollected, not filled with assumed nulls.
Every mapped location column is also required, including all address lines,
both descriptions, phonetic text, postal extension and address elements 1–5.
Changes to omitted location values remain explicit unrequested-effect findings.

## Observations

- Same reference/ID and unchanged values can report unchanged with the requested
  values. An update intent whose desired values already exist is distinguished
  from an observed change; it is not proof that an update API ran.
- Requested nonblank values come directly from the candidate and reviewed date
  conversion. Changed columns outside those values are reported for review.
  Blank input is never silently interpreted as clear/default/preserve authority.
- Reuse with changed values, reference target replacement, source-code resolution
  change, unexpected relationship changes and missing requested values remain
  distinct findings. Partial observations remain available by row and entity.
- New/missing references, ambiguous history or incomplete snapshots never become
  physical creation/deletion claims. The before/after ownership review statuses
  remain visible; value observations do not override ownership failures.

Profile/receipt effects, unmapped fields, concurrency, loader status, batch/request
correlation and physical creation evidence require separate verification. The
module does not promote registry readiness, authorize a retry or complete Journey.

## Receipt inventory differences

`assignment_delta(before_query, after_query)` compares complete all-assignment
inventories for the **same existing account** using the receipt evidence record
shape. It reports added, removed, changed and unchanged counts and changed column
names without IDs or values. Duplicate or incomplete inventories yield no delta
counts. Empty complete inventories describe only that queried account scope.

This low-level diff is intentionally not candidate/attempt-bound: the campaign
caller must bind both snapshots and compare differences with reviewed expectations.
It returns both expected_effects_verified and attempt_causality_verified false.
A new account requires separately proven baseline evidence; do not fabricate a
before snapshot using a post-import ID. Counts alone never establish that this
attempt caused a change or that unrelated changes were approved.

All these checks are offline. No live source/query contract, mutability rule,
automatic rollback or account-level receipt operation is introduced. Final
artifact ownership and test discovery remain subject to the separate agreement.
