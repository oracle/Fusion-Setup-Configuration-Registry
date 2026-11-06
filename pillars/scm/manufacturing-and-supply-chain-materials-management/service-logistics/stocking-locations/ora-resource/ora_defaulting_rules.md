# Stocking Locations Defaulting Rules

Source: the task Data Loader Mutation Workflow and current core.data-loader operation contract.

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| RestAction | POST | Explicit parent or child create request through Data Loader | No | |

Leave optional unspecified values blank. OrganizationId and Subinventory are resolved references, not defaults. Do not invent Condition or Location Type, reuse sampled identities, or convert a duplicate create into upsert/update. Preserve supplied meanings in Meaning fields.

PartySiteId, PartySiteNumber, customer identity, and StockLocationId are verified references, never defaults. Do not generate a SiteDedicatedLocId on create. Child-only sources contain no parent data operation; Data Loader owns hierarchy validation and serialization. For Data Loader updates explicitly require RestAction=PATCH; for deletion explicitly require RestAction=DELETE. These are selected operation values, not defaults. Include verified keys and only requested writable changes plus loader-required fields; replacement customer-site associations require the verified pair. Never send a JSON mutation body or default an update/delete to POST. An already saved match is a readback no-op, not an implicit upsert.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| RCL.SLOC.DEFAULT | decision | 12 | apply_default | applied->RCL.SLOC.GATE;not_applicable->RCL.SLOC.GATE;failed->RCL.SLOC.ISSUES | RCL.SLOC.SITE | stop | Evaluate defaults without changing captured records; explicit RestAction must already match operationClass; PATCH/DELETE never receive create defaults; a needed correction fails and requires a new immutable artifact |
