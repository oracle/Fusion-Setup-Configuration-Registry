# Product Management References

Use this file for references when implementing Oracle Fusion Cloud Product Management,
including Product Development and Product Hub.

## Select the documentation

| Product area | Implementation and setup | Functional usage |
| --- | --- | --- |
| Product Development | [Implementing Product Management](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/faipr/index.html) | [Using Product Development](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/faupd/index.html) |
| Product Hub | [Implementing Product Management](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/faipr/index.html) | [Using Product Master Data Management](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/fapim/index.html) |

## Use first

### Implementing Product Management

- URL: [Implementing Product Management (26D)](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/faipr/index.html)
- Type: oracle documentation
- Category: Product Management
- Relevance: high
- Authority: product documentation
- Freshness: version-sensitive
- Use when: The FSCR implementation scope includes Product Management, Product Development, Product Hub, or their relevant functional areas, and implementation or setup guidance is needed. This is the shared implementation guide for both product areas.
- Do not use for: Projects outside Product Management scope, or as a substitute for the relevant functional usage guide.

## Additional references

### Product Development

#### Using Product Development

- URL: [Using Product Development (26D)](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/faupd/index.html)
- Type: oracle documentation
- Category: Product Development
- Relevance: high
- Authority: product documentation
- Freshness: version-sensitive
- Use when: Product Development is in scope and guidance is needed on functional usage and user procedures. Pair this guide with Implementing Product Management for setup dependencies.
- Do not use for: Projects without Product Development scope, Product Hub-specific usage questions, or as the sole source for implementation setup.

### Product Hub

#### Using Product Master Data Management

- URL: [Using Product Master Data Management (26D)](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26d/fapim/index.html)
- Type: oracle documentation
- Category: Product Hub
- Relevance: high
- Authority: product documentation
- Freshness: version-sensitive
- Use when: Product Hub is in scope and guidance is needed on product master data management usage and user procedures. Pair this guide with Implementing Product Management for setup dependencies.
- Do not use for: Projects without Product Hub scope, Product Development-specific usage questions, or as the sole source for implementation setup.

## Repository usage guidance

The following recommendations describe how to use these references in FSCR;
they are repository guidance rather than Oracle product requirements.

1. Identify whether the question concerns Product Development, Product Hub, or shared Product Management setup.
2. Start setup research with Implementing Product Management, then consult the corresponding usage guide for the user procedure.
3. Cite the specific Oracle topic supporting a product-behavior claim. These guide landing pages establish the reference set; they do not verify every feature or setup step.
4. State Oracle-documented behavior separately from implementation recommendations, and check release-dependent details against the latest available documentation.

## Execution boundary

These references describe Oracle product documentation and do not establish
that a capability has an executable FSCR workflow. For an implementation
execution request, begin with
[the implementation router](../../../../../router/implementation-router/SKILL.md)
and follow the selected skills' prerequisites, supported operations, and
approval gates. Documentation links do not authorize live configuration,
imports, exports, authentication, or external environment calls.
