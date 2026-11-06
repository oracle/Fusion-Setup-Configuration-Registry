---
task_code: "ORA_MANAGE_ADDRESS_VERIFICATION_CLOUD_TO_CX_CLOUD_INTEGRATION"
task_name: "Manage Integration with Oracle Verification Services"
parent_skill_id: "scm.procurement.suppliers"
pillar: "SCM"
offering: "Procurement"
functional_area: "Suppliers"
functional_area_code: "ORA_EGP_SUPPLIERS"
available_flag: "Y"
export_import_supported_flag: "N"
csv_export_import_supported_flag: "N"
businessObject: ""
source_catalog: "knowledge/setup-task-catalog/effective/setupTasksAll.json"
---

# Manage Integration with Oracle Verification Services

**Manual task — guidance only.** State this up front. The user makes approved
changes in Fusion; no automated export/import, API calls, or browser actions.
Catalog flags and generated loader metadata do not authorize automation.

- Task code: `ORA_MANAGE_ADDRESS_VERIFICATION_CLOUD_TO_CX_CLOUD_INTEGRATION`
- Purpose: Connect the subscribed Oracle Verification service to Fusion. For Procurement, the documented integration provides address autocomplete; do not assume all Sales verification features apply.

Use [shared.common.manual-tasks](../../../../shared/common/manual-tasks/SKILL.md)
for the manual workflow.

Give navigation, task-specific steps, and validation directly. Reuse supplied
context; clarify only an ambiguous task or scope. Do not request configuration
values, credentials, or completion confirmation in chat. The implementer obtains
missing approved values from the administrator and enters them in Fusion.
Do not invent defaults or create separate guides to repeat these steps.

## Access the task

1. Sign in to the intended Fusion environment with access to Setup and Maintenance and this task.
2. Open **Navigator** > **Setup and Maintenance** > **Setup: Procurement** > **Suppliers**, set **Show** to **All Tasks**, and open **Manage Integration with Oracle Verification Services**. Alternatively, use **Search Tasks** or the **Tasks** panel search for the exact name and select **Go to Task**.
3. If access or expected controls are unavailable, consult the setup or security administrator. Follow the target release's Oracle documentation when labels differ; do not substitute another task or automated route.

## Manual steps

1. Confirm with the service administrator that the required subscription, active service instance, application access, and OAuth client are already available. This task does not purchase a subscription or create credentials.
2. Review the existing integration. Select **OAuth Authentication** and enter the administrator-provided service URL and client details directly in Fusion. Use the service instance address, removing the trailing `/data/ui` when present; do not substitute the Fusion pod URL.
3. Preserve unrelated integration settings. If the service, credentials, or expected controls are unavailable, resolve them with the service or security administrator before saving.
4. Save the approved integration changes using the controls available in the target release.

## Manual validation

Reopen the integration and verify the intended service and authentication method without displaying credentials. Where authorized, test address autocomplete using safe data in an applicable Procurement flow. Distinguish a saved connection from a successful service test; record a deferred test when the service or feature is unavailable. Retain the target environment, implementer, approved change reference, and expected versus actual result in implementation evidence; exclude credentials and sensitive payloads.

## Sources

- [Integrate with Oracle Sales or Procurement](https://docs.oracle.com/en/cloud/saas/address-verify-cloud/csads/integrate-with-oracle-sales-or-procurement.html)
- [Configure Oracle Address, Email, and Phone Verification](https://docs.oracle.com/en/cloud/saas/customer-data-management/fagcd/configure-oracle-address-email-and-phone-verification.html)
