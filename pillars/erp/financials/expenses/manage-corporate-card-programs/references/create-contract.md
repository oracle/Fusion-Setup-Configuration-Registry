# Bounded CREATE preparation contract

This task routes live CREATE through [the setup workflow](live-setup-workflow.md), using local preparation of one new Travel program, an optional
upload-rule row and an optional company-account row using existing issuer/site
references. Company-account payment codes are COMPANY and BOTH. The supported
field list is explicit in `scripts/prepare_fsm_package.py`; metadata/header
inventory is in `package-headers.json`. This is narrower than complete Fusion
UI parity. Reject nonempty unsupported fields and other requested operations.

## Empty fields and server ownership

The user-selected CREATE policy treats an optional blank as not supplied. The
writer emits an empty cell at that field's existing header position. It does
not remove columns or change metadata. No existing program is intentionally
modified: a fresh exact-task baseline must have zero exact or normalized name
collisions. Blank optional input is not an UPDATE clear operation. The helper
makes no claim that server defaults remain empty; read back requested values and
server-generated state after import. Never supply fabricated audit values, IDs,
SysDate, date strings, flags, alternate-key values or DFF data to fill a blank.

Source basis: the exact target template fixes the transport shape; task VO/EO
requiredness and import reference resolution are cited in the six rule resources.
[Oracle FSM CSV guidance](https://docs.oracle.com/en/cloud/saas/applications-common/26d/oafsm/export-and-import-csv-file-packages.html)
requires retaining the original format and unused members. The empty optional
cell policy is a client CREATE design decision, not a claim that generic CSV-to-XML
or UPDATE null semantics have been reverse engineered or live-qualified.

## Live workflow requirements

1. Bind the template and fresh unfiltered baseline to the exact environment,
   completed task export and release. The offline helper checks embedded metadata;
   the routed workflow independently verifies trusted acquisition and freshness.
2. Resolve supplied codes, mapping/source pairs, business unit, terms, currency,
   existing party and complete single-site visibility through qualified target
   evidence. The helper does not perform these network checks.
3. For Company/Both Pay, require an existing eligible clearing combination in the
   BU primary ledger/COA. Preserve the user's segment strings and leading zeros.
4. Reject unsupported supplied fields; retain all six CSVs and exact headers.
   Generate parent references from the validated root, never from customer IDs.
5. Run ordinary Data Loader conversion/preflight and Task Hook against the final
   immutable ZIP. `prepared_offline` is not upload readiness or approval.
6. Obtain the exact artifact approval through Data Loader, then submit only its
   approved bytes. On failure/uncertain completion retain IDs and do not resubmit.
   Verify persisted requested values and unrelated-state preservation afterward.

## Explicit unsupported scope

Updates, rename, deletion, new issuer/site, transfer credentials, administrator,
remittance, DFFs and nonempty inactive dates require a separate supported contract.
The author must extend the allowlist, field rules, references and tests together;
do not remove a guard merely to make a candidate pass. Inactive or absent optional
features are not reasons to ask the customer for unrelated inputs.
