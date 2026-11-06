# Knowledge Assets

The `knowledge` area stores reusable implementation intelligence that can be consumed by router, shared, core, and pillar skills.

## Knowledge Areas

| Area | Purpose |
| --- | --- |
| `oracle-reference-models` | Oracle-aligned process and implementation reference models. |
| `fusion-audit-metadata` | Fusion Audit Setup application/product metadata used by audit setup tooling. |
| `setup-task-catalog` | Offering, functional area, and task catalogs. Release catalogs are in `release/`; `pre_release/` holds additions and `removals`; `custom/` holds local extensions. Management scripts and release provenance metadata live in `core/fusion-dev/catalog-management/`; the static hierarchy browser stays here. Consumers resolve `effective/`, composed as `release - pre_release.removals + pre_release.items + custom.items`. |
| `dependency-graphs` | Cross-task, cross-functional-area, and cross-pillar dependencies. |
| `product-guidance` | Oracle product implementation guidance and offering-level reference documentation. |
| [`validation-rules`](validation-rules/README.md) | First reference for FSCR validation questions: FAQ, prompts, evidence, reports, ownership and links to executable contracts. |
| `data-mapping-templates` | Reusable conversion and mapping templates. |
| `reusable-prompts` | Prompt fragments and reusable guidance patterns. |
