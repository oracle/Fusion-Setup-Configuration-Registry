# Uploaded package compatibility

Use `validate-upload --target-context <selected-target.json>` with the existing
baseline, uploaded package, report and applicable reference evidence arguments.
The target file is a separate workflow input containing:

```json
{"environment": "selected-environment", "release": "<selected-target-release>"}
```

The values are illustrative. Obtain the actual environment and release from the
independently selected workflow target, not the submitted ZIP or saved build
report. Both must be nonblank strings without surrounding whitespace. A caller
using the Python API supplies the same object as `target_context`.

Before row validation, the adapter requires both the fresh baseline and uploaded
ZIP to declare exactly that `ProcessEnv` and `ProcessRelease`. It retains exact
task/package structure and all existing semantic and reference-evidence checks.
Missing selection produces `UPLOAD_TARGET_REQUIRED`; a mismatch produces
`UPLOAD_TARGET_MISMATCH`. CLI failures return exit code 2 and a safe failure
report. The source ZIPs are read without modification; validation does not create
a candidate or import anything.

This local validation path supports matching source/target environments and
releases. It has no independently verified cross-environment or cross-release
migration contract. Such a mismatch therefore stops with a compatibility
diagnostic; there is no boolean override. Route migration through a governed
workflow that establishes compatibility. Do not edit source ZIP metadata to
make it appear compatible.

The adapter does not pin uploaded packages to the descriptor's authoring
`evidenceRelease`. A baseline, package and selected target on a different runtime
release may still pass when the exact task schema and all semantic checks match.
That local result does not certify Oracle support for an arbitrary future release.

For reference-dependent uploads, continue to pass `--reference-context` and the
required reference evidence. A single independently selected JSON file may serve
both target and reference flags if it contains `environment`, `release` and
`baseUrl`. The environment must agree across both contexts; the existing reference
origin and timestamp checks still apply.

Existing callers must now provide the selected target. A matching baseline and
uploaded ZIP alone cannot choose the destination or establish compatibility.
