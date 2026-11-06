# Error Handling

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| PBF.READY | terminal | 2 | terminal | none | PBF.VALIDATE_INPUT | continue | Input validation has passed |
| PBF.BLOCKED | terminal | 3 | terminal | none | none | continue | Input validation has failed |
