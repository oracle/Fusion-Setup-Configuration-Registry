# Service Providers FSM Export and Import Prerequisites

These prerequisites extend the existing task-CSV export and import checks. Create/update orchestration and package preparation are owned by SKILL.md;
these read-only prerequisite rules do not alter a ZIP or require another CMK
task to have completed first. Package shape, provenance, and target binding remain owned
by ora_input_validation.md; upload approval remains with core.data-loader.

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Exact environment identity | Bind the export source or import destination to the configured Fusion host |
| 2 | Simplified B2B opt-in | Automatically call `verify_cmksp_b2b_document_setup_enabled` through `core.fusion-api.rest-api-client` on that same host and require `EnabledFlag: Y` before export POST or during import preapproval Task Hook validation; do not ask the user for the feature state |
| 3 | Existing input contract | For import, validate the immutable task ZIP and target binding |
| 4 | Dependency decision | Stop on missing, failed, stale, cross-environment, or ambiguous evidence |
| 5 | Existing execution gate | Continue to export-process creation or Data Loader approval only after all prerequisites pass |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| cmksp_b2b_document_setup_enabled | Simplify Configuration and Processing for B2B Messaging (`ORA_CMK_B2B_DOCUMENT_SETUP`) | Yes | Before template export, populated task-data export, and task-CSV import | Verify | Fresh filtered Fusion Features collection read automatically from the operation's exact source or target host through `core.fusion-api.rest-api-client` | verify_cmksp_b2b_document_setup_enabled | Oracle's 26C Collaboration Messaging migration procedure places export and import after this feature is enabled | If disabled, enable the feature through its separate approved opt-in workflow, then retry; do not ask the user to verify state or enable it as part of export or import | Exact FeatureCode and EnabledFlag Y, environment host, read time |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Satisfied | Every applicable check has authoritative evidence, including current same-target opt-in state | No |
| Verify | A complete approved resolver is available and evidence must be retrieved | Read-only lookup only |
| Blocked | The opt-in check fails, or required environment or input evidence is missing, stale, cross-environment, or ambiguous | No |

## Scope Boundaries

The [all-object migration workflow](https://docs.oracle.com/en/cloud/saas/readiness/scm/26c/sccv26c/26C-sccv-wn-f46531.htm)
includes both Service Providers and Simplified Configuration in its project.
That package-scope requirement does not establish a universal prior-task
completion requirement for this standalone task-CSV import. Do not reuse the
legacy trading-partner CSV import's provider/message prerequisites here.

Oracle's 26C procedure supports the opt-in prerequisite for the documented
Collaboration Messaging migration flow. Applying the same gate to the
standalone task-CSV template and data exporter is an FSCR fail-closed policy,
not an Oracle claim that the REST endpoint rejects exports when disabled.

The shared Core REST client performs this read-only check before the task
workflow reaches either shared CLI. The shared export CLI and Data Loader do
not call it automatically, so direct generic CLI use is not a verified Service
Providers workflow.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| CMKSP.CHECK_DEPENDENCIES | decision | 18 | resolve_dependency | ready->CMKSP.ENFORCE_CHANGES;blocked->RETURN_ISSUES | CMKSP.VERIFY_DELIVERY_IMPORT_TYPE | stop | Before task-CSV import approval |

## Sources

- [Oracle FSM 26C](https://docs.oracle.com/en/cloud/saas/applications-common/26c/oafsm/using-functional-setup-manager.pdf), printed pages 41 and 75–79.
- [Legacy CMK import scope](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/facmm/overview-of-importing-collaboration-messaging-setup-data.html).
- [Oracle 26C Collaboration Messaging export and import readiness](https://docs.oracle.com/en/cloud/saas/readiness/scm/26c/sccv26c/26C-sccv-wn-f46531.htm).
- [Oracle 26B CMK view showing `ORA_CMK_B2B_DOCUMENT_SETUP` in the feature-enable test](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26b/oedsc/cmkapplpartnerssetupvl-3023.html).
