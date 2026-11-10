---
skill_id: "erp.financials.payments.manage-formats.template-generator.avs-provider"
name: "Payments AVS Provider Template Engine"
description: "Generates source-backed AVS provider request and response templates for Manage Formats."
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
  - "avs_provider_api_specification_and_version"
  - "request_response_xml_first_conversion_contract"
  - "representative_masked_samples"
  - "project_context"
outputs:
  - "template_handoff_json"
  - "template_artifact"
  - "mapping_matrix"
  - "source_gap_report"
  - "offline_validation_report"
  - "request_response_template_pair"
  - "request_response_data_definitions"
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

Payments AVS Provider Template Engine is an optional, focused Payments design capability invoked by Manage Formats. It has no independent FSM task identity. Its source contracts, mapping rules, fixtures, and validation steps below are retained from the installed engine.

## Candidate generation objective

Read [candidate-generation.md](../references/candidate-generation.md) before mapping. Default to implementation_candidate: deliver a useful template with explicit assumptions and tests; strict_conformance is a separate review objective. Unresolved mappings gate readiness or the affected execution path, not all artifact creation.

## FSCR governed handoff

Read `../references/template-handoff-contract.md` from a child engine, or `references/template-handoff-contract.md` from the router. Record the machine-readable handoff and register artifacts under the project workspace. The parent owns format creation/update, attachment, runtime verification, and task completion. This skill never publishes BI catalog content, uploads direct XML templates, imports FSM data, or approves a candidate. The selected engine must complete its original source, mapping, sample, and offline validation requirements before status `validated` is claimed.

Preflight profile, direction, provider/bank specification and source contract. Capture verified parent format identity/type and attachment mechanism when available; otherwise leave those metadata unresolved in a draft/discovery/failed handoff and continue useful offline generation. Resolve them before any installation or format action. Missing input is a scoped gap; fail only when no useful candidate can be constructed or processing itself fails. Unsupported routes produce a discovery pack. Failure behavior: a failed engine returns a failed handoff with diagnostics; it never silently switches to an invented template. Redact account, card, credential, and customer data from durable output. No Fusion request or polling occurs here. Preserve failed runs for later review; retry only the offline step after correcting inputs. An artifact overwrite follows project versioning rules.

## FSCR AVS route contract

Accept this route only after tracing the Oracle AVS generic request XML from the source procedure and view and establishing the provider's request and response contracts, including JSON-to-XML/XML-to-JSON behavior when applicable. The original engine's request and response mapping and normalized response fields remain authoritative. A request/response pair is one generation run but each intended Manage Formats format receives its own handoff and primary template hash. Before `validated`, compile both XSLTs, transform the bundled masked request fixtures plus provider success, neutral/no-data, invalid/failure, and provider-error responses, and verify data-definition/XSD shape. Register both templates, mapping, gap report, and validation evidence. Missing provider response shape or unresolved status mapping is a gap; do not invent a response template or claim the format attached.

## Original engine workflow

# Generate AVS Provider Templates

## Overview

Create provider-specific AVS request and response XSLT templates from Oracle generic bank-account verification payloads and an external provider API specification. Keep the work evidence-backed: derive generic XML from the PL/SQL/view sources, map only data the generic XML can supply, and test every template with representative samples.

Oracle AVS uses an XML-first transformation contract even for JSON REST providers. The request flow starts with Oracle generic XML, applies a request XSLT to produce provider-shaped XML, and only then converts that XML to JSON when the provider API requires JSON. The response flow converts provider JSON to XML first, then applies a response XSLT to produce Oracle's normalized response XML.

Read [oracle-avs-payloads.md](references/oracle-avs-payloads.md) before drafting templates or schemas. Use masked project samples or construct synthetic samples from the evidenced Oracle source contract for baseline source-shape validation. Developer fixtures are optional test seeds and are not provider specifications.

## Workflow

1. Inventory the artifacts:
   - PL/SQL package containing `Create_Ba_Ownr_Verif_Extract_1_0`.
   - Generic request view files such as `iby_xml_temp_ba_verif_1_0_v.view` and any main-table equivalent.
   - Existing provider templates such as `JPM_AVS_Request.xml` and `JPM_AVS_Response.xml`.
   - Provider API specs, OpenAPI/YAML files, PDFs, test-account lists, and sample JSON responses.
   - Prefer seeded/current JPM AVS templates and JPM integration evidence when available. Treat exploratory provider pages or in-evaluation providers as provisional unless their artifacts are already accepted as Oracle seed/reference material.

2. Derive the generic request XML:
   - Read the procedure overloads and all `iby_utility_pvt.set_view_param` calls.
   - Identify which view is queried for each mode, especially `p_mode = 'TEMP'`.
   - Derive the XML tree from the view's `XMLELEMENT` calls, not from assumptions in prior generated docs.
   - Record source expressions for each generic XML field and call out declared-but-unused parameters.

3. Study the existing provider pattern:
   - Preserve the root and hint conventions used by the local templates, commonly `RequestMessage` plus `ExtraHints/EXTRA_HEADERS`.
   - Preserve the normalized response root and field names used by `JPM_AVS_Response.xml`.
   - Reuse the existing internal message vocabulary unless the codebase clearly defines provider-specific additions.
   - Model the provider JSON schema as the JSON serialization of provider-shaped XML. Do not skip the XML stage when drafting request or response XSLT.

4. Map the new provider request:
   - Confirm endpoint, required headers, request body fields, enums, max lengths, and formatting rules from the provider's current spec.
   - Map generic XML fields to provider fields one by one.
   - For JSON REST providers, design the XSLT output XML so its element names, arrays/repeating nodes, and text values serialize predictably into the provider JSON payload.
   - Do not emit provider fields that require data absent from the generic XML unless a payment-system option or explicit configuration source is present.
   - Document every omission, constant, truncation, format normalization, and header placeholder.

5. Map the new provider response:
   - Apply the response-literal and conflicting-evidence rules in `references/oracle-avs-payloads.md`; preserve exact provider values and test precedence before claiming successful verification.
   - Confirm how the application converts provider JSON to XML before XSLT. Build the response XSLT against that converted XML shape, not directly against conceptual JSON paths.
   - Normalize provider success, partial match, no-data, invalid-account, inactive, unsupported, timeout, and request-shape errors into the existing response fields.
   - Keep provider raw codes/messages in `*RespCode` and `*RespMsg` fields where possible.
   - Add optional provider detail fields only when useful for audit/debugging and reflect them in the response XSD.

6. Validate before delivery:
   - Compile each XSLT with an available XSLT 1.0 processor.
   - For request templates, transform representative masked or synthetic project samples to verify the generic Oracle AVS request structure across success/failure and applicable country profiles, including US/NL/IT-style shapes when supported.
   - Transform at least four samples: exact success, soft/neutral/no-data, invalid/failure, and provider error.
   - Check generated XSD files are well formed and match the documented XML tree.
   - Reconcile every mismatch against source artifacts or provider docs; update docs and templates together.

## Deliverables

Produce a small, reviewable artifact set:

- `<Provider>_AVS_Request.xml`
- `<Provider>_AVS_Response.xml`
- `BankAccountVerificationRequest.md`
- `BankAccountVerificationRequest.xsd`
- `BankAccountVerificationResponse.md`
- `BankAccountVerificationResponse.xsd`

When updating existing generated artifacts, state whether they were accurate as-is or list the corrections made.

