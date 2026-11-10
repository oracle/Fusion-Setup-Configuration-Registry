# Seed Template Inventory

These bundled Oracle seed templates are implementation patterns, not provider specifications.

| File | Use |
| --- | --- |
| `seed-templates/JPMVCPAYMENTS.xsl` | Outbound `OutboundPaymentInstruction` to JPM virtual-card `pain.001.001.03` pattern |
| `seed-templates/ISO_FD_ACK.xml` | Generic ISO `pain.002.001.03` to `AckResponse` baseline |
| `seed-templates/JPM_FD_ACK.xml` | JPM ISO acknowledgment status and invoice-hold mapping |
| `seed-templates/PNC_FD_ACK.xml` | PNC ISO acknowledgment pattern, including proprietary reason aggregation and clearing reference |
| `seed-templates/JPM_FD_Payment_Response.xml` | Generic CSV-converted XML to payment-response normalized contract |
| `seed-templates/JPM_FD_VC_Reconciliation.xml` | Generic CSV-converted XML to reconciliation normalized contract |

Start from the closest operation profile, then replace provider paths, conditions, codes, and constants using runtime provider evidence. Never preserve JPM or PNC constants merely because they appear in a seed.

The files were extracted from Oracle Fusion seed/source locations. No raw bank specification or Confluence export is bundled.
