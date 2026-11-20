---
task_code: "ORA_CSO_USER_GROUPS_MGMT"
task_name: "Manage Knowledge User Groups"
parent_skill_id: "cx.help-desk.knowledge-management"
pillar: "CX"
offering: "Help Desk"
functional_area: "Knowledge Management"
functional_area_code: "ORA_CSO_KNOWLEDGE_MANAGEMENT"
available_flag: "Y"
export_import_supported_flag: "Y"
csv_export_import_supported_flag: "Y"
dataloader_import_mode: "FSM"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
depends_on:
  - "cx.service.knowledge-management"
---

# Manage Knowledge User Groups

## Routing Metadata

Read the parent's [Help Desk Task Handoff](SKILL.md#help-desk-task-handoff)
first. Then delegate `ORA_CSO_USER_GROUPS_MGMT` to the exact
[Service task guidance](../../service/knowledge-management/manage-knowledge-user-groups.md) with its mandatory resources.
The parent handoff owns context preservation, domain validation, package evidence,
core/shared routing and project persistence. Keep the Help Desk catalog identity
above; use the Service contract without copying or renaming its objects here.
Do not execute directly from this metadata file.

## Route To

Route to cx.service.knowledge-management.
