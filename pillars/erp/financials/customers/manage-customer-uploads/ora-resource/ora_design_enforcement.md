# Customers Design Enforcement


## Enforcement Order

| Order | Gate | Purpose |
|---|---|---|
| 1 | Known input/package checks | Prevent malformed or source-proven invalid input |
| 2 | Existing-target intent | Distinguish new entities, reuse and intended updates |
| 3 | Business-validation disclosure | Allow explicit candidate-bound loader reliance for eligible missing evidence |
| 4 | Central preview and approval | Bind exact ZIP, environment, registration, arguments and intended effects |

## Design Rules

| Rule | Applies When | Severity | Required Lookup | What Blocks Preview | Fix Allowed | User Guidance |
|---|---|---|---|---|---|---|
| Exact entity effects | Before live preview | Error | resolve_customer_existing_targets | Ambiguous identity or unreviewed create/update effects | No silent selection | Resolve intended effects without imposing blanket creation-only scope |
| Receipt assignment reuse | PAYMENT_METHOD_NAME supplied for an existing account/site | Error |  | A before-phase API receipt review reports a visible period conflict or incomplete applicable period evidence | Resolve the assignment intent and evidence; no automatic replay or removal of supplied fields | Compare the exact account/site/method periods through the selected API collection step and independent ownership checks. A matching after-state is not permission to repeat a receipt assignment |
| Loader-validation acceptance | Named business gap applies | Warning |  | Missing business evidence alone does not block offline preview; runtime acceptance is separate | Explicit user decision only | Present uncertainty and possible rejection/partial persistence; never claim evidence confirmed |
| Immutable approval | Before central submission | Error |  | Changed ZIP, contract, gaps, operation, environment, registration, arguments or preview | New preview and decision | An acceptance record is not authentication or import approval |
| Central ownership | Every execution | Error |  | Unverified routing, failed required authentication/preflight, known access denial or missing approval for the selected core recovery contract | Resolve through declared central workflow | Untested upload access remains explicit in a non-mutating preview; core/server authorization applies at execution. No task-local UCM, REST-write, ESS or retry fallback |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| resolve_customer_existing_targets | Before live preview | Exact identities and requested effects; post-load persisted readback contract | ora_reference_lookups.md |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| ARCU.DESIGN | decision | 50 | design_enforcement | passed->ARCU.EXECUTION_GATE;blocked->ARCU.ERROR | ARCU.MATCH | stop | Before central import handoff |

<!-- E2E-DISCOVERY:AR-LOCATION-PROFILE-VERSIONING-26D -->
## Location-profile versioning during reconciliation

Reviewed 26D `HZ_CIMP_ADDRESS_PKG` provides the location-profile effect
boundary. `LOCATION_UPD_LOC_PROFILE` (lines 1398-1509) closes the current
profile for successfully staged location-update rows and inserts a profile
with a new sequence-generated `LOCATION_PROFILE_ID`, the same `LOCATION_ID`,
current location values and new audit stamps. `LOC_UPD_LOC_PROFINTRADAY`
(lines 1521-1642) handles the separate same-day versioning path. These routines
can therefore change the profile ID and profile CreationDate even when the
logical location and requested address values remain the same. An account-only
business change in a full Customers row does not imply that the loader performs
no location/profile or audit writes.

During supported API reconciliation, distinguish the logical LocationId from
the current LocationProfileId. Retain raw differences. Check the exact resolved
location/party/site owners and parents, all supplied values, API-visible omitted
values, current profile/address values, and the associated terminal import.
When those checks match and observed changes are limited to the source-backed
profile version and technical audit fields, explain the versioning effect and
finish the scoped business-outcome review. A new profile ID or its creation
timestamp alone is not an unresolved wider-effect concern or a reason to demand
an unavailable full-history query.

This does not authorize ignoring a changed logical owner, unexpected address
or other business value, conflicting profile parent, incomplete collection,
unexplained raw difference, or a concrete requirement about historical versions.
Such concerns still require review. Current-profile reads do not certify all
historical storage; disclose that limit rather than claiming hidden values were
preserved. Audit timestamps and internal RequestId are not proof of actor
causality or substitutes for ESS request association. No SQL, retry, additional
mutation or Run Book completion is authorized by this explanation.

Source trace: reviewed 26D `hz_cimp_address_pkg`, routines and ranges above;
retained source SHA-256 `b62cf288f90e7a78fc0834ab7501f84277a9b00d2c1d4e980b86691117095af0`.
