---
skill_id: "core.project-mgmt.artifact-registry-manager"
name: "Artifact Registry Manager"
description: "Registers generated skill outputs in the project artifact index and maps each artifact to the skill that produced it."
layer: "core"
pillar: "Core"
type: "import"
execution_mode: "hybrid"
owner_team: "Central platform team"
version: "0.2.0"
inputs:
  - "artifact_metadata"
  - "skill_id"
  - "artifact_location"
  - "project_root_for_artifact_path_preflight"
outputs:
  - "artifact_record"
  - "updated_artifact_index"
  - "validated_artifact_destination"
uses_core: []
persists_project_state: true
state_updates:
  - "skill_path"
workspace_outputs:
  - artifact_type: "other"
    default_location: "project/{project_id}/artifacts/artifact-index.json"
    versioning_policy: "replace-after-confirmation"
applicability:
  industries:
    - "All"
  countries:
    - "All"
  fusion_releases:
    - "Current Oracle Fusion Cloud release"
side_effects:
  - "Updates the local project artifact index."
required_privileges: []
---

# Artifact Registry Manager

## Purpose

Registers generated skill outputs in the project artifact index and maps each artifact to the skill that produced it.

## When to Use

Use this skill after any skill writes an output artifact under `project/{project_id}/artifacts`, `project/{project_id}/baselines`, `project/{project_id}/exports`, `project/{project_id}/decisions`, or `project/{project_id}/blueprints`.

## Inputs

- `artifact_metadata`
- `skill_id`
- `artifact_location`

## Outputs

- `artifact_record`
- `updated_artifact_index`

## Implementation Notes

Every artifact record must include artifact type, producing skill, location, version, status, timestamps, and checksum when available.

## Artifact path preflight

Use `scripts/project_artifact_paths.py` before writing a new artifact. Its
`validate_artifact_path(destination, project_root)` function requires an explicit
initialized `project/{project_id}` in this repository and a new descendant of
that project's `artifacts/` directory. It rejects `_template`, absent/invalid
project state, other projects, traversal, existing outputs, symlinks (including
dangling links) and symlinked ancestors. It never creates the project or changes
files; revalidate immediately before persistence. Export destinations remain
owned by the corresponding export service, not this artifact validator.

The validation-only CLI accepts `--project-root` and `--output`; every run is
read-only. It returns zero on a valid destination and 2 for input validation
failure. No retries, Fusion requests, privileges or approval are needed for
this pure local check. Do not expose file contents or raw project state in
diagnostics. A successful preflight grants no overwrite or Fusion authority;
the producer still owns persistence, diagnostics and index registration.

## Error handling and redaction

Reject missing/uninitialized projects, unsafe paths and existing destinations as
input validation failures before any producer writes. Do not retry an invalid
destination or silently choose another project. The validator is synchronous,
reads bounded local project-state JSON, and has no network, polling, timeout
recovery or rollback step. Report a safe stage, failure class and corrective
action; the CLI returns 2 without dumping raw state or filesystem exceptions.

Redact credentials, secrets, tokens, token-cache contents, private keys and
sensitive customer values from diagnostic excerpts. Never copy raw project-state
or artifact payloads into diagnostics. Artifact producers retain responsibility
for write failures, their project-local durable diagnostic/run records, and
registration of successful outputs. A failed index update is an artifact
persistence failure, not permission to overwrite or repeat a Fusion action.
Replacing an existing registered artifact/index remains subject to the version
manager and its required user confirmation.
