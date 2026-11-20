# ASL Status Defaulting Rules

The approved plan requires preservation of values and field presence except for explicitly declared boolean text normalization. Oracle's
[26D request contract](https://docs.oracle.com/en/cloud/saas/procurement/26d/fapra/op-purchasingapprovedsupplierliststatuses-post.html)
does not establish a client default for these business flags. A database NOT NULL
constraint is not a requirement to inject a value into every REST request.

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| Status and StatusDescription | None; missing required fields remain issues | Every row | No | |
| StatusId | None; never generate or resolve an ID | Every row | No | |
| Omitted optional fields | Remain absent; do not populate flags, description, or date | Every row, especially partial updates | No | |
| Accepted text in the three boolean fields | Typed true/false with raw input and conversion evidence retained | Before field validation via ASL.NORMALIZE_INPUT | Yes, only declared spellings | |
| Empty InactiveDate on explicit create | Preserve empty string as no initial date; never claim omission | JSON, CSV, and XLSX; single or bulk create | No | |
| Blank cells | Preserve empty strings; never reinterpret as omission or null | Every source format and every row | No | |
| Explicit null | Preserve the supplied null in evidence; never substitute a blank or invent a null marker | Any supplied field | No | |
| Supplied business values | Preserve exact names, types, precision, case, whitespace, and values | After boolean normalization and validation | No | |

## Permitted Boolean Normalization

Only AslDefaultFlag, AllowPurchasingApprovalFlag, and AllowSourcingFlag are
eligible. Trim and compare customer-friendly strings case-insensitively:
true/yes/y/1 become typed true; false/no/n/0 become typed false. Native booleans
remain unchanged. Retain an independent raw record and row/attribute conversion
evidence. Do not normalize any other value or field name. Accepted resulting
values are defined in [Field Validation](ora_input_validation.md#field-validation).

Use `../scripts/normalize_booleans.py`: `normalize_record` returns the typed
preparation view; `prepare_loader_record` produces canonical lowercase
"true"/"false" flag strings before source preparation. Helper success is not complete
ASL validation. Its encoding issues are governed by
[handoff gates](ora_error_handling.md#representation-and-handoff-gates).

## Source Preparation and Preservation

Keep absent fields absent. Blank cells, including short CSV rows padded during
capture, supply empty strings; they cannot represent per-row omission. For
explicit keep-date intent, prepare a source without the InactiveDate column.
Group records by supplied field set and compatible operation/date intent,
retaining original row references and scoped instructions outside business data.
Validation-cycle routing belongs to [skill routing](../SKILL.md#source-fidelity-and-inactivedate).

Preserve explicit create empty dates as no initial date. Plain-language date
clearing stays in caller context; do not manufacture null or a wire value from
it. [Design enforcement](ora_design_enforcement.md#design-rules) owns clearing
consent and scope; the handoff gates own serialization blockers.

After capture, retain an untouched copy of the validation cycle headers/rows. Use
`verify_captured_record` for a separate typed validation view and lossless ID
comparison. Preserve captured field presence and values; do not apply reported
changes to the capture. Recovery from a mismatch belongs to
[error handling](ora_error_handling.md#normalization-evidence-and-recovery).

## Delete Source Preparation

Use a dedicated delete source and validation cycle, separate from create/update
loads. Prepare a delete XLSX through core Data Loader's existing sample/preparation
workflow. These columns and values are a synthetic example:

| StatusId | RestAction |
|---|---|
| 300100676990233 | DELETE |

For explicit deletion, prepare exact RestAction=DELETE as separate loader
control metadata. Preserve the supplied ID and never default missing controls or
transform captured MERGE into DELETE. The accepted delete contract is defined
in [input validation](ora_input_validation.md#delete-validation).

Final directive/control agreement and unsupported conversion recovery belong to
the [prepared artifact gate](ora_error_handling.md#prepared-artifact-gate).

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| ASL.PRESERVE_VALUES | step | 20 | apply_default | preserved->ASL.CHECK_DESIGN;failed->ASL.HANDLE_ISSUES | ASL.VALIDATE_INPUT | stop | Verify captured field presence and values without rewriting rows; retain preparation evidence |
