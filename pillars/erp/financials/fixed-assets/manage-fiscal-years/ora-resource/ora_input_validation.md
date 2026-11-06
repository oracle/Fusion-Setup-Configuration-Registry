# Manage Fiscal Years: Input Validation

## Mandatory Input Completeness

| Creation path | Required business inputs | When incomplete |
|---|---|---|
| User-defined | Fiscal-year cycle. Fiscal Year Name may be omitted until existing fiscal years matching that cycle are listed and the user chooses reuse or create-new. Start year is optional because it can default from System Controls. | Stop for a missing fiscal-year cycle. If the user chooses create-new, stop until the user supplies a new Fiscal Year Name. |
| Ledger-derived | Ledger Name. Resolve the target environment from configured properties or active project context. Fiscal Year Name may be omitted only until the equivalent-fiscal-year lookup and reuse-or-create decision are complete. | Stop for a missing ledger name. If the user chooses create-new, stop until the user supplies a new Fiscal Year Name. |

## Field Validation

Validate each supplied or derived field as soon as it is received or resolved, before any lookup, reuse/create decision, or package work.

| Field | Data type and maximum length | Accepted value | Validation |
|---|---|---|---|
| Reuse existing fiscal year | Existing target record; no new field value | Exact existing fiscal year selected by the user. | Do not modify its fiscal-year type, name, description, translation, or date rows. Validate only that its existing cycle, coverage, and regular-period pattern match the request. |
| New fiscal-year type (Fiscal Year Name) | Text; 30 characters maximum | Create-new only: a new exact name supplied by the user. | Must be unique. |
| Description | Text; 80 characters maximum | Create-new only: user-supplied text or the human-readable sentence-case default from ora_defaulting_rules.md. | Validate the final value is no more than 80 characters. |
| Translation languages | Complete active target-environment language set | Create-new only: every language code returned by `resolve_active_translation_languages`. | Create one translation row per active language. Do not request or accept a user language selection; stop only if the fully paginated active-language result is missing, incomplete, or empty. |
| Fiscal-year dates | Fiscal-year number; dates in the target date format | Create-new only: fiscal-year number, start date, end date, and optional Midyear Start Date. | Start must not follow end; Midyear Start Date, when used, must be within the fiscal year. For an Oldest-DPIS-based creation, the first fiscal-year date row must contain Oldest DPIS inclusively. |
| Explicit ledger start basis | User states that the ledger start date is the fiscal-year start basis | The earliest complete regular ledger fiscal-year Start Date | Use the stated ledger basis directly after ledger resolution. Do not present, request, or await alternative start-basis choices. |

## Ledger-Derived Equivalent Fiscal Year Selection

After resolving the exact ledger and its regular accounting periods, present the available equivalent Fixed Assets fiscal years returned by the ledger-equivalent lookup.

| Ledger | Available equivalent fiscal year | Coverage | Regular periods | Match result |
|---|---|---|---|---|
| `<exact ledger name>` | `<fiscal year name>` | `<start> to <end>` | `<count> <frequency>` | `Equivalent` |

## User-Defined Equivalent Fiscal Year Selection

For a user-defined request, always present existing Fixed Assets fiscal years that match the supplied fiscal-year cycle and resolved start coverage, even when the user supplied a Fiscal Year Name. Compare any supplied name with that list; do not bypass the lookup.

| Fiscal-year cycle | Available equivalent fiscal year | Coverage | Regular periods | Match result |
|---|---|---|---|---|
| `<supplied cycle>` | `<fiscal year name>` | `<start> to <end>` | `<count> <frequency>` | `Equivalent` |

## Reuse or Create Decision

When there are 10 or fewer equivalent matches, list all of them. When there are more than 10, show the first 10 matches and the total count in chat, and provide the complete read-only match table for selection. When there are no matches, show one `No equivalent fiscal year available` row. Then ask the user exactly one decision: **Reuse one listed fiscal year, or create a new fiscal year?** For reuse, require the exact listed Fiscal Year Name. For create-new, require the new exact Fiscal Year Name in the decision response. A name or an instruction to create in the original request is only a candidate; it is never the reuse-or-create decision. Never select or suggest a name automatically.

### Non-skippable Fiscal-Year Cycle Gate

For every user-defined request, this is a blocking sequence: receive the
fiscal-year cycle; resolve the start year when it was omitted from System
Controls; check the exact existing state of a supplied candidate Fiscal Year
Name read-only, or mark that check not applicable when no name was supplied;
list all existing fiscal years matching that cycle and resolved coverage; then
obtain the user's reuse-or-create-new decision. A supplied Fiscal Year Name
never bypasses the list or decision. The candidate-name check does not
authorize creation. Do not prepare a preview or generate a package before
the list and decision are complete. A zero-match
list still requires the create-new decision and then a user-supplied new name.

### Mandatory Oldest-DPIS First-Year Containment

After the reuse-or-create decision and before preview or package preparation,
when the selected start basis is Oldest DPIS, including a missing start
defaulted from System Controls, identify the first fiscal year
from the requested cycle and validate its complete date range against Oldest
DPIS. The first fiscal-year row must contain Oldest DPIS inclusively:
`Start Date <= Oldest DPIS <= End Date`. Compare actual dates, not the
fiscal-year label. Reject a proposed first row that starts after Oldest DPIS or
ends before it. Generate subsequent fiscal years from that first cycle row.

## Fiscal-Year Name Handling

| Input condition | Required handling |
|---|---|
| Fiscal-year name supplied | Treat it as a candidate only. After the cycle and coverage are resolved, check its exact existing state, then show the equivalent-fiscal-year list and ask the mandatory reuse-or-create question. Wait for the subsequent user decision before creating a preview. |
| Supplied name is absent, ambiguous, or conflicts with the requirement | Present the finding and ask the business owner to decide whether to create, update, or use another fiscal year. Do not silently substitute or create one. |

Manage Asset Calendars owns Asset Calendar Name collection. Do not request, derive, or validate an Asset Calendar Name in this fiscal-year task.

## Values That Must Stay User-Supplied

| Value | Rule |
|---|---|
| Fiscal Year Name | For create-new, require a new exact name from the user. |
| Ledger-derived, DPIS-based, or user-specified start | Validate the user-selected or defaulted start fiscal year against the applicable fiscal-year cycle and coverage. For an Oldest-DPIS-based creation, the first date row must contain Oldest DPIS inclusively. Do not replace an accepted user selection. |

## Bulk Input Set

For 100 or more fiscal-year definitions, accept a tabular input set rather
than conversational rows. Each fiscal-year row must contain a unique business
key and enough values for exactly one of these paths:

| Key and required fields | Ledger-derived path | User-defined path |
|---|---|---|
| Identity | Ledger Name, Fiscal Year Name, Description | Fiscal Year Name, Description |
| Coverage | Start Basis: `Ledger-derived`, `DPIS-based`, or `user-specified` | Fiscal-year cycle and Start Fiscal Year, or complete Fiscal Year Date rows |
| Date rows | Generated from the selected basis after lookup | Fiscal Year, Start Date, End Date, and optional Midyear Start Date |

Reject and report all rows with a blank key, duplicate Fiscal Year Name,
ambiguous ledger, incompatible path values, or invalid dates. A rejected row
does not invalidate unrelated rows. Return row number, fiscal-year name when
present, failed check, and correction required; never silently omit a row.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| FY.VALIDATE_INPUT | decision | 10 | validate_input | valid->FY.RESOLVE_DEPENDENCIES;invalid->FY.HANDLE_INPUT | none | stop | Every request. |
| FY.DECIDE_EQUIVALENT | decision | 40 | validate_input | reuse->FY.DONE_EXISTS;create_new->FY.VALIDATE_DPIS_CONTAINMENT;unresolved->FY.HANDLE_DEPENDENCY | FY.LOOKUP_EXISTING | stop | Equivalent fiscal-year results and the supplied candidate name's exact status, when a name was supplied, are available; user must choose reuse or create-new. |
| FY.VALIDATE_DPIS_CONTAINMENT | decision | 45 | validate_input | valid->FY.APPLY_DEFAULTS;not_applicable->FY.APPLY_DEFAULTS;invalid->FY.HANDLE_INPUT | FY.DECIDE_EQUIVALENT | stop | User selected create-new. For an Oldest-DPIS-based start, including a missing start defaulted from System Controls, require the first Fiscal Year Date interval to contain Oldest DPIS; return valid or invalid. For a ledger-derived or explicitly supplied non-DPIS start, validate its selected cycle and coverage, preserve the accepted basis, and return not_applicable for DPIS containment; invalid basis or coverage returns invalid. |
