# Manage Channel User Statuses REST Defaulting Rules

## Standard Defaults

| Task Code | Task Name | Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|---|---|
| ORA_CJM_MANAGE_CHANNEL_USER_STATUSES | Manage Channel User Statuses | BuySideFlag | false | BuySideFlag is omitted from a create request | No | |
| ORA_CJM_MANAGE_CHANNEL_USER_STATUSES | Manage Channel User Statuses | EnabledFlag | true | EnabledFlag is omitted from a create request | No | |
| ORA_CJM_MANAGE_CHANNEL_USER_STATUSES | Manage Channel User Statuses | SeededFlag | false | SeededFlag is omitted from a create request | No | |
| ORA_CJM_MANAGE_CHANNEL_USER_STATUSES | Manage Channel User Statuses | SellSideDefaultFlag | false | SellSideDefaultFlag is omitted from a create request | No | |
| ORA_CJM_MANAGE_CHANNEL_USER_STATUSES | Manage Channel User Statuses | SellSideFlag | false | SellSideFlag is omitted from a create request | No | |

## Manage Channel Lookups

| Task Code | Task Name | Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|---|---|
| ORA_CJM_MANAGE_CHANNEL_LOOKUPS | Manage Channel Lookups | EnabledFlag | Y | EnabledFlag is omitted for a lookup-code create candidate | No | |

For this task, set `EnabledFlag=Y` only for a new lookup-code create candidate and explicitly report the applied default in the review and import summary. For an existing lookup-code update candidate, an omitted EnabledFlag preserves the current exported value. It must not infer, default, clear, or overwrite any other omitted lookup-code field.

DefaultFlag has no documented default and must remain unset when the source omits it.

## Manage Channel Profile Options

| Task Code | Task Name | Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|---|---|
| ORA_CJM_MANAGE_CHANNEL_PROFILE_OPTIONS | Manage Channel Profile Options | ProfileOptionValue | Trimmed invariant upper-case of the supplied credit-method meaning | ProfileOptionCode is `ORA_CJM_AR_CR_MTHD_FOR_INSTL` and a non-empty value is supplied | Yes, only as the documented display-to-return mapping | normalize_installment_credit_method |

This is a task-scoped transformation, not a universal profile-option default. It applies only to the documented `CREDIT_METHOD_FOR_INSTALLMENTS` lookup contract and must preserve internal spaces and non-letter characters while changing letter case only.

## Manage Channel Value Sets

| Task Code | Task Name | Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|---|---|
| ORA_CJM_MANAGE_CHANNEL_VALUE_SETS | Manage Channel Value Sets | Existing parent carrier | Apply supplied template-supported mutable changes to the carrier made available by CJMVS.VALUE_SET_PARENT; retain identity, immutable fields, and all omitted values. Stage only actual changes and treat an unchanged request as a no-op. | The parent-carrier dependency is satisfied for an existing value set | No | |
| ORA_CJM_MANAGE_CHANNEL_VALUE_SETS | Manage Channel Value Sets | ValueSetIdentifier | Use the technical identifier returned by derive_value_set_identifier_from_code | A new value-set parent is prepared and the source has no template-level ValueSetIdentifier field | Yes, for this derived technical field only | derive_value_set_identifier_from_code |

An existing parent carrier is relationship context, not a user value. Do not infer missing technical attributes, replace parent values from REST, or overwrite a supplied template-supported parent value. Retain identity and immutable parent fields, and stage an update only when a supplied mutable field differs from the exported carrier. `ValueSetIdentifier` is the exception for a new parent: the Fusion UI does not expose it as user-entered data, so derive it only from the exact supplied `ValueSetCode`, disclose the derived value in the preview, and never use this rule to replace an identifier retained from an existing exported parent carrier.

## Manage Channel Descriptive Flexfields

| Task Code | Task Name | Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|---|---|
| ORA_CJM_MANAGE_CHANNEL_DESCRIPTIVE_FLEXFIELDS | Manage Channel Descriptive Flexfields | DefaultType; DefaultValue; DefaultValueNumber; DefaultValueDate; DefaultValueTimestamp | unset | The source omits a DFF default | No | |
| ORA_CJM_MANAGE_CHANNEL_DESCRIPTIVE_FLEXFIELDS | Manage Channel Descriptive Flexfields | Context parent attributes | no inferred default | A context-sensitive segment requires a context parent carrier | No | |

Do not infer a constant default or validate an omitted default value. For a free-text value set, validate supplied text against its returned datatype and maximum length; do not resolve a child LOV value. For a list-validated value set, use the returned value-set validation contract before accepting a supplied default. Context-parent attributes are not defaults: derive only the template-required carrier fields from the supplied DFF and context identities. Require source input only for a true identity value that is absent; use a current export solely for optional reconciliation.

## Task Nodes

| Task Code | Task Name | Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|---|---|
| ORA_CJM_MANAGE_CHANNEL_USER_STATUSES | Manage Channel User Statuses | CJMUS.APPLY_DOCUMENTED_DEFAULTS | step | 5 | apply_default | applied->CJMUS.CONFIRM_CREATE_GATE;unchanged->CJMUS.CONFIRM_CREATE_GATE | CJMUS.DERIVE_SYSTEM_STATUS_CODE | stop | A validated create candidate omits one or more boolean attributes with Oracle-documented defaults |
| ORA_CJM_MANAGE_CHANNEL_LOOKUPS | Manage Channel Lookups | CJMLOOK.APPLY_ENABLED_DEFAULT | step | 2 | apply_default | applied->CJMLOOK.CONFIRM_ARCHIVE;unchanged->CJMLOOK.CONFIRM_ARCHIVE | CJMLOOK.VALIDATE_FSM_PACKAGE | stop | A validated new lookup-code candidate omits EnabledFlag; stage EnabledFlag=Y and disclose the default before the package approval gate |
| ORA_CJM_MANAGE_CHANNEL_PROFILE_OPTIONS | Manage Channel Profile Options | CJMPO.NORMALIZE_INSTALLMENT_CREDIT_METHOD | step | 5 | apply_default | applied->CJMPO.RETURN_INSTALLMENT_CREDIT_METHOD_RESOLVED;invalid->RETURN_ISSUES | CJMPO.VALIDATE_SUPPORTED_PROFILE_INPUT | stop | The supported-profile validation selected ORA_CJM_AR_CR_MTHD_FOR_INSTL; normalize the requested profile value |
| ORA_CJM_MANAGE_CHANNEL_VALUE_SETS | Manage Channel Value Sets | CJMVS.PRESERVE_PARENT_CARRIER | step | 5 | apply_default | applied->CJMVS.CONFIRM_ARCHIVE;unchanged->CJMVS.CONFIRM_ARCHIVE;blocked->RETURN_ISSUES | CJMVS.RESOLVE_MODULE | stop | Preserve an existing parent carrier or retain only supplied and previously documented technical parent values before archive review |
