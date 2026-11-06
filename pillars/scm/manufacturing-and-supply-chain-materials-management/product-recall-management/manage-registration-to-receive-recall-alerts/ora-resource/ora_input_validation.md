# Input Validation

For an import, apply these checks to the selected task and the captured records/native sources returned by the same live Data Loader session at awaiting_task_rules. Do not reread source files, serialize DAT/ZIP before approval, or persist source snapshots or validation previews. Names below are user-facing setup values; map them to REST attributes only after target metadata confirms the mapping. Never persist a client secret or refresh token in a project artifact.

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Import intent | One registration record with a selected mail client and the user-approved values to create or change | Stop before preview | Ask for the intended registration values; do not synthesize credentials or a server key | registrationForRecallAlerts import | |
| Microsoft registration | Accepted third-party terms, Microsoft mail address, Client ID, Tenant ID, and Client Secret supplied through an approved private channel | Stop the affected request | Obtain the values from the authorized email or Azure administrator | New Microsoft registration, or an update whose target contract requires credential replacement | |
| Google registration | Accepted third-party terms, Google mail address, Client ID, Refresh Token, and Client Secret supplied through an approved private channel | Stop the affected request | Obtain the values from the authorized Google administrator; do not substitute a Tenant ID for a Refresh Token | New Google registration, or an update whose target contract requires credential replacement | |
| Validation intent | Existing registration identity and an explicit request to validate credentials | Stop before any REST validation call | Select validateCredentials only for the requested validation operation | Validate registration request | |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Single source root | Count the populated registrationForRecallAlerts root records in the session's captured records/native sources; require exactly one and reject zero or two or more, including multiple captured spreadsheet or DAT root rows | Import preview | |
| Client-specific inputs | Require the documented Microsoft or Google input group for a new registration; for an existing registration validate only the fields required by the verified target operation contract. Reject a missing selected client or an unsupported mixed Microsoft and Google credential set | Import or credential validation | |
| Secret handling | Accept secrets only through an approved private source; reject secrets in tracked files or project artifacts; redact them from previews and diagnostics | Import or credential validation | |
| REST field mapping | Reject unknown or read-only fields after the current target metadata is inspected; do not infer exact REST attribute names from the setup guide's display labels | Import or credential validation | |

## Sources

- [Oracle: Enable Oracle Content Curation Service](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/faims/enable-oracle-content-curation-service.html) documents the task, terms acceptance, client details, email address, and Validate and Save flow.
- [Oracle: Receive Recall Alerts in a Google Email Account](https://docs.oracle.com/en/cloud/saas/readiness/scm/25c/inv25c/25C-inventory-wn-f38628.htm) documents the Google Client ID, Refresh Token, Client Secret, and email address.
- The one-root-record constraint and use of the two named REST business objects are supplied by the task owner in the request; Oracle's public setup guide does not define their REST payload contract.
- [Data Loader host workflow](../../../../../../core/data-loader/SKILL.md#host-workflow) defines captured-source validation and in-memory preview/approval; [Task Hook](../../../../../../core/data-loader/task-hook/SKILL.md) defines the same-session handoff.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| RECALL.REGISTRATION.VALIDATE-INPUT | decision | 10 | validate_input | valid->RECALL.REGISTRATION.LOOKUP-SITE-START-DATE;invalid->RECALL.REGISTRATION.HANDLE-ISSUE | none | stop | A registration import or explicit credential-validation request is made |
