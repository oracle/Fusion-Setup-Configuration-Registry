# Return Routing Rules Reference Lookups

Use an environment-bound, reviewed reference bundle held in memory or private local ignored staging outside `project/` and tracked files. Source extracts and any existing-rule export must follow the same location rule. Do not save customer reference values or raw exports in a project workspace. `shared.setup-export.task-level-export` may supply existing Return Routing Rules identity evidence only when its active workflow can keep the extract in permitted private staging; otherwise stop with the persistence gap. That export alone does not establish item, zone, organization or subinventory references. Use approved same-environment reference extracts with human review under `shared.validation.reference-data-validator`; metadata alone does not establish reference existence.

## Evidence Contract

The bundle uses `schema_version: "1.0"`, exact `environment` and `rest_base_url`, and these collections when the corresponding values are supplied:

| Collection | Required row fields | Purpose |
|---|---|---|
| `source_types` | `code` | SourceType code |
| `return_types` | `code` | ReturnType code |
| `items` | `number` | InventoryItemNumber |
| `zones` | `name`, `source_type_code` | GeographyName and its source-type classification |
| `organizations` | `id`, `code` | Organization ID and optional code evidence |
| `subinventories` | `organization_id`, `code` | Subinventory within its organization |
| `catalogs` | `id`, `name` | Category set or item catalog |
| `categories` | `catalog_id`, `id`, `name` | Category within its catalog |

The in-memory companion validation record must contain `status: "passed"`, matching `environment` and `rest_base_url`, the bundle's `bundle_sha256`, nonblank `reviewed_by`, `covered_collections`, and at least one `source_artifacts` entry. Each source entry needs an opaque `source_ref`, SHA-256, `covers` list and `route` equal to `shared.setup-export.task-level-export` or `reviewed_reference_extract`. Bind the source_ref to the actual in-memory bytes or a private staged file outside project/ and tracked files; never treat a caller-supplied hash as evidence that the source was reviewed. Reject project-contained source/bundle paths, tracked paths, symlink escapes and unsafe staging before reading or writing evidence.

The reviewing implementor verifies the bundle hash, every actual source hash, same-environment binding, exact collection coverage and transcription from each approved source before matching values. The shared validator supplies review methodology; this task defines the manual evidence checks, not an implemented hash-verifier API. Missing/stale evidence, missing review, changed hashes or environment mismatch blocks handoff. Revalidate the actual ephemeral sources after resume or target changes; a saved passed status alone cannot replace those records.

Persist only a redacted validation summary in the declared project validation artifact: task/operation, safe environment label, opaque source refs, hashes, coverage names, counts, review outcome and next action. Exclude reference rows, item/organization/subinventory/customer values, raw exports, private paths and sensitive host details. Do not copy the full in-memory validation record or bundle into project/. Retain or clean up permitted private staging under its owning workflow; no silent overwrites.


## Exact Match Rules

All code, number, name, and ID comparisons are exact and case-sensitive; surrounding whitespace is not silently normalized. Each supplied value must match **one** row. Zero or multiple matches block the rule. Organization IDs are positive integers, not display names or numeric strings. A supplied subinventory must match its code **and** the selected organization ID. A supplied category must match within the selected catalog; if both catalog ID and name are supplied, they must select the same catalog. For `SourceType=ZON`, the matched zone must have `source_type_code=ZON`. No default, first-row selection, or fuzzy match is allowed.

## Local Lookups

| Resolver | Runs When | Bundle match | Result / failure |
|---|---|---|---|
| validate_return_routing_reference_values | Any reference field supplied | Verify the reviewed bundle, validation record, target environment, source hashes, and exact collection coverage, then apply the field resolvers below | Pass all supplied values or stop before Data Loader handoff |
| resolve_return_routing_source_type | SourceType supplied | One `source_types.code` equals SourceType | Confirm code or stop |
| resolve_return_routing_return_type | ReturnType supplied | One `return_types.code` equals ReturnType | Confirm code or stop |
| resolve_return_routing_item | InventoryItemNumber supplied | One `items.number` equals InventoryItemNumber | Confirm item number or stop |
| resolve_return_routing_geography | GeographyName supplied | One `zones.name` equals GeographyName; a ZON source requires `source_type_code=ZON` | Confirm zone or stop |
| resolve_return_routing_destination_organization | DestinationOrganizationId supplied | One `organizations.id` equals the positive integer ID | Confirm destination organization or stop |
| resolve_return_routing_source_organization | SourceOrganizationId supplied | One `organizations.id` equals the positive integer ID | Confirm source organization or stop |
| resolve_return_routing_destination_subinventory | DestinationSubinventory supplied | One `subinventories` row matches DestinationOrganizationId and code | Confirm relationship or stop |
| resolve_return_routing_source_subinventory | SourceSubinventory supplied | One `subinventories` row matches SourceOrganizationId and code | Confirm relationship or stop |
| resolve_return_routing_category_set | CategorySetId or CategorySetName supplied | One `catalogs` row matches each supplied identifier; both identify the same row | Confirm catalog or stop |
| resolve_return_routing_category | CategoryId or CategoryName supplied | One `categories` row matches within the confirmed catalog | Confirm category or stop |
| find_return_routing_rule_by_key | Existing rule selected | Live Data Loader key fields and validated Return Routing Rules task export | Exactly one complete exported rule key matches; otherwise stop |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| RRR.LOOKUP_VALUES | step | 2 | evaluate_result | resolved->RRR.RESOLVE_DEPENDENCIES;unresolved->RRR.RETURN_REFUSAL | RRR.VALIDATE_INPUT | stop | When supplied values or an existing rule key require local reference checks; resolve organization and catalog before dependent subinventory and category values |
