# FSM metadata ordering contract


Reviewed implementation sources on 2026-10-28:

- `FSM_MAIN_GENERIC: ConfigurationPackageAMHelper.java`, lines5669–5786: the producer queries XML nodes by request ID, orders their generated IDs, assigns positive sequences, and reuses a parent's sequence for translation metadata. Sequence numbers identify package-local ordering, not stable business identities.
- `FSCORE_MAIN_GENERIC: XmlCSVAMImpl.java`, lines83–112 and248–338: the consumer groups objects by XML filename and hierarchy level; it sorts levels and uses a sequence-keyed TreeMap within each level. Distinct objects in one file/level must not collide. Numeric parent-before-child ordering is not required across levels.
- `FSM_MAIN_GENERIC: MigratorAMHelper.java`, lines1510–1596: CSV import selects the current service's object list, builds that object's hierarchy, filters exported metadata to the service, and assigns its recorded sequences. It does not combine every package metadata definition into one transform collection.
- `FSM_MAIN_GENERIC: XmlAMImpl.java`, lines286–319: the import collection is requested by business object ID in CSV mode.

Source locations and reviewed excerpts are retained in the restricted developer
qualification evidence. Internal service URLs are excluded from this package.

The exact XML filenames come from `SetupBusinessObjectSD.xml`, whose reviewed
SHA256 is recorded in `policy-package-metadata.json`. The task registrations in
`SetupTaskBusinessObjectSD.xml` identify 18 objects for this task. The package
also carries `ORA_EXM_CUMULATIVE_MILEAGE_DETERMINANT`, registered to Manage
Cumulative Mileage Determinants, as a metadata-only definition of the same XML
node as the task's `ORA_EXM_MILEAGE_POLICY_DETERMINANT`.

Validation retains all19 CSVs and all37 metadata records. It requires the exact
18 registered migration-object records and checks the metadata-only alias for
exact node, type and sequence equality with its canonical definition. It never
drops that definition or treats it as a second task transform. Unexpected
registrations, missing or altered aliases, nonpositive numbers and actual
file/level collisions stop processing.

With the explicit `export-local` descriptor policy, verification may classify
sequence-only differences as compatible after validating both packages. Raw
differences remain in the report. Paths, ordered attributes/types, table ownership,
record multiplicities and nonsequence fields remain strict. Without the policy,
legacy exact sequence checks remain. Submission metadata must always remain
byte-identical to the chosen baseline; no sequence is rewritten or reordered.

These are reviewed shared-framework sources and release-applicable task seed
registrations, not an assertion that a deployed pod's binaries were decompiled.
Actual target exports, native process results and complete persisted-state
reconciliation are required independently for each live qualification.
