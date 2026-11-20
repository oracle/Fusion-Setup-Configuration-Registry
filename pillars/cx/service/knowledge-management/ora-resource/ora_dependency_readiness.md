# Dependency Readiness

## Required Dependency Order

| Task Code | Task Name | Sequence | Dependency | What Must Happen |
|---|---|---|---|---|
| ORA_CSO_LOCALES_MGMT | Manage Knowledge Locales | 1 | Locale state | Resolve the selected locale's active, default, and default-preferred state through the completed Manage Knowledge Locales FSM export |
| ORA_CSO_LOCALES_MGMT | Manage Knowledge Locales | 2 | Default locale eligibility | Confirm that a selected default Knowledge locale is active |
| ORA_MANAGE_KNOWLEDGE_WORKFLOWS | Manage Knowledge Workflows | 1 | Workflow enablement | Enable Article Workflow under Manage Activity Type and Subtype and the ORA_KM_APPROVED and ORA_KM_REJECTED codes under ZMM_ACTIVITY_OUTCOME before use |
| ORA_MANAGE_KNOWLEDGE_WORKFLOWS | Manage Knowledge Workflows | 2 | Content types and approvers | Confirm selected content types and workflow-step approver privileges before creating the workflow |
| ORA_MANAGE_KNOWLEDGE_WORKFLOWS | Manage Knowledge Workflows | 3 | FSM package evidence | Reconcile a completed same-task export's four CSV members, headers, node sequence, and parent reference keys with the task fsm_contract before import preview |

## Dependency Rules

| Task Code | Task Name | Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ORA_CSO_LOCALES_MGMT | Manage Knowledge Locales | locale_current_state | Current locale state | Yes | Any locale review or configuration request | Lookup | Completed Manage Knowledge Locales FSM export | resolve_fsm_locale_state | The FSM active-locale object is authoritative for activity and the tenant object identifies the defaults | Provide the locale code or record ID when the request is for one locale | LocaleRecordId: recordId; Active: active; DefaultLocale: defaultLocale; DefaultPreferredLocale: defaultPreferredLocale |
| ORA_CSO_LOCALES_MGMT | Manage Knowledge Locales | default_locale_active | Active default locale | Yes | Set the default Knowledge locale | Verify | Completed Manage Knowledge Locales FSM export | resolve_fsm_locale_state | Only a locale present in the FSM active-locale object can be selected in the Default Locale list | Enable the locale first or select another active locale | LocaleCode: recordId; Active: active |
| ORA_CSO_LOCALES_MGMT | Manage Knowledge Locales | fsm_write_contract | FSM package contract | Yes | Any enable, default-locale, or default-preferred-locale change | Lookup | Completed Manage Knowledge Locales FSM export | resolve_fsm_package_contract | A write must use the current exported package structure rather than an inferred contract | Complete a fresh task export and use its package members, headers, metadata, and keys before a mutation preview | Package members, CSV headers, metadata, and parent-child keys |
| ORA_CSO_ARTICLE_STATUS_MGMT | Manage Knowledge Article Statuses | article_status_feature_enablement | Article Statuses feature enabled | Yes | Authors need predefined or user-defined article statuses | Verify | Completed Manage Knowledge Article Statuses FSM export | resolve_article_statuses_fsm_export | Predefined statuses are available to authors only after the feature is enabled | Enable Article Statuses before configuring or assigning statuses | FeatureState: KM_ARTICLE_STATUS_ENABLED; ArticleStatus: referenceKey, name, active |
| ORA_MANAGE_KNOWLEDGE_FOR_SERVICE_REQUESTS_PROFILE_OPTIONS | Manage Knowledge for Service Requests with Redwood User Interface Profile Options | fsm_profile_option_contract | FSM profile-option contract | Yes | Before an FSM profile-option update | Lookup | Completed task export and selected ProfileOptionName | resolve_fsm_service_requests_profile_option_export | The update must retain the exported definition, supported level, and audit fields while changing only the approved value and current update audit fields | Complete a fresh task export and select one existing profile option | ProfileOptionName; ApplicationId; supported LevelName and LevelValue; ProfileOptionValue; retained definition and audit fields |
| ORA_MANAGE_KNOWLEDGE_WORKFLOWS | Manage Knowledge Workflows | knowledge_workflow_prerequisites | Workflow activity and approval outcomes | Yes | Before creating or using a workflow | Verify | Manual verification evidence supplied in task context | verify_knowledge_workflow_prerequisites | Oracle requires Article Workflow and approval outcome lookup codes to be enabled | Provide approved verification evidence for the target environment | Article Workflow enabled; ORA_KM_APPROVED enabled; ORA_KM_REJECTED enabled |
| ORA_MANAGE_KNOWLEDGE_WORKFLOWS | Manage Knowledge Workflows | knowledge_workflow_content_types | Selected content types and approver access | Yes | Before creating a workflow | Verify | Manual verification evidence supplied in task context | verify_knowledge_workflow_prerequisites | A workflow is associated with selected content types and its steps require authorized approvers | Confirm exact content types and step approver privileges | Content-type identities; approver privileges |
| ORA_MANAGE_KNOWLEDGE_WORKFLOWS | Manage Knowledge Workflows | knowledge_workflow_fsm_contract | Same-task FSM package contract | Yes | Before preparing an FSM import | Lookup | Completed Manage Knowledge Workflows FSM export | resolve_knowledge_workflows_fsm_export | The completed export defines four objects, field headers, node order, and parent reference keys | Reconcile the current package; resolve any unverified new-workflow version, changed duration, or content-type linkage before preview | Workflow root; step; step-localized; workflow-localized CSVs; ASM_SETUP_CSV_METADATA.xml; exact keys and headers |

## Dependency Classification

| Task Code | Task Name | Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|---|---|
| ORA_CSO_LOCALES_MGMT | Manage Knowledge Locales | Lookup | Locale identity or active state must be resolved from the completed Manage Knowledge Locales FSM export | Yes |
| ORA_CSO_LOCALES_MGMT | Manage Knowledge Locales | Verify | The request requires a documented prerequisite to be confirmed | No |
| ORA_CSO_LOCALES_MGMT | Manage Knowledge Locales | Lookup | The current FSM package contract must be resolved from a completed task export | Yes |
| ORA_CSO_ARTICLE_STATUS_MGMT | Manage Knowledge Article Statuses | Verify | Article statuses must be enabled before authors can use them | No |
| ORA_MANAGE_KNOWLEDGE_FOR_SERVICE_REQUESTS_PROFILE_OPTIONS | Manage Knowledge for Service Requests with Redwood User Interface Profile Options | Lookup | The existing profile-option definition, level, and value row must be resolved from a completed task export | Yes |
| ORA_MANAGE_KNOWLEDGE_WORKFLOWS | Manage Knowledge Workflows | Verify | Workflow enablement, outcome codes, content types, and approver access need target-environment evidence | No |
| ORA_MANAGE_KNOWLEDGE_WORKFLOWS | Manage Knowledge Workflows | Lookup | A same-task export is needed to establish the FSM package contract | Yes |

## Task Nodes

| Task Code | Task Name | Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|---|---|
| ORA_CSO_ARTICLE_STATUS_MGMT | Manage Knowledge Article Statuses | ARTICLESTATUS.DEPENDENCIES | step | 3 | resolve_dependency | ok->ARTICLESTATUS.DESIGN;blocked->ARTICLESTATUS.FAILED;failure->ARTICLESTATUS.FAILED | ARTICLESTATUS.LOOKUP | stop | Before an Article Statuses request is ready for preview |
| ORA_CSO_LOCALES_MGMT | Manage Knowledge Locales | KNOWLEDGELOCALES.DEPENDENCIES | step | 3 | resolve_dependency | ok->KNOWLEDGELOCALES.DESIGN;blocked->KNOWLEDGELOCALES.FAILED;failure->KNOWLEDGELOCALES.FAILED | KNOWLEDGELOCALES.LOOKUP | stop | Before a locale configuration request is ready for preview |
| ORA_MANAGE_KNOWLEDGE_FOR_SERVICE_REQUESTS_PROFILE_OPTIONS | Manage Knowledge for Service Requests with Redwood User Interface Profile Options | SERVICEREQUESTSPROFILE.DEPENDENCIES | step | 3 | resolve_dependency | ok->SERVICEREQUESTSPROFILE.DESIGN;blocked->SERVICEREQUESTSPROFILE.FAILED;failure->SERVICEREQUESTSPROFILE.FAILED | SERVICEREQUESTSPROFILE.LOOKUP | stop | Before a Knowledge for Service Requests FSM profile-option update is ready for preview |
| ORA_MANAGE_KNOWLEDGE_WORKFLOWS | Manage Knowledge Workflows | KNOWLEDGEWORKFLOWS.DEPENDENCIES | step | 3 | resolve_dependency | ok->KNOWLEDGEWORKFLOWS.DESIGN;blocked->KNOWLEDGEWORKFLOWS.FAILED;failure->KNOWLEDGEWORKFLOWS.FAILED | KNOWLEDGEWORKFLOWS.LOOKUP | stop | Before a Knowledge workflow change is ready for preview |
