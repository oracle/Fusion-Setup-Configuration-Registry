# Design Enforcement

## Import Controls

Route every import only through `core.data-loader`. Require its immutable
approval preview and its Task Hook validation envelope bound to the archive
SHA-256. Do not use a direct FSM API, UCM upload, REST utility, browser action,
or reconstructed approval envelope.

The export can contain role hierarchy and privilege-membership data. Do not
claim that import is safe until the target environment, exact task identity,
archive hash, Data Loader validation, same-environment confirmation when
applicable, and separate immediate upload approval are all present.

## Optional assessment before import preview

Within `MJR.DESIGN_GATE`, follow the optional Risk and Security Checkup section
of the owning `SKILL.md` after archive validation and before the Data Loader
handoff. Wait for an explicit choice unless already supplied for this candidate
and target. A decline records **Security checkup: Not performed** and continues
without requiring assessment privileges. An opt-in delegates to
`shared.common.security.risk-and-security-checkup`; present the completed
findings and coverage gaps before passing this gate. Pending, failed or blocked
assessments cannot silently pass: resolve the issue or obtain an explicit
decline. Changed candidates repeat validation and the choice checkpoint.
Assessment consent is separate from Data Loader's single import approval.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
| --- | --- | ---: | --- | --- | --- | --- | --- |
| MJR.DESIGN_GATE | decision | 3 | design_enforcement | pass->MJR.EXECUTION_GATE; fail->MJR.BLOCKED | MJR.DEPENDENCY | stop | After archive validation; resolve the optional checkup choice and outcome before the Data Loader handoff. |
