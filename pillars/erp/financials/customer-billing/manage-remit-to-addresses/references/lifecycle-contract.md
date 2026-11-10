# Remit-to lifecycle contract

Reviewed 2026-09-15. Source series: FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64.
These are source-backed offline capabilities, not evidence of a successful
import in any target environment. No direct SOAP, entity REST or database
execution is permitted by this task.

## Supported boundary

| Request | Adapter behavior |
|---|---|
| New destination and/or new receipt-from coverage | Create using the existing parent/child contract; new criteria use Active (A) |
| Activate or inactivate existing customer coverage immediately | Update only AR_REMIT_TO_ADDRESS.Status to A or I against one exact exported AltCriteria key |
| Multiple status updates; mixed creates and status updates | One deterministic package after every row passes; unchanged parent dependencies appear once |
| Already-satisfied update | No candidate; report the satisfied requirement. In a mixed request, disclose its exclusion and obtain a new complete preview before packaging the remaining changes |
| Reverse a status update | Restore the baseline status only if the fresh current status still equals the submitted forward value; preserve all other current values |
| Change postal address, descriptions, criteria identity, or clear fields | Retain the requested intent and surface the specific missing field-level FSM contract; never silently create instead |
| Physically delete a location or criterion | Unsupported by the selected task CSV import route; removing rows from a package does not delete persisted records |
| End-date | No effective-end-date attribute exists in the reviewed two-BO CSV contract. Ask whether immediate coverage inactivation was intended, but never substitute it without a revised business instruction |

Preserve exact nullable key components, parent references, child SetCode, all
non-requested business fields, and baseline rows. Clear the five service-owned
audit columns only in the candidate. Require target-set authorization evidence.
Physical deletion must never be simulated by Status D. The supported adapter
domain A/I is narrower than the full CODE_STATUS lookup.

## Evidence register

- **SRC-REMIT-CODE-STATUS**: AR lookup seed data, lines 6069–6102: CODE_STATUS includes A / Active, D / Deleted, I / Inactive. Criteria table, lines 262–268 links STATUS to CODE_STATUS. Retrieved through CodeSearch MCP; not inferred from observed target values.
- **SRC-REMIT-CRITERIA-VO / EO**: Migration criteria VO maps Status to the mutable criteria entity; criteria EO declares required one-character Status and the AltCriteria identity. This does not authorize key changes.
- **SRC-REMIT-MIGRATION-UPDATE-TEST**: Migration update test, lines 101–114 and 214: export, perturb underlying criteria, reimport using MigratorHelper. Its fixture uses STATUS=Y as a perturbation, not a valid business status. Source review is not a claim that this upstream test was executed here.
- **SRC-REMIT-AM-IMPL / LOCATION-VO**: import derives parent identity and calls MigratorHelper.readXML; LocationPEO is read-only/reference. Existing shared-location reuse does not apply additional postal changes. See the original reviewed source identities in the task rules.
- **SRC-FSM-CSV-NO-DELETE-26C**: [Oracle 26C Compare Task Setup Data](https://docs.oracle.com/en/cloud/saas/applications-common/26c/oafsm/compare-task-setup-data.html) explicitly states that CSV import does not delete existing records. This route limitation is distinct from UI or service deletion capabilities.

## Testing and release boundary

The task-local tests exercise package generation, independent validation,
determinism, status round trips, preservation, concurrency, and mixed/bulk
preflight using isolated synthetic exports. They do not prove business address
validation, privileges, target patch parity, or a completed live import.

The full campaign remains not live-verified. Project-specific evidence qualifies
criteria creation and Status changes under an existing destination. New postal
creates now use the split in [postal-validation-contract.md](postal-validation-contract.md):
local business-input and known-match checks, then application-owned country/address
validation and location resolution through normal FSM import, followed by exact
fresh-export reconciliation. Global shared-location enumeration is not a blanket
precondition, and global uniqueness or postal deliverability is never claimed.
The dated historical normal-path create, parent/child, mixed and status-reversal
evidence is summarized in [release-scope-and-coverage.md](release-scope-and-coverage.md).
It is narrower than the full catalog and does not certify every country or release.
Use that register for the current per-variant disposition; do not treat an older
pending-live statement or a successful probe as the complete coverage record.

Each expanded live campaign needs its own confirmed design and supported cleanup
or explicitly approved retained-state policy. Prior campaign approval does not
authorize new destinations. A live run still needs fresh exact-task evidence,
real authorization, approval through the selected execution owner, successful
process review and fresh-export reconciliation. Do not publish a blanket
ready-for-live flag from a narrower successful campaign.

The adapter's `cleanupPolicy.retainedStateException` declares this exception for
the test orchestrator; it is not an automatic waiver in the package builder.
It is disabled by default and requires nonproduction scope, explicit retention
consent and a bounded destination inventory, the confirmed campaign design and
normal import authorization. Newly created coverage must finish Inactive;
pre-existing test coverage must be restored without overwriting concurrent edits.
Retaining destinations does not satisfy a catalog assertion requiring their
absence and must never be reported as deletion or successful create rollback.
