# Manage AutoAccounting Rules Design Enforcement


<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: AR_AUTO_ACCOUNTING::Attribute1, AR_AUTO_ACCOUNTING::Attribute10, AR_AUTO_ACCOUNTING::Attribute11, AR_AUTO_ACCOUNTING::Attribute12, AR_AUTO_ACCOUNTING::Attribute13, AR_AUTO_ACCOUNTING::Attribute14, AR_AUTO_ACCOUNTING::Attribute15, AR_AUTO_ACCOUNTING::Attribute2, AR_AUTO_ACCOUNTING::Attribute3, AR_AUTO_ACCOUNTING::Attribute4, AR_AUTO_ACCOUNTING::Attribute5, AR_AUTO_ACCOUNTING::Attribute6, AR_AUTO_ACCOUNTING::Attribute7, AR_AUTO_ACCOUNTING::Attribute8, AR_AUTO_ACCOUNTING::Attribute9, AR_AUTO_ACCOUNTING::AttributeCategory, AR_AUTO_ACCOUNTING::BuName, AR_AUTO_ACCOUNTING::Type, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute1, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute10, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute11, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute12, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute13, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute14, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute15, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute2, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute3, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute4, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute5, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute6, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute7, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute8, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute9, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::AttributeCategory, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Constant, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Segment, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::SegmentNum, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::TableName -->
<!-- fscr-update-fields: AR_AUTO_ACCOUNTING::Attribute1, AR_AUTO_ACCOUNTING::Attribute10, AR_AUTO_ACCOUNTING::Attribute11, AR_AUTO_ACCOUNTING::Attribute12, AR_AUTO_ACCOUNTING::Attribute13, AR_AUTO_ACCOUNTING::Attribute14, AR_AUTO_ACCOUNTING::Attribute15, AR_AUTO_ACCOUNTING::Attribute2, AR_AUTO_ACCOUNTING::Attribute3, AR_AUTO_ACCOUNTING::Attribute4, AR_AUTO_ACCOUNTING::Attribute5, AR_AUTO_ACCOUNTING::Attribute6, AR_AUTO_ACCOUNTING::Attribute7, AR_AUTO_ACCOUNTING::Attribute8, AR_AUTO_ACCOUNTING::Attribute9, AR_AUTO_ACCOUNTING::AttributeCategory, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute1, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute10, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute11, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute12, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute13, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute14, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute15, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute2, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute3, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute4, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute5, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute6, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute7, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute8, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute9, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::AttributeCategory, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Constant, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::TableName -->

## Mandatory Design Gates

| Gate | Pass Condition | Blocking Outcome | Evidence |
|---|---|---|---|
| Exact scope | Request resolves only to AR_MANAGE_AUTOACCOUNTING_RULES | Separate mixed-task scopes and ask which to prepare | SRC-CATALOG-TASKS; SRC-CODE-TASK-LIST |
| Complete create | Every required current segment has exactly one rule | Ask for missing/conflicting segment design | SRC-DOC-AUTOACCOUNTING-26D; SRC-FSM-PACKAGE |
| One derivation | Each segment has one compatible TableName or valid Constant | Ask for a valid source-or-constant choice | SRC-DOC-AUTOACCOUNTING-26D; SRC-CODE-UI-SEGMENT-VO |
| Immutable identity | BuName, Type, Segment, and SegmentNum are preserved on update | Reject rename, movement, or segment identity change | SRC-CODE-HEADER-EO; SRC-CODE-SEGMENT-EO |
| Parent context | Every segment create or update includes exactly one matching, unchanged `AR_AUTO_ACCOUNTING` parent row; only service-owned audit fields are blanked | Reject a child-only package, missing baseline parent, duplicate parent, or changed parent business value | SRC-FSM-PACKAGE; Fusion FSM application-validation regression |
| Atomic request | Every operation in a mixed or bulk request passes | Build no partial candidate | SRC-FSM-PACKAGE |
| Preservation | Unrequested fields, children, DFFs, and unrelated rows remain unchanged | Reject collateral change | SRC-FSM-PACKAGE; SRC-CODE-SERVICE-IMPL |
| Package fidelity | Exact members, headers, metadata, field counts, and trailing blanks remain | Reject malformed or drifted package | SRC-FSM-PACKAGE |
| Confirmation boundary | Complete preview is bound to Run Book confirmation | Stop before build | Active Run Book contract |
| Import boundary | Immutable candidate and SHA are bound to Data Loader approval | Stop before import | Active Data Loader contract |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AAR.ENFORCE_DESIGN | decision | 5 | design_enforcement | pass->AAR.HANDOFF_GATE;blocked->AAR.RETURN_ISSUES | AAR.APPLY_DEFAULTS | stop | Every complete normalized request before package handoff |

## Source Anchors

| Source IDs | Use |
|---|---|
| SRC-DOC-AUTOACCOUNTING-26D | Complete account-type and segment-value design |
| SRC-FSM-PACKAGE; SRC-CODE-SERVICE-IMPL | Exact package, preservation, and task-owned service path |
| SRC-CODE-HEADER-EO; SRC-CODE-SEGMENT-EO | Identity and entity relationships |
