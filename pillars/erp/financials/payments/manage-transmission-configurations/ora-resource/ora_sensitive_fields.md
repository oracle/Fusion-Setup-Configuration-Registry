# Sensitive setup: manual completion policy



## Customer interaction

Before collecting setup inputs, say:

> I can configure the non-sensitive transmission settings. Enter passwords,
> client secrets and key files directly in Payments UI. Do not include them
> in this chat or attached documents.

If supplied anyway, omit the fields from the working design and all generated
artifacts; identify the excluded **field names**, never quote their values.
The runtime also removes blocked value operations during normalization. Do not
copy a raw attachment/chat message into a project request/design file first.
Use a sanitized requirements summary as `--request`. The task cannot remove
values already entered into chat or the user's original document.

Show `manualSteps` in the approval preview and completion summary. A
`MANUAL_ONLY` result means no import ZIP was produced. A successful non-sensitive
import does not mean credential setup or bank connectivity is complete.

## Field policy and developer changes

[`sensitive-field-policy.json`](sensitive-field-policy.json) is the sole
developer-owned policy. It contains reviewed seed required/secured metadata and
protocol/parameter datatypes from the reviewed FSM metadata export. The export
does **not** include `SecuredFlag` or `MandatoryFlag`. This mapping is version
qualified, not proof of target customization. Unknown parameters are deferred;
missing target identity and changed known datatypes are validation errors.

Database-secured parameters, semantic password/secret fields (including those
not secured in seed), and key-registration references are manual. The imported
value row is **omitted**, not blanked or replaced with a redaction marker.
Existing credentials must not be cleared or copied back into an import.

Only `SECURE_FTP_GET.USERNAME` and `SECURE_FTP_PUT.USERNAME` have a create
placeholder: `changeit`. It is generated only when the same design creates a
configuration absent from the target baseline. A supplied username is excluded.
The preview and completion report must say:

> SFTP Username will be/was initialized with the placeholder `changeit`.
> Replace it and complete authentication in Manage Transmission Configurations
> before using this configuration.

This placeholder is an actual stored string, not an inactive/draft control.
Do not claim it prevents transmission. Do not connect, transmit, or enable
automatic use as part of this task. Passwords and key setup remain manual.
Other mandatory sensitive fields stop creation with `MTC-MANUAL-REQUIRED`;
complete the prerequisite through UI and take a fresh sanitized baseline.

`ordinaryImportExceptions` is initially empty. Developers may add an exact
protocol/parameter pair for a reviewed ordinary identifier, even if
database-secured. It never turns off export redaction. Semantic secrets and
key references cannot use this ordinary exception mechanism. Supporting real
secrets requires the future approved secure framework. No chat, document,
blueprint, environment variable or runtime CLI flag can change this policy.
Policy changes invalidate old blueprints; normalize and approve a new package.
Requalify the metadata on a supported product revision before expanding scope.

## Export boundary

Use the existing governed task-export route for task discovery, authorization,
and export-job creation. For MTC, replace its raw download/write step with the
task's [`sanitize_export.py`](../scripts/sanitize_export.py), which calls the
same shared export engine and core authentication. Do not run the ordinary
one-shot export command that writes the raw package to `project/`.

```text
python <task>/scripts/sanitize_export.py --process-id <approved-export-id> \
  --properties <existing-properties-file> --token-cache <existing-token-cache> \
  --output <project-baseline-path>/mtc-sanitized.zip
```

The helper does not create export jobs, import, register keys, or transmit.
It uses the already-authorized process ID, reads returned bytes in memory, and
writes only a sanitized exact-shape ZIP plus `.sanitization.json` evidence.
Use `--template-only` for a template process. A user-supplied local export may
be sanitized with `--input <path> --output <new-path>`; the original is untouched.
Do not copy the original into the project. Process-log/HTTP error payloads are
not printed or saved by this helper; inspect failures through the governed UI.
Core authentication token-cache handling remains owned by the core skill.

Secured/unknown values are replaced with `[FSCR value withheld]` in **baseline
snapshots only**. The exact public `changeit` username sentinel is retained to
verify placeholder persistence. It is the only placeholder exception; ordinary
customer usernames remain redacted. These snapshots are not import packages.
Artifact provenance distinguishes original archive hash from sanitized hash;
blueprints bind to the sanitized baseline hash and policy hash.

## Import, comparison and key prerequisites

Normalize before building, then independently validate the exact candidate ZIP
before existing Run Book / Data Loader approval and submission. All blocked
parameter-value rows are rejected, including empty/masked rows and unchanged
credential copies. The two approved **new-configuration** username rows are
the sole placeholder exception. Rollback obeys the same policy.

Compare requested ordinary setup values normally; report parameter comparisons
without their values. Compare the generated username placeholder against its
known literal. Do not interpret equal redaction markers as credential equality:
reports explicitly say `credentialPreservation: NOT_VERIFIED`. Existing
sensitive fields are excluded from the credential-value preservation check,
while row existence and non-sensitive fields remain checked. No raw secrets or
per-secret hashes are retained between commands.

Configuration DML can inspect existing crypto references even on an ordinary
update. Preserve this prerequisite check. For a withheld existing reference,
the baseline-bound `MTC-CREDENTIAL-DML` prerequisite must record the exact
configuration, parameter, credential type, UI evidence and
`noRegistrationVerifiedInUI: true`, with `resolution: existing-type-and-alias`.
Do not record the private key, password, or withheld alias. If existing-key
presence/no-registration cannot be established, defer that configuration's
update to UI. Intentional UCM key registration is not an FSCR completion path.
