# Manage Payment Codes



Task-specific FSCR guidance and an offline FSM CSV adapter for Oracle Fusion
Payments. Begin implementation work through the repository's
[Implementation Router](../../../../../router/implementation-router/SKILL.md),
then follow the authoritative [task skill](SKILL.md) and its resource rules.
This README describes the package and its current validation status; it does
not replace the task rules or authorize an import.

## Task identity

| Property | Value |
|---|---|
| Offering | Financials |
| Functional area | Payments |
| FSM task | Manage Payment Codes |
| Task code / package ObjectShortName | `IBY_MANAGE_PAYMENT_CODES` |
| CSV export/import support | `Y` |
| Data Loader import mode | `FSM` |
| Root entity | `IBY_PAYMENT_CODE` |
| Root business key | `PaymentCodeType` + `PaymentCode` |
| Dependency entity | `IBY_PAYMENT_CODE_TRANSLATION` |
| Translation key | `PaymentCode` + `PaymentCodeType` + `Language` |
| Package evidence release | `11.13.26.10.0` |

## Package contents

| Path | Purpose |
|---|---|
| [SKILL.md](SKILL.md) | Task metadata, workflow routing, source evidence and behavior boundaries |
| [ora-resource/](ora-resource/) | Input, dependency, lookup, defaulting, design and error-handling rules, plus the compiled registry |
| [e2e-adapter.json](e2e-adapter.json) | Customer v2 offline runtime contract, field constraints and operation ownership |
| [scripts/fsm_task_adapter.py](scripts/fsm_task_adapter.py) | Offline normalization, package generation, validation, reconciliation and reverse-update preparation |
| [tests/test_noship_adapter.py](tests/test_noship_adapter.py) | Explicit CLI launcher for the canonical developer tests |
| [../noship/tests/manage-payment-codes/](../noship/tests/manage-payment-codes/) | Developer catalog, test sidecar, canonical assertions, support and verification evidence |

The runtime does not connect to Fusion. Imports belong to the active Run Book
and [Data Loader](../../../../../core/data-loader/SKILL.md). Developer tests and
their fixtures remain in `noship`; they do not establish customer business rules.

## Supported behavior and protections

Root create and same-key update have source-backed contracts. Consult
[Input Validation](ora-resource/ora_input_validation.md) for the complete field
dispositions and operation-specific requiredness.

- Type uses the five canonical codes: `BANK_INSTRUCTION`, `DELIVERY_CHANNEL`,
  `LOCAL_INSTRUMENT`, `PAYMENT_REASON`, and `SERVICE_LEVEL`.
- Existing `PaymentCodeType` and `PaymentCode` are immutable. On create, service
  `Code` equals `PaymentCode`; on update, preserve its exported cell because its
  setter writes the insert-only key.
- Alias (`FormatValue`) is limited to 80 characters; Country (`TerritoryCode`)
  to two. The resource tables own all remaining field limits.
- Use strict valid `YYYY/MM/DD` dates, with end date on or after start date.
  `EndDateDsp` is blank for sentinel `4712/12/31`; otherwise it equals the finite
  end date. The declared date serialization contract canonicalizes strict ISO
  date input to this CSV spelling before design preview and package generation.
  Ambiguous, impossible and timestamp inputs remain invalid.
- Audit fields and `SeededFlag` are system-owned. Create retains empty structural
  cells; update preserves exported cells without accepting user-authored changes.
  Seeded-record restrictions remain applicable.
- Obtain a fresh, complete, exact-task current-data export for existence,
  identity and preservation checks. Verify Country through the declared
  current-environment resolver before preview.
- Package membership does not authorize direct translation operations.
  Direct translation lifecycle operations remain unqualified. Source and
  current-environment evidence qualify the framework-created dependent rows
  for the bounded developer create fixtures; this does not establish general
  language/default behavior. Physical deletion is not qualified.

Read the owning resources in the order specified by `SKILL.md`. The six
historical translation placeholders have source-backed operation-specific
validation and stop conditions. A complete registry does not establish current
language values, session-dependent effects, deployed source parity or approval.
Direct translation writes remain excluded; unknown applicable effects stop
before preview. Historical findings and preview exceptions remain evidence of
their original runs and are not rewritten as passed.

## Offline commands and developer tests

From the repository root, list runtime commands and their arguments:

```bash
python3 -B pillars/erp/financials/payments/manage-payment-codes/scripts/fsm_task_adapter.py --help
python3 -B pillars/erp/financials/payments/manage-payment-codes/scripts/fsm_task_adapter.py normalize --help
python3 -B pillars/erp/financials/payments/manage-payment-codes/scripts/fsm_task_adapter.py build --help
python3 -B pillars/erp/financials/payments/manage-payment-codes/scripts/fsm_task_adapter.py reconcile --help
```

| Command | Responsibility |
|---|---|
| `manifest` | Validate and describe an exact-task source package |
| `normalize` | Validate a normalized design and emit blueprint, preview and requirements |
| `build` | Generate an offline candidate from template, baseline and design |
| `validate` | Check package shape and semantics against the baseline and design |
| `determinism` | Check that identical inputs produce identical candidate bytes |
| `rollback` | Prepare a narrow reverse update against verified current values |
| `reconcile` | Compare a fresh persisted export with the candidate and requirements |

Run the complete generated task suite through its supported launcher:

```bash
python3 -B pillars/erp/financials/payments/manage-payment-codes/tests/test_noship_adapter.py
```

The launcher requires the sibling noship bundle and checks its manifest and
helper hashes. Invoke it explicitly; generic discovery of the launcher folder
alone is not the canonical suite. The manifest binds every task and test file,
including this README. Refresh that binding after reviewed package changes.

## Validation status

As of **2026-10-30**:

| Check | Result |
|---|---|
| Adapter schema, semantic validation and runtime command probe | Passed; readiness findings retained |
| Catalog validation | Passed: 24 cases, 101 variants |
| Generated task suite | 22 passed, 3 conditional skips, no failures |
| Scoped live root Alias update | Persisted-state verified: 1 loaded, 0 failed, 0 warnings; 4/4 checks passed |
| Reverse restoration | Persisted-state verified: 1 loaded, 0 failed, 0 warnings; 4/4 checks passed |
| Alias-test business baseline | Restored across the original 392 root and 784 translation rows |
| Minimum live create | Request 572460 succeeded; one root and US/KO dependent rows independently verified, original rows preserved |
| Retained test state | Three exact approved records retained; current inventory is 393 roots and 786 translations |
| Manual Country state comparison | Exported UN → US → UN states verified; 393 roots and 786 translations preserved, with only target update audit fields differing after restoration |
| Manual Country import evidence | Successful task CSV import screenshot observed; its effect and restoration execution route are not established by the supplied exports |
| Translation operations | Excluded; preservation does not qualify translation behavior |
| Semantic interpretations | All 22 existing review rows accepted; unchanged interpretations retain that approval |

The [noship verification summary](../noship/tests/manage-payment-codes/tests/evidence/root-update-restoration-2026-10-29.md)
records the exact scope, process identities, independent comparisons and limits.
The [minimum-create verification summary](../noship/tests/manage-payment-codes/tests/evidence/minimum-create-verification-2026-10-30.md)
distinguishes application success from its failed campaign observation/recording
lifecycle. The three records were intentionally retained; no deletion or full
baseline restoration is claimed for that create. The successful Alias pair does
not establish arbitrary field updates or date-mutation coverage.

## Remaining completion and contribution gates

The preserved native 101-variant campaign has **96 passed, one not applicable,
one blocked and three pending**. Successful application effects and missing
native recording proof remain distinct. The exact current source and test
manifest must accompany the separate coverage-owner disposition and final MR
audit; the hash-bound historical ledger is not transferred or relabelled.

Documentation packaging corrections preserve source identifiers, repository
paths, revisions and claim boundaries while keeping internal source URLs in
the implementation project's restricted provenance record. Runtime guidance
uses the governing Data Loader contract distributed with the repository.

Full native campaign completion is not claimed. Required technical evidence,
the current consolidated MR audit and external reviewer approvals remain
separate contribution gates. A passing offline suite alone does not establish
merge readiness. Preserve private local settings outside the contribution.

Keep credentials, local OAuth/client configuration, Run Book settings, raw
environment exports and native session/approval data out of the contribution.
