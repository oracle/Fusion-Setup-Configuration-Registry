# Implementation candidates and conformance review

Default objective: `implementation_candidate`. Generate the most complete useful template that the provider specification and bundled Oracle contracts/patterns support. Deliver the actual file for implementation testing, even when some mappings need confirmation. `strict_conformance` is a review objective: identify what prevents meeting the supplied specification; it does not confer bank certification. Record the selected objective.

Before coding, distinguish confirmed mappings, evidenced assumptions, missing setup, omitted optional fields, and unresolved critical behavior in the mapping matrix. Common-profile mappings and bundled seed patterns can support a provisional design; explain their relevance and do not present them as confirmed requirements for a different provider/profile. A seed is implementation knowledge, not authority to override a conflicting bank requirement.

## Generation decisions

- Implement confirmed mappings and test them.
- For a reasonable common-profile inference, implement a provisional mapping with its basis, impact and confirmation/test requirement. Do not stop solely because the bank has not yet confirmed every inference.
- Omit unresolved optional fields and record the omission. Do not omit schema-required fields and then claim schema validity.
- For missing setup or critical bindings (recipient, amount, currency, correlation, processing status), prefer explicit configuration or a supported branch whose missing prerequisites terminate with a useful diagnostic. Generate the supported code; reject the affected execution path when the required value/binding is unresolved. Never silently invent identifiers, financial values, acceptance statuses or truncation rules.
- Keep provisional configuration and synthetic demonstration values visibly separate from production defaults. If execution requires enabling an assumption, document exactly which assumption and how the intended runtime supplies that setting. Do not use an impossible-to-bind parameter as a claim of deployment readiness.
- If meaningful transformation logic cannot be established, still deliver a clearly labelled partial scaffold where useful, with unsupported branches identified. Do not call that scaffold a runnable or schema-valid payment template.

An unresolved required correlation mapping prevents claiming that mapping verified or emitting silently guessed identifiers; it does not prohibit writing a candidate template. Prefer full identifiers within evidenced limits. If shortening is proposed, document the evidence and check collisions on the resulting values; a single successful example does not establish general uniqueness. Verify duplicate and missing identifiers, grouping and totals, not just XML shape.

## Preserve contract-supported behavior

When comparing supplied monetary totals with derived totals, validate the supplied value's cardinality, decimal syntax, sign and permitted scale before numeric comparison. Do not round away a discrepancy or silently coerce malformed input. Use consistent decimal/minor-unit arithmetic within the processor's supported precision. Aggregate totals may exceed a single-payment limit; do not reuse that limit for an aggregate. Preserve output amounts and rounding rules already established by the contract.

For timestamps, preserve valid source values supported by the target contract, including timezone offsets where allowed. Do not impose a Z-only restriction without evidence, strip offsets, or convert timezones implicitly. Retain stricter provider constraints when documented; record any deliberately unsupported forms.

Distinguish required source/provider fields from optional ones. Where gross/discount fields are evidenced optional, validate paid amounts and reconciliation without inventing missing values; check gross-minus-discount relationships when applicable values exist. Do not infer optionality for one provider from an ISO schema or another provider. Unknown requiredness remains a documented scope decision, not a universal relaxation.

Apply [candidate-regression-cases.md](candidate-regression-cases.md) to the affected profile when changing these behaviors. Preserve previous positive outputs and existing negative checks except for explicitly reviewed expectation changes. These are scoped generation/review rules, not an instruction to retrofit or rewrite proven seed templates.

## Validation and delivery

Run compile, representative transforms, applicable XSD and known business-rule checks on the implemented portions. Test positive configured paths and rejection paths (missing critical configuration, malformed/duplicate correlation, invalid amounts/currency where applicable). Use source-derived masked/synthetic samples when customer samples are absent. A skipped check is `not_run`, not a pass. Record which assumptions and test-only settings each passing sample used. Schema validity does not establish bank acceptance.

Deliver the template, mapping/assumptions/gap report, actual validation results, and concrete implementation-test instructions. A material assumption or gap must always be disclosed; the report can be concise. A candidate with unconfirmed mappings is `draft` even when compilation and schema checks pass. Draft describes readiness, not poor quality or absence of a file. Confirmed mappings and offline tests retain their individual results. Customer implementation testing and bank acceptance remain separate.

Use this policy to interpret the retained engine workflows: source tracing, mapping matrices, PCI controls and tests still apply; blanket rules that previously prevented artifact creation for unresolved mappings now gate verified execution/readiness instead. Supported profiles should produce useful candidates, not only gap reports.
