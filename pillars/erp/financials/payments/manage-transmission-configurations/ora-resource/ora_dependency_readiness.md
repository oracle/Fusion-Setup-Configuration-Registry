# Transmission dependency readiness



Task: IBY_MANAGE_TRANSMISSION_CONFIGURATIONS — Manage Transmission Configurations.

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Target protocol | Resolve existing protocol and its parameter definitions |
| 2 | Target references | Verify requested tunnel and conditional security/OAuth references |
| 3 | Configuration | Establish exact create/update identity and parent context |
| 4 | Values and translations | Validate children against that configuration and its protocol |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|
| MTC-PROTOCOL | Existing protocol | Yes | Always | Lookup | Fresh target export | resolve_transmission_protocol | Protocol defines parameter contract | Select bank-supported target protocol | Protocol code/name |
| MTC-PARAMETER | Existing parameter | Yes | Parameter supplied | Lookup | Fresh target export | resolve_transmission_parameter | Parameters are protocol-specific | Use exact parameter code | Type and dynamic metadata |
| MTC-TUNNEL | Target tunneling configuration | Conditional | Tunnel requested | Lookup | Fresh target export | find_transmission_tunnel | Import maps name to target ID | Select existing target tunnel | Tunnel name |
| MTC-SECURITY | Credential and OAuth identity | Conditional | Credential parameter supplied or crypto configuration touched | Verify | Target credential state and source-confirmed configuration DML | resolve_parameter_value_contract | Configuration DML can register missing keys from UCM; exported paths may be nonportable | Verify existing credentials through UI without retaining values; key registration remains manual; OAuth mapping remains separately unresolved | Verified reference and declared registration side effects |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Satisfied | Exact target identity and supported metadata are verified | Read-only lookup only |
| Missing | Required dependency absent | Complete credential/key prerequisites manually in Payments UI; no FSCR import of credential values or intentional UCM key registration |
| Ambiguous | More than one exact match or inconsistent context | No package build |
| Blocked | Unsupported or unresolved conditional reference | No affected execution |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MTC.DEPENDENCY | step | 30 | resolve_dependency | success->MTC.DEFAULT;failure->MTC.ERROR | MTC.INPUT | stop | Always |

## Evidence

- FSM name resolution (reviewed implementation evidence).
- [Credential prerequisite and assignment](https://docs.oracle.com/en/cloud/saas/financials/26c/fairp/import-a-security-credential-file.html).

- Configuration DML and credential registration (reviewed implementation evidence) — existing-key check, UCM fetch, password/file checks and conditional deletion.
- Credential utility (reviewed implementation evidence) — type/name existence, materialization and legacy-path side effects.

## Sensitive setup boundary

Apply [the sensitive-field policy](ora_sensitive_fields.md) before these checks. Credential import and intentional key registration are manual; only the explicit SFTP create username placeholder is permitted.
