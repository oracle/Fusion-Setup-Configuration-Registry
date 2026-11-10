# Receipt-from coverage uniqueness

The FSM parent-qualified transport key and the database business unique key
serve different purposes. Retain all seven parent-reference fields for import,
target selection and reconciliation. Additionally reject a child create when
its exact reference set, country, state and postal bounds already exist under
any destination in the current export or elsewhere in the proposed batch.

Status is not part of that unique key: an Inactive existing rule still reserves
the combination. A different parent, parent postal address, or parent external
reference does not release it. Blank state/postal values and DEFAULT country
remain exact business values; preserve leading zeros. This check does not infer
that distinct or overlapping ranges are prohibited: broader validation still
belongs to source-backed rules and Fusion's application checks.

Ask: “This customer coverage already belongs to [existing destination] in
[reference set]. Which different coverage should the new destination serve,
or did you mean to change the existing coverage?” Preserve both the requested
and existing identities. A reassignment is not a supported Status-only update.
Do not change ZIP codes, broaden coverage, delete rows, or silently replace the
requested create. In a bulk/mixed request, retain all rows and generate no
partial ZIP until the conflict is resolved and the revised design is confirmed.

## Source evidence

SRC-REMIT-CRITERIA-U1: CodeSearch MCP reviewed 2026-09-21, FPHDEV
ra_remit_tos_all.table.
The unique marker is at line 1066, RA_REMIT_TOS_U1 at 1068, STATE at 1076,
COUNTRY at 1079, POSTAL_CODE_LOW at 1082, POSTAL_CODE_HIGH at 1085 and SET_ID
at 1088. ADDRESS_SEQ_ID belongs to the separate index at 1139, not U1.
SetCode is the task-export business reference resolved to SET_ID.

A live parent-plus-coverage create on 2026-09-21 was rejected with
RA_REMIT_TOS_U1 when the same exact coverage was already assigned to another
destination in that set. Its fresh post-failure export had identical non-audit
rows to its baseline. This observed rollback is not a general atomic-import
guarantee; every failed or uncertain import still requires a fresh export.
