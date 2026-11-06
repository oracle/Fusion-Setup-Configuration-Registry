---
skill_id: "scm.procurement.approval-management"
name: "Approval Management"
description: "Provides manual guidance for Oracle Fusion Procurement approval-management setup tasks."
layer: "pillar"
pillar: "SCM"
offering: "Procurement"
functional_area: "Approval Management"
functional_area_code: "ORA_PO_APPROVAL_MANAGEMENT_FA"
type: "advisory"
execution_mode: "advisory"
owner_team: "SCM procurement pillar team"
version: "0.1.0"
inputs:
  - "approval_task_name"
  - "approved_configuration_change"
  - "target_environment"
outputs:
  - "manual_execution_guidance"
  - "manual_validation_checklist"
  - "token_usage_record"
depends_on:
  - "shared.common.manual-tasks"
uses_core: []
persists_project_state: false
required_setup_tasks:
  - "ORA_POZ_MANAGE_INTERNAL_SUPPLIER_REGISTRATION_APPROVALS"
  - "ORA_POZ_MANAGE_SUPPLIER_REGISTRATION_APPROVALS"
  - "ORA_POZ_MANAGE_INTERNAL_SUPPLIER_PROFILE_CHANGE_APPROVALS"
  - "ORA_POZ_MANAGE_SUPPLIER_SPEND_AUTHORIZATION_APPROVALS"
  - "ORA_POZ_MANAGE_SUPPLIER_PROFILE_CHANGE_APPROVALS"
  - "PO_MANAGE_PURCHASING_DOCUMENT_APPROVALS"
  - "ORA_PO_MANAGE_INTAKE_REQUEST_APPROVALS"
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
applicability:
  industries:
    - "All"
  countries:
    - "All"
  fusion_releases:
    - "Current Oracle Fusion Cloud release"
side_effects: []
required_privileges:
  - "Privilege to access the named Setup and Maintenance task"
---

# Approval Management

## Purpose

Provide manual Oracle Fusion guidance for the requested Procurement approval-management setup task.

## Use

Use the matching task-specific guidance with the approved configuration change and target environment. Do not automate Approval Management configuration.

## Setup Tasks

- [Manage Internal Supplier Registration Approvals](manage-internal-supplier-registration-approvals.md) (`ORA_POZ_MANAGE_INTERNAL_SUPPLIER_REGISTRATION_APPROVALS`)
- [Manage Supplier Registration Approvals](manage-supplier-registration-approvals.md) (`ORA_POZ_MANAGE_SUPPLIER_REGISTRATION_APPROVALS`)
- [Manage Internal Supplier Profile Change Approvals](manage-internal-supplier-profile-change-approvals.md) (`ORA_POZ_MANAGE_INTERNAL_SUPPLIER_PROFILE_CHANGE_APPROVALS`)
- [Manage Supplier Spend Authorization Approvals](manage-supplier-spend-authorization-approvals.md) (`ORA_POZ_MANAGE_SUPPLIER_SPEND_AUTHORIZATION_APPROVALS`)
- [Manage Supplier Profile Change Approvals](manage-supplier-profile-change-approvals.md) (`ORA_POZ_MANAGE_SUPPLIER_PROFILE_CHANGE_APPROVALS`)
- [Manage Purchasing Document Approvals](manage-purchasing-document-approvals.md) (`PO_MANAGE_PURCHASING_DOCUMENT_APPROVALS`)
- [Manage Intake Request Approvals](manage-intake-request-approvals.md) (`ORA_PO_MANAGE_INTAKE_REQUEST_APPROVALS`)
