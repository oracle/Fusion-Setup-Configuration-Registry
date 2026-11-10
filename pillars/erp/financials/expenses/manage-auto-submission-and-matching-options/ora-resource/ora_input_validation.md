# Input validation

These rules are reusable across target environments. Planner readiness means the execution rules are defined; all applicable runtime checks must still pass. The portable execution contract in ../references/execution-contract.md defines environment selection, input mapping, FSM compatibility checks and the in-memory Data Loader handoff. A missing product qualification is an explicit runtime blocker, never implicit approval.

<!-- fscr-supported-operations: create, update -->
<!-- fscr-evidence-unresolved-operations:  -->

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Task and requested operation | Exact task code; supplied Business Unit, BU Name or BuName establishes BU-scoped modify intent; otherwise explicit operation and scope | Ask only for unresolved intent or scope; never infer global scope from blank BU | Retain the user's requested modification; clarify conflicting explicit inputs; Use scripts/input_contract.py to validate normalized business intent, then qualify_fsm_transport before mapping CSV rows; require explicit scope and a verified template | Every request |  |
| Organization setting identity | EXM_ORG_SETTING.SettingCode and explicit scope; BuName for BU-specific intent | Stop before candidate construction | Use the reviewed control mapping and preserve its scope; additional controls require source evidence; never use the entire shared EO list | Organization-setting intent | resolve_setting_code |
| Setup option identity | EXM_SETUP_OPTION.OptionCode and explicit scope; BuName for BU-specific intent | Stop before candidate construction | Automatic-submission enable maps to ENABLE_AUTO_SUB_DA_EXP; validate its ValueCode separately | Setup-option intent | resolve_option_code |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Input fields versus package fields | Apply the source-backed field roles below. The table is not package approval; candidate serialization and alias gates must also pass. | Every request |  |
| Target environment | Use the latest explicit user-selected environment over stale workbook defaults; do not reuse another environment's resolved IDs or authentication context. | Workbook and conversational context differ |  |
| Audit fields | Do not offer CreatedBy, CreationDate, LastUpdatedBy, LastUpdateDate or LastUpdateLogin as business edits in EXM_ORG_SETTING or EXM_SETUP_OPTION. Preserve template headers; serialize system-managed audit fields as empty CSV fields only after qualify_fsm_transport passes the applicable serialization profile. SRC-ORG-VO and SRC-OPTION-VO. | Audit input or serialization |  |
| Auto-submission value | Validate the source-backed System enum: Yes/Y maps to Y and No/N maps to N. Blank preserves intent as unspecified; reject other values. | EXM_SETUP_OPTION.ValueCode | resolve_auto_submission_value |
| Setting encoding | Use the confirmed per-control encodings in the lookup resource: HH:mm, integer amount tolerance 0–50 and nonnegative whole days. Weekday and direction System enums are source-confirmed in the lookup resource. Apply resolve_time_zone_evidence when a time zone changes; merchant list editing returns FEATURE_CONTRACT_REQUIRED; qualify_fsm_transport is mandatory before composition. | Affected matching/schedule setting | resolve_setting_value |
| CSV shape | Use exact same-task template member names, ordered headers and metadata types. Reject wrong field counts and preserve explicit trailing blank fields. Do not replay broad exported rows. | Future governed package preparation |  |
| Decoded values | Do not assume SettingValueDecoded is independently writable or a universal substitute for SettingValue. Import remapping exists for specific account/template codes outside this task contract. | Decoded projection supplied |  |

## Package field inventory

The table distinguishes source-proven field roles from candidate CSV serialization. Apply the shipped organization-setting transport profile to its exact schema; framework qualification of populated EXM_SETUP_OPTION aliases remains required when setup-option writes remain after verified baseline comparison. Create means inserting an expense setting for a verified scope, never creating a business unit. Update retains the same setting/option code and scope; changing a key is not a rename operation.

| Entity | CSV column | Type | Position | Create | Update | Evidence |
|---|---|---|---|---|---|---|
| EXM_ORG_SETTING | CreationDate | dateTime | 3 | System-managed; not business input | System-managed; not business input | SRC-FSM-TEMPLATE; SRC-ORG-VO; SRC-ORG-EO |
| EXM_ORG_SETTING | CreatedBy | string | 4 | System-managed; not business input | System-managed; not business input | SRC-FSM-TEMPLATE; SRC-ORG-VO; SRC-ORG-EO |
| EXM_ORG_SETTING | LastUpdateDate | dateTime | 5 | System-managed; not business input | System-managed; not business input | SRC-FSM-TEMPLATE; SRC-ORG-VO; SRC-ORG-EO |
| EXM_ORG_SETTING | LastUpdatedBy | string | 6 | System-managed; not business input | System-managed; not business input | SRC-FSM-TEMPLATE; SRC-ORG-VO; SRC-ORG-EO |
| EXM_ORG_SETTING | LastUpdateLogin | string | 7 | System-managed; not business input | System-managed; not business input | SRC-FSM-TEMPLATE; SRC-ORG-VO; SRC-ORG-EO |
| EXM_ORG_SETTING | SettingCode | string | 2 | Required identity; reviewed code only | Required unchanged identity; no rename | SRC-FSM-TEMPLATE; SRC-ORG-VO; SRC-ORG-EO |
| EXM_ORG_SETTING | SettingValue | string | 8 | Explicit validated value | Explicit validated replacement for selected row | SRC-FSM-TEMPLATE; SRC-ORG-VO; SRC-ORG-EO; SRC-ORG-AMIMPL; SRC-ORG-EOIMPL; SRC-UI-DA-PAGE; SRC-UI-DA-PAGEDEF; SRC-UI-DA-BEAN |
| EXM_ORG_SETTING | BuName | string | 1 | Scope identity; verified BU or explicit global | Unchanged scope identity; no BU move | SRC-FSM-TEMPLATE; SRC-ORG-VO; SRC-ORG-EO; SRC-BU-PEO; SRC-FSM-MIGRATOR-HELPER |
| EXM_ORG_SETTING | SettingValueDecoded | string | 9 | Derived projection; not independent input | Derived projection; not independent input | SRC-FSM-TEMPLATE; SRC-ORG-VO; SRC-ORG-EO; SRC-ORG-AMIMPL; SRC-ORG-EOIMPL |
| EXM_SETUP_OPTION | OptionCode | string | 2 | Required identity; reviewed code only | Required unchanged identity; no rename | SRC-FSM-TEMPLATE; SRC-OPTION-VO; SRC-OPTION-EO |
| EXM_SETUP_OPTION | ValueCode | string | 3 | Explicit validated value | Explicit validated replacement for selected row | SRC-FSM-TEMPLATE; SRC-OPTION-VO; SRC-OPTION-EO; SRC-UI-AUTOSUBMIT-VO; SRC-OPTION-EOIMPL; SRC-ALM-REPORT-FETCH |
| EXM_SETUP_OPTION | CreationDate | dateTime | 4 | System-managed; not business input | System-managed; not business input | SRC-FSM-TEMPLATE; SRC-OPTION-VO; SRC-OPTION-EO |
| EXM_SETUP_OPTION | CreatedBy | string | 5 | System-managed; not business input | System-managed; not business input | SRC-FSM-TEMPLATE; SRC-OPTION-VO; SRC-OPTION-EO |
| EXM_SETUP_OPTION | LastUpdateLogin | string | 6 | System-managed; not business input | System-managed; not business input | SRC-FSM-TEMPLATE; SRC-OPTION-VO; SRC-OPTION-EO |
| EXM_SETUP_OPTION | LastUpdateDate | dateTime | 7 | System-managed; not business input | System-managed; not business input | SRC-FSM-TEMPLATE; SRC-OPTION-VO; SRC-OPTION-EO |
| EXM_SETUP_OPTION | LastUpdatedBy | string | 8 | System-managed; not business input | System-managed; not business input | SRC-FSM-TEMPLATE; SRC-OPTION-VO; SRC-OPTION-EO |
| EXM_SETUP_OPTION | BuName | string | 1 | Scope identity; verified BU or explicit global | Unchanged scope identity; no BU move | SRC-FSM-TEMPLATE; SRC-OPTION-VO; SRC-OPTION-EO; SRC-BU-PEO; SRC-FSM-MIGRATOR-HELPER |
| EXM_SETUP_OPTION | OtherOrgId | long | 9 | Import scope marker; not user numeric BU ID | Import scope marker; not user numeric BU ID | SRC-FSM-TEMPLATE; SRC-OPTION-VO; SRC-OPTION-EO |
| EXM_CASH_ADV_SETUP_AND_POLICY | OptionCode | string | 2 | Shared package alias; no independent business edit | Shared package alias; subject to qualify_fsm_transport | ASM_SETUP_CSV_METADATA.xml  /  EXM_CASH_ADV_SETUP_AND_POLICY.OptionCode; SRC-BO-SEEDS-COMPLETE |
| EXM_CASH_ADV_SETUP_AND_POLICY | ValueCode | string | 3 | Shared package alias; no independent business edit | Shared package alias; subject to qualify_fsm_transport | ASM_SETUP_CSV_METADATA.xml  /  EXM_CASH_ADV_SETUP_AND_POLICY.ValueCode; SRC-BO-SEEDS-COMPLETE |
| EXM_CASH_ADV_SETUP_AND_POLICY | CreationDate | dateTime | 4 | Shared package alias; no independent business edit | Shared package alias; subject to qualify_fsm_transport | ASM_SETUP_CSV_METADATA.xml  /  EXM_CASH_ADV_SETUP_AND_POLICY.CreationDate; SRC-BO-SEEDS-COMPLETE |
| EXM_CASH_ADV_SETUP_AND_POLICY | CreatedBy | string | 5 | Shared package alias; no independent business edit | Shared package alias; subject to qualify_fsm_transport | ASM_SETUP_CSV_METADATA.xml  /  EXM_CASH_ADV_SETUP_AND_POLICY.CreatedBy; SRC-BO-SEEDS-COMPLETE |
| EXM_CASH_ADV_SETUP_AND_POLICY | LastUpdateLogin | string | 6 | Shared package alias; no independent business edit | Shared package alias; subject to qualify_fsm_transport | ASM_SETUP_CSV_METADATA.xml  /  EXM_CASH_ADV_SETUP_AND_POLICY.LastUpdateLogin; SRC-BO-SEEDS-COMPLETE |
| EXM_CASH_ADV_SETUP_AND_POLICY | LastUpdateDate | dateTime | 7 | Shared package alias; no independent business edit | Shared package alias; subject to qualify_fsm_transport | ASM_SETUP_CSV_METADATA.xml  /  EXM_CASH_ADV_SETUP_AND_POLICY.LastUpdateDate; SRC-BO-SEEDS-COMPLETE |
| EXM_CASH_ADV_SETUP_AND_POLICY | LastUpdatedBy | string | 8 | Shared package alias; no independent business edit | Shared package alias; subject to qualify_fsm_transport | ASM_SETUP_CSV_METADATA.xml  /  EXM_CASH_ADV_SETUP_AND_POLICY.LastUpdatedBy; SRC-BO-SEEDS-COMPLETE |
| EXM_CASH_ADV_SETUP_AND_POLICY | BuName | string | 1 | Shared package alias; no independent business edit | Shared package alias; subject to qualify_fsm_transport | ASM_SETUP_CSV_METADATA.xml  /  EXM_CASH_ADV_SETUP_AND_POLICY.BuName; SRC-BO-SEEDS-COMPLETE |
| EXM_CASH_ADV_SETUP_AND_POLICY | OtherOrgId | long | 9 | Shared package alias; no independent business edit | Shared package alias; subject to qualify_fsm_transport | ASM_SETUP_CSV_METADATA.xml  /  EXM_CASH_ADV_SETUP_AND_POLICY.OtherOrgId; SRC-BO-SEEDS-COMPLETE |

The positions above come from the captured CSV headers, not XML attribute-list order. Fresh target CSV headers own runtime ordering; compare metadata attributes by name and preserve the original CSV order.

## Import field semantics

- The organization-setting and setup-option service hooks resolve scope, run `updatePrimaryKeysInXML` with `AltKey`, then call `MigratorHelper.readXML`. Existing alternate-key matches retain their primary key; missing matches obtain an eligible generated key. This supports source-level insert/update semantics, not an unconditional create-only route. The import must not rename codes, move scope, or replay unrelated rows.
- All five exported audit attributes have `IsUpdateable="false"` in both service VOs. The FSM framework FAQ states that `readXML` ignores non-updateable attributes. The shipped organization-setting profile combines this owner contract with the CSV parser empty-date handling and EO history columns to qualify empty audit fields. This is source-backed qualification, not a claim that the user-provided ZIP tested empty audits. Do not copy exported users or timestamps into candidates.
- For the reviewed codes, `SettingValueDecoded` is the nonpersistent projection of `SettingValue`. The import remaps it only for the expense-template and three account codes outside this task's reviewed mapping. Accept no independent decoded-value override.
- Both hooks obtain enterprise context from `ADFContext.getCurrent().getTenantId()`, falling back to session `FND_ENTERPRISE_ID`. This is server-owned context, not a workbook field or a value to synthesize from the public BU LOV. Runtime still requires the selected environment, authenticated privileges, and a unique verified BU.
- An omitted workbook control produces no candidate row. This preserves unrequested controls without depending on blank-cell semantics. An included row cannot use a blank business value as an implicit preserve or clear operation.

Evidence: SRC-ORG-AMIMPL (importData), SRC-OPTION-AMIMPL (importData), SRC-FSM-MIGRATOR-HELPER (updatePrimaryKeysInXML/readXML), SRC-ORG-VO, SRC-OPTION-VO, and SRC-FSM-FRAMEWORK-FAQ (source lines 305–347). CSV transport and global blank-scope qualification use ../references/fsm-transport-profile.md for the exact reviewed organization-setting schema; unsupported operations remain blocked.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AUTO_VALIDATE | step | 10 | validate_input | passed->AUTO_DEPENDENCIES | none | stop | Task validation before any Data Loader handoff |

## Evidence

Maintainer provenance IDs: `SRC-FSM-TEMPLATE`, `SRC-ORG-VO`, `SRC-OPTION-VO`, `SRC-ORG-EO`, `SRC-OPTION-EO`, `SRC-UI-DA-PAGE`, `SRC-UI-DA-BEAN`.

The reusable contract is the task-local field, scope and package rules. Maintainer source locations are excluded from distribution and are not runtime inputs. Historical review does not qualify a new target or authorize an import. Retain every current-target and approval check.

## Organization-setting profile

Use [the shipped transport profile](../references/fsm-transport-profile.md) for
organization-only writes and its documented source and verified-import boundaries. It
requires no customer-provided import ZIP. Other operations keep their explicit
qualification checks.

Supported create/update operations are bounded to organization-setting rows
under the shipped transport profile. A required setup-option write remains
blocked by FSM_ALIAS_COLLISION; these markers do not waive that check.

## Customer intake and target binding

Apply ../references/customer-input.md. Map captured readable input to the
canonical model; normalize unambiguous human values with normalize_friendly.
Use combine_requests for one target with multiple BUs and reject conflicting
global requests. Require validate_environment_binding across selected auth,
Run Book, loader and both export provenances before composing. A target change
requires a fresh candidate, core preflight and preview. Unsupported input is a precise intake
blocker; it is not silently omitted or treated as an execution instruction.
