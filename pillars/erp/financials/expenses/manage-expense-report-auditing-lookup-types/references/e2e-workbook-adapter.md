# Workbook E2E adapter scope

The standard adapter commands build, validate and determinism use the existing workbook intake and candidate builder. They require an explicit `--reference-snapshot` captured from the destination by the task workflow. The snapshot must identify the destination, match the template and baseline SHA-256 values, and provide fresh, complete type, set and code evidence. An FSM export alone cannot satisfy these checks. A blueprint prerequisite assertion is never a substitute for the snapshot.

The current adapter qualifies lookup-code create and update. Parent lookup-type text and independent translation mutations are not qualified by this adapter; this does not remove those customer workbook capabilities. Selected existing translations are carried unchanged and independently checked. Automatic rollback is not qualified: use a fresh, reviewed workbook update through the normal workflow.

The generated structural tests exercise schema and generic package mechanics. `test_workbook_adapter.py` separately exercises the actual customer workbook runtime with synthetic snapshots and fixtures. Neither suite is live execution evidence. A tester variant that cannot supply the required destination snapshot must report a missing prerequisite instead of substituting the generic package builder.

Reconciliation checks requested values, serialized business defaults, retained fields and untouched baseline rows against a fresh export. ModuleKey and ModuleType are package context rather than ordinary persisted code values; audit fields and UpdateStartDate are excluded from retained-field comparison. If the fresh export does not contain required rows, reconciliation fails rather than inferring success.
