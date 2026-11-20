# Transmission reference lookups



Task: IBY_MANAGE_TRANSMISSION_CONFIGURATIONS — Manage Transmission Configurations.

The user-authorized exact-task target export is the authority for offline matching. Record its environment, release and language in restricted run evidence. Refresh it before execution. These are local reads of that captured export, not invented REST endpoints. The 26D published REST catalog supplies no transmission-configuration CRUD contract.

## Local Lookups

| Resolver | Runs When | Source Values | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|
| resolve_transmission_protocol | Every configuration request | Fresh target ORA_IBY_TRANSMISSION_CONFIG_PROTOCOL.csv; requested protocol name or code | Exact name/code in the export language; supplied pair must identify the same row | TransmitProtocolCode and TransmitProtocolName and preserved TransmitCodeLanguage | Block; do not create protocol definitions or use fuzzy match |
| find_transmission_configuration | Create or update | Fresh target IBY_TRANSMISSION_CONFIGURATION.csv; exact requested name | Exact TransmitConfigurationName; zero for create, exactly one for update | Current configuration row, protocol context and existence outcome | Reject duplicate create, missing update or ambiguous name |
| resolve_transmission_parameter | Parameter supplied | Fresh target ORA_IBY_TRANSMISSION_CONFIG_PARA.csv; resolved protocol and requested parameter code | Exact TransmitProtocolCode plus TransmitParameterCode | TransmitParameterType, DynamicFlag and label metadata | Block; do not borrow same-named parameter from another protocol |
| resolve_transmission_language | Translation supplied | Fresh target translation CSVs; requested Language and SourceLang | Exact language code in target export context; no locale-name conversion | Validated target Language and SourceLang | Block new/unproven language until target evidence is supplied |
| find_transmission_tunnel | Tunnel requested | Fresh target configuration CSV; requested tunnel name | Exactly one target configuration by name | Referenced name and its current TunnelTransmitConfigurationName | Block zero/multiple matches; FSM resolves internal ID |
| resolve_parameter_value_contract | Parameter value create/change or touched crypto configuration | Target parameter metadata, reviewed seed and conditional credential/OAuth evidence | Exact protocol+parameter; credential DML checks type/name in store and may register a missing key from UCM; existing hits skip registration validation | Typed value column, required/protected classification and manual completion steps; existing-key UI evidence contains no sensitive values; OAuth assignment returns blocked result MTC-OAUTH-01; no ID is generated | Block unproven affected mapping; never derive alias from an exported path; defer intentional key registration to UI |

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| Export identity or language mismatch | Stop and acquire the exact task export in the intended environment and language |
| Reference value obtained from another environment | Re-resolve in target; configuration/value IDs are not portable |
| Parameter metadata absent from CSV | MandatoryFlag, SecuredFlag and DynCodePackage are explicitly excluded by FSM export; do not infer them from blanks or populated values |
| Seed and target differ | Record exact protocol/parameter difference; require target-specific metadata before affected value creation/change |
| Credential material in export | Keep raw file restricted; omit raw values from visible diagnostics, previews and Git |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MTC.LOOKUP | step | 10 | reference_lookup | success->MTC.INPUT;failure->MTC.ERROR | none | stop | Always |

## Evidence

- FSM export/import mapping (reviewed implementation evidence) — excluded fields, name resolution and alternate keys.
- Configuration key (reviewed implementation evidence).
- Value export (reviewed implementation evidence).
- [REST catalog26D](https://docs.oracle.com/en/cloud/saas/financials/26d/farfa/rest-endpoints.html) — negative published-resource evidence only.
- Seed parameter metadata (reviewed implementation evidence) — current branch seed; target customization must be checked.

- Configuration DML and credential registration (reviewed implementation evidence) — existing-key check, UCM fetch, password/file checks and conditional deletion.
- Credential utility (reviewed implementation evidence) — type/name existence, materialization and legacy-path side effects.

## OAuth import boundary

The reviewed FSM helper remaps primary keys and declared linked child attributes. Payments links configuration IDs to child TransmitConfigurationId; it does not bind OAuth TransmitNumberValue. Do not assume a related configuration import rewrites the OAuth parameter. New or changed OAuth references require independently verified target name, OAUTH_2_0 protocol and numeric ID. The acquisition path remains unqualified. Evidence: restricted ADE helper review; fphdev label261001.1200.S; AdfFunctionalSetupPublicModel.jar SHA256 ea858bf0877dce1d1ba3b3cb82973db4e989286a8639518c25f3edc22fd2355f.

## Deferred product enhancement MTC-OAUTH-01

The developer accepted deferral of new or changed OAUTH_TRANSMIT_CONFIG assignment. Reject those assignments before preview/import. Preserve an unchanged reference only from the same target baseline. This does not prohibit creating an OAUTH_2_0 configuration or using ordinary numeric protocol parameters. The proposed product change is to export the OAuth reference name and resolve that name during FSM import. Do not use the deprecated unsupported SOAP find operation or developer SQL as a runtime shortcut.

## Sensitive setup boundary

Apply [the sensitive-field policy](ora_sensitive_fields.md) before these checks. Credential import and intentional key registration are manual; only the explicit SFTP create username placeholder is permitted.
