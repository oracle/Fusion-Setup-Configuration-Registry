# Delegate Customer loading to core



## Responsibilities

The task owns Customer input, entity intent, before-state checks, registration
qualification, expected effects, eligible business uncertainty and reconciliation.
The selected checkout's core/data-loader/SKILL.md owns source capture, route
resolution, ordered rule evaluation protocol, preview, approval, integrity,
submission and recovery. Follow that skill rather than selecting a protocol by
branch name. Do not import its private session implementation into task code.

## Handoff

1. Prepare and inspect the exact native Customers ZIP with ArUpdCustomers.csv.
   Retain its hash, reviewed input/provenance, operation, entity intent and
   before-state evidence. Complete the applicable task checks; historical passes
   and generated examples cannot supply missing evidence.
2. Review the qualified registration recipe, fresh targeted public BO/FBDI
   metadata, active Run Book control and loader action-capability evidence using
   review_delegated_registration. Require the one Customers registration,
   interface 59, account and file prefixes. This grants no execution authority.
3. Invoke the selected core workflow with that archive, selected environment,
   actual Run Book task context, task name/sequence and customers business
   object selection. Core must resolve the native FBDI route. Do not select FSM,
   omit task validation, or replace a failed shared prevalidation with this check.
4. Evaluate planned resources against core's retained source. Compare the captured
   native member with the reviewed ArUpdCustomers.csv. For text capture compare
   UTF-8 decoded text exactly, including line endings. Retain the comparison.
   Any difference requires fresh review; never pass rules for a different source.
   Preserve input provenance and review hashes in supported rule evidence.
5. Request core's preview only after required checks pass. Follow its exact
   presentation and approval contract. For eligible business uncertainty retain
   the existing package review context with the actual public preview reference,
   environment and registration/argument hashes. This records decision scope;
   it does not authenticate or approve anything. The normal core decision must
   cover effects and eligible gaps. Changed source, scope, environment or lost
   core state requires fresh validation/decision according to core. Do not inspect
   private session state or synthesize a legacy approval/preflight envelope.
6. Let core execute the approved source. Follow its evidence-retention policy;
   memory-only previews and decisions stay in the live session. Retain permitted
   public initiation/status evidence with selected revision and timestamps. Obtain
   actual content/request IDs, never inferred IDs. Build the task v2 binding in
   [attempt association](attempt-association.md). It is evidence, not a core
   receipt or permission token. Follow core's recovery policy; add no task retry.
7. Collect status and reconcile the exact attempt, Run Book/task association,
   product results and business effects. Missing association or incomplete
   readback cannot be called verified completion. Preserve partial success and
   use status-only recovery for uncertain submission.

## Evidence boundary

Core need not export its private route plan in a particular file format. The
Customer task checks registration prerequisites independently; core enforces
actual route resolution and source/approval binding. Public preview evidence
identifies the decision, not a serialized execution plan. Legacy envelope
reviewers remain for historical artifacts, not the active runtime entry point.

Shared environment prevalidation remains a separate routed step. An unfiltered
catalog absence is not corrected by pretending this task check is the shared
check. Record the discrepancy and follow that workflow's supported resolution
or skip decision, keeping skipped distinct from passed. Never blank the business
object, change shared code or bypass an enforced blocker.

Advertised runBookTaskCode support is a prerequisite, not proof of stored server
association. Post-import exact association remains mandatory. Read access does
not establish upload permission; core/server authorization applies at execution.

Offline protocol tests and previous live runs have separate scopes. Do not claim
full live qualification of this candidate until its own core invocation and
business reconciliation complete.
