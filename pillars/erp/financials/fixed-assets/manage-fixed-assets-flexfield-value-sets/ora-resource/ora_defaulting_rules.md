# Defaulting Rules

## Default Sources

First-time-definition defaults apply only when VSET.LOOKUP_EXISTING returned
absent. When VSET.CHECK_VALUE_SCOPE returns values_missing, retain all existing
material definition fields and existing values unchanged. Apply only requested
values and documented value-row defaults to the confirmed-missing additions;
do not derive or default the existing ValueSetIdentifier, ModuleId, length,
flags, description or validation type. The reference lookup owns the exact
existing-definition-to-package mapping and its completeness check.

| Source | Defaulting use |
|---|---|
| Fixed Assets ModuleId fallback | Fill a blank ModuleId for a first-time definition. |
| Approved client design | Preserves client-supplied code, description, validation choice, length, flags, security, values, and dates. |

## Standard Defaults

Use `ora_input_validation.md` to present the allowed client choices. The table
below is the initial **Independent / Character / Text** default proposal: each
default applies only when the user leaves that field blank, and never replaces
an explicit client value. If the user selects a different Validation Type,
Value Data Type, or Value Subtype, use the matching Definition Field Matrix.

| Field | Internal | Default Value | Applies When | Replace Explicit Client Value? | Resolver |
|---|---|---|---|---|---|
| ValueSetCode | No | No default | Every definition | No | |
| ModuleId | No | `47110F64AC0708E2E040449823C60DB6` | User leaves it blank | No | |
| ValueSetIdentifier | Yes | Derive from ValueSetCode; maximum 30 characters | User leaves it blank | No | |
| Description | No | Human-readable sentence-case form of ValueSetCode | User leaves it blank for a new definition | No | |
| ValidationType | No | `INDEP` | User leaves it blank | No | |
| ValueDataType | No | `VARCHAR2` | User leaves it blank | No | |
| ValueSubtype | No | `TEXT` | User leaves it blank | No | |
| MaximumLength | No | `20` | User leaves it blank for a new Character definition | No | resolve_value_set_definition_fields |
| Precision | No | Blank | User leaves it blank | No | |
| Scale | No | Blank | User leaves it blank | No | |
| UppercaseOnlyFlag | No | `Y` | Value Subtype is Text, the current same-task export contains the column, and user leaves it blank | No | |
| ZeroFillFlag | No | `N` | Value Subtype is Text, the current same-task export contains the column, and user leaves it blank | No | |
| SecurityEnabledFlag | No | `N` | User leaves it blank | No | |
| DataSecurityObjectName | No | Blank | User leaves it blank | No | |
| MinimumValue | No | Blank | User leaves it blank | No | |
| MinimumValueNumber | No | Blank | User leaves it blank | No | |
| MinimumValueDate | No | Blank | User leaves it blank | No | |
| MinimumValueTimestamp | No | Blank | User leaves it blank | No | |
| MaximumValue | No | Blank | User leaves it blank | No | |
| MaximumValueNumber | No | Blank | User leaves it blank | No | |
| MaximumValueDate | No | Blank | User leaves it blank | No | |
| MaximumValueTimestamp | No | Blank | User leaves it blank | No | |
| Audit columns (CreationDate, CreatedBy, LastUpdateDate, LastUpdatedBy, LastUpdateLogin) | Yes | Leave system-managed | Every package | No | |
| IndependentValueSetCode and typed parent field | No | Blank for nondependent values; populate only from a verified compatible parent | A dependent definition or value requires parent context | No | resolve_parent_value |
| Independent definition value rows | No | Leave absent for an approved definition-only request; populate only when the requested scope explicitly includes Manage Values | ValidationType is Independent | No | resolve_value_set_definition_fields |
| Table validation attributes | No | No generic default; populate only the export-supported attributes of the approved matching validation-table definition | ValidationType is Table | No | resolve_value_set_definition_fields |
| Values per set | No | Derive values from the approved request; apply the parent Fixed Assets Import Scope rule | Every value set | No | resolve_export_package_inventory |

For a different validation-type/data-type selection, use the matching FSM
Definition Field Matrix in `ora_input_validation.md`; do not carry this
proposal's subtype, length, flags, parent, or range values into it.

## Definition Proposal Preview

For **every new value-set definition request**, before a live lookup or package
work, render this exact Field/Value proposal layout. Use it for complete,
code-only, and partially specified requests; do not replace it with a bullet
list or a missing-field-only response.

```text
Proposed <ValueSetCode or "new value set"> definition:

| Field | Value |
|---|---|
| Module | Fixed Assets |
| Validation | <resolved or proposed value> |
| Data type | <resolved or proposed data type / subtype> |
| Maximum length | <supplied value, proposed value, or Required> |
| Uppercase Only | <resolved or proposed value> |
| Zero Fill | <resolved or proposed value> |
| Security | <resolved or proposed value> |
| Description | <supplied value or human-readable ValueSetCode description (proposed)> |
| Value rows | <requested scope or None — definition only> |
| Technical identifier check | <Passed or Failed — length/30, or Unresolved> |

Recommendations shown with the proposal:
- Review or change any proposed value before continuing.
- When a Value Set Code is supplied, run the read-only existence check directly. The customer may still change any proposed value before package creation.
- When one or more required inputs are absent, use `new value set` when the Value Set Code is absent and show `Required` for each unresolved field. Then request only the missing inputs. Do not perform a lookup, create a package, or import until they are supplied.
- No FSM package or import will be created at this stage. Request approval only for package creation and import submission.
```

Apply explicit client values first. For a code-only request, propose
Independent / Character / Text, Uppercase Only: Yes, Zero Fill: No, Security:
No, a human-readable sentence-case Description derived from the Value Set Code, and no value rows. When Maximum Length is not supplied,
show `20 (proposed)`. For a
Character request without a subtype, show `Character / Text (proposed)` and
state the other supported choices only as optional changes.

For every Text-subtype definition, including Format Only, when the current
same-task export contains `UppercaseOnlyFlag` and `ZeroFillFlag`, show and
describe the resolved flags as Yes or No in previews. Serialize them only
as uppercase `Y` or `N`, respectively. Do not label either
supported field Not applicable or serialize it blank. A client may override
either default with an explicit supported value.

For a definition-only request, show only the resolved proposal values and the
recommendations above, including the technical identifier check result. Keep
the identifier value internal; do not restate defaulting rationale or value-row
length validation in customer-facing text.

If the client changes Validation Type, Value Data Type, or Value Subtype,
discard incompatible proposal fields and use the matching Definition Field
Matrix. Do not create a ZIP, call Fusion, or imply that a definition was
created while any required input remains unresolved.

## ValueSet Identifier Derivation

| Source Value | Derived ValueSetIdentifier | Rule |
|---|---|---|
| test-1-fixedassets | Test1FixedAssets | Remove nonalphanumeric separators and capitalize the next alphabetic character after each separator; capitalize the first alphabetic character for user-provided ValueSetCode sources. |
| tst1 fixedassets | Tst1FixedAssets | Remove the space and capitalize the next alphabetic character. |
| test1@fixedassets | Test1FixedAssets | Remove the special character and capitalize the next alphabetic character. |

## Default Safety Rules

| Situation | What Happens |
|---|---|
| A business value is absent | Do not guess the code, parent, or value. Apply only the documented defaults above for blank definition fields. |
| Description is blank for a new definition | Derive a human-readable sentence-case Description by replacing separators with spaces, retaining recognized uppercase acronym tokens such as `FA`, and lowercasing ordinary words after the first word. For example, `FA_SERIAL_REFERENCE_1002` becomes `FA serial reference 1002`. A client-supplied Description always replaces this default. |
| Character value rows are supplied and MaximumLength is blank | Use default 20 and apply the value-length capacity rule in ora_input_validation.md to original and canonical values for that exact new set. Never derive a longer definition, truncate, or abbreviate a value. |
| Character definition has no value rows and MaximumLength is blank | Propose MaximumLength 20. |
| Text-subtype export fields are present | Resolve Uppercase Only and Zero Fill for every validation type, including Format Only. Default Uppercase Only to `Y` and Zero Fill to `N` only when the client leaves them blank; translate client-supplied supported values case-insensitively to uppercase `Y`/`N` before serialization. Show Yes/No in previews. |
| A client supplies a business value | Preserve the original input. A customer-supplied MaximumLength replaces the default and is the sole value-row length limit for that definition. When Value Subtype is Text and Uppercase Only defaults to or is selected as Yes, apply the conversion rules in ora_reference_lookups.md. In the Design Preview, recommend the default in plain language and ask whether the customer wants to keep or change it; do not show a conversion-only list. Other defaults fill only blank fields unless the client explicitly approves a correction. |
| A selected combination changes | Re-evaluate the Definition matrix. Do not carry subtype, length, parent, range, precision, or flag values from the previous selection unless the new combination explicitly supports them. |
| Security is not selected | Keep DataSecurityObjectName blank; do not retain a security object from a prior selection. |
| A blank is intentional | Serialize a true empty CSV field, never whitespace, `null`, `None`, or escaped control text. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---:|---|---|---|---|---|
| VSET.APPLY_DEFAULTS | step | 40 | apply_default | applied->VSET.SELECT_PACKAGE_SOURCE | VSET.LOOKUP_EXISTING | stop | Definition is absent, or CHECK_VALUE_SCOPE confirmed values_missing; preserve existing definitions in the latter branch |
