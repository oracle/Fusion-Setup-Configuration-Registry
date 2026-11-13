# Sales Orchestration Prerequisite Readiness

## Purpose

Use this reference only for functional prerequisite readiness for Sales
Orchestration. Do not duplicate task-specific guidance owned by the Sales
Motions, Sales Plays and Content, or Data Capture Rules skills.

## Baseline Readiness

The Oracle playbook assumes that the main Oracle Sales features are already
configured. Beyond that baseline, confirm these functional prerequisites:

- Configure the Dispatcher Service to route users to the Sales Orchestration
  pages.
- Configure Oracle Knowledge Management content management so sales enablement
  content is available in the customer environment.
- Configure supported web-conferencing applications, such as Microsoft Teams
  and Zoom, when meetings and conference interactions must be captured and
  summarized for sellers.
- Configure Microsoft Exchange integration when email and calendar
  synchronization is required.

Without the Microsoft email integration, users must log email engagements
manually with **Log an Interaction**, and appointment and calendaring
functionality is unavailable.

## First-Time Environment Validation

Complete these checks before treating a target environment as ready for the
first Sales Orchestration rollout. They are validation requirements, not an
authorization to create, enable, or change any environment resource.

### Signals

Confirm that every required signal definition exists and has `ActiveFlag` set
to `true`:

| Required signal |
|---|
| `ORA_ENGMT_INSIGHTS__Opportunity__ConversationMessage__Create` |
| `ORA_ENGMT_INSIGHTS__Opportunity__ConversationMessage__Update` |
| `ORA_ENGMT_INSIGHTS__Opportunity__ConversationReference__Create` |
| `ORA_ENGMT_INSIGHTS__Opportunity__Create` |
| `ORA_ENGMT_INSIGHTS__Opportunity__Interaction__Update` |
| `ORA_ENGMT_INSIGHTS__Opportunity__WrapUpAttachment__Create` |
| `ORA_ENGMT_INSIGHTS__Opportunity__WrapUp__Create` |
| `ORA_ENGMT_INSIGHTS__Opportunity__WrapUp__Update` |

When the active workflow authorizes a read, validate one exact signal at a
time with the target environment's `crmRestApi` signal-definitions collection,
using an exact `SignalName` filter and a bound of one. A missing record or an
`ActiveFlag` other than `true` is a prerequisite failure requiring manual
environment configuration; do not create or enable the signal from this skill.

Use this read-only URL template, replacing `{{HostName}}` and `{{SignalName}}`:

```
https://{{HostName}}/crmRestApi/resources/latest/signalDefinitions?limit=1&q=(SignalName='{{SignalName}}')
```

For example, `{{SignalName}}` can be
`ORA_ENGMT_INSIGHTS__Opportunity__ConversationMessage__Create`. A matching
response with `ActiveFlag: true` passes; no matching item or any other value
fails.

#### Signal Remediation Boundary

For a missing or inactive required signal, hand off to an authorized
environment administrator. The administrator must resolve signal IDs in the
target environment, review the exact set of required signals for the target
release, obtain explicit approval immediately before the change, set the
required signal definitions to `ActiveFlag: true`, and rerun this validation.
Do not reuse signal IDs from another environment and do not activate only a
subset because an older procedure lists fewer signals. This skill documents
the remediation sequence and a supplied request shape, but does not execute
the mutation.

#### Approved Activation Request Shape

After an authorized administrator has resolved the **target environment's**
signal-definition ID and obtained explicit approval immediately before the
change, the activation request is:

```http
PATCH https://{{HostName}}/crmRestApi/resources/latest/signalDefinitions/{{SignalDefinitionId}}
Content-Type: application/json

{
  "ActiveFlag": true
}
```

`{{SignalDefinitionId}}` must come from the preceding exact-name GET in the
same environment. Do not copy an ID between environments. The screenshot
source shows `{ "ActiveFlag": false }`, which is a deactivation example; use
`true` only to activate an inactive target signal. Rerun the exact-name GET
after the PATCH and confirm `ActiveFlag: true`. Do not retry a failed PATCH
without checking the response and obtaining fresh approval when needed.

### Microsoft Outlook and Email Integration

Validate these layers without exposing or persisting application IDs, keys, or
client-secret values:

| Layer | Readiness condition |
|---|---|
| Email Integration service record | An active record has `EmailIntegrationActiveFlag: true` and `IsActive: "Y"`. |
| Outlook Integration service record | An active record has a non-null `MsDomainName` and `IsActive: "Y"`. |
| Microsoft 365 setup UI | The Email Integration application ID, application key, integration address, and keyword are populated; the Outlook add-in registration has an application ID, client-secret value, and primary Microsoft domain. Validate presence only. |
| Profile options | `ORA_ZCA_DS_EMAIL_OPTIONS` is `MS Exchange Office365 UI`; `ORA_ZCA_ENABLE_EMAILAI_OUTLOOK` is `Yes`. |
| Scheduled processing | **Microsoft Exchange Email Sync Job** appears in Scheduled Processes. |

The Email and Outlook service values can occur in separate `zpsApps` response
items. Do not require all conditions to occur in one item. A live service-read,
when selected by the active workflow, uses the target environment's
`crmRestApi/resources/latest/zpsApps` collection:

```
https://{{HostName}}/crmRestApi/resources/latest/zpsApps
```

If any condition fails,
record the failed check and route the remediation to the owning Microsoft 365
or Outlook integration setup process; do not change the integration from this
skill.

#### Microsoft 365 and Outlook UI Checklist

Validate presence only; never include an application key or client secret in
an artifact or response.

1. In **Setup and Maintenance**, open **Manage Microsoft 365**, then the
   **Email Integration** tab. Confirm values for **Application ID**,
   **Application Key**, **Email Integration Address**, and **Email Integration
   Keyword**.
2. In **App Composer**, open **Productivity Applications Configuration**, then
   **Oracle Sales for Outlook**. Select **Accept** when that option is enabled;
   on **Add-In Registration**, confirm **Application (client) ID**, **Client
   Secret value**, and **Primary Microsoft Domain** are present.
3. In **Setup and Maintenance**, open **Manage Administrator Profile Values**
   and validate `ORA_ZCA_DS_EMAIL_OPTIONS = MS Exchange Office365 UI` and
   `ORA_ZCA_ENABLE_EMAILAI_OUTLOOK = Yes`.
4. In **Tools > Scheduled Processes**, confirm **Microsoft Exchange Email Sync
   Job** appears.

The Email Integration and Outlook Integration Azure applications must exist
before performing this checklist.

### Dispatcher Routing

Validate that the target environment has a Dispatcher rule whose name or
content contains `opportunities-insights`. When the active workflow authorizes
a read, inspect the target environment's
`crmRestApi/cxfRestApi/latest/dispatcherrules` collection:

```
https://{{HostName}}/crmRestApi/cxfRestApi/latest/dispatcherrules
```

If no such rule is
found, treat Dispatcher routing as incomplete and route configuration to the
documented Dispatcher setup process; do not create or change a rule from this
skill.

## Access Boundary

The public playbook states that salespeople do not need new permissions merely
to start using Sales Orchestration because their existing access covers the
relevant seller capabilities. Administrator and product-expert access for
task-specific setup is owned by the corresponding nested task skill; do not
restate those roles, privileges, permission groups, or data-security policies
here.

## Task-Specific Routing

Route the request without adding task-specific setup details:

| Request subject | Owning skill |
|---|---|
| Sales Motion setup, security, or access | `cx.sales.sales-orchestration.sales-motions` |
| Sales Play, content, Knowledge access, or Content Intelligence | `cx.sales.sales-orchestration.sales-plays-and-content` |
| Data Capture Rule setup, attributes, security, or access | `cx.sales.sales-orchestration.data-capture-rules` |

For a question spanning more than one task, route to
`cx.sales.sales-orchestration` for cross-task synthesis.

## Source and Scope Boundary

- Oracle Fusion Cloud Sales, *Prerequisite Setup for Sales Orchestration*:
  https://docs.oracle.com/en/cloud/saas/sales/gsaso/prerequisite-setup-for-sales-orchestration.html
- Source accessed: 2026-08-10.
- The Oracle page is published under the `latest` documentation path. Recheck
  the page when answering release-sensitive questions.
- Environment setup and validation guidance supplied 2026-08-25 covers
  first-time signals, validation URL templates, Outlook/email UI and service
  checks, and Dispatcher validation.
- Screenshot source supplied 2026-08-25: `PATCH` target-record shape for
  `/crmRestApi/resources/latest/signalDefinitions/{{SignalDefinitionId}}` and
  the `ActiveFlag` body field. The supplied `false` body is documented above as
  a deactivation example; the activation example uses `true`.
- Signal-activation guidance supplied 2026-08-25 is normalized above as a
  manual, approval-gated remediation sequence.
- This local reference is self-contained for the supported prerequisite
  explanation, validation, and remediation guidance.
- This reference summarizes readiness; it does not authorize browser changes,
  setup mutations, ESS jobs, or external API calls.
