# Reference Lookups

## Lookup Operations

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| find_chart_of_accounts | Before any FSM export, package, or create | COA Name and StructureInstanceCode; preserve a supplied code, otherwise derive StructureInstanceCode from COA Name by replacing spaces with underscores | GET /fscmRestApi/resources/11.13.18.05/chartOfAccountsLOV?q=Name='{COA Name}' or StructureInstanceCode='{StructureInstanceCode}'; required header REST-Framework-Version: 9 | Name, StructureInstanceId, StructureInstanceCode, StructureInstanceNumber, Description, EnabledFlag | Match either exact Name or exact StructureInstanceCode; zero matches means absent; exactly one means compare the existing definition | Existing instance identity for detail lookup when matched | On a successful, complete lookup with zero matches, continue to COAINS.DEFAULT for creation preparation through the declared workflow and its validation and approval gates. Compare one match, including any name/code difference, before continuing. Stop on ambiguity or a failed or incomplete lookup; never treat a lookup failure as absence. |
| get_chart_of_accounts | A unique StructureInstanceId was found | StructureInstanceId | GET /fscmRestApi/resources/11.13.18.05/chartOfAccountsLOV/{StructureInstanceId} | Name, StructureInstanceCode, StructureInstanceNumber, Description, EnabledFlag | Exact ID | Existing instance detail | Stop if the detail response is unavailable |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| COAINS.LOOKUP | decision | 4 | reference_lookup | absent->COAINS.DEFAULT;match->COAINS.DONE_MATCH | COAINS.READY | stop | Always |
