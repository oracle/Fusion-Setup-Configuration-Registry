# Manage Legal Entity Input Validation

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Legal identity | Name, LegalEntityIdentifier, Country | Block before preview | User supplies the approved statutory identity; resolve Country as one enabled territory and one active country geography receipt | Always | resolve_entity_country_geography |
| Identifying jurisdiction | User-supplied identifying-jurisdiction name or partial search text | Ask for the missing name/search text and stop before preview; reuse it when already supplied | Resolve the input and any explicit candidate selection through the jurisdiction lookup | Always | resolve_entity_identifying_jurisdiction |
| Legal location | Existing or earlier-approved in-package legal address, identified by components, display address, or LeFormattedAddress | Block before preview | Resolve one active internal legal address in the same country | Always | resolve_entity_legal_address |
| Explicit identifying registrations | EntityRegistrationNumber and MainLruRegistrationNumber | Block before preview | User supplies both statutory numbers, each no longer than 30 and free of scoped collisions | Always | find_entity_conflict |
| Complete UI-equivalent aggregate | One XLE_ENTITY_PROFILE root, one same-name main XLE_ETB_PROFILE row, one identifying XLE_REGISTRATION row, and one identifying ORA_XLE_LEGAL_REPORTING_UNIT_REGISTRATION row | Block before preview | Author all four rows explicitly; root-only import does not regenerate children | Every CREATE |  |

## Dependency-Aware Validation

| Applies When | Result | Next Action | Resolver |
|---|---|---|---|
| Country input is present | Continue only with a uniquely resolved territory and effective primary country result under the country resolver | Populate root and main-LRU carriers using ora_defaulting_rules.md; no country GeographyId is required | resolve_entity_country_geography |
| Country geography resolves and jurisdiction input is available | Continue only with one resolved eligible jurisdiction and an unambiguous import Name under the jurisdiction resolver | Use the selected exact Name and registration type codes for both identifying children; keep separately evidenced localized UI labels distinct from codes | resolve_entity_identifying_jurisdiction |
| Legal address is supplied | Continue only with one exact active internal address or an earlier approved address row | Populate LegalAddress and both child FormattedAddress natural keys; keep LocationId blank | resolve_entity_legal_address |
| Identifier and name are ready | CREATE only when identifier has zero exact matches and name collision results are disclosed | Reuse or resolve conflict instead of duplicate creation | find_entity_conflict |
| Parent PSU is supplied or required | Continue only with one exact effective eligible PSU | Populate the natural parent identifier; retain physical ID only in receipt | resolve_entity_parent_psu |
| Function text or code is supplied | The enabled lookup may identify ICINV, ITC, DAS2, or SITC, but the candidate remains unsupported | Remove the function and preserve both function files with zero candidate rows | resolve_entity_enabled_function_code |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Required aggregate inputs | Reject blank Name, LegalEntityIdentifier, Country, legal address, EntityRegistrationNumber, or MainLruRegistrationNumber; collect missing identifying-jurisdiction input before preview | Always |  |
| Lengths | Reject Name over 240, LegalEntityIdentifier over 30, or either registration number over 30; never truncate | Values supplied |  |
| Country geography tuple | Require values consistent with the country mapping in ora_defaulting_rules.md, matching normal/transient fields, and the existing target CSV columns; do not substitute TerritoryShortName for GeographyName or an identifier-row key for GeographyId | Root and main-LRU rows | resolve_entity_country_geography |
| Identifying jurisdiction | Accept a supplied name/search term and explicit selection among eligible candidates; require the resolver's eligibility and exact-name uniqueness evidence, not merely user text | Every CREATE | resolve_entity_identifying_jurisdiction |
| Explicit children | Reject zero, duplicate, differently named, nonidentifying, or partial main-LRU/entity-registration/main-LRU-registration child rows | Every CREATE |  |
| Authority and functions | Reject PartyName, IssuingFormattedAddress, hidden authority/site values, or any function input; require both function CSVs to contain zero candidate rows | Every supported CREATE | resolve_entity_enabled_function_code |
| Dates and flags | Dates may be null; when both are supplied start must not follow end. TransactingEntityFlag, PsuFlag, and LegalEmployerFlag accept Y or N only | Applicable fields supplied |  |
| System ownership | Reject user-supplied physical IDs, LocationId, SourceId, audit, ESS, object-version, generated display, or other system values as CREATE values; display address text may identify the lookup row | Every CREATE |  |
| DFF and localization | Keep base families null unless a supplied or active runtime context requires exact segment validation | Context or segment supplied |  |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| LE.VALIDATE_INPUT | step | 10 | validate_input | valid->LE.RESOLVE_REFERENCES;invalid->LE.HANDLE_ERROR | none | stop | Before any lookup or package preview |
