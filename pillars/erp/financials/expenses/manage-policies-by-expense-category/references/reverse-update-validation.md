# Explicit reverse-workbook validation

Car Rental reverse requests use the normal public protocol with a separately
prepared workbook, fresh post-forward baseline and operation-bound target
references. Keys, dates, currency and omitted values remain protected. Every
eligible unresolved reverse field needs its own exact implementor acceptance;
forward acceptance never authorizes a reverse candidate or import.

The optional absolute regular file `policyPreparation.reverse_update_of`
contains exactly `schemaVersion: fscr-policy-reverse-update-proof-v1` and
`artifacts`, whose `before`, `forward_blueprint` and `forward_candidate` entries
each contain exact absolute `path` and `sha256` values. These artifacts belong
to the verified forward run. Normal input bindings retain their hashes.

The source-owned verifier checks the forward task/target and original baseline
binding, package target/task identity, unchanged forward submission metadata,
unique full identities, persisted forward values and preservation. Reverse
operations must name the same targets and fields and restore exact original
values. Other baseline business rows cannot be removed or changed. Audit
differences and unrelated concurrent inserts follow ordinary reconciliation
rules. It rechecks immutable inputs after reading.

Public normalize returns `rollbackOfDesignSha256`. Public validation returns
the bound `fscr-public-reverse-update-proof-v1` report; ordinary references,
field acceptance, native rules and exact candidate checks still run first.
The companion must independently bind this proof to the actual VERIFIED
forward run and replay public validation and determinism. This is a local
restoration proof, not an observed persistence claim or automatic rollback.

The automatic rollback command remains unavailable. Native Data Loader owns
separate approval and submission of the reverse candidate. No helper logs in,
imports, deletes, retries, or manufactures reference evidence. A failed or
uncertain forward import stops cleanup planning until its outcome is resolved.
