# Adaptive Search Publish Dependency Readiness

For the separately approved ABO initialization operation, follow
[ora_abo_initialization.md](ora_abo_initialization.md). Known catalog blocker
and consumed parent preparation permission precede Full workbook generation;
separate Core approval precedes submission. Exact Full load/job success and
fresh catalog presence precede a new Partial Publish proposal, not ESS.
The fixed-pair dependent order below describes normal Partial Publish only.

## Required Dependency Order for Standalone Requests

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Environment identity | Confirm the exact Fusion environment and non-production intent |
| 2 | Authentication and privilege | Confirm valid authentication and Adaptive Search publish authorization |
| 3 | Document-object catalog and active objects | Call the Entities endpoint with only `isDocument=true` as the catalog filter for every request and distinguish a nonempty catalog from a null or empty new-environment result; recognized CPQ aliases bypass catalog validation but not this new-environment check and resolve directly to both CPQ entity names when the response is nonempty |
| 4 | Publish concurrency | Confirm no publish is WAIT, RUNNING, or PAUSED after entity resolution |
| 5 | Embedded API contract | Semantically validate the bundled publish contract and map the payload |
| 6 | Combined confirmation | Show one combined review and obtain the single authorization for the publish |

## Fusion ABO Dependent Dependency Order

| Sequence | Dependency | What must happen |
|---|---|---|
| 1 | Verified CPQ predecessor | Exact request success and fresh settings/process/function GET readbacks. |
| 2 | Core handoff preparation | Fixed pair, target and entity/concurrency checks; Core workbook handoff followed by persisted-preflight/Task Hook handoff for its confirmed workbook. |
| 3 | Parent provenance | Exact v2 workflow identity and verified predecessor; not publish approval. |
| 4 | Core approval | Ordered evidence-backed rules and separate current preview approval on the persisted Task Hook preview. |
| 5 | Accepted submission | Private receipt checkpoint and opaque operation ID; pause for explicit user status request. |
| 6 | Exact loader success | One user-requested check; pending stops without automatic polling. |
| 7 | Final job readiness | Discover/pin the new job; parent checks once then offers monitoring choice if pending. Repeat job-only ticks at 15 seconds only on current consent; return exact final readiness, no ESS here. |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| AS.ENV | Fusion environment identity | Yes | Always | Verify | Runtime environment configuration | Environment preflight | Prevents publishing to the wrong tenant | Confirm the hostname and environment purpose | environment |
| AS.AUTH | Publish privilege | Yes | Before preview | Verify | Fusion authorization response | Approved authentication service | Publishing is configuration-changing | Use an authorized implementation account without exposing credentials | authorization status |
| AS.ENTITIES | Document-object catalog discovery, display-name validation, internal-name mapping, active-object derivation, and new-environment detection | Conditional | Before publish-status preflight | Lookup | GET entities with isDocument=true and without isEnabled | Document objects catalog lookup | A nonempty response supplies labels, mappings, and active objects; HTTP 400 `Could not find active meta model`, a null response, or an empty result selects the OOTB full-publish fallback | Correct display names absent from a nonempty response; other HTTP errors stop | valid object display names, active object display names, mapped internal names, lookup outcome, and publish mode |
| AS.ACTIVE_JOB | Existing publish state | Yes | After validation and before the combined confirmation | Lookup | GET publishStatus | Adaptive Search latest-status lookup | Concurrent publishes are rejected; HTTP 404 with exactly `{"Error":"Cannot parse null string"}` means no prior publish | Wait until the existing job is terminal; continue on the recognized no-prior-publish response | latest jobId and status, or no-prior-publish result |
| AS.COMBINED_CONFIRM | Final selection and publish authorization | Yes | After current-status check and payload mapping | Verify | User response to combined confirmation table | Combined confirmation gate | Prevents a publish without one current, fully informed approval | Confirm or supply a revised nonempty list | final approval |
| AS.CONTRACT | Embedded publish action contract | Yes | Before payload mapping | Verify | `scripts/validate_publish_contract.py --json` over ora-resource/ora_publish_contract.json | Embedded contract verifier | Validates the declared contract ID, method, endpoint, JSON content type, `Preference: transient` header, Partial Publish schema, and Full Publish schema | Stop only if the bundled file is missing, malformed, or fails semantic validation | method, endpoint, headers, publish mode, body, and validated contract binding |
| AS.ABO.AUTHORIZATION | Fusion ABO parent provenance | Conditional | Before companion preflight | Verify | V2 workflow and verified CPQ checkpoint | Companion validator | Prevents cross-target/operation reuse | Stop on mismatch | project, target, fixed pair, workflow identity, exact predecessor |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Ready | All mandatory dependencies are satisfied | Yes, lookup only until approval |
| Lookup | Current publish status is unknown | Yes, read-only lookup |
| Blocked | Environment, privilege, concurrency, or embedded contract validation fails | No |
