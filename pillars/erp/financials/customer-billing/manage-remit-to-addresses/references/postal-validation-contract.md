# Postal destination validation: local versus application checks

Policy: `fsm-postal-application-validation-v1`. Reviewed 2026-09-17.

## Corrected boundary

Creating a remit-to destination means making the requested destination available
in the selected reference set. It does not promise a brand-new underlying shared
HZ location. The FSM implementation may reuse a shared location or create one.
There is no requirement to obtain a global HZ dump or invoke a separate SOAP
lookup before every ordinary create. Nor does an FSM export establish global
uniqueness. If the requirement specifically demands a new shared location or
global uniqueness, retain that requirement as unresolved; this task cannot prove it.

The previous `REMIT-POSTAL` prerequisite combined three different checks and
required all of them to be declared satisfied before packaging. Replace that
blanket gate with the following split, not with a fabricated resolver receipt.

| Stage | Required checks and result |
|---|---|
| Local preparation | Exact task and compatible successful exports; explicit authorized reference set; destination country code and address line; source-compatible fields; exact parent references; known create collisions, ambiguous matching references, non-ASCII comparison uncertainty and ignored-on-reuse value conflicts. Ask focused questions for missing or conflicting business input. |
| Immutable preview | For each new parent, disclose `applicationValidation` with `pending_import`, possible shared-location reuse, and no global-uniqueness assertion. Normalization derives this disclosure; build and independent validation reject missing, changed or falsely passed entries. |
| Normal FSM import | Existing Core Data Loader route, current approval policy, and Fusion's configured country/address validation and shared-location resolution. No separate task-owned network client, SOAP, entity REST or database access. |
| Completion | Successful terminal process, no failed rows or unresolved warnings, then fresh exact-task export and exact requirement reconciliation. Missing or changed postal values, ambiguous resulting identities, missing children or baseline drift fail verification. |

The two-letter country shape check is not a country-domain lookup. Do not invent
one universal mandatory city/state/postal-code pattern: requirements depend on
the country and target configuration. Apply any authoritative country-specific
requirements already available; do not erase known invalid input just to let
the application reject it. Missing target configuration visibility is disclosed
as application-owned validation, not proof that the input is valid everywhere.
User-supplied country labels must be resolved rather than guessed.

No-op, audit, flexfield deployment, unauthorized scope, unsupported postal update,
delete and end-date checks are unchanged. `PASS` from the offline validator means
local candidate validation only. A successful import proves acceptance under the
target's configuration, not deliverability or that optional address verification
features were enabled. The offline reconciler checks supplied artifacts; the E2E
orchestrator separately proves export freshness and process success.

## Source evidence

- `SRC-REMIT-AM-IMPL`: RemitToServiceAMImpl.java, reviewed retained source lines 438–530: six nonempty match inputs; reuse the first returned location; otherwise create through InsertLocationVO, copy postal values and derive an omitted external reference. Lines 294–397 show commit and recoverable error collection. Read a fresh export before any retry after a failure or unknown result.
- `SRC-REMIT-SERVICE-AM`: RemitToServiceAM.xml: InsertLocationVO uses the shared CDM location service view inside FSM; this is not an instruction to call that service directly.
- `SRC-REMIT-CDM-LOCATION-EO`: retained LocationEO.xml review, lines 730–736, 2681–2704, 2784–2873: required two-character Country and validation-level-dependent country, geography error/warning and address-style mandatory checks. This supports application ownership, not an assertion that every target enables all validators.

Cached FPHDEV implementation evidence was re-reviewed for this correction; it is
not a fresh CodeSearch response or proof of the target patch level. The earlier
single-record probe and subsequent normal-route live scenarios are narrow,
dated evidence. See [release-scope-and-coverage.md](release-scope-and-coverage.md)
for the verified scope and every remaining catalog disposition. These results
do not establish full live readiness or postal validation for other deployments.
