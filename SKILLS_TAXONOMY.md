# FSCR Skills Taxonomy

Updated: 2026-10-23

Source: Oracle Fusion Setup and Configuration Skills Registry (FSCR)

## Purpose

Use this taxonomy to find the skills relevant to your Oracle Fusion implementation, understand the responsibilities of each repository layer, and locate guidance for your business domain. Counts and categories reflect the current repository after applying the release distribution exclusions.

For an introduction, environment setup guidance, or authentication questions, start with [FSCR Onboarding](core/getting-started/onboarding/SKILL.md). To start or resume implementation work, use the [Implementation Router](router/implementation-router/SKILL.md). Describe your business objective, offering, environment, and existing project context when known.

The domain links below help you explore available guidance. Each selected workflow defines its prerequisites, supported operations, human review, and approvals. A skill's presence or execution-mode label alone does not establish that a particular live operation is supported.

## Repository Taxonomy At A Glance

| Layer | Current skills | Taxonomy role | What it provides for implementation users |
| --- | ---: | --- | --- |
| [router](router/) | 3 | Implementation orchestration | Objective classification, workflow coordination, and next-action planning. |
| [core](core/) | 34 | Reusable technical services | Onboarding, authentication, API services, data loading, Run Books, environment checks, project state, and report generation. |
| [shared](shared/) | 86 | Cross-pillar implementation methods | Intake, planning, baseline assessment, setup movement, validation, conversion, integration, extensibility, reporting, and instance strategy. |
| [pillars](pillars/) | 1,039 | Business-domain guidance | Common, CX, ERP, HCM, and SCM offering, functional-area, setup-task, and specialized guidance. |

Supporting areas supply reference material and preserve implementation work:

| Area | What implementation users find here |
| --- | --- |
| [knowledge](knowledge/) | Setup-task catalogs, product guidance, dependency information, validation guidance, and reusable reference material. |
| [schemas](schemas/) | Definitions used to check the structure of implementation data, project state, and artifacts. |
| [governance](governance/) | Repository standards, review guidance, and operating conventions. |
| [project](project/) | Durable implementation workspaces containing state, artifacts, exports, baselines, decisions, and blueprints. |

Implementation outputs belong to the selected `project/{project_id}` workspace. Configuration exports are retained under `project/{project_id}/exports/`; durable run records are retained under `project/{project_id}/state/runs/`. This allows later sessions to resume from recorded work.

## Current Catalog Summary

Total included skill manifests: **1,162**.

This snapshot counts each included `SKILL.md` under the four skill layers once, including nested skills and compatibility redirects. Release distribution exclusions apply before counting or selecting navigation links: excluded directories and their descendants contribute no entries. Supporting documents and project artifacts are outside the count. These are manifest counts, not counts of distinct executable operations or completed implementation tasks.

### By Layer

| Layer | Count |
| --- | ---: |
| Core | 34 |
| Pillar | 1,039 |
| Router | 3 |
| Shared | 86 |
| **Total** | **1,162** |

The manifest layer value `pillar` corresponds to the repository folder `pillars/`.

### By Skill Type

| Declared type | Count | How to interpret it |
| --- | ---: | --- |
| `advisory` | 32 | Guidance, recommendations, and design considerations. |
| `assessment` | 16 | Scope, requirements, current-state, or readiness assessment. |
| `export` | 5 | Preparation or retrieval of setup packages and related export artifacts. |
| `import` | 66 | Import preparation, coordination, or execution within the owning workflow. |
| `orchestration` | 146 | Coordination of skills, business domains, or implementation activities. |
| `planning` | 875 | Roadmaps, dependencies, functional-area guidance, and setup-task preparation. |
| `support` | 1 | Supporting task execution, as declared by the current manifest. |
| `validation` | 7 | Checks of configuration, evidence, or readiness. |
| `verification` | 14 | Verification of specific outcomes within the skill's declared scope. |
| **Total** | **1,162** | |

Types report the values declared in the current manifests, including `support`; they do not assert schema conformance or replace the workflow descriptions.

### By Execution Mode

| Declared execution mode | Count | What to expect |
| --- | ---: | --- |
| `advisory` | 28 | Guidance for the implementer to apply. |
| `assisted` | 922 | Guided work, artifacts, or recommendations requiring human involvement. |
| `automated` | 7 | Supported actions executed by automation under the workflow's checks and approvals. |
| `hybrid` | 205 | A combination of automation and human decisions or approvals. |
| **Total** | **1,162** | |

### By Pillar Value

| Declared pillar | Count |
| --- | ---: |
| CX | 203 |
| Common | 92 |
| Core | 31 |
| ERP | 104 |
| HCM | 457 |
| Router | 3 |
| SCM | 266 |
| Not declared | 6 |
| **Total** | **1,162** |

Pillar values describe manifest applicability, so they differ from folder counts. For example, `Common` includes cross-pillar shared skills as well as Common-pillar skills. Six manifests omit a pillar value and remain included in the other summaries.

## Domain Inventory

Use these domain summaries to locate relevant work. Counts include all nested manifests within the listed domain. The linked examples are starting points for exploration; the Implementation Router remains the entry point for implementation execution.

### Implementation Orchestration

| Domain | Count | Implementation purpose |
| --- | ---: | --- |
| [router/implementation-router](router/implementation-router/SKILL.md) | 1 | Start or resume an implementation objective and coordinate the applicable skills. |
| [router/project-objective-classifier](router/project-objective-classifier/SKILL.md) | 1 | Identify the pillar, offering, functional area, geography, scope, and delivery phase. |
| [router/next-action-planner](router/next-action-planner/SKILL.md) | 1 | Determine the next skill or human action from project state and dependencies. |

### Core Services

| Domain | Count | Implementation purpose and useful starting points |
| --- | ---: | --- |
| [core/getting-started](core/getting-started/) | 2 | [Onboarding](core/getting-started/onboarding/SKILL.md) for introduction and authentication guidance; [Implementation Users](core/getting-started/implementation-users/SKILL.md) for user setup. |
| [core/auth](core/auth/) | 1 | [Fusion OAuth Authentication](core/auth/fusion-oauth-authentication/SKILL.md) for environment enrollment, login, and token handling when selected by the active workflow. |
| [core/diagnostics](core/diagnostics/) | 3 | Environment health, instance capabilities, and role/access checks. |
| [core/data-loader](core/data-loader/SKILL.md) | 4 | Sample preparation, validation, approved data imports, status, and task-specific execution support. Data Loader owns the mandatory orchestration workflow for Fusion data imports. |
| [core/fusion-api](core/fusion-api/) | 16 | Shared REST, FSM, UCM, ESS, CX import/export, and audit services; [Apps Common](core/fusion-api/apps-common/SKILL.md) covers lookups, flexfields, profile options, trees, value sets, and attachment setup. |
| [core/fusion-ai](core/fusion-ai/) | 1 | [Workflow Agent Invoker](core/fusion-ai/workflow-agent-invoker/SKILL.md) for submitting and tracking supported Fusion AI Studio workflow-agent requests. |
| [core/project-mgmt](core/project-mgmt/) | 5 | Workspace initialization, resumable project state, artifact registration/versioning, and configuration baselines. |
| [core/runbook](core/runbook/SKILL.md) | 1 | Run Book and task management for organizing and tracking implementation work in Fusion. |
| [core/validation](core/validation/) | 1 | [Validation Reporting](core/validation/reporting/SKILL.md) generates local HTML/JSON reports and executive indexes from supplied sanitized evidence. |

### Shared Implementation Methods

| Domain | Count | Implementation purpose and useful starting points |
| --- | ---: | --- |
| [shared/project-intake](shared/project-intake/) | 6 | Capture requirements, enterprise structure, localization, integrations, and [confirmed scope](shared/project-intake/scope-definition/SKILL.md). |
| [shared/implementation-planning](shared/implementation-planning/) | 9 | Build roadmaps, task maps, dependency sequences, wave plans, and readiness checklists; coordinate supported offering, functional-area, and feature opt-ins. |
| [shared/baseline-assessment](shared/baseline-assessment/) | 11 | Assess fit/gap and drift, compare setup packages or environments, and work with topology information. [Export and Compare](shared/baseline-assessment/setup-compare/export-and-compare/SKILL.md) is a useful setup-comparison starting point. |
| [shared/setup-data-task-matching](shared/setup-data-task-matching/SKILL.md) | 1 | Identify setup tasks from supplied evidence or map tabular data to catalog tasks and task-scoped extracts. |
| [shared/setup-export](shared/setup-export/) | 4 | Export task, functional-area, or offering CSV template/spec packages by default; export setup data when explicitly requested. |
| [shared/setup-import](shared/setup-import/) | 6 | Setup-import preparation, task/functional-area/offering import services, and status monitoring within the Data Loader workflow. |
| [shared/validation](shared/validation/) | 7 | Prevalidation, Implementation Review, setup/reference/dependency checks, coordination of a selected transactional check, and evidence summaries. |
| [shared/common](shared/common/) | 2 | [Manual Tasks](shared/common/manual-tasks/SKILL.md) guidance and [Risk and Security Checkup](shared/common/security/risk-and-security-checkup/SKILL.md) for role-set assessment. |
| [shared/best-practices](shared/best-practices/) | 5 | Process alignment, security-role guidance, approval workflows, localization, and implementation risk. |
| [shared/data-conversion](shared/data-conversion/) | 5 | Conversion strategy, legacy-data profiling, cleansing, mapping templates, and reconciliation guidance. |
| [shared/extensibility](shared/extensibility/) | 6 | Extension strategy, Groovy, low-code, Page Composer, sandbox/migration guidance, and [VBLens Express Mode](shared/extensibility/vblens-express-mode/SKILL.md). |
| [shared/integrations](shared/integrations/) | 5 | Integration strategy, OIC design, API-led and event-driven patterns, and legacy-system integration guidance. |
| [shared/reporting](shared/reporting/) | 5 | Business-reporting strategy, OTBI, BI Publisher, operational report catalogs, and analytics/KPI guidance. |
| [shared/instance-strategy](shared/instance-strategy/) | 5 | Instance and pod strategy, migration paths, environment refresh, and release-update readiness. |
| [shared/security-console](shared/security-console/SKILL.md) | 9 | Compatibility redirects to the current [Common-pillar Security Console](pillars/common/security-console/SKILL.md) skills. |

For validation, [Prevalidation](shared/validation/prevalidation/SKILL.md) addresses environment readiness, [Implementation Review](shared/validation/configuration-completeness-validator/SKILL.md) examines requirements and implementation evidence, and [Transactional Validation Coordinator](shared/validation/transactional-validation-coordinator/SKILL.md) coordinates one supported pillar-owned check. Transactional execution depends on the selected check's declared route; the coordinator supplies no generic transaction runner. See [What validation means](knowledge/validation-rules/fscr-validation-faq.md#1-what-validation-means) for the distinctions. Report generation summarizes evidence and does not itself execute live checks.

### Pillar Domains

Pillar folders organize business guidance by offering or specialist domain, then by functional area and setup task where available. The coverage examples below are navigation aids rather than an exhaustive list of skills.

| Domain | Count | Coverage and example entry points |
| --- | ---: | --- |
| [pillars/common](pillars/common/) | 9 | [Security Console](pillars/common/security-console/SKILL.md): roles, duties, data-security policies, user provisioning, HCM role-provisioning rules, and related security setup across pillars. |
| [pillars/cx](pillars/cx/) | 203 | [Sales](pillars/cx/sales/SKILL.md), [Service](pillars/cx/service/SKILL.md), [Field Service](pillars/cx/field-service/SKILL.md), [Customer Data Management](pillars/cx/customer-data-management/SKILL.md), [Subscriptions](pillars/cx/subscriptions/SKILL.md), [Configure Price Quote](pillars/cx/configure-price-quote/SKILL.md), [Customer Loyalty](pillars/cx/customer-loyalty/SKILL.md), [Marketing](pillars/cx/marketing/SKILL.md), [Sales Marketing](pillars/cx/sales-marketing/SKILL.md), and [PRM](pillars/cx/prm-offering/SKILL.md). |
| [pillars/erp](pillars/erp/) | 104 | [Financials](pillars/erp/financials/SKILL.md), [Project Financial Management](pillars/erp/project-financial-management/SKILL.md), [Risk and Security](pillars/erp/risk-and-security/SKILL.md), [Fusion Accounting Hub](pillars/erp/fusion-accounting-hub/SKILL.md), [Grants Management](pillars/erp/grants-management/SKILL.md), [Project Execution Management](pillars/erp/project-execution-management/SKILL.md), [Public Sector Permits](pillars/erp/public-sector-permits/SKILL.md), [Public Sector Business Licenses](pillars/erp/public-sector-business-licenses/SKILL.md), [Public Sector Code Enforcement](pillars/erp/public-sector-code-enforcement/SKILL.md), and [Public Sector Planning and Zoning](pillars/erp/public-sector-planning-and-zoning/SKILL.md). |
| [pillars/hcm](pillars/hcm/) | 457 | [Global Human Resources](pillars/hcm/global-human-resources/SKILL.md), [Global Payroll](pillars/hcm/global-payroll/SKILL.md), [Recruiting](pillars/hcm/recruiting/SKILL.md), [HCM Security](pillars/hcm/hcm-security/SKILL.md), [Benefits Configuration](pillars/hcm/benefits-configuration/SKILL.md), [Compensation](pillars/hcm/compensation/SKILL.md), [Goal Management](pillars/hcm/goal-management/SKILL.md), [Learning Management](pillars/hcm/learning-management/SKILL.md), [Performance Management](pillars/hcm/performance-management/SKILL.md), [Succession Management and Talent Pool](pillars/hcm/succession-management-and-talent-pool/SKILL.md), [Talent Review Setup](pillars/hcm/talent-review-setup/SKILL.md), [Workforce Absence Management](pillars/hcm/workforce-absence-management/SKILL.md), [Workforce Scheduling Management](pillars/hcm/workforce-scheduling-management/SKILL.md), [Workforce Time Management](pillars/hcm/workforce-time-management/SKILL.md), [HCM Communicate](pillars/hcm/hcm-communicate/SKILL.md), and [HCM Tool](pillars/hcm/hcm-tool/SKILL.md). |
| [pillars/scm](pillars/scm/) | 266 | [Manufacturing and Supply Chain Materials Management](pillars/scm/manufacturing-and-supply-chain-materials-management/SKILL.md), [Order Management](pillars/scm/order-management/SKILL.md), [Procurement](pillars/scm/procurement/SKILL.md), [Product Management](pillars/scm/product-management/SKILL.md), and [Supply Chain Planning](pillars/scm/supply-chain-planning/SKILL.md). |

For example, [Product Management](pillars/scm/product-management/SKILL.md) contains [Items](pillars/scm/product-management/items/SKILL.md), which contains focused setup guidance such as [Manage Units of Measure](pillars/scm/product-management/items/manage-units-of-measure/SKILL.md). This hierarchy lets an implementation team move from business scope to the relevant task detail.

### Supporting Reference Domains

| Reference area | When it helps |
| --- | --- |
| [Product guidance](knowledge/product-guidance/) | Find repository guidance for the relevant pillar or offering before researching release-specific product behavior. |
| [Setup-task catalog](knowledge/setup-task-catalog/) | Resolve offering, functional-area, and setup-task identities and catalog metadata. |
| [Validation guidance](knowledge/validation-rules/README.md) | Understand validation stages, prompts, evidence, reports, and current execution boundaries. |
| [Project template](project/_template/) | Understand the standard workspace structure used by project initialization. |

For product behavior, consult the latest available official Oracle Fusion documentation for the specific topic; repository guidance and catalog coverage are separate from release-specific product support.
