# FSCR Skill Layer Responsibilities

## Purpose

Define the layer-boundary rules used to audit an FSCR skill before merge. Apply
this standard to `router`, `pillar`, `shared`, and `core` skills together with
`governance/skill-design-standards.md`, `governance/review-checklists.md`, and
`schemas/skill-manifest.schema.json`.

This standard is derived from the FSCR layer-responsibility validation draft.
That draft proposes Oracle Journeys as a possible durable execution engine; the
repository must not treat that product choice as final until the architecture
decision is approved. The separation of routing, durable coordination, focused
skill execution, project memory, reusable knowledge, contracts, governance,
and Fusion execution remains applicable regardless of the selected workflow
engine.

## Contents

- Responsibility model and common rules
- Router, pillar, shared, and core audit rules
- Adjacent-layer boundary checks
- Setup sequencing responsibility matrix
- Finding severity and merge decision
- Required audit record

## Responsibility Model

Use this model when classifying a skill:

> The router decides. The durable workflow coordinates. Skills perform.
> Project Memory remembers. Foundation standardizes. Fusion executes.

An audit must assess both:

1. whether the skill contains the responsibilities owned by its declared
   layer; and
2. whether the skill has absorbed responsibilities owned by another layer.

Correct behavior in the wrong layer is a merge-readiness defect.

## Rules That Apply to Every Skill

Every skill must:

- own one focused responsibility;
- use a `SKILL.md` manifest that validates against the current skill-manifest
  schema;
- declare explicit inputs, outputs, dependencies, execution mode, ownership,
  applicability, side effects, privileges, and project persistence where
  relevant;
- expose machine-readable output when it performs planning, validation,
  import, export, verification, generation, or automation;
- declare local preconditions, postconditions, evidence, validation behavior,
  and failure behavior appropriate to its responsibility;
- reuse `shared` methods and `core` primitives instead of copying them;
- keep reusable code and guidance free of customer-specific values,
  cross-project state, credentials, secrets, tokens, private keys, and real
  customer data;
- keep durable customer decisions, execution evidence, and run history in the
  project workspace rather than relying on chat history or skill source;
- use preview, approval, bounded retry, timeout, diagnostic, and redaction
  controls required by its execution mode; and
- provide tests, fixtures, dry-run evidence, or review evidence proportionate
  to its behavior and risk.

## Router Skill Audit Rules

### Purpose

Understand the implementation objective and select the appropriate execution
path.

### Router skills should contain

- intent and objective classification;
- pillar, offering, module, or capability identification;
- scope determination;
- complexity and risk classification;
- selection of the appropriate workflow or Journey template when such a
  durable workflow is part of the approved architecture;
- selection of the next best action when the path is not predetermined;
- rerouting after a decision, failure, or scope change; and
- safe-next-step and stop-condition logic.

### Router skills should not contain

- long-running or authoritative workflow-instance state;
- every setup step for every module;
- HDL, REST, FBDI, FSM, loader, authentication, or transport implementation;
- large amounts of domain-specific configuration knowledge;
- customer artifacts, execution logs, or the only copy of customer decisions;
- duplicated dependency catalogs; or
- direct, ungoverned Fusion mutation logic.

### Router audit evidence

Confirm that the router can state the classified objective, resolved scope,
risk or complexity, selected route, next action, and reason for the route.
Confirm that execution is delegated to focused skills and durable state is
delegated to the approved workflow engine and project workspace.

## Pillar Skill Audit Rules

### Purpose

Provide domain-specific implementation intelligence and focused capabilities
for ERP, HCM, SCM, CX, or common setup.

### Pillar skills should contain

- Fusion business-object and setup-object knowledge;
- setup-specific rules and domain-specific validation;
- pillar-specific design guidance;
- transformation of approved business decisions into setup data;
- local preconditions and postconditions;
- required reference objects and dependency-readiness facts needed locally;
- pillar-specific error interpretation;
- explicit invocation of applicable shared methods and core capabilities; and
- evidence expected from preparation, execution, or validation.

### Pillar skills should not contain

- a complete end-to-end implementation program or all-module workflow;
- generic authentication, token handling, transport, polling, retry, loader,
  parsing, or reporting frameworks;
- customer-specific values embedded in reusable code or guidance;
- cross-project state, raw secrets, or durable customer artifacts;
- a copy of the complete FSM or setup dependency catalog; or
- duplicated shared methodology or core execution plumbing.

Pillar code must use governed core service interfaces rather than importing,
calling or executing private Python helpers from Data Loader, authentication,
FSM or REST clients. A leading underscore identifies a private symbol or
module; standard Python dunder names are excluded. Other internal scripts
require a service-contract determination rather than an inference from their
filename. Unresolved helper origins require semantic review.

### Pillar audit evidence

Confirm catalog-backed placement and naming, generator provenance where
applicable, correct `ora-resource/` placement, source-aligned domain guidance,
local dependency declarations, shared/core delegation, expected evidence, and
task-appropriate golden scenarios. A pillar skill may state what must be true
before it runs, but must not own the entire implementation sequence.

## Shared Skill Audit Rules

### Purpose

Provide implementation methods and patterns reusable across pillars.

### Shared skills should contain

- scope-intake and requirements-extraction methods;
- common planning methods;
- readiness assessments;
- conversion strategy and mapping-template generation;
- common reporting;
- common preflight and post-execution validation patterns;
- export and import patterns that genuinely apply across pillars; and
- reusable evidence-generation patterns.

### Shared skills should not contain

- ERP-, HCM-, SCM-, or CX-specific setup logic;
- raw authentication, API, loader, or transport implementation;
- customer project state or the only copy of project decisions;
- a large end-to-end implementation workflow; or
- separate copies of the same method customized unnecessarily for individual
  pillars.

### Shared audit evidence

Confirm that at least two pillars can use the method without embedding
pillar-specific configuration logic. Confirm that the consuming pillar supplies
domain requirements and that technical execution is delegated to `core`.

## Core Skill Audit Rules

### Purpose

Provide low-level technical primitives for interacting with Oracle Fusion and
operating FSCR.

### Core skills should contain

- authentication and credential validation without credential persistence;
- REST and other Fusion API clients;
- HDL generation and submission primitives;
- FBDI submission primitives;
- FSM import and export primitives;
- file transfer;
- ESS job submission and monitoring;
- polling and bounded standard retries;
- diagnostics, security checks, and environment connectivity;
- generic loaders; and
- logging and telemetry hooks with secret redaction.

A core skill does not need to contain all of these capabilities. It must remain
a focused primitive within this technical responsibility set.

### Core skills should not contain

- customer business decisions;
- ERP, HCM, SCM, or CX design guidance;
- a full implementation workflow or domain-specific sequencing;
- customer-specific setup values or cross-project state;
- customer-facing business approval logic; or
- persisted credentials, secrets, or token contents.

### Core audit evidence

Confirm a stable, domain-neutral input/output contract, bounded execution,
preflight checks, declared side effects and privileges, approval gates for live
mutations, retry and timeout limits, standard diagnostics, external identifiers,
and redaction. The consuming pillar determines what data is valid and why it
should be executed; the core primitive performs the technical mechanism.

## Adjacent-Layer Boundary Checks

Audit every skill for accidental ownership of these non-skill responsibilities.

### Coding-agent experience

The coding-agent experience may collect prompts and documents, ask for
clarification or approval, present plans and status, explain errors, recommend
remediation, and link to artifacts and evidence. A reusable FSCR skill must not
assume that chat is the authoritative workflow state, hard-code all setup
sequences into the conversational layer, store secrets, retain the only copy of
decisions, or perform ungoverned Fusion writes.

### Durable workflow or Journey execution layer

The approved durable workflow engine owns ordered stages, human and automated
tasks, step status, approval and review points, assignment, pause/resume,
decision branches, wait conditions, escalations, timeouts, skill invocation,
failure remediation paths, and evidence gates between steps. It must not absorb
raw HDL or API code, authentication, duplicated pillar logic, the master FSM
catalog, all project artifacts, or customer-intent reasoning.

Oracle Journeys is a proposed engine for this role, not a finalized dependency
unless a current architecture decision says otherwise.

### Project Workspace or Project Memory

The project workspace owns source documents, generated artifacts, customer
decisions and assumptions, decision history, workflow-instance references,
skill-run history, Fusion job identifiers, validation results, baselines,
approved setup data, project status, outstanding clarifications, and traceable
links from source to decision to execution to result. Skills must not persist
these only in source code or chat. The project workspace must not contain
reusable skill code, global standards, the master dependency catalog, secrets,
or silent unexplained overwrites.

### Knowledge layer

The knowledge layer owns reusable facts: the FSM setup-task catalog,
dependencies, sequencing constraints, offering-to-task mappings,
business-object catalogs, reference-data definitions, reusable implementation
patterns, best practices, known limitations, lessons learned, valid execution
mechanisms, and skill-to-task mappings. Skills may consume and reference this
knowledge but must not copy the master catalog. Knowledge must not contain
customer decisions, current workflow status, runtime logs, secrets, executable
API plumbing, approval records, or hard-coded customer values.

### Schema layer

The schema layer owns machine-readable contracts for manifests, inputs,
outputs, project state, decisions, artifact metadata, validation results,
errors, execution results, dependencies, workflow invocation, versioning, and
compatibility. Skill guidance must conform to these contracts rather than
redefining incompatible local versions. Schemas must not become implementation
guidance, executable workflows, customer data, domain logic, secrets, or
unstructured policy.

### Governance layer

Governance owns naming, taxonomy, skill anatomy, ownership, shared-capability
stewardship, review gates, security, documentation, tests and evidence,
versioning, lifecycle, publishing, release control, deprecation, exceptions,
and quality metrics. A skill must comply with governance and must not embed an
alternative release policy. Governance must remain enforceable and must not
contain customer status, individual implementation workflows, Fusion
interaction code, setup data, credentials, or business decisions.

### Oracle Fusion Cloud

Fusion owns actual application configuration, submitted jobs, business data,
Fusion-native security, setup-task execution, application validation results,
and transactional state. Fusion must not be treated as the only store for the
FSCR decision history, implementation evidence, routing model, skill source, or
customer work package. Skills must not enable unapproved changes outside the
governed FSCR process.

## Setup Sequencing Responsibility Matrix

Use this matrix to detect misplaced sequencing logic.

| Question | Responsible layer |
| --- | --- |
| What is the customer trying to accomplish? | Router |
| Which durable workflow should be started? | Router |
| What reusable dependencies exist between setup tasks? | Knowledge / FSM catalog |
| What step is currently active? | Durable workflow engine |
| Who must approve the next step? | Durable workflow engine |
| What must be true before this focused skill can run? | Skill metadata and schema |
| How is the specific business object configured? | Pillar skill |
| How is HDL, API, FBDI, loader, ESS, or FSM technically invoked? | Core skill |
| Where are decisions, artifacts, run history, and evidence retained? | Project workspace |
| What standards must every component follow? | Governance |

Do not put an entire setup sequence into every pillar skill. Knowledge declares
reusable dependency facts; the router determines scope and selects the process;
the workflow engine coordinates the instantiated sequence and human steps;
skills declare local preconditions and perform focused actions; and Project
Memory records what happened.

## Finding Severity and Merge Decision

Classify findings consistently:

- **Blocker**: schema-invalid manifest, secret or customer-data exposure,
  ungoverned live mutation, destructive behavior without approval, unsafe path,
  or a fundamental layer violation that makes execution unsafe.
- **Major**: missing required layer responsibility, duplicated responsibility
  from another layer, missing machine-readable contract, missing validation or
  error-handling controls, incorrect generated pillar structure, or behavior
  that cannot be reviewed reliably.
- **Minor**: bounded documentation, naming, evidence, test, or maintainability
  issue that does not make the skill unsafe or misplace its responsibility.
- **Observation**: non-blocking improvement or external merge-process gate.

A skill is **READY FOR MERGE** only when automated checks pass, no blocker or
major finding remains open, required tests and evidence pass, and the semantic
layer-boundary review is complete. Otherwise it is **NOT READY FOR MERGE**.
Required human reviewers and merge-request approvals remain mandatory even
when the skill package is technically ready.

## Required Audit Record

The audit report must record:

- target path, skill ID, declared layer, type, and execution mode;
- standards and rule profile applied;
- automated commands and results;
- findings with ID, severity, rule, evidence, impact, and remediation;
- checks passed, skipped, or not applicable with reasons;
- security and customer-data result;
- test and validation evidence;
- required human reviewers and external merge gates;
- a binary `READY FOR MERGE` or `NOT READY FOR MERGE` verdict; and
- the exact open blockers or major findings that control a negative verdict.
