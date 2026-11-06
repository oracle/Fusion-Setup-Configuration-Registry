# Adaptive Search Publish Design Enforcement

ABO initial Full Publish is the separately approved exception specified by
[ora_abo_initialization.md](ora_abo_initialization.md). For that phase use its
nine-object/blank-`publishType` validated-row rule rather than the normal
selective-pair rule. Initialization receipts/status never satisfy ESS.

## Standalone Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Confirm target | Bind the plan to one explicitly identified non-production environment |
| 2 | Validate selection | Require a nonempty list; display unknown values and complete the correction loop until every name is valid |
| 3 | Discover and compare objects | For Partial or explicit Full Publish, on HTTP 200 with nonempty items show active and requested objects by display name; on HTTP 400 `Could not find active meta model`, a null result, or an empty result use the OOTB Full Publish flow; on other errors stop |
| 4 | Explicit Full Publish selection | After a nonempty Entities response, ask whether to retain active objects with newly requested objects; select the union on Yes or requested objects on No |
| 5 | Check concurrency | Block a conflicting nonterminal publish after final entity selection; recognized CPQ aliases do not require Entities validation |
| 6 | Validate embedded contract | Run the deterministic semantic contract validator and persist the mapped payload report |
| 7 | Combined confirmation | Show the exact selection, final publish details, and side effects in one table; require one explicit live approval matching it |

## Fusion ABO Dependent Enforcement Order

1. Prepare the companion only after exact verified CPQ success.
2. Validate v2 parent identity, fixed pair and concurrency; return the Core workbook handoff.
3. Accept its confirmed path, follow one Core persisted-preflight/Task Hook handoff, evaluate ordered rules from validated workbook rows and display
   Core's current preview Markdown verbatim for separate approval.
4. Reserve once and return the Core submit handoff. Core approves and verifies the exact persisted artifact, uploads it once, then returns a bound receipt for `complete-data-load`. Return receipt/opaque operation and pause.
5. Check Data Loader only on the explicit user status request through its bound Core status handoff. Pending stops.
6. After exact load success, check only the discovered/pinned Adaptive Search
   job. The parent checks once, then repeats at 15 seconds only on a current
   keep-checking choice. Check-later saves/stops. Return final readiness; never
   submit ESS or republish on uncertainty.

## Design Rules

| Rule ID | Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|---|
| AS-DES-001 | Every publish | Error | Environment identity | Target is absent, ambiguous, or production without explicit authorization | Use a named non-production environment for the first hands-on run | Yes |
| AS-DES-002 | Object selection after Entities HTTP 200 | Error | Document objects catalog lookup | Object list is empty, a non-CPQ-alias requested name is absent from nonempty localizedName values, or a duplicate display label has not been disambiguated | Show invalid names and up to three nearest display-name suggestions; for duplicate labels show internal names in parentheses and require an exact choice before preview; recognized CPQ aliases resolve to both direct CPQ entity names without catalog validation; never show the full catalog | Yes |
| AS-DES-003 | Before POST | Error | Latest publish status | Existing status is WAIT, READY, RUNNING, or PAUSED | Wait for or resolve the existing job | No |
| AS-DES-004 | POST returns a sandbox conflict | Error | Fusion API response | Fusion rejects metamodel synchronization because of sandbox state | Report the response, resolve the sandbox, and require new approval before a later POST | No |
| AS-DES-005 | Before POST | Error | Mapped payload artifacts | Payload or mapping report is absent, stale, or not tied to the current input | Regenerate the artifacts | Yes |
| AS-DES-006 | Before POST | Error | Approval record | Approval does not match environment, endpoint, entities, or artifact fingerprint | Request a new explicit approval | Yes |
| AS-DES-007 | Entities GET returned HTTP 200 | Error | Document objects catalog lookup | Response is malformed, localizedName was not used for validation/display, isEnabled was incorrectly applied to name validation, or active/requested lists were not displayed separately | Correct the response handling and repeat object review | Yes |
| AS-DES-008 | Before POST | Error | Combined confirmation | User has not confirmed the combined selection and final publish details | Confirm or collect a revised list | Yes |
| AS-DES-009 | Whenever environment, endpoint, normalized entities, or validated contract binding changes or cannot be matched | Error | Mapped artifact binding metadata | An old payload or mapping report remains under an executable current name, or prior preview/approval remains usable | Archive when supported, remove executable-current names, write a body-free invalidation record, revoke preview/approval, then regenerate after semantic contract validation | Yes |
| AS-DES-010 | Every administrator-facing interaction | Error | Administrator presentation contract | Normal output exposes hashes, contract IDs, artifact paths, node IDs, or unnecessarily technical approval language | Render the functional table from ora_user_presentation.md and retain technical metadata only in internal artifacts | Yes |
| AS-DES-011 | Start of every new publish request | Error | New-request presentation rule | Opening output mentions a historical job or treats persisted initial status as current concurrency state | Ask for missing objects or begin validation; defer a fresh latest-status GET until after entity validation | Yes |
| AS-DES-012 | Before POST | Error | Publish mode and payload | A Partial Publish with a nonempty entity catalog does not produce `publishType: selective` with mapped `entities`, or a Full Publish lacks a nonempty `entities` array or includes `publishType` | Regenerate the payload for the selected mode and obtain new approval | Yes |
| AS-DES-013 | After latest-status lookup | Error | Terminal-status continuation | A terminal latest status, or an already-enabled requested object, causes the flow to skip the combined confirmation or suppress the requested publish as redundant | Continue to payload mapping and the combined confirmation; block only WAIT, READY, RUNNING, or PAUSED | Yes |
| AS-DES-014 | Fusion ABO preparation | Error | CPQ predecessor and Core handoff | No verified CPQ success or no bound Core workbook/preflight result | Stop; prepare values and follow Core handoffs after CPQ verification | Yes |
| AS-DES-015 | Fusion ABO submission | Error | Exact workflow and persisted Task Hook preview | Identity mismatched or current preview not contextually approved on the exact validated archive | Block submission; require the exact Core persisted approval route | No |
| AS-DES-016 | Fusion ABO `get_partial_publish_status` | Error | Exact persisted operation | The caller supplies a Data Loader ID or mismatched operation ID; post-loader discovery is malformed or has an unknown state; or a later exact status does not echo the pinned job ID | Stop as indeterminate; use only the operation's private Data Loader, one approved post-loader discovery GET, and later exact-job status reads. A discovery response equal to the fresh pre-submit job remains pending and is not pinned. | No |
| AS-DES-017 | Fusion ABO recovery | Error | Durable operation state | A prior submit may have occurred but exact correlation cannot be proven | Return indeterminate and do not re-submit, re-publish, or create a new operation automatically | No |

## Design Lookup Requirements

| Rule ID | Resolver | When Required | Values Needed | Source File |
|---|---|---|---|---|
| AS-DES-001 | Environment preflight | Before preview | hostname and environment classification | ora_dependency_readiness.md |
| AS-DES-002 | Document objects catalog lookup | Before object review | every nonempty localizedName and its unique entityName mapping returned with isDocument=true and without isEnabled | ora_reference_lookups.md |
| AS-DES-003 | Adaptive Search latest-status lookup | After entity resolution and before the combined confirmation | jobId and status | ora_reference_lookups.md |
| AS-DES-004 | Fusion publish response | After the single approved POST only | HTTP status, redacted message, and safe ECID | ora_error_handling.md |
| AS-DES-007 | Document objects catalog lookup | Before object confirmation | localizedName, entityName, isDocument, and isEnabled | ora_reference_lookups.md |
| AS-DES-009 | Artifact version and registry metadata | At input intake and before preview | environment, endpoint, normalized entities, validated contract binding, payload binding, current/versioned status | ora_rest_execution.md |
| AS-DES-010 | Administrator presentation contract | Before every user-facing response | allowed functional fields, hidden technical fields, and exact approval wording | ora_user_presentation.md |
| AS-DES-011 | New-request presentation rule | Before the first administrator-facing response | whether objects are present; historical state must remain hidden | ora_user_presentation.md |
| AS-DES-014 | Live companion preparation | After CPQ verification | project, target, fixed entities and valid Core preflight | ora_rest_execution.md |
| AS-DES-015 | Live approval validator | Before companion submission | exact workflow, predecessor and current persisted Task Hook preview | ora_input_intake.md |
| AS-DES-016 | Companion status resolver | During explicit loader checks and verified-load job ticks; parent repeats only on current monitoring choice | opaque operation ID, private Data Loader correlation, fresh pre-submit baseline, discovered job ID, and later exact-job status response | ora_rest_execution.md |
