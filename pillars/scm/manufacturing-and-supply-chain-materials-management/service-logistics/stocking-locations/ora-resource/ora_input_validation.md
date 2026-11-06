# Stocking Locations Input Validation

Source: the task Data Loader Mutation Workflow and current core.data-loader metadata and immutable-artifact contract. Validate against the selected environment’s loader template; mutation endpoint schemas are not a submission route.

## Required Groups

Data Loader Site-Dedicated Location deletion requires an exact existing parent and a current SiteDedicatedLocId or current PartySiteNumber. Resolve with resolve_site_dedicated_location_by_exact_identity and require agreement with supplied customer selectors. Validate a child-only loader row with RestAction=DELETE and required keys. Reject parent operations, ambiguous children or unsupported loader deletion; do not select using replacement site values.

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Data Loader REST routing | Data Loader import mode REST and business object stockingLocations | Block resource routing | Set the import mode to REST and use stockingLocations as the business object | Preparing Stocking Locations setup-data import | |
| Organization input | At least one of OrganizationId, OrganizationCode, OrganizationName, or business label Organization; an exact existing StockLocationName can supply verified parent references for child work | Block identity resolution | Resolve the supplied identifier and require all supplied identifiers to agree; for an existing parent name resolve the parent first, then verify its returned references | Parent create or references derived from a resolved existing parent | resolve_stocking_location_organization |
| Subinventory input | Subinventory or business label SubinventoryName; for existing-parent child work the exact parent's returned Subinventory is accepted after verification | Block selection | Resolve the subinventory under the selected organization and compare all supplied aliases | Parent create or references derived from a resolved existing parent | resolve_stocking_location_subinventory |
| Data Loader parent create | Resolved OrganizationId, canonical Subinventory, LocationTypeMeaning or confirmed LocationType, ConditionMeaning or confirmed Condition, RestAction=POST | Block prepared-source readiness | Include resolved OrganizationId even when OrganizationName is supplied; validate current template and operation-specific values | Creating a parent through Data Loader | |
| Data Loader parent update | Verified parent selector and at least one supported changed field | Block update preflight | Resolve exactly one current parent, validate each requested value against the current loader update contract, and prepare verified keys, requested changes and RestAction=PATCH | Data Loader parent update | resolve_stocking_location_by_exact_name |
| Data Loader Site-Dedicated Location update | Exact parent StockLocationName or verified organization/subinventory pair, exact existing child identity, and one or more supported changed fields | Block child-update preflight | Resolve exactly one parent and exactly one existing child; for a customer-site replacement resolve the authoritative PartySiteId/PartySiteNumber pair from customer/site selection. Include verified parent/child keys and RestAction=PATCH | Data Loader child update | resolve_site_dedicated_location_by_exact_identity |
| Child linkage | Existing unique parent, authoritative PartySiteId, exact PartySiteNumber, and RestAction=POST in siteDedicatedLocations | Block child preparation | Resolve the existing parent, resolve PartySiteId from the documented customer-site contract when customer/site inputs are supplied, and validate the site relationship; no parent data row in a child-only load | Site Dedication child create only | resolve_customer_party_site |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Data Loader import mode | Accept only REST for this resource-authoring scope | Preparing Stocking Locations setup-data import | |
| Data Loader business object | Accept only stockingLocations for this resource-authoring scope | Preparing Stocking Locations setup-data import | |
| Business labels | Map Organization to OrganizationName only for an identified name, SubinventoryName to Subinventory, Location Type to LocationTypeMeaning, and a display-meaning Condition to ConditionMeaning. Latitude maps to Latitude; Longitude or an unambiguous Langitude typo maps to Longitude. Unknown, conflicting, fuzzy, or duplicate-target mappings require Data Loader review | Preparing source values | |
| Condition and Location Type | Preserve display meanings in Meaning fields; Usable and Manned Warehouse were verified by Data Loader creation. For other meanings or supplied technical codes, require current authoritative lookup/describe evidence. Never uppercase a label to invent a code. If code and meaning are both supplied, require agreement | Parent preparation | |
| OrganizationId | Require a positive integer resolved or verified by Fusion; include in parent create records and other operations only when loader metadata requires it; existing keys may supply canonical reference context | Parent or child preparation | resolve_stocking_location_organization |
| Subinventory | Require the canonical reference string no longer than 10 characters; parent create requires this field, existing-key operations can obtain it from the resolved parent without adding an unsolicited payload field | Parent or child preparation | resolve_stocking_location_subinventory |
| Coordinates | Supplied Latitude must be finite numeric between -90 and 90; Longitude between -180 and 180. Preserve decimal precision and zero; optional blanks stay blank. Reject NaN, infinity, and nonnumeric values | Parent preparation | |
| Location Type update | Resolve the supplied display meaning through ORA_RCL_STOCK_LOC_TYPE and require one exact code/meaning match. For Site Dedicated Warehouse, use only the verified lookup output; do not derive a code from text | Data Loader parent update | resolve_stocking_location_type |
| Site-Dedicated Location customer site | For customer-site replacement resolve a matching active customer/site and include its authoritative PartySiteId with the exact PartySiteNumber, at most 30 characters. Compare any supplied ID/name with that result. For other partial changes preserve the existing linkage; do not resend unrelated required-on-create fields | Data Loader child update | resolve_customer_party_site |
| Site-Dedicated Location create customer site | Require PartySiteId as a positive authoritative integer, PartySiteNumber as the exact associated site number no longer than 30 characters, and RestAction=POST. When Customer is supplied with PartySiteNumber, resolve and compare through the documented customer-site resolver. PartyName is optional and is not a substitute for PartySiteId | Child-only Data Loader create | resolve_customer_party_site |
| Source shape | Validate exact sections and attributes, mapping completeness, field lengths, safe delimiters, and child linkage against the live template. Do not insert sample placeholder IDs or sampled REST values into unspecified user fields | Every import | |
| Customer/site business labels | Customer or Customer Name is a resolver selector; Site number or Customer Site maps to PartySiteNumber. Resolved AddressId maps to PartySiteId. Customer maps to PartyName only after matching the authoritative customer response and only when the optional field is requested. Never map an account PartyId to PartySiteId | Child creation or customer-site replacement | resolve_customer_party_site |
| Existing child selector | Keep current SiteDedicatedLocId or current PartySiteNumber separate from replacement customer/site input. Require current parent and child keys to match the selected item. Reject a different supplied StockLocationId or an attempted parent reassignment | Child update | resolve_site_dedicated_location_by_exact_identity |
| IDs and optional child values | Require supplied IDs to be positive int64 integers without rounding; accept numeric strings only after exact integer validation. Validate PartyName length at most 360 and LocationAddress at most 4000 against current operation metadata. Omit generated SiteDedicatedLocId on create | Child create/update preparation | |
| Captured child-only source structure | Validate captured sections and linkage against current Data Loader metadata, with requested child rows only and no parent data operation. All child parent keys must match their resolved parents. Require the exact prepared DAT/ZIP at Task Hook validation; conversion and serialization belong to core and must finish before this gate | Child-only import | |
| Row mapping conflicts | Reject conflicting aliases, unsupported attributes, blank required selectors, duplicate organization/subinventory create rows, and duplicate parent/customer-site rows. Preserve identifiers as exact strings/integers and coordinate precision; report every affected row | Batch preparation | |

## Dependency-Aware Validation

| Applies When | Result | Next Action | Resolver |
|---|---|---|---|
| Only organization name/code supplied | Identity incomplete | Resolve and include OrganizationId before source generation | resolve_stocking_location_organization |
| Organization resolved, subinventory not verified | Selection incomplete | Verify the subinventory within that organization, never globally | resolve_stocking_location_subinventory |
| References, target or mappings change during preparation | Existing artifact validation does not cover corrected input | Prepare a corrected immutable artifact and rerun Task Hook before core approval; never reuse a preflight or Task Hook envelope for changed bytes | |

## Operation Contract

In this resource, captured records/values mean rows parsed from core's exact prepared immutable upload artifact for Task Hook review, not a persistent session snapshot or a reread original source. Core must finish serialization before this gate. Any needed correction starts fresh artifact preparation and Task Hook validation before approval.

The exact prepared immutable upload artifact and validated requested operation are authoritative for this validation. Evaluate every row; require one operation class per artifact and reject mixed parent/child mutations or mixed actions with an actionable request to split sources into separate prepared artifacts. A child-only source may contain header-only parent structure but no parent data operation. Do not mutate captured rows, fill missing keys in place, or infer action from defaults. Resolved values that differ from captured loader fields require a fresh corrected immutable artifact.

| Operation Class | Required Captured Values | Required Checks | Not Required |
|---|---|---|---|
| parent_create | RestAction=POST, resolved OrganizationId, Subinventory, type and condition accepted by current loader schema | Organization/subinventory match; parent absent; all supplied field validation | Existing parent key, technician assignment or customer-site lookup |
| parent_update | RestAction=PATCH, exact existing StockLocationId and loader-required keys, at least one requested writable change | Exact parent; canonical references; no technician assignment; changed-field validation; type lookup when supplied | Create-only fields not required by current update schema; customer-site lookup |
| parent_delete | RestAction=DELETE, exact existing StockLocationId and loader-required keys only | Exact parent; canonical references; no technician assignment; complete child collection empty | Type, condition, coordinates, active customer-site eligibility |
| child_create | RestAction=POST, existing StockLocationId, authoritative PartySiteId and PartySiteNumber; no generated SiteDedicatedLocId | Parent references; active customer-site match; relationship absent | Parent data row or technician assignment |
| child_update | RestAction=PATCH, existing StockLocationId and SiteDedicatedLocId, loader-required keys and requested writable changes | Parent/current child identity; customer-site resolution and duplicate check only when replacing association | New customer-site selection for unrelated field updates; parent data row |
| child_delete | RestAction=DELETE, existing StockLocationId and SiteDedicatedLocId plus loader-required keys only | Parent/current child identity; capture complete sibling identity set | Active customer-site eligibility, new site values or parent data row |

Human-readable current selectors may guide preparation, but captured keys must agree with the resolved identity before readiness. For key-only update/delete, resolve canonical organization/subinventory from the existing parent and validate those references without requiring them as payload fields unless loader metadata requires them. Validate optional fields only when supplied and permitted for the selected operation; deletion rows reject changed-field values beyond required keys/action. Positive int64 validation applies to all keys without rounding. Unknown actions, missing action, action/intent mismatch, missing current keys, ambiguous identities and duplicate mutation targets block.

For each row retain transient operationClass, parentPresent, childPresent, noOp and reference outcomes. not_applicable is allowed only under the explicit node conditions. Verified absence on deletion sets noOp; absence on update or child create fails. Skip dependent lookups for an absent target, but still require valid captured shape. All-row noOp returns the no-op terminal and stops preparation without submission. Mixed no-op and actionable rows fail with a request for a fresh source containing actionable rows only; do not silently drop captured rows.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| RCL.SLOC.VALIDATE | decision | 1 | validate_input | passed->RCL.SLOC.PARENT;failed->RCL.SLOC.ISSUES | none | stop | Validate captured operation and source using Operation Contract; no approval prerequisite |
