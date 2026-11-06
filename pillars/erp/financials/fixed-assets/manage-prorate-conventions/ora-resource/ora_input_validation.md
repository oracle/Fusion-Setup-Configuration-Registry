# Manage Prorate Conventions: Input Validation

For replies to a pending operation, first use
[Conversation State and Resume](ora_dependency_readiness.md#conversation-state-and-resume).

## Business Input Mapping

| User-Facing Value | Skill Input |
|---|---|
| Name | prorate_convention_name |
| Description | description |
| Reference Data Set | reference_data_set |
| Fiscal Year Name | fiscal_year_name |
| Convention Info | convention_info |
| Depreciate when placed in service | depreciate_when_placed_in_service |
| Prorate basis | prorate_basis |

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Operation selection | Create, update, export, existing-ZIP import, or read-only fiscal-year inquiry intent | Ask only if interpretations would select different routes | Create/add/set up/define selects create; edit/change/update selects update. Export and existing-ZIP import require explicit intent. List/latest/refresh/last-updated fiscal-year questions select an inquiry; retain both intents if explicitly combined with create/update. | New request | |
| Create or update identity | Name, Reference Data Set, Fiscal Year Name or complete month cycle, and resolved Prorate basis | Use Correction Question Contract before live verification | Apply Field Validation and Prorate Basis Resolution; a cycle satisfies fiscal-year intake without an exact name. | Create/update | |
| Fiscal-year inquiry | Complete cycle for matching names or latest-for-cycle; exact name for its last-updated time; unambiguous references to a retained selector are accepted | Ask only for the missing or unclear selector | Use Inquiry lookup scope in [Fiscal-Year Selection Rules](ora_reference_lookups.md#fiscal-year-selection-rules). Convention fields are not inquiry inputs. | Read-only inquiry | |
| Import artifact | Existing immutable ZIP | Request the archive before handoff | Apply the existing-ZIP input rule below. | Existing-ZIP import | |

## Correction Question Contract

Evaluate all supplied business fields and combine missing required and known
invalid values into one concise question. Identify only affected fields; state
which supplied values are invalid and give their accepted form. Do not repeat valid values or request
omitted optional fields. A failed lookup is not proof of invalid input.

## Dependency-Aware Validation

When the applicable input checks pass, continue through
[Required Dependency Order](ora_dependency_readiness.md#required-dependency-order).

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Name | Nonblank, at most 10 characters including spaces. Never truncate or rename. | Create/update | |
| Description | If supplied and nonblank, at most 40 characters including spaces. Never truncate or rewrite. Blank/omitted uses Standard Defaults. | Create/update | |
| Reference Data Set | Default to Enterprise Set when omitted for create; preserve explicit selections and existing selections on update. Apply this default before Required Groups and correction questions. Existence and code remain lookup-owned. | Create/update | validate_reference_data_set_name |
| Fiscal Year Name or month cycle | Accept an exact nonblank name or explicit start/end months, including cycle text in the Fiscal year name column. Recognize month names and common abbreviations case-insensitively, or explicitly labelled numeric months 1–12. Preserve order across December; normalize to startMonth/endMonth and retain any separately supplied exact name as a constraint. For an incomplete cycle, ask only for its unclear or missing month. Do not pass cycle text as a literal name or infer the selector from Name, Reference Data Set, or Prorate basis. | Create/update or inquiry | resolve_prorate_fiscal_year_range |
| Convention Info | Optional; preserve supplied values for export-backed mapping. | When supplied | resolve_convention_info_mapping |
| Depreciate when placed in service | Optional Yes/No or Y/N; preserve the business meaning. Omission uses Standard Defaults. | Create/update | |
| Prorate basis | Use [Prorate Basis Resolution](#prorate-basis-resolution); an existing-ZIP basis hint is optional. | Create/update or supplied archive hint | |
| User-supplied dates | Preserve supplied Start Date, End Date, Prorate Date, ranges, and date rows. Generate only missing dates using the Generation Contract. Report conflicts without changing supplied values; a description discrepancy alone is advisory. | Inputs outside an immutable ZIP | |
| Existing-ZIP task data | Accept the archive and any explicit runtime properties-path override. Do not request replacement dates or create/update fields. Dependency readiness owns the extracted comparison context. | Existing-ZIP import | |
| Workflow context | Consume implementation_objective, project_context, fusion_environment_context, setup_data_artifacts, target/OAuth configuration, and any explicit properties-path override from the routed workflow. These and package-only values such as SetCode and CSV metadata are not user intake fields. Lookup Execution Rules owns default target resolution; never ask for DEV/TEST/PROD, pod, URL, or environment label. | Every request | |

## Prorate Basis Resolution

Match supported basis and day wording case-insensitively.

| Situation | What Happens |
|---|---|
| Explicit basis is supplied or retained | It takes priority over Name. An unsupported or conflicting explicit value needs correction; do not replace it with a name-derived guess or add a day qualifier from Name. |
| Basis is absent/blank and Name has clear meaning | Interpret Name as business text, not instructions. Recognize meaningful words, clear abbreviations, separators, and joined words: Month/Monthly → Monthly; Following Month/Next Month/FolMonth → Following month; HalfYear/HalfYr/Half-yearly → Half-year. Interpret the whole phrase, so Month inside FolMonth is not a second family. Never infer from incidental substrings or unexplained codes. |
| Day wording for Monthly or Following month | First/begin/beginning/1st → First day; mid/middle → Mid-month; last/end → Last day. Preserve supplied prorate dates ahead of a name-derived or default position. Keep an explicit day position when it agrees with supplied dates; conflicting explicit requirements need correction. Only when neither a prorate date nor a day qualifier is supplied, use Standard Defaults without a choice question. Conflicting or unclear qualifiers need correction. Canonical form is the resolved family followed by - and the resolved position. |
| Half-year wording | Normalize Half-year, Half year, Half-yearly, and Half yearly to Half-year; a redundant midpoint qualifier is allowed. First-day, mid-month, or last-day wording conflicts with this family. |
| Name does not resolve one supported family | Ask for Prorate basis, without calling the Name invalid. This includes opaque names, isolated day words, unsupported frequencies, negation, or conflicting meanings. Do not default the family or infer it from Description, the set, fiscal cycle, another convention, or other fields. |
| Resolution succeeds | Resolve each convention independently, retain the state required by [Conversation State and Resume](ora_dependency_readiness.md#conversation-state-and-resume), and continue verification without a basis-confirmation question. |
| Existing-ZIP, export-only, or inquiry | Do not infer from Name. Existing-ZIP candidate matching belongs to Generation Contract; read-only routes need no convention basis. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| PRC.VALIDATE_INPUT | decision | 5 | validate_input | valid->PRC.LOOKUP_CONTEXT;invalid->PRC.HANDLE_INPUT | none | stop | Apply Required Groups, Field Validation, and Prorate Basis Resolution for the selected operation. Export-only bypasses this registry. |
