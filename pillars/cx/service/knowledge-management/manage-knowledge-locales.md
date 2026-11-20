---
task_code: "ORA_CSO_LOCALES_MGMT"
task_name: "Manage Knowledge Locales"
parent_skill_id: "cx.service.knowledge-management"
pillar: "CX"
offering: "Service"
functional_area: "Knowledge Management"
functional_area_code: "ORA_CSO_KNOWLEDGE_MANAGEMENT"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
---

# Manage Knowledge Locales

## Setup Task Metadata

- Task name: `Manage Knowledge Locales`
- Task code: `ORA_CSO_LOCALES_MGMT`
- Available: `Y`
- Export/import supported: `Y`
- CSV export/import supported: `Y`
- CSV export/import routing: `supported`
- Data Loader import mode: `FSM`
- Business Object: ``

## FSM Contract

### ORA_CSO_LOCALE_OBJECT

- `referenceKey`: Use TENANT as the locale-root reference key. Do not create a new locale root or substitute a different tenant reference key.
- `recordId`: Use the locale identifier in language-and-territory form, such as en_US. Do not invent or reformat this value.
- `defaultLocale`: Read and retain the current value from the completed export. For an approved change, validate the requested language-and-territory code against the static Available Knowledge Locales list in the task guidance, then match it to exactly one ORA_CSO_ACTIVE_LOCALE_OBJECT.recordId row. Write that row's exact export representation, such as en_US rather than a reformatted code; do not select a supported locale that is absent from the active-locale object.
- `defaultPreferredLocale`: Read and retain the current value from the completed export. Before a locale change, if this value is missing or blank, obtain customer approval to use the effective defaultLocale or another supported locale. Reuse an explicitly requested preferred value; stop if no value is approved. For a default-locale change, the effective defaultLocale is the proposed new default; otherwise it is the current default. Preserve populated preferences unless their change is requested. For an approved change, validate the requested language-and-territory code against the static Available Knowledge Locales list in the task guidance, then write the exact current-export representation for the selected supported locale. Do not infer a locale code from its display name. Locale deactivation is unsupported by this workflow; do not prepare that change.

### ORA_CSO_ACTIVE_LOCALE_OBJECT

- `ORA_CSO_LOCALE_OBJECT.referenceKey`: Use TENANT as the active-locale row's parent linkage. Do not add an active-locale row without this matching parent relationship.
- `recordId`: Validate the requested language-and-territory code against the static Available Knowledge Locales list in the task guidance and use its exact current-export representation as the locale-code value. Match it to an existing active-locale row for review or default-locale selection. For an approved enable, add the supported locale using the fresh export's row shape. Activity is represented by row presence in ORA_CSO_ACTIVE_LOCALE_OBJECT.csv, not by an Active column or the Get Locales REST response. Do not remove an active-locale row to deactivate it; FSM deactivation is unsupported.
## Guard Rails

1. Require an authenticated Fusion user context before any Fusion operation; use `core.auth.fusion-oauth-authentication`.
2. Do not use `core.fusion-api.rest-api-client` to create, update, or delete records.
3. Do not use `shared.setup-import.task-level-import` to create, update, or delete records.
## Purpose

Manage Knowledge locales and their active and default states.
## Use Cases

### View All Locales

View all available Knowledge locales.

1. Export locales with shared.setup-export.task-level-export.

### View All Active Locales

View active Knowledge locales.

1. Export locales with shared.setup-export.task-level-export.
2. Read ORA_CSO_ACTIVE_LOCALE_OBJECT.csv; do not use the Get Locales REST response for active-state determination.

### View All Inactive Locales

View inactive Knowledge locales.

1. Export locales with shared.setup-export.task-level-export.
2. Treat available locales absent from ORA_CSO_ACTIVE_LOCALE_OBJECT.csv as inactive; do not use the Get Locales REST response.

### View Default Locale

View the default API locale.

1. Export locales with shared.setup-export.task-level-export.
2. Read defaultLocale from ORA_CSO_LOCALE_OBJECT.csv.

### View Default Preferred Knowledge Locale

View the default preferred Knowledge locale.

1. Export locales with shared.setup-export.task-level-export.
2. Read defaultPreferredLocale from ORA_CSO_LOCALE_OBJECT.csv.

### Activate Knowledge Locale

Activate a Knowledge locale.

1. Export locales with shared.setup-export.task-level-export.
2. If defaultPreferredLocale is missing or blank, obtain customer approval to use the effective defaultLocale or another supported locale. Reuse an explicitly requested preferred value. Explain the impact on users without their own preference; wait for approval and stop if declined. Preserve a populated preference unless its change is requested.
3. Set the selected supported locale to active.
4. Validate the FSM package with shared.validation.setup-data-validator.
5. Import the approved ZIP with core.data-loader.
6. Verify the locale is active with a fresh export.

### Deactivate Knowledge Locale

Deactivate a Knowledge locale.

Not supported. Locale deactivation is not supported.

### Change Default Locale

Change the default API locale.

1. Export locales with shared.setup-export.task-level-export.
2. If defaultPreferredLocale is missing or blank, obtain customer approval to use the effective defaultLocale or another supported locale. Reuse an explicitly requested preferred value. Explain the impact on users without their own preference; wait for approval and stop if declined. Preserve a populated preference unless its change is requested.
3. Show "Changing the default locale will impact the display language for knowledge objects that are not available in the requested language or locale and are therefore displayed in the default locale. Before a locale can be set to the new knowledge default locale, all knowledge objects must be translated into this locale." and wait for confirmation.
4. Set an active locale as the default locale.
5. Validate the FSM package with shared.validation.setup-data-validator.
6. Import the approved ZIP with core.data-loader.
7. Verify the default locale with a fresh export.

### Change Default Preferred Knowledge Locale

Change the default preferred Knowledge locale.

1. Export locales with shared.setup-export.task-level-export.
2. If defaultPreferredLocale is missing or blank, obtain customer approval to use the effective defaultLocale or another supported locale. Reuse an explicitly requested preferred value. Explain the impact on users without their own preference; wait for approval and stop if declined. Preserve a populated preference unless its change is requested.
3. Set the selected locale as the default preferred Knowledge locale.
4. Show "Changes to this setting will change the default locale in My Knowledge, the Knowledge Panel and Knowledge Authoring for users who have not set a preferred knowledge locale in their user preferences. Do you want to change the default preferred knowledge locale?" and wait for confirmation.
5. Validate the FSM package with shared.validation.setup-data-validator.
6. Import the approved ZIP with core.data-loader.
7. Verify the default preferred locale with a fresh export.

### Create Knowledge Locale

Create a Knowledge locale.

Not supported. Locale creation is not supported.

### Delete Knowledge Locale

Delete a Knowledge locale.

Not supported. Locale deletion is not supported.
## CSV Export, Import, and Validation Workflow

`CSVExportImportSupportedFlag` is `Y` for this task, so route task setup data work through the relevant skills:

1. Export task setup data with `shared.setup-export.task-level-export`.
2. Validate exported or prepared task setup data with `shared.validation.setup-data-validator`.
3. Import setup task data with `core.data-loader`.

Use this task metadata when invoking those skills:

- Offering: `Service`
- Functional area / Setup Object: `Knowledge Management`
- Setup task name: `Manage Knowledge Locales`
- Setup task code: `ORA_CSO_LOCALES_MGMT`




## FSM Data Loader Package Requirements

1. Read the task's fsm_contract first when it is present. Treat its objects and field guidance as the task-specific starting point for classifying each requested change as an existing-root update, new root, existing-child update, new child of an existing parent, new relationship, or mixed package change.
2. Read `ASM_SETUP_CSV_METADATA.xml` in the task export package for business objects, XML paths, node sequence, attributes, scope, and relationships; reconcile it with the task's fsm_contract when one is present.
3. Use the fsm_contract object and field guidance together with metadata-defined node sequence and relationships to determine package order and required object coverage.
4. Verify the selected baseline or template package includes the members, file names, structure, headers, encoding, scope, relationship rows, and fsm_contract objects and fields required for the requested change.
5. Treat a completed export of this same setup task as authoritative evidence for package structure, headers, node order, key and linkage shape, and generated-identity handling. Use it to corroborate the fsm_contract and record provenance for copied template values.
6. For existing-row updates, retain exported identities and all unchanged values, parent rows, child rows, and relationships required by the fsm_contract and package evidence; do not carry unrelated baseline rows into the change package unless they are required for import integrity. Change only approved fields.
7. For a new child or relationship, retain the existing parent identity and use only linkage, keys, and required values specified by the fsm_contract or confirmed by same-task package evidence.
8. For greenfield rows, construct the create contract from the fsm_contract, task-specific documented requirements, `ASM_SETUP_CSV_METADATA.xml`, a completed export of this same task, and supported preview or dry-run results where available.
9. An export whose data CSV members contain only headers is valid structural evidence for a greenfield contract, not an automatic blocker. Use the fsm_contract, exported package structure, and explicit supported inputs to construct the rows; stop only when required fields, keys, relationships, or values remain unresolved or validation rejects the package.
10. Populate every root, child, scoped, localized, and relationship object required by the fsm_contract or confirmed package contract. Populate approved business keys, required values, and reference values; omit generated identities unless explicitly required.
11. Classify every populated fsm_contract field as request-provided, documented requirement, export-derived structural value, export-derived template value, generated or omittable, or unresolved.
12. A fsm_contract field may be omitted only when it is documented as generated or optional, is absent or consistently blank in semantically comparable exports of this same task, or is accepted as omitted by supported preview or dry-run validation. Do not infer a value solely from a field name or description.
13. Do not copy identities, reference keys, parent keys, scope values, localized values, lookup codes, or behavior-changing settings unless the fsm_contract, request, documented guidance, or approved compatible template default explicitly supports the value.
14. Verify every non-generated parent, lookup, code, scope, locale, and related-object reference required by the fsm_contract against approved same-task package evidence or the workflow's documented resolver; include required parents or relationship rows only when the package contract requires them.
15. Build the complete package required by the fsm_contract and package evidence; never use a child-only package or infer fields, defaults, identities, or relationships from another task or object type.
16. Validate package members, fsm_contract objects and fields, metadata, keys, scopes, references, relationships, node order, field-value provenance, and approved changes before import; confirm that no baseline identity, template-only setting, or unrelated row is introduced or modified unintentionally. Use preview or dry-run validation when available.
17. Stop when a required fsm_contract field or object, identity rule, parent-child linkage, scope, dependency, or behavior-changing setting remains unresolved and lacks an explicit approved value or sufficient same-task evidence. Do not block for fields evidenced as generated or validated-omittable.
## Available Knowledge Locales

Use Oracle's [List of Available Locales](https://docs.oracle.com/en/cloud/saas/fusion-service/farik/available-locales.html) as the authoritative catalog of supported Knowledge locales. Locale codes use a hyphen between language and territory. Do not derive the supported-locale catalog from the Get Locales REST response; use the Manage Knowledge Locales FSM export/import workflow for tenant locale setup data.

| Language | Locale codes |
| --- | --- |
| Arabic | `ar-EG`, `ar-SA`, `ar-AE`, `ar-DZ`, `ar-BH`, `ar-IQ`, `ar-JO`, `ar-KW`, `ar-LB`, `ar-LY`, `ar-MA`, `ar-OM`, `ar-QA`, `ar-SY`, `ar-TN`, `ar-YE` |
| Chinese (Simplified) | `zh-CN`, `zh-HK`, `zh-MO`, `zh-SG` |
| Chinese (Traditional) | `zh-TW` |
| Croatian | `hr-HR` |
| Czech | `cs-CZ` |
| Danish | `da-DK` |
| Dutch | `nl-BE`, `nl-NL` |
| English | `en-AU`, `en-CA`, `en-IE`, `en-NZ`, `en-GB`, `en-US`, `en-HK`, `en-IS`, `en-IN`, `en-ID`, `en-IL`, `en-SG`, `en-SA` |
| Finnish | `fi-FI` |
| French (Canadian) | `fr-CA` |
| French (European) | `fr-BE`, `fr-FR`, `fr-CH`, `fr-LU` |
| German | `de-AT`, `de-DE`, `de-CH`, `de-LU` |
| Hebrew | `he-IL` |
| Hungarian | `hu-HU` |
| Italian | `it-IT`, `it-CH` |
| Japanese | `ja-JP` |
| Korean | `ko-KR` |
| Norwegian | `no-NO` |
| Polish | `pl-PL` |
| Portuguese | `pt-BR`, `pt-PT` |
| Romanian | `ro-RO` |
| Russian | `ru-RU` |
| Slovak | `sk-SK` |
| Spanish | `es-MX`, `es-ES`, `es-AR`, `es-CL`, `es-CO`, `es-CR`, `es-EC`, `es-SV`, `es-GT`, `es-HN`, `es-NI`, `es-PA`, `es-PE`, `es-PR`, `es-US`, `es-VE` |
| Swedish | `sv-SV` |
| Thai | `th-TH` |
| Turkish | `tr-TR` |
| Vietnamese | `vi-VN` |

## Usage

Use this metadata file when planning, sequencing, exporting, importing, or validating setup data for `Manage Knowledge Locales` under `Knowledge Management`.


## Locale Identifier Comparison

For supported-locale checks only, compare language/territory codes without case
sensitivity and treat a hyphen and underscore as equivalent separators. This
comparison does not supply an FSM identifier. Resolve exactly one matching
owner-task export row and retain its recordId/localeId byte for byte for package
serialization and parent links. If normalized comparison matches multiple rows,
stop rather than choose a spelling. If an enable operation has no active row,
require approved same-task schema/validation evidence for the supplied new code;
do not generate a code by replacing separators or deriving a display name.
