---
skill_id: "erp.financials.payments.manage-formats.template-generator"
name: "Payments Template Generator"
description: "Routes and generates source-backed Oracle Payments template artifacts for Manage Formats."
layer: "pillar"
pillar: "ERP"
type: "planning"
execution_mode: "assisted"
owner_team: "ERP financials pillar team"
version: "0.2.1"
inputs:
  - "format_identity_and_type"
  - "attachment_mechanism"
  - "source_payload_contract"
  - "provider_or_bank_specification"
  - "representative_masked_samples"
  - "assistance_mode"
  - "requested_template_profile"
  - "project_context"
outputs:
  - "template_handoff_json"
  - "template_artifact"
  - "mapping_matrix"
  - "source_gap_report"
  - "offline_validation_report"
  - "route_decision_and_discovery_pack"
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

Payments Template Generator is an optional, focused Payments design capability invoked by Manage Formats. It has no independent FSM task identity. Its source contracts, mapping rules, fixtures, and validation steps below are retained from the installed engine.

## Candidate generation objective

Read [candidate-generation.md](references/candidate-generation.md) before mapping. Default to implementation_candidate: deliver a useful template with explicit assumptions and tests; strict_conformance is a separate review objective. Unresolved mappings gate readiness or the affected execution path, not all artifact creation.

## FSCR governed handoff

Read `../references/template-handoff-contract.md` from a child engine, or `references/template-handoff-contract.md` from the router. Record the machine-readable handoff and register artifacts under the project workspace. The parent owns format creation/update, attachment, runtime verification, and task completion. This skill never publishes BI catalog content, uploads direct XML templates, imports FSM data, or approves a candidate. The selected engine must complete its original source, mapping, sample, and offline validation requirements before status `validated` is claimed.

Preflight profile, direction, provider/bank specification and source contract. Capture verified parent format identity/type and attachment mechanism when available; otherwise leave those metadata unresolved in a draft/discovery/failed handoff and continue useful offline generation. Resolve them before any installation or format action. Missing input is a scoped gap; fail only when no useful candidate can be constructed or processing itself fails. Unsupported routes produce a discovery pack. Failure behavior: a failed engine returns a failed handoff with diagnostics; it never silently switches to an invented template. Redact account, card, credential, and customer data from durable output. No Fusion request or polling occurs here. Preserve failed runs for later review; retry only the offline step after correcting inputs. An artifact overwrite follows project versioning rules.

## FSCR route decision and exit contract

Use the registry below to select exactly one packaged engine for each requested template profile. Resolve the original installed-skill names to `bank-iso/SKILL.md`, `avs-provider/SKILL.md`, or `virtual-card-provider/SKILL.md` within this package. Record usage type, selected profile, engine ID, source-contract version, attachment mechanism, and reason for the route. An unknown category returns a discovery pack with missing source, provider, sample, and processor evidence; it cannot return `validated`. If assistance is `guided-manual` or `disabled`, do not invoke an engine, and return the corresponding durable handoff. A route failure returns diagnostics and the manual next action without changing the Manage Formats create/update route. The parent checks the format-specific handoff before presenting any attachment step; a child does not alter FSM CSV packages or format setup status.

## Original engine workflow

# Generate Oracle Payments Templates

## Overview

Use this wrapper skill to classify Oracle Payments template work by usage type, source payload, and target output before loading a specialized generation workflow. Keep this skill as the router and shared governance layer; keep detailed mapping logic, bundled examples, and validation scripts in child skills.

Read `references/usage-type-registry.md` before routing a request.

## Routing Workflow

1. Classify the request:
   - Usage type: funds disbursement, AVS, virtual card, funds capture, payment gateway, or unknown.
   - Subtype: ISO credit transfer, virtual-card payment/acknowledgment/response/reconciliation, ISO direct debit, bank EFT, card gateway request/response, provider AVS, or another integration family.
   - Source contract: source XML root, PL/SQL procedure/view, sample XML, JSON-to-XML envelope, or eText extract.
   - Output type: XSLT-generated XML, JSON payload through XML-to-JSON conventions, eText/flat file, XSD/data definition, mapping matrix, or review report.
2. Route to the focused child skill when one exists:
   - Funds Disbursement ISO credit transfer: use `generate-bank-iso-templates`.
   - Account Validation Service: use `generate-avs-provider-templates`.
   - Virtual-card provider payment, acknowledgment, payment response, or reconciliation: use `generate-virtual-card-provider-templates`.
3. For a new or unsupported category:
   - Build a discovery pack instead of guessing a template.
   - Identify the source XML/data contract, target output format, existing generic templates, provider/bank specification, sample inputs, expected outputs, and validation processor.
   - Propose a new child skill only when the workflow has repeatable source structures, output conventions, and validation steps.
4. Load only the selected child skill and the references needed for that route. Load multiple child skills only when the user explicitly asks for cross-category design, comparison, or shared refactoring.

## Shared Rules

- Derive mappings from source XML/view/procedure definitions and provider or bank specifications, not from plausible field names.
- Produce a row-by-row or field-by-field mapping matrix before generating templates.
- Distinguish OOB mappings, bank/provider overrides, constants, setup values, extension fields, unsupported fields, and open questions.
- Suppress optional or conditional output elements unless the selected specification permits the element and the source has a meaningful value.
- Do not persist production-sensitive sample data. Mask or scramble PII, account numbers, IBANs, credentials, endpoint secrets, and connectivity attributes before creating durable test assets.
- Validate templates with representative samples and report exact commands, input files, generated outputs, and residual gaps.

## Output Expectations

When routing a template request, state:

- Selected usage type and child skill.
- Source contract and output type.
- Required input artifacts still missing, if any.
- Generated or reviewed artifacts.
- Validation summary and known gaps.

When creating a new category, update `references/usage-type-registry.md` with the route, source contract, output type, validation plan, and recommended child-skill name.

