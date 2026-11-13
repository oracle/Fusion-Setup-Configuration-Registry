---
skill_id: "erp.financials.payments.manage-formats.template-generator.virtual-card-provider"
name: "Payments Virtual Card Provider Template Engine"
description: "Generates source-backed virtual-card provider templates by requested profile for Manage Formats."
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
  - "requested_virtual_card_profiles"
  - "provider_correlation_and_status_contract"
  - "representative_masked_samples"
  - "project_context"
outputs:
  - "template_handoff_json"
  - "template_artifact"
  - "mapping_matrix"
  - "source_gap_report"
  - "offline_validation_report"
  - "per_profile_mapping_matrices"
  - "correlation_status_mapping_summary"
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

Payments Virtual Card Provider Template Engine is an optional, focused Payments design capability invoked by Manage Formats. It has no independent FSM task identity. Its source contracts, mapping rules, fixtures, and validation steps below are retained from the installed engine.

## Candidate generation objective

Read [candidate-generation.md](../references/candidate-generation.md) before mapping. Default to implementation_candidate: deliver a useful template with explicit assumptions and tests; strict_conformance is a separate review objective. Unresolved mappings gate readiness or the affected execution path, not all artifact creation.

## FSCR governed handoff

Read `../references/template-handoff-contract.md` from a child engine, or `references/template-handoff-contract.md` from the router. Record the machine-readable handoff and register artifacts under the project workspace. The parent owns format creation/update, attachment, runtime verification, and task completion. This skill never publishes BI catalog content, uploads direct XML templates, imports FSM data, or approves a candidate. The selected engine must complete its original source, mapping, sample, and offline validation requirements before status `validated` is claimed.

Preflight profile, direction, provider/bank specification and source contract. Capture verified parent format identity/type and attachment mechanism when available; otherwise leave those metadata unresolved in a draft/discovery/failed handoff and continue useful offline generation. Resolve them before any installation or format action. Missing input is a scoped gap; fail only when no useful candidate can be constructed or processing itself fails. Unsupported routes produce a discovery pack. Failure behavior: a failed engine returns a failed handoff with diagnostics; it never silently switches to an invented template. Redact account, card, credential, and customer data from durable output. No Fusion request or polling occurs here. Preserve failed runs for later review; retry only the offline step after correcting inputs. An artifact overwrite follows project versioning rules.

## FSCR virtual-card route contract

Classify each requested outbound payment, acknowledgment, payment response, or reconciliation profile and its exact Oracle source or normalized target contract. Inventory provider specification/version, payload conversion shape, correlation IDs, status/error mapping, masked fixtures and a PCI boundary. Construct source-derived samples when needed and expose missing mappings through the candidate policy. The original engine's per-profile matrices, source/target gap rules, seed selection, and conservative output rules remain authoritative. For each intended format, emit a format-specific handoff with its primary template hash. Before `validated`, compile and transform every requested profile; check matching ISO and normalized-contract schemas where applicable; test accepted, rejected, partial/pending, repeated, and malformed-correlation cases; and validate the selected seed assets and generated transformations. The bundled developer regression is optional when available. Keep PCI data out of project artifacts. An unresolved required correlation key is a material gap: deliver supported candidate logic and require an explicit binding or reject its affected execution path.

## Original engine workflow

# Generate Virtual Card Provider Templates

## Overview

Generate provider-specific virtual-card templates without collapsing all inbound processing into one response. Oracle uses one enriched Funds Disbursement outbound source contract and separate normalized inbound contracts for acknowledgment, payment response, and reconciliation.

Read [oracle-virtual-card-contracts.md](references/oracle-virtual-card-contracts.md) before mapping any profile. For contract-sensitive mapping or disputed field semantics, read [source-manifest.md](references/source-code/source-manifest.md) and the relevant bundled contract reference. Use these packaged contracts without access to Oracle internal systems. If the customer requirement conflicts with a bundled contract, record the exact gap and request the applicable supported contract or an updated skill package; do not invent a replacement mapping. Then read only the operation-specific sections and seed templates needed for the request.

## Profiles

Classify every requested artifact as one of these profiles:

| Profile | Template direction | Oracle contract |
| --- | --- | --- |
| Outbound payment | Oracle XML to provider payload | `OutboundPaymentInstruction` with virtual-card extensions |
| Acknowledgment | Provider payload to Oracle XML | `AckResponse` |
| Payment response | Provider payload to Oracle XML | `records/record` |
| Reconciliation | Provider payload to Oracle XML | `reconRcrd/reconDetls` |

Treat card-statement processing, provider onboarding, transmission setup, and API orchestration as separate integration concerns unless the user explicitly requests discovery for them.

## Workflow

1. Inventory runtime evidence:
   - Provider implementation guide and requested profiles.
   - Provider payload type, version, encoding, and samples for each profile.
   - For delimited input: delimiter, quoting, label row, header/footer behavior, and column definitions.
   - Correlation identifiers, status/error mappings, PCI boundary, and required setup values.
2. Build one mapping matrix per profile before writing XSLT:
   - Provider path or column.
   - Oracle source or normalized target path.
   - Cardinality, condition, formatting, default, truncation, and status.
   - Evidence source and unresolved gap.
   - Whether an outbound source field is unconditional, setup-dependent, or emitted only by an opt-in branch.
3. Generate supported candidate logic when a required correlation mapping is unresolved. Make the affected path require an explicit binding or terminate with a diagnostic; do not silently invent payment reference, payment instruction, provider transaction, authorization, or clearing-reference mappings. Record evidenced provisional choices and test their assumptions.
4. Select the closest bundled seed pattern from [seed-template-inventory.md](references/seed-template-inventory.md). Preserve XSLT 1.0 unless the runtime explicitly supports another version.
5. For ISO payloads, read [iso-schema-inventory.md](references/iso-schema-inventory.md):
   - Match the XSD to the exact namespace and provider profile.
   - Do not treat XSD validity as proof of provider acceptance.
   - Use the bundled base pain.002 schema by default; use the SEPA-restricted profile only when the provider explicitly requires it.
6. Generate conservatively:
   - Emit only fields permitted by the provider specification and available from the Oracle contract or explicit setup.
   - Preserve provider raw status and error values where the Oracle normalized contract has a destination.
   - Map provider statuses explicitly to Oracle application statuses and invoice-hold behavior.
   - Keep PCI data out of non-PCI templates, logs, fixtures, mapping reports, and generated examples.
   - Emit the exact case-sensitive normalized element names recorded in [contract-elements.json](references/source-code/contract-elements.json).
   - Account for Oracle consumer truncation documented in [inbound-contract-source.md](references/source-code/inbound-contract-source.md); report possible diagnostic or identifier loss instead of relying on silent truncation.
7. Validate:
   - Parse and compile all generated XSLT.
   - Transform synthetic or masked fixtures for every generated profile.
   - Validate ISO output/input against the exact applicable XSD when available.
   - Validate inbound transformed output against the bundled Oracle normalized-contract XSD.
   - Verify repeated records, success, rejection, partial/pending status, missing optional data, and malformed required correlation data.
   - Validate the applicable bundled schemas and seed transformations against masked or synthetic project samples; the optional developer regression runner provides additional coverage when available.
   - Record the provenance of selected project samples; never treat sample values as provider requirements.

## Provider Formats

- XML: transform directly between provider XML and the Oracle contract.
- CSV or delimited text: model Fusion's generic converted XML as `/root/records/record/colN`; map columns only after the file layout is confirmed.
- JSON REST: preserve Oracle's XML-first convention. Define the provider-shaped XML that serializes to JSON, or the provider JSON-to-XML shape received before response XSLT.
- Fixed-width or eText: document the preprocessing contract and do not pretend the XSLT consumes raw text if Fusion converts it first.

## Deliverables

Return only the profiles requested, plus:

- Provider-specific XSLT files.
- Per-profile mapping matrices.
- Correlation and status/error mapping summary.
- Source/target gap list and deliberately suppressed fields.
- PCI-data handling statement.
- Validation report listing processor, fixtures, XSDs, outputs, and residual gaps.

When only reviewing a provider specification, produce the profile classification, matrices, and gaps before drafting templates.

