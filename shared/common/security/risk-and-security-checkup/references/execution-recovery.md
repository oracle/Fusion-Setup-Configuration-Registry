# Execution recovery in FSCR

Distinguish failure to start a local process from a process that started and
failed. For a startup error, use bounded harmless workspace probes through the
authorized execution tool. Never bypass a denied permission or change execution
routes to obtain credentials.

For missing `environment` or `restBaseUrl`, unreadable selected properties, or
an environment mismatch, correct the active FSCR profile through
[onboarding guidance](../../../../../core/getting-started/onboarding/SKILL.md).
Do not ask for a checkup-specific host or application username. Never dump the
properties file, OAuth cache, or token contents in diagnostics.

For a fresh ZIP normalization, use `run_from_zip.py --zip <source.zip>
--output-directory <project-request-directory> --normalize-only`. It includes
all submitted roles/categories and obtains environment provenance from FSCR.
Preserve source and completed artifacts, and use a new directory for changed
input. Do not restart a running assessment simply because output is absent.

`awaiting_core_responses` with exit code `2` means a normal internal handoff.
Execute the prepared GET requests through the selected Core REST skill and
resume with all saved current-run Core results. Preserve the request directory,
request ID, selected profile, and earlier response files during continuation.
A new assessment uses a new directory and new delegated evidence.

On a failed Core result, follow Core authentication and recovery guidance.
The planner never retries HTTP or refreshes a token. Do not alter the response
status, use stale data, or bypass a missing scope or privilege. A terminal
password handoff, manual bearer token, or personal skill is not a recovery route.
Do not repeatedly resubmit a known failed response: resolve its underlying Core
failure and preserve the old diagnostic before providing fresh same-run evidence.

Verify the actual process result and matching assessment/tree/rule/summary
artifacts before reporting findings. A user reply such as "done" or successful
normalization alone does not prove an assessment completed. Never present clean
risk coverage after extraction failure.
