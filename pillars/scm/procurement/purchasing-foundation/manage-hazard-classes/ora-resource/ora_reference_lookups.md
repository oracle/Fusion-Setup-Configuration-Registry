# Hazard Class Reference Lookups

No local or live reference lookup is required by this task's validation graph.
The approved operation-neutral plan removes record-existence verification,
ID/code resolution, query construction, pagination, and lookup evidence.

Validation must not call Fusion REST, authenticate, or refresh tokens. Supplied
business values pass to Data Loader unchanged; Data Loader owns identity and
operation handling through its own declared workflow. Its metadata or execution
calls are outside this local graph.

This standard resource file is retained as explicit no-lookup guidance and
contributes no resolver rows or Task Nodes.
