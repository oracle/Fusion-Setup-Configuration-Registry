# Manage Formats defaults

Source-backed static guidance; live qualification remains separate.

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| IBY_FORMAT.SeededFlag | N | Customer create | No |  |
| IBY_FORMAT.ShreddingHandledByParser | N | Create with reviewed profile using EO default | No |  |
| IBY_FORMAT.EndDate | 4712-12-31 | Create explicitly reviewed as having no end date | No |  |
| ORA_IBY_VALIDATION_ASSIGN.EndDate | 4712-12-31 | Assignment create explicitly reviewed as having no end date | No |  |

## Default provenance and exclusions

Use the field inventory for exact source IDs. Format StartDate has an EO database-date default, but request and serialize the reviewed business date. Assignment StartDate has no proven default. XDO versus ADFBC is profile-dependent; do not apply XDO universally. The direct-XSLT class and payload type require the reviewed profile. Preserve explicit user input; never synthesize parameter values, languages, format types or templates. No template-generation default installs a file.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| FMT-DEFAULTS | step | 40 | apply_default | pass->FMT-DESIGN;missing->FMT-MISSING | FMT-DEPENDENCIES | stop | Only explicit source-backed defaults whose conditions are met |

