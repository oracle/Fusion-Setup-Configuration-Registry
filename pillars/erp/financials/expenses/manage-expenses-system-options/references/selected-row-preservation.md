# Selected-row preservation evidence

## Contract and decision

Ordinary build-import now emits only complete requested BU/code rows in the
three CSV members. Both option aliases, all four members, ordered headers and
the exact fresh descriptor remain. Existing selected rows keep non-input cells;
new rows keep audit inputs blank. Unrequested baseline rows are never submitted.
Normal validator, native Data Loader preflight, Task Hook, immutable approval
and fresh-export reconciliation remain mandatory.

## Controlled observations

| Source ID | Scope | Observed result |
|---|---|---|
| OBS-SELECTED-ROW-20261110-CREATE | One absent BU-specific ENABLE_ORACLE_MAPS option set to N and one absent INACTIVE_EMPLOYEE_GRACE_PERIOD setting set to 0, with both option aliases | 48/48 checks passed; three submitted rows; all 978 unrelated transport rows, business values and audit cells unchanged; audit generation, aliases, metadata and headers verified |
| OBS-SELECTED-ROW-20261110-UPDATE | Same keys changed to Y and 1 respectively; complete selected rows with retained non-input cells | 57/57 checks passed; creation history and other selected cells retained; all 978 unrelated full rows/audits unchanged; aliases, metadata and headers verified |

These approved nonproduction tests used the task's actual workbook validator,
builder, current BU reference client, native preflight/Task Hook, immutable
submission and fresh verification exports. They did not use a direct import
endpoint or alter failed historical results. The earlier full-baseline audit
finding remains recorded separately; this decision promotes the verified
selected-row serialization, not full-baseline replay.

## Boundaries

Evidence covers the tested BU-specific option/scalar create and update cases.
It does not certify every mapping, global setting, value combination, release,
target, UI/transactional effect or fixture cleanup. The builder's existing
confirmed mappings and input restrictions remain; unknown/dynamic/inherited
fields do not gain support. A local candidate is unqualified for that run until
actual import and reconciliation establish its outcome. Preserve all failures,
including unrelated audit changes, rather than calling job acceptance a pass.

Private run receipts, exports and disposition records remain in the active
project and are not portable runtime dependencies. No private target identity,
internal source URL or live credential is required by this contract.
