---
skill_id: "erp.financials.payments.manage-formats.template-generator.bank-iso"
name: "Payments Bank ISO Template Engine"
description: "Generates source-backed bank ISO credit-transfer templates for Manage Formats."
layer: "pillar"
pillar: "ERP"
type: "planning"
execution_mode: "assisted"
owner_team: "ERP financials pillar team"
version: "0.2.2"
inputs:
  - "format_identity_and_type"
  - "attachment_mechanism"
  - "source_payload_contract"
  - "provider_or_bank_specification"
  - "bank_pain_profile_and_version"
  - "supported_country_currency_rail_matrix"
  - "representative_masked_samples"
  - "project_context"
outputs:
  - "template_handoff_json"
  - "template_artifact"
  - "mapping_matrix"
  - "source_gap_report"
  - "offline_validation_report"
  - "country_rail_matrix"
  - "skill_run_record"
  - "token_usage_record"
depends_on: []
uses_core:
  - "core.project-mgmt.artifact-version-manager"
  - "core.project-mgmt.artifact-registry-manager"
  - "core.project-mgmt.project-state-manager"
persists_project_state: true
token_usage_tracking:
  enabled: true
  granularity: "per_skill_run"
  artifact_type: "token_usage_record"
  default_location: "project/{project_id}/artifacts/shared/token-usage/current/token-usage-log.md"
  estimation_method: "chars/4 estimate unless exact tokenizer or API accounting is available"
  required_fields:
    - "activity_start_time"
    - "skill_id"
    - "task"
    - "trigger"
    - "artifacts_written"
    - "files_read"
    - "estimated_input_tokens"
    - "estimated_output_tokens"
    - "estimated_total_tokens"
    - "estimation_method"
    - "notes"
state_updates:
  - "configuration_blueprints"
  - "validation_results"
  - "token_usage_records"
workspace_outputs:
  - artifact_type: "configuration_blueprint"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payments/manage-formats/template-generator/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "validation_result"
    default_location: "project/{project_id}/artifacts/pillars/erp/financials/payments/manage-formats/template-generator/current/"
    versioning_policy: "major-new-version-minor-confirm-update"
  - artifact_type: "skill_run"
    default_location: "project/{project_id}/state/runs/"
    versioning_policy: "append-only"
  - artifact_type: "token_usage_record"
    default_location: "project/{project_id}/artifacts/shared/token-usage/current/"
    versioning_policy: "append-only"
applicability:
  industries:
    - "All"
  countries:
    - "All"
  fusion_releases:
    - "Current Oracle Fusion Cloud release"
side_effects:
  - "Writes versioned template design and validation artifacts to the project workspace."
required_privileges: []
---

## Purpose

Payments Bank ISO Template Engine is an optional, focused Payments design capability invoked by Manage Formats. It has no independent FSM task identity. Its source contracts, mapping rules, fixtures, and validation steps below are retained from the installed engine.

## Candidate generation objective

Read [candidate-generation.md](../references/candidate-generation.md) before mapping. Default to implementation_candidate: deliver a useful template with explicit assumptions and tests; strict_conformance is a separate review objective. Unresolved mappings gate readiness or the affected execution path, not all artifact creation.

## FSCR governed handoff

Read `../references/template-handoff-contract.md` from a child engine, or `references/template-handoff-contract.md` from the router. Record the machine-readable handoff and register artifacts under the project workspace. The parent owns format creation/update, attachment, runtime verification, and task completion. This skill never publishes BI catalog content, uploads direct XML templates, imports FSM data, or approves a candidate. The selected engine must complete its original source, mapping, sample, and offline validation requirements before status `validated` is claimed.

Preflight profile, direction, provider/bank specification and source contract. Capture verified parent format identity/type and attachment mechanism when available; otherwise leave those metadata unresolved in a draft/discovery/failed handoff and continue useful offline generation. Resolve them before any installation or format action. Missing input is a scoped gap; fail only when no useful candidate can be constructed or processing itself fails. Unsupported routes produce a discovery pack. Failure behavior: a failed engine returns a failed handoff with diagnostics; it never silently switches to an invented template. Redact account, card, credential, and customer data from durable output. No Fusion request or polling occurs here. Preserve failed runs for later review; retry only the offline step after correcting inputs. An artifact overwrite follows project versioning rules.

## FSCR bank ISO route contract

Accept this route only for a bank-specific funds-disbursement ISO credit-transfer profile with an evidenced `OutboundPaymentInstruction` source contract, bank guide/version, target pain namespace, and supported country/currency/rail combinations. Before a validated handoff, complete the original workflow's bank mapping and country/rail matrices; inspect source XPath coverage and deliberately suppressed optional tags; compile XSLT; transform masked bank-specific scenario variants; and check the exact applicable ISO schema and bank conditions. Persist the matrix, source gaps (including an explicit empty list when none), and validation report alongside the template. A missing bank requirement, unsupported source value, or untested rail leaves generation in `draft` or `failed` with a next action. The generator never asserts that an XSLT is a selectable BI Publisher layout or an uploaded direct XML file.

## Original engine workflow

# Generate Bank ISO Templates

## Overview

Use this skill to turn a bank implementation guide into a source-backed Oracle Payments XSLT template. Keep the work anchored in the `OutboundPaymentInstruction` source XML generated from `IBY_XML_FD_INS_1_0_V`, the bundled Oracle seed ISO/SEPA/JPM/PNC XSL templates, the ISO schemas, and sanitized template-pattern references.

## Required References

Read these references before generating or materially changing a template:

- `references/source-xml-data-definition.md` for the source XML contract and view/package provenance.
- `references/source-xml-outline.xsd` when a concise data definition artifact is needed.
- `references/bank-template-workflow.md` for the bank-spec review and template-generation procedure.
- `references/country-rail-matrix.md` for the required country, currency, rail, bank-agent, clearing-code, account-id, and postal-address decision matrix.
- `references/template-inventory.md` for the bundled template package inventory and observed template patterns.
- `references/iso-schema-inventory.md` for bundled ISO schema selection and validation guidance.
- `references/iso-template-patterns.md` for sanitized message and mapping patterns derived from the allowed Oracle seed XSL templates.
- `references/test-scenario-generation.md` for bank-neutral source XML scenarios and runtime bank-specific validation variant rules.
- `references/template-generation/` for bundled generic ISO/SEPA seed XSL templates and JPM/PNC seed XSL templates. Raw JPM/PNC specification workbooks and bank-derived mapping workbooks are intentionally not bundled.

Use `scripts/extract_xslt_usage.py` on existing or generated XSL files to inventory target ISO tags, source XML paths, account settings, and conditional logic.

## Workflow

1. Resolve the inputs:
   - Runtime bank implementation guide, mapping workbook, or extracted specification text supplied by the user.
   - Candidate base template: bundled generic CGI, bundled generic SEPA, bundled JPM CGI/SEPA, bundled PNC CGI, or a user-provided current template.
   - Source XML reference: use the source contract and samples bundled in this skill. Treat the skill-local references as the durable source of truth for generation.
   - Test inputs: use bundled masked source XML only as structural fixtures and neutral scenario seeds. Generate bank-specific runtime validation XML variants from the completed country/rail matrix rather than treating bundled scenarios as any one bank's accepted input.
   - Use only bundled reference templates, sanitized pattern references, ISO schemas, scripts, and masked test XML unless the user explicitly supplies new runtime bank specifications or sample XML.
2. Identify the required output family:
   - CGI credit transfer, SEPA credit transfer, ACH/check/wire variant, or another bank-specific pain.001 profile.
   - Pain version and namespace, such as `pain.001.001.03` or `pain.001.001.09`.
   - Payment methods, service levels, delivery channels, countries, currencies, cutoffs, remittance limits, and bank-assigned IDs.
3. Build a mapping matrix before editing XSL:
   - ISO element number, structural sequence, message element, tag, multiplicity.
   - Bank requirement and condition.
   - Rail/payment coverage from every bank-specific column, including required, optional, conditional, and not-applicable markers.
   - Source XPath from `OutboundPaymentInstruction`.
   - Transformation rule, constants/defaults, truncation, formatting, and fallback.
   - Status: mapped, not supported, needs setup value, needs sample validation, or source gap.
4. Build a country/rail matrix before editing XSL. This is mandatory for any bank template that has more than one payment rail, country-specific clearing rule, or agent/account identifier rule:
   - Cover each supported combination of payment method, service level, delivery channel, debtor country, creditor country, currency, and bank account identifier.
   - Decide the exact output rule for `CdtrAgt`, `IntrmyAgt`, `ClrSysMmbId`, `Othr/Id`, BIC, local clearing member IDs, local clearing system codes, and postal-address structure.
   - Record source predicates from `OutboundPaymentInstruction`; do not use target paths such as `PmtInf/...` or `CdtTrfTxInf/...` as source paths.
   - If the matrix is incomplete, stop and return the mapping gaps instead of generating XSL, unless the user explicitly asks for a partial draft.
5. Generate the XSL conservatively:
   - Start from the closest working template.
   - Preserve XSLT 1.0, the `OutboundPaymentInstruction` root template, and the `contacts-by-LogicalGroupReference` grouping pattern unless the bank spec requires a different grouping.
   - Prefer source XML paths already present in `source-xml-data-definition.md` or existing working templates.
   - Use payment system account settings, DFF `Extend` fields, or bank-account setup fields only when the source XML exposes them.
   - Generate a seed-reviewable base template: use generic ISO only for required structural scaffolding and use Oracle/OOB mappings only when the bank spec is silent and the element is required or clearly supported.
   - Do not emit optional bank elements merely because source data exists. Suppress them unless the bank requirement row allows the element for the current rail and the source value is meaningful.
   - Do not map `DeliveryChannel`, `ServiceLevel`, or source setup codes into bank tags unless the bank-specific requirement allows that exact rail or value. Treat unclear conditions as mapping gaps rather than guesses.
   - Do not invent source elements. Mark unsupported bank requirements explicitly.
6. Validate:
   - Run `scripts/extract_xslt_usage.py` against the generated XSL and compare source paths to the source XML data definition.
   - Check the XSL is well-formed XML.
   - If a sample `OutboundPaymentInstruction` XML is available, run a transform and inspect the generated pain.001 output.
   - For bank-specific validation, select shipping seeds from `assets/validation/scenario-catalog/iso-source-scenarios.json` and derive project variants from the completed bank matrix. Apply the runtime-shape checks in `references/test-scenario-generation.md`, including the shipping `runtime-shape-cases.json` recipes. Preserve the source characteristic being tested rather than rewriting it to the desired bank output. Record pass, fail, or exclusion with its mapping-based reason; a relevant unresolved case remains an explicit candidate gap. Skip scenarios that do not map to a supported bank rail.
   - Verify mandatory bank tags, conditional tags, truncation, hard-coded values, namespaces, and payment-type branching.
   - Check row coverage against the runtime bank workbook/spec, rail-by-rail branch coverage, country/rail matrix coverage, optional-tag suppression, and a source-gap list for unresolved bank rows.
   - Fail validation if the XSL contains target output paths as source XPath roots, invalid XML constructs, `NaN` numeric output, empty mandatory leaf elements, or an agent/account/postal rule that is not traceable to the mapping and country/rail matrices.

## Output Expectations

Return these artifacts when the user asks for a generated template:

- Bank-specific `.xsl` file.
- Mapping matrix or mapping notes that distinguish OOB mappings from bank-specific overrides.
- Country/rail matrix or a concise summary of its resolved decisions.
- Source-gap list for bank requirements that cannot be satisfied from the current source XML.
- Optional/conditional row list that was deliberately suppressed because the bank condition or source support was missing.
- Validation summary with the exact checks run.

When only reviewing a specification, produce the mapping matrix and source-gap list before drafting XSL.

