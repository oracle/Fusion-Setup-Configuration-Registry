# FSM descriptor identity and cross-export comparison

Read this when authoring a package or reconciling an import. The task's
metadata_contract.py keeps the owning metadata table, every record occurrence,
attribute lists/types, XML path and NodeSequence. A map keyed only by entity is
unsafe: the same entity occurs in both business-object and migration-object
metadata tables. Record listing order is not used to hide duplicate records.

There are three comparison results:

- EXACT_METADATA_MATCH: selected records match, including sequences.
- SEQUENCE_DRIFT_REQUIRES_FRESH_DESCRIPTOR: only NodeSequence changed across
  exports; preserve the difference and bind any future candidate to its freshly
  exported descriptor. This does not prove arbitrary sequence equivalence.
- STRUCTURAL_METADATA_DRIFT_STOP: fields, types, ownership path, record counts
  or other metadata differ. Stop and review the exact descriptor/schema change.

Regardless of cross-export classification, a submitted candidate must preserve
its own bound baseline ASM_SETUP_CSV_METADATA.xml byte-for-byte. Do not copy an
older descriptor into a new baseline, reorder its nodes, repair NodeSequence or
ignore structural drift. The normal builder verifies descriptor bytes in its
final ZIP; verify_submission_metadata additionally checks persisted archives.

Persisted business-data reconciliation and metadata comparison are separate
outcomes. The accepted OBS-XLS01 result proves all164submitted business cells
and preservation of1217prior full rows for that exact package. A subsequent
Meals parent/line NodeSequence reversal is a cross-export descriptor change,
not a CSV business-cell mismatch. Retain both the accepted scoped result and
the historical strict mismatch report. Do not use acceptance to enable a new
descriptor without its own baseline binding or broaden product readiness.

The available FPH CodeSearch index did not expose the FSM consumer of
NodeSequence. Only unrelated symbols were found. Its broader semantics remain
unproved; these checks enforce local artifact integrity rather than inventing
an ordering contract.
