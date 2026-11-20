# Account segment transport

Read this when preparing, validating, reconciling or rolling back account-field
changes in `AP_FINANCIAL_SYS_PARAM.csv`.

The task's same-task Fusion export establishes the transport representation:
each populated account is a quoted CSV cell with 30 LF-terminated segment
slots. This is a task-specific encoding, not a general rule for other FSM
objects. Check the fresh export if its release or representation changes.

- Keep business input, approval context and SOAP validation receipts in their
  account representation, such as the synthetic `10-020-0300-0400-050`.
- At CSV generation, write the ordered segment strings into the first slots,
  pad remaining slots with empty strings, and terminate all 30 slots with actual
  LF characters. Preserve leading zeroes. The CSV writer quotes the multiline
  cell; literal backslash-n text is not the encoding.
- Apply this conversion only to fields declared with the
  `validate_account_segments_read_only` resolver. Accept one through 30 nonempty
  segments; reject interior gaps, excess slots and bare CR line endings. CRLF
  arrays can be read and normalized to LF.
- An explicit empty value remains an empty cell, subject to existing required
  field and reference checks. Omitted update values and unrelated rows retain
  their existing values; do not re-encode unrequested baseline cells.
- Candidate validation requires the encoded value, independently of the
  business string. Hyphen-only, truncated or incorrectly padded candidate cells
  must fail. Repeatable output alone does not prove valid encoding.
- Readback compares ordered account segments while retaining the existing
  fresh-export/import evidence requirements. Blank, malformed or different
  persisted accounts do not prove the requested value was saved.
- Rollback compares the current account with the forward request by segments.
  Convert the original exported account back to its business representation for
  fresh rollback validation receipts, then encode the restored candidate at the
  CSV boundary. If a native segment itself contains a hyphen, stop for review
  instead of splitting that segment when reconstructing the business value.
  Preserve concurrency checks and separate rollback approval.

The task's standard noship test launcher includes synthetic transport tests for
quoted CSV round trips, leading zeroes, malformed arrays, preserved values,
candidate rejection, readback and rollback. Passing those offline checks does
not establish a successful Fusion import or authorize submission of a package.
