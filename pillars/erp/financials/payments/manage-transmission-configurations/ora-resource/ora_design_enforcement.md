# Transmission design enforcement



Task: IBY_MANAGE_TRANSMISSION_CONFIGURATIONS — Manage Transmission Configurations.

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Identity and preservation | Respect exact target business keys and preserve unrelated setup |
| 2 | Dates and tunneling | Enforce validity and non-chained tunnel rules |
| 3 | Protected references | Prove target credential/OAuth mappings and prevent sensitive-data disclosure |
| 4 | Execution handoff | Return validated design to Run Book/Data Loader; no direct transmission |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Configuration dates supplied | Error | | EndDate precedes StartDate or EndDateDsp conflicts | Correct dates before preview | Only with explicit validity intent |
| Tunnel supplied | Error | find_transmission_tunnel | Self-reference or target tunnel itself references another tunnel | Select an existing non-chained tunnel | No silent replacement |
| Existing configuration updated | Error | find_transmission_configuration | Rename used as update identity, ambiguous target or unintended protocol change | Preserve identity; handle rename/protocol conversion only after source-backed migration design | No |
| Protocol or parameter definition edit requested | Error | resolve_transmission_protocol | Configuration task used to alter seeded implementation definitions or languages | Route definition work to its own supported workflow | No |
| Target differs from seed | Error | resolve_parameter_value_contract | Required/protected status of affected target parameter is unknown | Obtain current target metadata; HTTP_MPART.NO_ACK is an observed example | No guessed flags |
| Credential/OAuth value included | Error | resolve_parameter_value_contract | Reference is an unproven source-environment ID, exported resolved path presented as a portable alias, or unresolved credential dependency with undeclared registration effects | Use non-secret UI evidence for existing credentials; registration remains manual; do not derive alias from a path; resolve OAuth mapping separately | No guessed mapping |
| Crypto configuration touched | Error | resolve_parameter_value_contract | Only changed fields were reviewed while existing credential references can reach importKey | Assess every existing credential reference on the touched configuration; block if a missing key could trigger UCM registration; complete that prerequisite manually in UI | No implicit credential provisioning |
| Export or package is processed | Error | | Parameter values exposed in logs, visible preview, fixtures or Git | Redact all parameter values regardless of SecuredFlag; restrict actual package artifacts | Redaction only |
| Refreshed nonproduction environment | Error | | Bank endpoint or wallet context unverified | Confirm intended nonproduction connectivity before any later transmission test | No automatic endpoint substitution |
| Package ready | Error | | Preview treated as execution approval or test sends files to a bank | Use Run Book/Data Loader approval and later persisted-state verification | No |

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| find_transmission_tunnel | Tunnel supplied | Exact target reference and its tunnel relationship | ora_reference_lookups.md |
| find_transmission_configuration | Existing configuration updated | Exact target row | ora_reference_lookups.md |
| resolve_transmission_protocol | Always | Existing protocol identity | ora_reference_lookups.md |
| resolve_parameter_value_contract | Parameter values supplied | Requiredness, type, protection and conditional references | ora_reference_lookups.md |
## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MTC.DESIGN | step | 50 | design_enforcement | success->MTC.GATE;failure->MTC.ERROR | MTC.DEFAULT | stop | Always |

## Evidence

- Date validator and alternate key (reviewed implementation evidence).
- Actual values and secured DML (reviewed implementation evidence).
- [Tunneling and refresh guidance](https://docs.oracle.com/en/cloud/saas/financials/26c/fairp/how-you-set-up-transmission-configurations.html).
- Current core.runbook and core.data-loader own payload assembly, preview, approval, mutation, and verification.

- Configuration DML and credential registration (reviewed implementation evidence) — existing-key check, UCM fetch, password/file checks and conditional deletion.
- Credential utility (reviewed implementation evidence) — type/name existence, materialization and legacy-path side effects.




### Deferred OAuth assignment

For parameter OAUTH_TRANSMIT_CONFIG, reject a new nonblank reference or any change to an existing reference under MTC-OAUTH-01. Preserve unchanged same-target data. OAuth configuration creation and ordinary numeric parameters remain in scope. No automatic credential registration is implied by this deferral.

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: IBY_TRANSMISSION_CONFIGURATION::TransmitProtocolCode, IBY_TRANSMISSION_CONFIGURATION::TransmitProtocolName, IBY_TRANSMISSION_CONFIGURATION::TransmitConfigurationName, IBY_TRANSMISSION_CONFIGURATION::StartDate, IBY_TRANSMISSION_CONFIGURATION::EndDate, IBY_TRANSMISSION_CONFIGURATION::InactiveDate, IBY_TRANSMISSION_CONFIGURATION::TunnelTransmitConfigurationName, IBY_TRANSMISSION_CONFIGURATION::EndDateDsp, IBY_TRANSMISSION_CONFIGURATION_TRANSLATION::Language, IBY_TRANSMISSION_CONFIGURATION_TRANSLATION::SourceLang, IBY_TRANSMISSION_CONFIGURATION_TRANSLATION::TransmitConfigurationName, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::TransmitParameterCode, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::TransmitVarchar2Value, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::TransmitNumberValue, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::TransmitDateValue, IBY_TRANSMISSION_CONFIGURATION::ORA_IBY_TRANSMISSION_CONFIG_PROTOCOL.TransmitProtocolCode, IBY_TRANSMISSION_CONFIGURATION::ORA_IBY_TRANSMISSION_CONFIG_PROTOCOL.TransmitProtocolName, IBY_TRANSMISSION_CONFIGURATION::ORA_IBY_TRANSMISSION_CONFIG_PROTOCOL.TransmitCodeLanguage, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::ORA_IBY_TRANSMISSION_CONFIG_PROTOCOL.TransmitProtocolCode, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::ORA_IBY_TRANSMISSION_CONFIG_PROTOCOL.TransmitProtocolName, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::ORA_IBY_TRANSMISSION_CONFIG_PROTOCOL.TransmitCodeLanguage, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::IBY_TRANSMISSION_CONFIGURATION.TransmitConfigurationName, IBY_TRANSMISSION_CONFIGURATION_TRANSLATION::ORA_IBY_TRANSMISSION_CONFIG_PROTOCOL.TransmitProtocolCode, IBY_TRANSMISSION_CONFIGURATION_TRANSLATION::ORA_IBY_TRANSMISSION_CONFIG_PROTOCOL.TransmitProtocolName, IBY_TRANSMISSION_CONFIGURATION_TRANSLATION::ORA_IBY_TRANSMISSION_CONFIG_PROTOCOL.TransmitCodeLanguage, IBY_TRANSMISSION_CONFIGURATION_TRANSLATION::IBY_TRANSMISSION_CONFIGURATION.TransmitConfigurationName -->
<!-- fscr-update-fields: IBY_TRANSMISSION_CONFIGURATION::StartDate, IBY_TRANSMISSION_CONFIGURATION::EndDate, IBY_TRANSMISSION_CONFIGURATION::InactiveDate, IBY_TRANSMISSION_CONFIGURATION::TunnelTransmitConfigurationName, IBY_TRANSMISSION_CONFIGURATION::EndDateDsp, IBY_TRANSMISSION_CONFIGURATION_TRANSLATION::SourceLang, IBY_TRANSMISSION_CONFIGURATION_TRANSLATION::TransmitConfigurationName, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::TransmitVarchar2Value, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::TransmitNumberValue, ORA_IBY_PAYMENT_SYSTEM_TRAN_VAL::TransmitDateValue -->

## Sensitive setup boundary

Apply [the sensitive-field policy](ora_sensitive_fields.md) before these checks. Credential import and intentional key registration are manual; only the explicit SFTP create username placeholder is permitted.
