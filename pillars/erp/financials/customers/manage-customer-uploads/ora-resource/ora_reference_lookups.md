# Customers Reference Lookups


## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| resolve_customer_existing_targets | ARCU.MATCH after dependency inputs are supplied | Exact candidate bytes and operation/environment; raw API before collection and explicit API target plan for existing targets, or supplied identity/ownership/target-plan documents | Recompute raw API projections then customer_api_target_review.analyze for existing targets, or customer_target_review.analyze for detailed supplied evidence; require complete bound source/reference/number observations and unambiguous ownership/intent | Seven entity target findings, parent/purpose findings, number collision findings and evidence fingerprints; preserve candidate bytes | Missing or ambiguous observations return blocked; new/partial API hierarchies need their separate review; an existing reference cannot satisfy create intent; never select first or authorize import |

## Assisted Evidence Boundary

ARCU.MATCH uses `evaluate_result` on supplied read-only evidence. It performs no
Fusion query itself. The selected route collects raw observations before this node.
ARCU.DEPENDENCIES requires the raw candidate-bound documents described in
[the assisted evidence contract](../references/assisted-evidence.md). A developer
may supply reviewed FSCM Publisher evidence for the initial campaign, as agreed
with the user. Preserve query scope, every returned row, completeness and capture
provenance; a report claiming that checks passed is not raw evidence. The API
existing-target evaluator and scope/effect reviewers are distinct components;
their availability does not certify all runtime scenarios or remove field/attempt
reviews. SQL is never a functional prerequisite.

The evaluator checks target identity and ownership. ARCU.DESIGN separately
reviews intended field effects, defaults and eligible loader-validation gaps.
Post-import value/effect evidence belongs after submission, not in this resolver.

## Source Findings

The 26D product matches an existing account-level profile through HZ_CUSTOMER_PROFILES_F, HZ_CUST_ACCOUNTS and HZ_ORIG_SYS_REFERENCES and can switch an interface row from I to U inside ESSCREATE. This establishes an existing-profile update path, not every field's mutability or a ready runtime endpoint. Source SQL is evidence, not authorization to run ad hoc queries from the task.

The 26D source at lines 13209–13215 resolves the exact source-system display name to its registered code before populating HZ interfaces. Do not assume the supplied ADE control's punctuation-stripped name equals the registered code. The profile-update existence query at lines 14618–14629 checks reference dates but does not filter reference status; retain inactive references for that review.

The supplied ADE control and target template agree on all 87 inputs. Blank party, account and account-site references fall back to PARTY_NUMBER, ACCOUNT_NUMBER and PARTY_SITE_NUMBER respectively. The generated party-site key uses PARTY_NUMBER concatenated with `-partysite-` and LOCATION_ORIG_SYSTEM_REFERENCE. These lookup derivations do not modify the input file. See `references/identity-evidence.md` for precedence, whitespace handling, provenance and limitations. Parent ownership and complete persisted-value coverage remain separate checks.

The task-local `scripts/customer_identity_review.py` classifies supplied scoped evidence. `scripts/customer_target_review.py` combines that classification with before-ownership evidence and proposed target intent. Missing queries are unknown, duplicates are ambiguous, and zero records do not authorize creation. Neither helper establishes every field's mutability or completes the execution gate.

## Supported REST Evidence Components

The scoped Customer Account Sites LOV GET in `references/rest-reconciliation.md` can corroborate account/site identity through the shared REST client. Its display identifiers do not replace original-system references. The existing-target API route combines full reference observations, independent numbers and hierarchy through shared collectors and raw replay. Qualify the actual composed journey before claiming runtime completion; deeper supplied evidence remains developer-only.

The same reference documents the separately qualified `hubSourceSystemReferences` GET and offline reference classifier. It can corroborate seven entity IDs using the full source-code, owner-entity and reference tuple. Keep missing/duplicate matches and date-only precision visible; it does not complete ownership, values, source-name resolution or existing-target authorization. Developer SQL remains test-only and is not a fallback functional route.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| ARCU.MATCH | decision | 40 | evaluate_result | resolved->ARCU.DESIGN;blocked->ARCU.ERROR | ARCU.DEPENDENCIES | stop | Classify supplied candidate-bound before-state evidence; no live lookup or import authorization |
