# Governed customer reads and current availability


This is the runtime route contract for the task-only cleanup. The inspected
framework baseline is `erp-pillar-integration` commit
`efb4b2a0a6d271a3e5b03d23a3d127028e581211`. The task does not install or extend
core, shared, catalog or schema capabilities. A later file with a familiar name
does not establish approval or compatible semantics.

## Available central route and its limits

The task now provides an explicitly selected
[partial REST identity mode](rest-identity.md), using the existing central client.
It supports party-number lookup, scoped address ownership and positive LOV
account/party corroboration. This narrows the earlier gap; it does not supply the
complete bundle described below. The complete collector preserves the original REST/SOAP division. Offline SOAP replay uses the task-owned pure XML contract.

The existing `core.fusion-api.rest-api-client` owns REST transport and OAuth.
Read its `SKILL.md` and `references/fusion-rest-api.md` in the selected repository.
The active FSCR workflow must first select the evidence operation and establish
the candidate, environment, identity scope, privilege prerequisites and purpose.
Only then may it invoke `scripts/fusion_rest_client.py` with `--method GET`.
An endpoint or a cached token alone is not a workflow selection.

The following task-selected REST projections already use that central route.
They are partial evidence, not replacements for all SOAP-dependent checks.

| Evidence | Existing REST resource | Prerequisite and limit |
| --- | --- | --- |
| Source-reference owners and visible reference history | `/crmRestApi/resources/11.13.18.05/hubSourceSystemReferences` | Requires independently resolved source-system code. A display name is not a code; this resource does not replace source-name resolution. Preserve exact tuple, active/history queries and pagination. |
| Organization addresses and purposes | `/crmRestApi/resources/11.13.18.05/hubOrganizations/{PartyNumber}/child/Address` and `Address/{AddressNumber}/child/AddressPurpose` | Requires verified party/site scope. These projections do not establish the complete customer account-site/use hierarchy or all location fields. |
| Receipt assignments | `/fscmRestApi/resources/11.13.18.05/receiptMethodAssignments` | Use the declared `receiptMethodSearch` finder only after account-number ownership is verified. An empty visible collection is not global absence. |
| Party tax profiles | `/fscmRestApi/resources/11.13.18.05/partyTaxProfiles` | Requires independently verified party identity and type; not proof of asynchronous tax effects. |
| Deployed account DFF metadata | `/fscmRestApi/applcoreApi/latest/flexfields/runtime/x/describe` | Describes mappings. It does not supply persisted customer-account DFF values. Do not infer blank storage from absent metadata. |

Use the exact query and interpretation contracts in `rest-reconciliation.md` for
these projections. If their identity prerequisites depend on an unavailable read,
stop at that prerequisite. Do not accept guessed identifiers or perform broader
searches as a fallback. See the developer evidence for the exact qualified source and read scope.

## Task-owned SOAP reads using unchanged core

The earlier central SOAP companion is removed. Its customer-specific request and
response rules now live in `scripts/customer_soap_contract.py`; the thin adapter
in `scripts/customer_soap_read.py` calls existing core OAuth and byte transport.
The complete collector preserves its original read selection to minimize
regression. REST remains responsible for source references, addresses/purposes,
receipt assignments, tax and DFF metadata. SOAP supplies the following evidence:

| Fixed read | Evidence and limits |
| --- | --- |
| `source-system-by-name` | Exact display name/code, active/TCA status; reject ambiguity. |
| `organization-by-number` | Independent party-number identity and organization values; visible organizations only. |
| `organization-by-site-number` | Independent site-number search and actual party/site/location owners; no expected-parent filter or global absence claim. |
| `customer-account-by-number` | Account number, actual account ID and party ownership; reject ambiguous results. |
| `customer-account` | Account/sites/uses, parents, sets, Bill-to links and selected DFF values; missing children do not establish global absence. |
| `active-customer-profile` | Active profile identity, values and effective bounds; not complete profile history. |
| `location` | Selected location values, including fields absent from address REST. |

The adapter uses `core.fusion-api.ucm-rest-client` functions
`get_authorization_header` and `request_bytes(props, url, ...)`. Core retains
OAuth, TLS, host/redirect checks and transport. The task adds no generic HTTP,
token storage, retry, submission, arbitrary URL or arbitrary SOAP action path.
Unsupported core signatures and wrong-checkout module imports fail before calls.
SOAP faults, wrong namespaces, unsafe XML and required identity mismatches fail
validation. A read request grants no import approval.

An earlier candidate imposed an additional central-confirmation gate. Review of
the architecture and FSCR discussions found no explicit prohibition on reusing
this existing byte helper and no requirement for that extra gate. It has been
removed; ordinary workflow selection, input/identity checks, privilege checks,
request limits and evidence requirements continue to apply. This does not claim
a new general-purpose central SOAP capability or central-owner endorsement.

`customer_api_collect.py --read-scope complete` selects the original combined
read plan, capped by `--max-requests` (1 to 256). The separately selected
`rest-identity` mode remains partial and does not replace the combined plan.
Run only for the explicit candidate, environment, phase and authorized purpose.
Raw responses must remain outside the source checkout. No automatic SOAP retry.

`customer_api_replay.py` imports the task-owned pure parser rather than executable
code from a historical checkout. It rechecks operation, identities and hashes,
performs no network fallback, and preserves historical evidence and timestamps.
Historical replay is a regression comparison, not fresh observation or import
qualification. Full field reconciliation and data-load completion remain separate.

## Other required central contracts

1. **Catalog and planning — existing replacement:** the baseline already associates
   `ORA_AR_MANAGE_CUSTOMER_UPLOADS` with Financials (`XLE_FINANCIALS_JUR`) /
   Customers (`ORA_EGP_CUSTOMER`), catalog display sequence `629`. Use the normal
   router, dependency resolver and active Run Book to select that context. The
   existing Task Context policy permits a unique code-and-name match to reuse
   this Receivables-owned skill across functional areas (`canonical-task-reuse`).
   The task location does not require a new Financials / Receivables catalog
   association. Catalog display sequence is not a fabricated Run Book ordering.
   Do not use the removed explicit-single-task planner or local catalog overrides.
   No Receivables catalog association is added; the task now lives in the
   existing Customers catalog context.
2. **Submission:** existing core Data Loader is the only FBDI upload/initiation
   route. Task Hook and normal exact-candidate approvals remain mandatory.
   Apply the bounded recovery approval and uncertain-outcome rules in
   [central handoff](central-handoff.md). Do not patch core, monkey-patch it,
   add task retries or submit directly. A missing server Run Book association
   remains unverified; the local approval binding is not a substitute for it.
3. **Status and diagnostics:** retain normal core monitoring and ESS logs.
   For exact customer attempt evidence, select
   [task-owned REST collection](attempt-association.md) after initiation.
   It reads the bound data set's processes, Customers object and errors through
   unchanged core REST GETs. It produces an explicitly task-owned observation,
   not fabricated native core output. The reviewer preserves exact identity,
   stage, completeness and Run Book checks. Counts and labels cannot substitute
   for missing identifiers; after-state reads and row lineage remain separate.

Qualification of retained-attempt reads is not a new live import. Historical
successful imports qualify only their recorded source and environment. A new
candidate must pass the normal preparation, approval, status and business-outcome
checks; incomplete evidence never grants execution, retry or completion authority.
