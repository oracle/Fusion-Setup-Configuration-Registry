# Release scope and catalog coverage dispositions

Evidence review: 2026-09-21.

## Release claim

This package supports creation of remit-to destinations and receipt-from criteria, plus immediate Active/Inactive (A/I) updates to one exact existing criterion. Multiple creates and status updates may share a package after whole-request preflight. Reverse update restores a status only when fresh evidence still matches the forward change. This is **not** general-purpose address maintenance or all-operation certification.

Postal field edits, key changes, explicit clearing, physical deletion, scheduled end-dating and undeclared DFF/GDF processing remain outside this version's implemented contract. Preserve those intents and ask business clarifications where useful; a customer's answer does not supply a missing product contract. Do not treat a CSV limitation as a statement about all UI capabilities.

Runtime code remains environment-independent. The historical live evidence qualifies only release **11.13.26.10.0**, US postal scenarios in one nonproduction environment/selected reference set. Other releases, countries, access policies, deployed flexfields and address validators require target evidence and their own validation. Broad manifest applicability is not broad test certification.

## Evidence levels

| Evidence | What is established | What is not established |
|---|---|---|
| Local regression at source commit 123da9a7ee8d9aebac4e6cd8b6352d68cdf5efc1 | 109 passing tests, five skips; synthetic identity, packaging, A/I preservation, rollback, mixed and 100-row preflight tests | Catalog execution, real NLP routing, live 100-row volume or all countries |
| Historical live attachment, page version 4 | Five added scenarios C02/L01/L02/L03/L04: destination creation, parent/child creation, bounded multi-parent create, mixed create/status change and status restoration; 22 formal requirements | A fresh live run for subsequent commits or completion of all catalog variants |
| Continuation live campaign, page version 5 | Nine verified phases, 264 passing requirements, zero final mismatches; exact and bulk A/I updates/restoration, creates, parent/child create, 97-parent bulk create, mixed create/update and cleanup | All 236 catalog variants, a single 100-row live import, physical deletion, or complete UI inspection of every row |
| Current catalog disposition | Every one of 236 variant IDs is accounted for | Disposition completeness is not execution completeness or merge approval |

The historical evidence is on the testing page. Attachment: `manage-remit-to-addresses-evidence-20260917.zip`; SHA-256 `52a6677351f579b964d99833acd3473ddc2c400b2d3304a5ed3d6223f1739e37`. It contains 118 members. Only the dated evidence scope is carried forward; no customer records, credentials or machine-specific paths are copied into this skill.

Five generic tests were skipped because the adapter declares no transient create fields, no override-eligible unresolved update fields, no generic choice contracts, no generic string-length constraints, and no unresolved identity keys. A/I rules have separate task tests. Local maximum-length coverage is not established by those skips.

### Continuation campaign and repair (2026-09-21)

The same testing page, version 5, documents cases 13–21 with prompts, follow-ups,
designs, import results and fresh-export checks. Evidence attachment:
`manage-remit-to-addresses-evidence-20260921.zip` (212 members), SHA-256
`d7dcad9aad0d97f6a09fc3c3e3952bb3592678b1b49f1d04eb9903facc08a966`.
This is historical live evidence for the tested working-tree implementation;
the final-commit premerge report separately binds regression results to Git.

| Case | Verified phase | Passing requirements |
|---|---|---:|
| 13 | Exact criteria inactivation | 4 |
| 14 | Restore the exact criterion | 4 |
| 15 | Activate five existing criteria | 20 |
| 16 | Restore the five criteria | 20 |
| 17 | Create one destination | 2 |
| 18 | Create destination and coverage, corrected retry | 6 |
| 19 | Create 97 destinations in one import | 194 |
| 20 | Mixed destination create and exact status update | 6 |
| 21 | Restore existing status and inactivate new coverage | 8 |

Ten attempts were retained, including the failed first attempt for case 18.
Fusion rejected duplicate coverage under a different parent (RA_REMIT_TOS_U1).
A fresh export established no non-audit changes after that failure. The repair
adds set-wide coverage collision preflight and six identity/business regressions;
see [coverage uniqueness](coverage-uniqueness.md). The retry used clarified,
distinct coverage, a new candidate and authorization; it was not a resubmission.

Final reconciliation confirmed all original non-audit rows restored, 100 new
destinations retained under explicit bounded test consent and one new criterion
Inactive. The 100 destinations were created across four imports (1 + 1 + 97 + 1),
not one 100-row live import. Retention is **not deletion or create rollback** and
does not satisfy catalog absence assertions. UI evidence is a sampled destination
and coverage view; fresh exports establish the full requirement matrix and status.
No new authorization follows from this historical consent.

These targeted results do not promote an entire catalog variant to Passed.
The machine-readable register preserves the outstanding per-variant prerequisites.
This package has not established exhaustive catalog, all-country, cross-OS or
multi-release certification. Final merge readiness still requires a passing
repository audit and the designated human reviews.

## Disposition rules

[coverage-disposition.json](coverage-disposition.json) is the machine-readable review register, bound to the catalog's canonical JSON SHA-256 (sorted keys, compact separators, ASCII escapes). This ignores checkout line-ending/indentation changes but detects semantic catalog changes. It does not replace or alter campaign state, approval policy, adapter capabilities or test-run evidence.

- **Blocked (235):** not verified as the complete catalog variant, or waiting for its stated fixture/evidence prerequisite. This does not mean 235 observed product failures. Related unit tests and narrower historical scenarios remain supporting evidence only.
- **Not applicable (1):** SM-02-B's positive effective-date chronology has no implemented date operation in the reviewed contract. End-date clarification/refusal is still a valid negative test.
- **Passed (0), failed (0):** no full catalog-ID-bound execution records were verified in this documentation review. Do not invent them from `automation.status: ready`.
- Record a pass only with exact prompt/fixture, follow-ups when applicable, normalized design, expected stopping result, assertions and required artifacts. Live variants additionally need governed import/process evidence and fresh-export reconciliation; unsupported create cleanup requires an explicit retained-state policy.
- A catalog change invalidates this snapshot. Update every affected disposition and evidence binding; rerun regression, rule compilation and the exact-commit premerge audit. Do not mark unrun variants not applicable merely to close coverage.

## Remaining prerequisites and next actions

| Reason code | Why still open / excluded | Next action |
|---|---|---|
| PROMPT_TRANSCRIPT | No complete catalog-ID-bound agent transcript proves routing, all follow-up questions/answers and the expected stopping rule. | Run this variant through the Implementation Router and task skill; retain the unchanged prompt, follow-ups, final classification and absence/presence of the expected candidate. |
| FIELD_MATRIX | Aggregate unit results are available, but no catalog-ID-bound field fixture and full assertion result were verified for this individual variant. | Execute the exact named field/identity variant with a compatible baseline and record normalization, candidate or rejection, plus every expected assertion. |
| RESOLVER_MATRIX | No catalog-ID-bound authoritative zero/one/many-match resolver evidence was verified for this variant; task exports do not prove exhaustive reference domains. | Resolve the listed task-owned prerequisite from authorized FSM evidence; record exact match-count outcomes. If authority remains unavailable, retain the blocker rather than inventing a direct API/DB route. |
| STATUS_CAMPAIGN_FIXTURE | Status-update/rollback unit coverage exists, but the catalog campaign fixture is still conditional and its complete per-variant execution evidence is absent. | Register the exact-key A/I fixture and execute this variant. A live rollback requires a successful forward import, separately governed reverse candidate, fresh exports and reconciliation. |
| CREATE_RETENTION | The catalog live-create variant has no declared supported removal path or candidate-specific governed retained-state policy. Historical retained-state approvals do not authorize another run. | Obtain a supported cleanup declaration or explicit retained-state authorization for the exact scenario, then execute the normal task route and retain process results plus fresh-export reconciliation. |
| OWNER_GATES | No complete campaign-owner evidence binds this variant's confirmation/approval invalidation, process state, or warning policy to an immutable design/candidate. | Exercise the relevant Run Book/Data Loader or tester gate with controlled fixtures; record prior and changed fingerprints, process identity and expected no-resubmit/no-handoff outcome. |
| CATALOG_EXECUTION | Related unit tests are supporting evidence only; the complete catalog variant was not separately executed and its required evidence was not bound to its ID. | Execute this exact catalog variant and retain every required artifact and assertion. Do not promote related synthetic tests to live or conversation-level evidence. |
| REPORT_RENDER | The existing historical page is not proof of this catalog report-rendering variant's complete acceptance checks. | Render the full campaign from actual run records and validate inventory, prompts, follow-ups, artifact references and dispositions. Publish only under separately authorized classification/destination. |
| NO_EFFECTIVE_DATE | This generic variant expects valid/invalid effective-date chronology, but the reviewed two-BO CSV contract exposes no supported scheduled end-date operation. | Keep this positive chronology variant not applicable to the declared release scope. Continue testing end-date request clarification under the lifecycle negative cases; never substitute immediate inactivation silently. |

## Complete variant register

Titles and execution classes below identify catalog scenarios, not new execution results. Each row's reason code resolves to the exact prerequisite above; variant-specific catalog blockers and supporting unit tests are retained in JSON.

### RT-01 — Exact-task routing

| Variant | Scenario | Execution class | Disposition | Reason |
|---|---|---|---|---|
| RT-01-A | Exact task | static | Blocked | PROMPT_TRANSCRIPT |

### RT-02 — Ambiguous and multi-task input

| Variant | Scenario | Execution class | Disposition | Reason |
|---|---|---|---|---|
| RT-02-A | Missing task | static | Blocked | PROMPT_TRANSCRIPT |
| RT-02-B | Multiple tasks | static | Blocked | PROMPT_TRANSCRIPT |

### RT-03 — Unsupported route and mutation requests

| Variant | Scenario | Execution class | Disposition | Reason |
|---|---|---|---|---|
| RT-03-A | Direct write | static | Blocked | PROMPT_TRANSCRIPT |
| RT-03-B | Hard delete | static | Blocked | PROMPT_TRANSCRIPT |

### RT-04 — Broad-document selected-task extraction

| Variant | Scenario | Execution class | Disposition | Reason |
|---|---|---|---|---|
| RT-04-A | Selected task inside a broad rollout note | static | Blocked | PROMPT_TRANSCRIPT |

### RT-05 — Action-specific workflow-owner routing

| Variant | Scenario | Execution class | Disposition | Reason |
|---|---|---|---|---|
| RT-05-A | Export request | static | Blocked | PROMPT_TRANSCRIPT |
| RT-05-B | Prepare and review request | static | Blocked | PROMPT_TRANSCRIPT |
| RT-05-C | Import request | static | Blocked | PROMPT_TRANSCRIPT |
| RT-05-D | Monitoring request | static | Blocked | PROMPT_TRANSCRIPT |
| RT-05-E | Verification request | static | Blocked | PROMPT_TRANSCRIPT |

### BR-01 — Complete field-contract matrix

| Variant | Scenario | Execution class | Disposition | Reason |
|---|---|---|---|---|
| BR-FIELD-AR_REMIT_TO_LOCATION-SetCode-VALID | Accept source-backed identity key AR_REMIT_TO_LOCATION.SetCode | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-SetCode-INVALID | Reject invalid identity key AR_REMIT_TO_LOCATION.SetCode | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-SetCode-KEY-MUTATION | Reject identity key mutation for AR_REMIT_TO_LOCATION.SetCode | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-TerritoryCode-VALID | Accept source-backed identity key AR_REMIT_TO_LOCATION.TerritoryCode | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-TerritoryCode-INVALID | Reject invalid identity key AR_REMIT_TO_LOCATION.TerritoryCode | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-TerritoryCode-KEY-MUTATION | Reject identity key mutation for AR_REMIT_TO_LOCATION.TerritoryCode | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-Address1-VALID | Accept source-backed identity key AR_REMIT_TO_LOCATION.Address1 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-Address1-INVALID | Reject invalid identity key AR_REMIT_TO_LOCATION.Address1 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-Address1-KEY-MUTATION | Reject identity key mutation for AR_REMIT_TO_LOCATION.Address1 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-OrigSystemReference-VALID | Accept source-backed identity key AR_REMIT_TO_LOCATION.OrigSystemReference | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-OrigSystemReference-INVALID | Reject invalid identity key AR_REMIT_TO_LOCATION.OrigSystemReference | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-OrigSystemReference-KEY-MUTATION | Reject identity key mutation for AR_REMIT_TO_LOCATION.OrigSystemReference | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-ShortDescription-CREATE-UNRESOLVED | Block unproven create field AR_REMIT_TO_LOCATION.ShortDescription | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-Description-CREATE-UNRESOLVED | Block unproven create field AR_REMIT_TO_LOCATION.Description | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-PostalCode-VALID | Accept source-backed identity key AR_REMIT_TO_LOCATION.PostalCode | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-PostalCode-INVALID | Reject invalid identity key AR_REMIT_TO_LOCATION.PostalCode | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-PostalCode-KEY-MUTATION | Reject identity key mutation for AR_REMIT_TO_LOCATION.PostalCode | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-State-VALID | Accept source-backed identity key AR_REMIT_TO_LOCATION.State | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-State-INVALID | Reject invalid identity key AR_REMIT_TO_LOCATION.State | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-State-KEY-MUTATION | Reject identity key mutation for AR_REMIT_TO_LOCATION.State | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-City-VALID | Accept source-backed identity key AR_REMIT_TO_LOCATION.City | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-City-INVALID | Reject invalid identity key AR_REMIT_TO_LOCATION.City | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-City-KEY-MUTATION | Reject identity key mutation for AR_REMIT_TO_LOCATION.City | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-CreatedBy-AUDIT | Reject or clear system-managed AR_REMIT_TO_LOCATION.CreatedBy | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-CreationDate-AUDIT | Reject or clear system-managed AR_REMIT_TO_LOCATION.CreationDate | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-LastUpdatedBy-AUDIT | Reject or clear system-managed AR_REMIT_TO_LOCATION.LastUpdatedBy | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-LastUpdateDate-AUDIT | Reject or clear system-managed AR_REMIT_TO_LOCATION.LastUpdateDate | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-LastUpdateLogin-AUDIT | Reject or clear system-managed AR_REMIT_TO_LOCATION.LastUpdateLogin | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-SetName-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.SetName | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-Address2-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.Address2 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-AddrElementAttribute2-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.AddrElementAttribute2 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-AddrElementAttribute3-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.AddrElementAttribute3 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-GlobalAttribute1-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.GlobalAttribute1 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-GlobalAttribute10-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.GlobalAttribute10 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-GlobalAttribute11-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.GlobalAttribute11 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-GlobalAttribute12-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.GlobalAttribute12 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-GlobalAttribute13-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.GlobalAttribute13 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-GlobalAttribute14-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.GlobalAttribute14 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-GlobalAttribute15-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.GlobalAttribute15 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-GlobalAttribute16-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.GlobalAttribute16 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-GlobalAttribute17-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.GlobalAttribute17 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-GlobalAttribute18-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.GlobalAttribute18 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-GlobalAttribute19-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.GlobalAttribute19 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-GlobalAttribute2-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.GlobalAttribute2 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-GlobalAttribute20-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.GlobalAttribute20 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-GlobalAttribute3-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.GlobalAttribute3 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-GlobalAttribute4-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.GlobalAttribute4 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-GlobalAttribute5-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.GlobalAttribute5 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-GlobalAttribute6-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.GlobalAttribute6 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-GlobalAttribute7-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.GlobalAttribute7 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-GlobalAttribute8-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.GlobalAttribute8 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-GlobalAttribute9-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.GlobalAttribute9 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-GlobalAttributeCategory-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.GlobalAttributeCategory | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-GlobalAttributeDate1-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.GlobalAttributeDate1 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-GlobalAttributeDate2-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.GlobalAttributeDate2 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-GlobalAttributeDate3-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.GlobalAttributeDate3 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-GlobalAttributeDate4-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.GlobalAttributeDate4 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-GlobalAttributeDate5-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.GlobalAttributeDate5 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-GlobalAttributeNumber1-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.GlobalAttributeNumber1 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-GlobalAttributeNumber2-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.GlobalAttributeNumber2 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-GlobalAttributeNumber3-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.GlobalAttributeNumber3 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-GlobalAttributeNumber4-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.GlobalAttributeNumber4 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-GlobalAttributeNumber5-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.GlobalAttributeNumber5 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-County-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.County | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-Address3-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.Address3 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-Address4-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.Address4 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_LOCATION-Province-BLOCKED | Block unresolved reference field AR_REMIT_TO_LOCATION.Province | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-AR_REMIT_TO_LOCATION.SetCode-VALID | Accept source-backed identity key AR_REMIT_TO_ADDRESS.AR_REMIT_TO_LOCATION.SetCode | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-AR_REMIT_TO_LOCATION.SetCode-INVALID | Reject invalid identity key AR_REMIT_TO_ADDRESS.AR_REMIT_TO_LOCATION.SetCode | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-AR_REMIT_TO_LOCATION.SetCode-KEY-MUTATION | Reject identity key mutation for AR_REMIT_TO_ADDRESS.AR_REMIT_TO_LOCATION.SetCode | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-AR_REMIT_TO_LOCATION.TerritoryCode-VALID | Accept source-backed identity key AR_REMIT_TO_ADDRESS.AR_REMIT_TO_LOCATION.TerritoryCode | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-AR_REMIT_TO_LOCATION.TerritoryCode-INVALID | Reject invalid identity key AR_REMIT_TO_ADDRESS.AR_REMIT_TO_LOCATION.TerritoryCode | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-AR_REMIT_TO_LOCATION.TerritoryCode-KEY-MUTATION | Reject identity key mutation for AR_REMIT_TO_ADDRESS.AR_REMIT_TO_LOCATION.TerritoryCode | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-AR_REMIT_TO_LOCATION.Address1-VALID | Accept source-backed identity key AR_REMIT_TO_ADDRESS.AR_REMIT_TO_LOCATION.Address1 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-AR_REMIT_TO_LOCATION.Address1-INVALID | Reject invalid identity key AR_REMIT_TO_ADDRESS.AR_REMIT_TO_LOCATION.Address1 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-AR_REMIT_TO_LOCATION.Address1-KEY-MUTATION | Reject identity key mutation for AR_REMIT_TO_ADDRESS.AR_REMIT_TO_LOCATION.Address1 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-AR_REMIT_TO_LOCATION.OrigSystemReference-VALID | Accept source-backed identity key AR_REMIT_TO_ADDRESS.AR_REMIT_TO_LOCATION.OrigSystemReference | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-AR_REMIT_TO_LOCATION.OrigSystemReference-INVALID | Reject invalid identity key AR_REMIT_TO_ADDRESS.AR_REMIT_TO_LOCATION.OrigSystemReference | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-AR_REMIT_TO_LOCATION.OrigSystemReference-KEY-MUTATION | Reject identity key mutation for AR_REMIT_TO_ADDRESS.AR_REMIT_TO_LOCATION.OrigSystemReference | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-AR_REMIT_TO_LOCATION.PostalCode-VALID | Accept source-backed identity key AR_REMIT_TO_ADDRESS.AR_REMIT_TO_LOCATION.PostalCode | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-AR_REMIT_TO_LOCATION.PostalCode-INVALID | Reject invalid identity key AR_REMIT_TO_ADDRESS.AR_REMIT_TO_LOCATION.PostalCode | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-AR_REMIT_TO_LOCATION.PostalCode-KEY-MUTATION | Reject identity key mutation for AR_REMIT_TO_ADDRESS.AR_REMIT_TO_LOCATION.PostalCode | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-AR_REMIT_TO_LOCATION.State-VALID | Accept source-backed identity key AR_REMIT_TO_ADDRESS.AR_REMIT_TO_LOCATION.State | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-AR_REMIT_TO_LOCATION.State-INVALID | Reject invalid identity key AR_REMIT_TO_ADDRESS.AR_REMIT_TO_LOCATION.State | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-AR_REMIT_TO_LOCATION.State-KEY-MUTATION | Reject identity key mutation for AR_REMIT_TO_ADDRESS.AR_REMIT_TO_LOCATION.State | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-AR_REMIT_TO_LOCATION.City-VALID | Accept source-backed identity key AR_REMIT_TO_ADDRESS.AR_REMIT_TO_LOCATION.City | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-AR_REMIT_TO_LOCATION.City-INVALID | Reject invalid identity key AR_REMIT_TO_ADDRESS.AR_REMIT_TO_LOCATION.City | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-AR_REMIT_TO_LOCATION.City-KEY-MUTATION | Reject identity key mutation for AR_REMIT_TO_ADDRESS.AR_REMIT_TO_LOCATION.City | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-Country-VALID | Accept source-backed identity key AR_REMIT_TO_ADDRESS.Country | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-Country-INVALID | Reject invalid identity key AR_REMIT_TO_ADDRESS.Country | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-Country-KEY-MUTATION | Reject identity key mutation for AR_REMIT_TO_ADDRESS.Country | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-State-VALID | Accept source-backed identity key AR_REMIT_TO_ADDRESS.State | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-State-INVALID | Reject invalid identity key AR_REMIT_TO_ADDRESS.State | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-State-KEY-MUTATION | Reject identity key mutation for AR_REMIT_TO_ADDRESS.State | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-PostalCodeHigh-VALID | Accept source-backed identity key AR_REMIT_TO_ADDRESS.PostalCodeHigh | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-PostalCodeHigh-INVALID | Reject invalid identity key AR_REMIT_TO_ADDRESS.PostalCodeHigh | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-PostalCodeHigh-KEY-MUTATION | Reject identity key mutation for AR_REMIT_TO_ADDRESS.PostalCodeHigh | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-PostalCodeLow-VALID | Accept source-backed identity key AR_REMIT_TO_ADDRESS.PostalCodeLow | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-PostalCodeLow-INVALID | Reject invalid identity key AR_REMIT_TO_ADDRESS.PostalCodeLow | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-PostalCodeLow-KEY-MUTATION | Reject identity key mutation for AR_REMIT_TO_ADDRESS.PostalCodeLow | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-LastUpdateDate-AUDIT | Reject or clear system-managed AR_REMIT_TO_ADDRESS.LastUpdateDate | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-LastUpdatedBy-AUDIT | Reject or clear system-managed AR_REMIT_TO_ADDRESS.LastUpdatedBy | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-CreationDate-AUDIT | Reject or clear system-managed AR_REMIT_TO_ADDRESS.CreationDate | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-CreatedBy-AUDIT | Reject or clear system-managed AR_REMIT_TO_ADDRESS.CreatedBy | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-LastUpdateLogin-AUDIT | Reject or clear system-managed AR_REMIT_TO_ADDRESS.LastUpdateLogin | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-Status-VALID | Accept source-backed source-backed create input field AR_REMIT_TO_ADDRESS.Status | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-Status-INVALID | Reject invalid AR_REMIT_TO_ADDRESS.Status | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-AttributeCategory-BLOCKED | Block unresolved reference field AR_REMIT_TO_ADDRESS.AttributeCategory | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-Attribute1-BLOCKED | Block unresolved reference field AR_REMIT_TO_ADDRESS.Attribute1 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-Attribute2-BLOCKED | Block unresolved reference field AR_REMIT_TO_ADDRESS.Attribute2 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-Attribute3-BLOCKED | Block unresolved reference field AR_REMIT_TO_ADDRESS.Attribute3 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-Attribute4-BLOCKED | Block unresolved reference field AR_REMIT_TO_ADDRESS.Attribute4 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-Attribute5-BLOCKED | Block unresolved reference field AR_REMIT_TO_ADDRESS.Attribute5 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-Attribute6-BLOCKED | Block unresolved reference field AR_REMIT_TO_ADDRESS.Attribute6 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-Attribute7-BLOCKED | Block unresolved reference field AR_REMIT_TO_ADDRESS.Attribute7 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-Attribute8-BLOCKED | Block unresolved reference field AR_REMIT_TO_ADDRESS.Attribute8 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-Attribute9-BLOCKED | Block unresolved reference field AR_REMIT_TO_ADDRESS.Attribute9 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-Attribute10-BLOCKED | Block unresolved reference field AR_REMIT_TO_ADDRESS.Attribute10 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-Attribute11-BLOCKED | Block unresolved reference field AR_REMIT_TO_ADDRESS.Attribute11 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-Attribute12-BLOCKED | Block unresolved reference field AR_REMIT_TO_ADDRESS.Attribute12 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-Attribute13-BLOCKED | Block unresolved reference field AR_REMIT_TO_ADDRESS.Attribute13 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-Attribute14-BLOCKED | Block unresolved reference field AR_REMIT_TO_ADDRESS.Attribute14 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-Attribute15-BLOCKED | Block unresolved reference field AR_REMIT_TO_ADDRESS.Attribute15 | offline | Blocked | FIELD_MATRIX |
| BR-FIELD-AR_REMIT_TO_ADDRESS-SetCode-BLOCKED | Block unresolved reference field AR_REMIT_TO_ADDRESS.SetCode | offline | Blocked | FIELD_MATRIX |

### RD-01 — Reference resolver coverage

| Variant | Scenario | Execution class | Disposition | Reason |
|---|---|---|---|---|
| RD-AR_REMIT_TO_LOCATION-SetCode | Resolve AR_REMIT_TO_LOCATION.SetCode | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-TerritoryCode | Resolve AR_REMIT_TO_LOCATION.TerritoryCode | offline | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-Address1 | Resolve AR_REMIT_TO_LOCATION.Address1 | offline | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-OrigSystemReference | Resolve AR_REMIT_TO_LOCATION.OrigSystemReference | offline | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-PostalCode | Resolve AR_REMIT_TO_LOCATION.PostalCode | offline | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-State | Resolve AR_REMIT_TO_LOCATION.State | offline | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-City | Resolve AR_REMIT_TO_LOCATION.City | offline | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-SetName | Resolve AR_REMIT_TO_LOCATION.SetName | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-Address2 | Resolve AR_REMIT_TO_LOCATION.Address2 | offline | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-AddrElementAttribute2 | Resolve AR_REMIT_TO_LOCATION.AddrElementAttribute2 | offline | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-AddrElementAttribute3 | Resolve AR_REMIT_TO_LOCATION.AddrElementAttribute3 | offline | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-GlobalAttribute1 | Resolve AR_REMIT_TO_LOCATION.GlobalAttribute1 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-GlobalAttribute10 | Resolve AR_REMIT_TO_LOCATION.GlobalAttribute10 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-GlobalAttribute11 | Resolve AR_REMIT_TO_LOCATION.GlobalAttribute11 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-GlobalAttribute12 | Resolve AR_REMIT_TO_LOCATION.GlobalAttribute12 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-GlobalAttribute13 | Resolve AR_REMIT_TO_LOCATION.GlobalAttribute13 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-GlobalAttribute14 | Resolve AR_REMIT_TO_LOCATION.GlobalAttribute14 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-GlobalAttribute15 | Resolve AR_REMIT_TO_LOCATION.GlobalAttribute15 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-GlobalAttribute16 | Resolve AR_REMIT_TO_LOCATION.GlobalAttribute16 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-GlobalAttribute17 | Resolve AR_REMIT_TO_LOCATION.GlobalAttribute17 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-GlobalAttribute18 | Resolve AR_REMIT_TO_LOCATION.GlobalAttribute18 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-GlobalAttribute19 | Resolve AR_REMIT_TO_LOCATION.GlobalAttribute19 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-GlobalAttribute2 | Resolve AR_REMIT_TO_LOCATION.GlobalAttribute2 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-GlobalAttribute20 | Resolve AR_REMIT_TO_LOCATION.GlobalAttribute20 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-GlobalAttribute3 | Resolve AR_REMIT_TO_LOCATION.GlobalAttribute3 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-GlobalAttribute4 | Resolve AR_REMIT_TO_LOCATION.GlobalAttribute4 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-GlobalAttribute5 | Resolve AR_REMIT_TO_LOCATION.GlobalAttribute5 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-GlobalAttribute6 | Resolve AR_REMIT_TO_LOCATION.GlobalAttribute6 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-GlobalAttribute7 | Resolve AR_REMIT_TO_LOCATION.GlobalAttribute7 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-GlobalAttribute8 | Resolve AR_REMIT_TO_LOCATION.GlobalAttribute8 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-GlobalAttribute9 | Resolve AR_REMIT_TO_LOCATION.GlobalAttribute9 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-GlobalAttributeCategory | Resolve AR_REMIT_TO_LOCATION.GlobalAttributeCategory | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-GlobalAttributeDate1 | Resolve AR_REMIT_TO_LOCATION.GlobalAttributeDate1 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-GlobalAttributeDate2 | Resolve AR_REMIT_TO_LOCATION.GlobalAttributeDate2 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-GlobalAttributeDate3 | Resolve AR_REMIT_TO_LOCATION.GlobalAttributeDate3 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-GlobalAttributeDate4 | Resolve AR_REMIT_TO_LOCATION.GlobalAttributeDate4 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-GlobalAttributeDate5 | Resolve AR_REMIT_TO_LOCATION.GlobalAttributeDate5 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-GlobalAttributeNumber1 | Resolve AR_REMIT_TO_LOCATION.GlobalAttributeNumber1 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-GlobalAttributeNumber2 | Resolve AR_REMIT_TO_LOCATION.GlobalAttributeNumber2 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-GlobalAttributeNumber3 | Resolve AR_REMIT_TO_LOCATION.GlobalAttributeNumber3 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-GlobalAttributeNumber4 | Resolve AR_REMIT_TO_LOCATION.GlobalAttributeNumber4 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-GlobalAttributeNumber5 | Resolve AR_REMIT_TO_LOCATION.GlobalAttributeNumber5 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-County | Resolve AR_REMIT_TO_LOCATION.County | offline | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-Address3 | Resolve AR_REMIT_TO_LOCATION.Address3 | offline | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-Address4 | Resolve AR_REMIT_TO_LOCATION.Address4 | offline | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_LOCATION-Province | Resolve AR_REMIT_TO_LOCATION.Province | offline | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_ADDRESS-Country | Resolve AR_REMIT_TO_ADDRESS.Country | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_ADDRESS-State | Resolve AR_REMIT_TO_ADDRESS.State | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_ADDRESS-AttributeCategory | Resolve AR_REMIT_TO_ADDRESS.AttributeCategory | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_ADDRESS-Attribute1 | Resolve AR_REMIT_TO_ADDRESS.Attribute1 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_ADDRESS-Attribute2 | Resolve AR_REMIT_TO_ADDRESS.Attribute2 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_ADDRESS-Attribute3 | Resolve AR_REMIT_TO_ADDRESS.Attribute3 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_ADDRESS-Attribute4 | Resolve AR_REMIT_TO_ADDRESS.Attribute4 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_ADDRESS-Attribute5 | Resolve AR_REMIT_TO_ADDRESS.Attribute5 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_ADDRESS-Attribute6 | Resolve AR_REMIT_TO_ADDRESS.Attribute6 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_ADDRESS-Attribute7 | Resolve AR_REMIT_TO_ADDRESS.Attribute7 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_ADDRESS-Attribute8 | Resolve AR_REMIT_TO_ADDRESS.Attribute8 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_ADDRESS-Attribute9 | Resolve AR_REMIT_TO_ADDRESS.Attribute9 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_ADDRESS-Attribute10 | Resolve AR_REMIT_TO_ADDRESS.Attribute10 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_ADDRESS-Attribute11 | Resolve AR_REMIT_TO_ADDRESS.Attribute11 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_ADDRESS-Attribute12 | Resolve AR_REMIT_TO_ADDRESS.Attribute12 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_ADDRESS-Attribute13 | Resolve AR_REMIT_TO_ADDRESS.Attribute13 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_ADDRESS-Attribute14 | Resolve AR_REMIT_TO_ADDRESS.Attribute14 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_ADDRESS-Attribute15 | Resolve AR_REMIT_TO_ADDRESS.Attribute15 | live-readonly | Blocked | RESOLVER_MATRIX |
| RD-AR_REMIT_TO_ADDRESS-SetCode | Resolve AR_REMIT_TO_ADDRESS.SetCode | live-readonly | Blocked | RESOLVER_MATRIX |

### LC-01 — Smallest-scope update and preservation

| Variant | Scenario | Execution class | Disposition | Reason |
|---|---|---|---|---|
| LC-01-A | Minimal update | offline | Blocked | STATUS_CAMPAIGN_FIXTURE |

### LC-02 — Already-satisfied, repeated and reordered input

| Variant | Scenario | Execution class | Disposition | Reason |
|---|---|---|---|---|
| LC-02-A | Already satisfied | offline | Blocked | CATALOG_EXECUTION |
| LC-02-B | Repeated build | offline | Blocked | CATALOG_EXECUTION |

### LC-03 — Narrow forward and rollback pair

| Variant | Scenario | Execution class | Disposition | Reason |
|---|---|---|---|---|
| LC-03-A | Offline rollback package | offline | Blocked | STATUS_CAMPAIGN_FIXTURE |
| LC-03-B | Persisted rollback | live-mutation | Blocked | STATUS_CAMPAIGN_FIXTURE |

### LC-04 — Stale source and changed adapter/input

| Variant | Scenario | Execution class | Disposition | Reason |
|---|---|---|---|---|
| LC-04-A | Stale current export | offline | Blocked | OWNER_GATES |
| LC-04-B | Changed adapter | static | Blocked | OWNER_GATES |

### BI-01 — Target isolation, duplicates and conflicts

| Variant | Scenario | Execution class | Disposition | Reason |
|---|---|---|---|---|
| BI-01-A | Unrelated row | offline | Blocked | CATALOG_EXECUTION |
| BI-01-B | Exact duplicate | offline | Blocked | CATALOG_EXECUTION |
| BI-01-C | Conflicting duplicate | offline | Blocked | CATALOG_EXECUTION |

### SM-01 — Composite identity, collision and target resolution

| Variant | Scenario | Execution class | Disposition | Reason |
|---|---|---|---|---|
| SM-01-A | Create collision | offline | Blocked | CATALOG_EXECUTION |

### SM-02 — Missing and invalid values are repaired conversationally

| Variant | Scenario | Execution class | Disposition | Reason |
|---|---|---|---|---|
| SM-02-A | Missing mandatory value | static | Blocked | PROMPT_TRANSCRIPT |
| SM-02-B | Invalid effective date | static | Not applicable | NO_EFFECTIVE_DATE |

### SM-03 — System-owned fields, explicit clearing and no-op suppression

| Variant | Scenario | Execution class | Disposition | Reason |
|---|---|---|---|---|
| SM-03-A | Protected audit field | offline | Blocked | CATALOG_EXECUTION |
| SM-03-B | Omission versus explicit blank on create | offline | Blocked | CATALOG_EXECUTION |

### SM-04 — Operation-compatible mixed or multi-record processing

| Variant | Scenario | Execution class | Disposition | Reason |
|---|---|---|---|---|
| SM-04-A | Multi-record create | offline | Blocked | CATALOG_EXECUTION |
| SM-04-B | Deterministic bulk create | offline | Blocked | CATALOG_EXECUTION |
| SM-04-C | Bulk atomic failure | offline | Blocked | CATALOG_EXECUTION |

### SM-05 — Baseline protection with concurrent unrelated inserts

| Variant | Scenario | Execution class | Disposition | Reason |
|---|---|---|---|---|
| SM-05-A | Concurrent unrelated row | offline | Blocked | CATALOG_EXECUTION |
| SM-05-B | Baseline row removed | offline | Blocked | CATALOG_EXECUTION |
| SM-05-C | Baseline row changed | offline | Blocked | CATALOG_EXECUTION |

### PK-01 — Exact-task package contract

| Variant | Scenario | Execution class | Disposition | Reason |
|---|---|---|---|---|
| PK-01-A | Valid exact-task package | offline | Blocked | CATALOG_EXECUTION |

### PK-02 — Wrong scope, release, schema and malformed archives

| Variant | Scenario | Execution class | Disposition | Reason |
|---|---|---|---|---|
| PK-02-A | Wrong task or broader export | offline | Blocked | CATALOG_EXECUTION |
| PK-02-B | Schema mismatch | offline | Blocked | CATALOG_EXECUTION |
| PK-02-C | Unsafe archive | static | Blocked | CATALOG_EXECUTION |
| PK-02-D | Malformed CSV/XML | offline | Blocked | CATALOG_EXECUTION |

### OF-01 — Preview, confirmation, warning and hash gates

| Variant | Scenario | Execution class | Disposition | Reason |
|---|---|---|---|---|
| OF-01-A | Review only | offline | Blocked | OWNER_GATES |
| OF-01-B | Changed input | static | Blocked | OWNER_GATES |
| OF-01-C | Unresolved warning | offline | Blocked | OWNER_GATES |

### IM-01 — Approved import and persisted-state reconciliation

| Variant | Scenario | Execution class | Disposition | Reason |
|---|---|---|---|---|
| IM-01-A | Minimum/default create | live-mutation | Blocked | CREATE_RETENTION |

### IM-02 — Submitted, running, failed, partial and unknown outcomes

| Variant | Scenario | Execution class | Disposition | Reason |
|---|---|---|---|---|
| IM-02-A | Status classification | offline | Blocked | OWNER_GATES |
| IM-02-B | Unknown outcome | offline | Blocked | OWNER_GATES |

### IM-03 — Exact match, mismatch, missing export and warning

| Variant | Scenario | Execution class | Disposition | Reason |
|---|---|---|---|---|
| IM-03-A | Exact match | offline | Blocked | CATALOG_EXECUTION |
| IM-03-B | Mismatch | offline | Blocked | CATALOG_EXECUTION |
| IM-03-C | Missing evidence | offline | Blocked | CATALOG_EXECUTION |

### DOC-01 — Complete campaign disposition and Confluence evidence page

| Variant | Scenario | Execution class | Disposition | Reason |
|---|---|---|---|---|
| DOC-01-A | Render campaign page | static | Blocked | REPORT_RENDER |

## Merge boundary

This register fixes evidence accounting, not the missing live executions. The effective-catalog hierarchy finding is separate and unchanged. A future source commit still needs the repository premerge audit and required human reviewers; this document grants no merge approval.
