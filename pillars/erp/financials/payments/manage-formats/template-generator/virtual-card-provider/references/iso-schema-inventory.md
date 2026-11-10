# ISO Schema Inventory

## Bundled Files

| File | Scope | Use |
| --- | --- | --- |
| `iso-schemas/pain.001.001.03.xsd` | ISO Customer Credit Transfer Initiation V03 base schema | Validate outbound virtual-card `pain.001.001.03` only |
| `iso-schemas/pain.002.001.03.xsd` | ISO Customer Payment Status Report V03 base schema | Validate generic ISO `pain.002.001.03` acknowledgments and status reports |
| `iso-schemas/pain.002.001.03-sepa-profile.xsd` | Public German Banking Industry Committee SEPA-compatible profile using the `pain.002.001.03` namespace | Use only when the provider profile is confirmed compatible with these SEPA restrictions |

The ISO 20022 public archive identifies `pain.001.001.03` and `pain.002.001.03` in the archived Payments Initiation V03 message set. Its individual download endpoints are:

- `https://www.iso20022.org/message/14316/download`
- `https://www.iso20022.org/message/14361/download`

The two base V03 schemas were manually downloaded from the ISO 20022 archive and supplied for bundling. The separately named pain.002 SEPA profile remains available only for provider profiles that explicitly require its additional restrictions.

## Rules

- Match the `Document` namespace exactly.
- Do not validate provider-specific proprietary XML against an ISO XSD.
- Use the base pain.002 schema by default. Use the SEPA-restricted pain.002 profile only when the provider documentation explicitly requires a compatible SEPA profile.
- When the provider names another version, add that exact public XSD and do not silently upgrade or downgrade.
- XSD validity is necessary but insufficient. Provider implementation guides can impose stricter cardinality, code, and conditional rules.
