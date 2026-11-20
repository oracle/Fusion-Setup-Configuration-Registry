# Transmission input validation



Task: IBY_MANAGE_TRANSMISSION_CONFIGURATIONS — Manage Transmission Configurations.

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Configuration identity | Exact TransmitConfigurationName and explicit create/update intent | Stop before preview | Obtain intended name/action; never use row position | Always | find_transmission_configuration |
| Protocol selection | Target TransmitProtocolName or code with consistent resolved pair | Stop | Select existing target protocol | Create or parameter update | resolve_transmission_protocol |
| Parameter value | TransmitParameterCode and the matching typed value | Report field name without its value | Obtain bank/user value and resolve parameter metadata | Parameter create/change | resolve_parameter_value_contract |
| Effective dates | StartDate and EndDate with consistent EndDateDsp | Stop or apply only confirmed documented default | Resolve explicit validity intent | Create or date update | |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Name and code shape | Configuration/protocol/parameter names at most100 characters; protocol and parameter codes at most30; required names/codes nonempty | Supplied field | |
| Type selection | VARCHAR2 uses TransmitVarchar2Value up to255 characters; NUMBER uses integral Java Long-compatible value; DATE uses valid date; reject conflicting populated typed columns | Parameter value | resolve_parameter_value_contract |
| Required parameter | Non-dynamic MandatoryFlag=Y requires a value in its selected typed column; MandatoryFlag=D is not Y | Create/change configuration parameters | resolve_parameter_value_contract |
| Translation shape | Language and SourceLang required up to4; translated name required up to100; no duplicate parent/language key | Included translation | resolve_transmission_language |
| Package field contract | Use seven exact template members and ordered97 CSV columns; retain74 intrinsic fields plus23 inherited key columns; reject unknown fields and inconsistent inherited keys | Package | |
| Parent/key integrity | Configuration name is business key; value key is configuration name plus parameter code; translation adds Language; parameter key is protocol plus parameter code | Package | |
| Audit and helper ownership | Reject requested edits to who columns and transient display/create helpers; preserve baseline serialization. MandatoryFlagCreate cannot override seeded requiredness | Update | |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MTC.INPUT | step | 20 | validate_input | success->MTC.DEPENDENCY;failure->MTC.ERROR | MTC.LOOKUP | stop | Always |

## Evidence

- Entity field types (reviewed implementation evidence).
- UI requiredness (reviewed implementation evidence) — preflight behavior; reviewed FSM AM does not invoke this UI method.
- FSM helpers and audit flags (reviewed implementation evidence).
- Same-task CSV Template Report and ASM_SETUP_CSV_METADATA.xml establish members, headers and parent key columns. Runtime must use its own fresh authorized template/export.




### Deferred OAuth assignment

For parameter OAUTH_TRANSMIT_CONFIG, reject a new nonblank reference or any change to an existing reference under MTC-OAUTH-01. Preserve unchanged same-target data. OAuth configuration creation and ordinary numeric parameters remain in scope. No automatic credential registration is implied by this deferral.

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: IBY_TRANSMISSION_CONFIGURATION::TransmitProtocolCode, IBY_TRANSMISSION_CONFIGURATION::TransmitProtocolName, IBY_TRANSMISSION_CONFIGURATION::TransmitConfigurationName, IBY_TRANSMISSION_CONFIGURATION::StartDate, IBY_TRANSMISSION_CONFIGURATION::EndDate, IBY_TRANSMISSION_CONFIGURATION::InactiveDate, IBY_TRANSMISSION_CONFIGURATION::TunnelTransmitConfigurationName, IBY_TRANSMISSION_CONFIGURATION::EndDateDsp, IBY_TRANSMISSION_CONFIGURATION_TRANSLATION::Language, IBY_TRANSMISSION_CONFIGURATION_TRANSLATION::SourceLang, IBY_TRANSMISSION_CONFIGURATION_TRANSLATION::TransmitConfigurationName, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::TransmitParameterCode, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::TransmitVarchar2Value, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::TransmitNumberValue, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::TransmitDateValue, IBY_TRANSMISSION_CONFIGURATION::ORA_IBY_TRANSMISSION_CONFIG_PROTOCOL.TransmitProtocolCode, IBY_TRANSMISSION_CONFIGURATION::ORA_IBY_TRANSMISSION_CONFIG_PROTOCOL.TransmitProtocolName, IBY_TRANSMISSION_CONFIGURATION::ORA_IBY_TRANSMISSION_CONFIG_PROTOCOL.TransmitCodeLanguage, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::ORA_IBY_TRANSMISSION_CONFIG_PROTOCOL.TransmitProtocolCode, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::ORA_IBY_TRANSMISSION_CONFIG_PROTOCOL.TransmitProtocolName, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::ORA_IBY_TRANSMISSION_CONFIG_PROTOCOL.TransmitCodeLanguage, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::IBY_TRANSMISSION_CONFIGURATION.TransmitConfigurationName, IBY_TRANSMISSION_CONFIGURATION_TRANSLATION::ORA_IBY_TRANSMISSION_CONFIG_PROTOCOL.TransmitProtocolCode, IBY_TRANSMISSION_CONFIGURATION_TRANSLATION::ORA_IBY_TRANSMISSION_CONFIG_PROTOCOL.TransmitProtocolName, IBY_TRANSMISSION_CONFIGURATION_TRANSLATION::ORA_IBY_TRANSMISSION_CONFIG_PROTOCOL.TransmitCodeLanguage, IBY_TRANSMISSION_CONFIGURATION_TRANSLATION::IBY_TRANSMISSION_CONFIGURATION.TransmitConfigurationName -->
<!-- fscr-update-fields: IBY_TRANSMISSION_CONFIGURATION::StartDate, IBY_TRANSMISSION_CONFIGURATION::EndDate, IBY_TRANSMISSION_CONFIGURATION::InactiveDate, IBY_TRANSMISSION_CONFIGURATION::TunnelTransmitConfigurationName, IBY_TRANSMISSION_CONFIGURATION::EndDateDsp, IBY_TRANSMISSION_CONFIGURATION_TRANSLATION::SourceLang, IBY_TRANSMISSION_CONFIGURATION_TRANSLATION::TransmitConfigurationName, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::TransmitVarchar2Value, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::TransmitNumberValue, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::TransmitDateValue -->

## Sensitive setup boundary

Apply [the sensitive-field policy](ora_sensitive_fields.md): omit sensitive inputs, expose only field-name notices, and validate the final ZIP against the task-owned policy. Unknown/custom parameters require review.
