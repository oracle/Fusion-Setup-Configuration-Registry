# Manage AutoAccounting Rules Defaulting Rules


## Defaults

| Field or Group | Default | Applies When | Override Rule | Evidence |
|---|---|---|---|---|
| BuName | No default | Every operation | Require explicit or uniquely resolved business input | SRC-CODE-UI-AM-IMPL; SRC-FSM-PACKAGE |
| Type | No default | Every operation | Normalize only one evidenced code or label | SRC-CODE-AUTOGL-LOOKUP |
| Segment and SegmentNum | Preserve current target structure | Create and update | Never renumber or invent a segment | SRC-FSM-PACKAGE; SRC-CODE-SEGMENT-EO |
| TableName and Constant | No default | Every segment rule | Require one explicit compatible source or constant | SRC-DOC-AUTOACCOUNTING-26D; SRC-CODE-UI-SEGMENT-VO |
| Audit fields | Blank in candidates | Create and update | No business override is permitted | SRC-CODE-HEADER-EO; SRC-CODE-SEGMENT-EO |
| DFF fields | Blank on create; preserve baseline on update | No DFF change is requested | Override only with exact deployed evidence | SRC-FSM-PACKAGE; SRC-CODE-HEADER-EO; SRC-CODE-SEGMENT-EO |

Observed export values are evidence, not universal defaults. Never copy another business unit's accounting design to fill missing input.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AAR.APPLY_DEFAULTS | step | 4 | apply_default | applied->AAR.ENFORCE_DESIGN;unchanged->AAR.ENFORCE_DESIGN;blocked->AAR.RETURN_ISSUES | AAR.LOOKUP_REFERENCES | stop | After required references resolve |

## Source Anchors

| Source IDs | Use |
|---|---|
| SRC-FSM-PACKAGE | Baseline preservation and exact package shape |
| SRC-CODE-HEADER-EO; SRC-CODE-SEGMENT-EO | Audit ownership and identity |
| SRC-DOC-AUTOACCOUNTING-26D | Source-or-constant rule |
