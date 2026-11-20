# Service Provider CSV Preparation Defaults

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| UserDefined | Y | Provider business-input create only, when UserDefined was not supplied; unchanged completed-export imports and other BOs are not applicable | No | |
| DelStatusUpdateEnabled | N | Provider business-input create only, when DelStatusUpdateEnabled was not supplied; unchanged completed-export imports and other BOs are not applicable | No | |

Both preparation defaults are declared FSCR policy.
They are string values for the CSV, not claims about server-side importer
defaults. Preserve explicit customer values, including an explicit blank; any
supplied value still needs the applicable validation before import.
Other optional columns follow ora_input_validation.md; do not add defaults
for them or change existing rows in an exported package.

No File Export attachment flag or repository account default is supplied by
the public guide. Preserve the applicable template's optional-field semantics;
leave non-applicable cells empty. No provider default applies to a delivery row.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.APPLY_PROVIDER_DEFAULTS | decision | 13 | apply_default | applied->CMKSP.CHECK_PROVIDER_DUPLICATE;not_applicable->CMKSP.CHECK_PROVIDER_DUPLICATE;blocked->RETURN_ISSUES | CMKSP.INPUT_CONTRACT | stop | After input and preparation-contract validation; apply UserDefined and DelStatusUpdateEnabled defaults only to provider business-input creation; preserve supplied values and unchanged exported rows |
| CMKSP.APPLY_DELIVERY_DEFAULTS | decision | 39 | apply_default | applied->CMKSP.DELIVERY_CREATE_NEEDED;not_applicable->CMKSP.DELIVERY_CREATE_NEEDED;blocked->RETURN_ISSUES | CMKSP.DELIVERY_PREPARATION_CHECK | stop | After supported delivery intake and representation checks, return not_applicable: no delivery-specific default is declared by this public-guidance profile. Preserve supplied applicable values and optional blanks; no ZIP mutation or approval occurs here |
