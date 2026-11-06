# Input Validation

## Required Client Inputs

| Input | Required When | Validation |
|---|---|---|
| Value Set Code | Every definition | Supply one explicit code. |
| Description | Optional | Preserve a supplied value; otherwise apply the user-friendly code-derived default in `ora_defaulting_rules.md`. |
| Validation Type | Every definition | Accept the resolved or explicit `Format Only`, `Independent`, `Dependent`, or `Table` choice. |
| Value Data Type | Every definition | Select `Character`, `Number`, `Date`, or `Date Time`. |
| Definition fields | Every definition | Supply the fields required by the selected matrix row below. |
| Independent Value Set Code | Validation Type is Dependent | Supply exactly one parent code. If it is missing, ask which independent value set the dependent set must use; parent readiness is a dependency check. |
| Data Security Resource Name | Security Enabled is Yes | Supply one nonblank target-supported object. |
| Value rows | Requested scope includes Manage Values | Supply the value-row fields for the selected data type. |

## FSM-Supported Client Choices

### Immediate Invalid-Value Rejection

For a new Character definition, resolve Maximum Length from the
customer-supplied value when present; otherwise use the default `20`. For an
existing Character value set receiving new values, use its verified target
Maximum Length. Do not apply the default `20`, create a new definition, or
change the existing definition. Calculate every nonblank proposed value's
character count by Value Set Code and reject every value that exceeds the
resolved length. Do not derive or increase the definition length from a value row, and do not truncate,
abbreviate, normalize, or rename a supplied value to fit. Stop before lookup,
package generation, or Fusion import when this check fails, and report each
set, value, actual length, and resolved Maximum Length.

After the case-handling rules in `ora_reference_lookups.md` have resolved the
working values, repeat length validation on those values before package
generation. Uppercasing is not a way to shorten an invalid value. A derived
new-definition length must accommodate both original and converted values;
never increase an existing definition's length automatically.

| Field | Allowed Client Choices | Applies When |
|---|---|---|
| Validation Type | Format Only, Independent, Dependent, Table | Every definition |
| Value Data Type | Character, Number, Date, Date Time | Every definition |
| Value Subtype | Format Only + Character: Text, Numeric digits only, Time (20:08), Time (20:08:08). Independent or Dependent + Character: Text, Translated text, Numeric digits only, Time (20:08), Time (20:08:08). | Character combinations that require a subtype |
| Maximum Length | Positive whole number | Character combinations that require it |
| Precision | Nonnegative whole number | Number |
| Scale | Nonnegative whole number | Number |
| Uppercase Only | Yes, No | Value Subtype is Text when supported by the selected target contract |
| Zero Fill | Yes, No | Value Subtype is Text when supported by the selected target contract |
| Security Enabled | Yes, No | Independent, Dependent, or Table |

## Technical Identifier Validation

Check every supplied or derived `ValueSetIdentifier` before ZIP creation and
submission. Maximum length: **30 characters**, separate from value-row length.
Stop if it is too long; do not silently shorten it or replace an existing identifier.

Keep the identifier hidden, but show each set's check in the Design and Final
ZIP previews: `Passed — <length>/30`, `Failed — <length>/30`, or `Unresolved`.
Do not show Passed until checked. Obtain approval for any corrected default.

## FSM Definition Field Matrix

Ask only for fields in the selected row. A field not required by that row stays
blank unless the approved design or target package contract requires it.

| Validation Type | Value Data Type | Required definition fields |
|---|---|---|
| Format Only | Character | Value Subtype; Maximum Length; and, when Value Subtype is Text and the current same-task export contains the columns, Uppercase Only and Zero Fill. Minimum Value and Maximum Value are optional. |
| Format Only | Number | Precision; Scale; optional Minimum Value and Maximum Value. |
| Format Only | Date | Optional Minimum Value and Maximum Value. |
| Format Only | Date Time | Optional Minimum Value and Maximum Value. |
| Independent | Character | Value Subtype; Maximum Length; optional Minimum Value and Maximum Value; applicable uppercase-only and zero-fill flags; conditional security fields. For Text, use the default proposal in `ora_defaulting_rules.md` when the client leaves a field blank. |
| Independent | Number | Precision; Scale; optional ranges; Security Enabled and Data Security Resource Name only when security is enabled. |
| Independent | Date | Optional ranges; Security Enabled and Data Security Resource Name only when security is enabled. |
| Independent | Date Time | Optional ranges; Security Enabled and Data Security Resource Name only when security is enabled. |
| Dependent | Character | Value Subtype; Maximum Length; optional Minimum Value and Maximum Value; applicable uppercase-only and zero-fill flags; Independent Value Set Code; conditional security fields. |
| Dependent | Number | Precision; Scale; optional ranges; Independent Value Set Code; conditional security fields. |
| Dependent | Date | Optional ranges; Independent Value Set Code; conditional security fields. |
| Dependent | Date Time | Optional ranges; Independent Value Set Code; conditional security fields. |
| Table | Character, Number, Date, or Date Time | From Clause; Value Column Name; and only approved optional table fields. Do not infer database objects or SQL. |

## Field and Cross-Field Checks

| Check | Applies When | Validation |
|---|---|---|
| Character fields | Character | Require a supported subtype and Maximum Length. When Value Subtype is Text and the current same-task export contains case and fill columns, resolve both flags before packaging. |
| Uppercase Only | Value Subtype is Text and the current same-task export contains `UppercaseOnlyFlag` | Default to Yes when blank. Serialize the resolved Yes or No value; never serialize a blank. Before package approval, recommend the default and ask whether the customer wants to keep or change it. |
| Zero Fill | Value Subtype is Text and the current same-task export contains `ZeroFillFlag` | Default to No when blank. Serialize the resolved Yes or No value; never serialize a blank. |
| Value-length capacity | Independent or Dependent + Character with value rows | For a new definition, use the customer-supplied Maximum Length when present; otherwise use default 20. For an existing Value Set, use the verified target Maximum Length and add only the requested values; do not create or update its definition. Require every value to fit the resolved length. Do not derive, increase, truncate, or rename values. |
| Number fields | Number | Reject Precision or Scale for another data type; reject Scale greater than Precision when both are supplied. |
| Format Only | Format Only | Reject parent and security fields. For a Character / Text definition, accept and resolve Maximum Length and the case/fill flags whenever the current same-task export supports those columns; do not label supported flags Not applicable. |
| Security fields | Security input is supplied | Require an object when enabled; require a blank object when disabled or Format Only is selected. |
| Parent fields | Independent or Dependent | Independent definitions must have blank parent fields. Dependent definitions must supply an exact Independent Value Set Code; evaluate its readiness through VSET-PARENT. |
| Table fields | Table | Require From Clause and Value Column Name plus only target-required optional attributes. |
| Value row | Scope includes Manage Values | Require ValueSetCode, exactly one matching typed Value, and EnabledFlag `Y` or `N`; Dependent rows also require exactly one matching typed parent value. |
| Duplicate value row | Scope includes Manage Values | Check both source and canonical working rows after applicable case conversion. Reject repeated independent set-value keys or dependent set-parent-child keys, including distinct inputs that become identical after uppercasing. Show affected source records and converted keys; do not silently merge rows or choose between conflicting descriptions or attributes. Repeated references may share a lookup, but proposed value-definition rows must be unique. |
| Value description | Value rows contain descriptions | Reject a description longer than 240 characters. |
| Date range | Value rows contain both dates | Reject Start Date later than End Date. |

## Invalid Definition Response

When supplied fields are incompatible, render the validation result before any
proposal table, lookup, ZIP generation, or Fusion operation. State the exact
conflict, then give the customer every safe correction path and the applicable
readiness recommendations; do not compress this into a one-line blocker.

For an Independent definition that includes an Independent Value Set Code, use
this response structure:

```text
This request is invalid as written: an **Independent** value set cannot have a
parent value set.

Choose one:

- Create <ValueSetCode> as an Independent value set: remove <ParentValueSetCode>
  and provide the Value Data Type.
- Create it under <ParentValueSetCode>: change Validation Type to Dependent,
  then provide the Value Data Type and any conditional fields.

Recommendations shown with the proposal:

- Verify <ParentValueSetCode> is an existing compatible Independent parent
  before preparing a Dependent definition.
- Do not generate a package until the parent and selected data type are
  confirmed.
```

For another incompatible combination, retain the same headings and level of
detail: explain the exact invalid combination, show each valid correction, and
state the next required validation. Do not infer a replacement validation type,
parent, data type, length, security setting, or value row.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---:|---|---|---|---|---|
| VSET.VALIDATE_INPUT | decision | 10 | validate_input | valid->VSET.RESOLVE_DEPENDENCIES;missing_required_input->VSET.REQUEST_REQUIRED_INPUT;invalid->VSET.HANDLE_INPUT | none | stop | Every request |
| VSET.REQUEST_REQUIRED_INPUT | step | 15 | evaluate_result | stopped->VSET.ISSUES | VSET.VALIDATE_INPUT | stop | Render the Definition Proposal Preview with `new value set` when the Value Set Code is missing and `Required` for every unresolved required field. Request only the missing inputs. Do not perform lookup, package, or import work. |
