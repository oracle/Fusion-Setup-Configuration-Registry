# Standard Operations — Dependency Readiness

## Release and evidence boundary

Reviewed 29 October 2026. The [Oracle SCM documentation hub](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/) identifies 26D as current. The 26D overview/setup topics were retrieved; detailed Standard Operations REST pages could be retrieved only in 26C, and the detailed creation guide in 26B. These are retrieval gaps, not proof that newer topics do not exist. Use the cited release for each rule and verify the deployed contract before execution.

Public contract, request-preparation policy and deployment-dependent behavior are distinguished below. Public citations establish only what the linked pages document. No live create/update tests were performed. Keep supplied intent separate from the persisted result; the owning core workflow controls reads, preparation, authorization, writes and result verification.

## Public references

- [26D: Overview of Manufacturing Plants](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/faumf/overview-of-manufacturing-plants.html): work areas, resources, work centers and standard-operation context.
- [26D: Outside Processing Setup](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/faims/overview-of-outside-processing-setup.html): supplier-operation setup context.

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Selected deployment contract | Establish supported fields/operations and requested child relationships through the owning core workflow |
| 2 | Existing parent identity | For updates or adding children to existing parents, identify header before resource and resource before alternate |
| 3 | Supplied reference intent | Identify intended organization, work center and resource/reference values; let server resolution and validation decide validity and access |
| 4 | Requested extensions | Establish deployment metadata and core support only if DFF, attachment or feature-dependent work is requested |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| STDOP.CONTRACT | Deployed REST contract | Yes | Preparation in selected environment or changed metadata context | Verify | Fusion resource metadata | read_standard_operation_contract | Confirm version, operations and field shapes; a DAT column list alone does not satisfy this dependency | Use owning core workflow; do not infer from another release or a template version marker | Confirmed capability and child metadata |
| STDOP.HEADER_ID | Header identity by ID | Conditional | Original header ID supplied for existing-record work | Verify | Fusion standardOperations | find_standard_operation_by_id | Establish exact current parent | Supply original identity | Header/current values/links |
| STDOP.HEADER_CODE | Header identity by code and organization | Conditional | Existing target without original ID | Verify | Fusion standardOperations | find_standard_operation_by_code | Code uniqueness scope includes organization | Supply original code and organization | Header/current values/links |
| STDOP.RESOURCE | Existing primary resource | Conditional | Primary update, alternate work beneath an existing primary, or authorized partial-load reconciliation | Verify | Fusion returned child collection | find_standard_operation_resource | Establish correct child and context | Supply original child ID or original sequence/resource | Primary/current values/links |
| STDOP.ALTERNATE | Existing alternate resource | Conditional | Alternate update | Verify | Fusion returned alternate collection | find_standard_operation_alternate | Prevent wrong-child update | Supply original alternate identity | Alternate/current values |
| STDOP.EXTENSIONS | DFF/attachment contract | Conditional | Requested extension work | Verify | Deployed child metadata from Fusion | read_standard_operation_contract | Required fields/categories are deployment-specific | Missing requirements stop only affected extension scope; never silently drop it | Confirmed metadata and missing requirements |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Satisfied | Applicable identity and contract evidence established | Only declared read lookups under owning workflow |
| Not applicable | Wholly new hierarchy has no existing-record dependency, or optional feature not requested | No unnecessary read or dependent creation |
| Blocked | Required identity, metadata or declared core capability is missing/ambiguous | Stop affected request; report precise missing fact |

Organization security, active work-center/resource relationships, resource quantities, supplier/site association, lead-time UOM class and profile eligibility remain server validations. Do not create missing setup objects automatically. No duplicate, reference-usage or graph preflight is introduced. Rely on server validation for supplier OSP eligibility; no additional lookup dependency is required.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| STDOP.DEPENDENCIES | step | 30 | resolve_dependency | passed->STDOP.DEFAULTS;failed->STDOP.ERROR | STDOP.LOOKUPS | stop | Evaluate applicable contract and parent/child evidence; no speculative setup creation or duplicate checks |
