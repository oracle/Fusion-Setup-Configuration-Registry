# Customers input byte limits


The reviewed 26D `ArUpdCustomers.ctl` uses delimited character fields with no
character-length override. For this task's UTF-8 file route, validate decoded
field bytes as well as the separately established business character limits.

| Input field | Maximum UTF-8 bytes |
| --- | ---: |
| PARTY_NAME | 360 |
| ADDRESS_LINES_PHONETIC | 560 |
| ADDRESS_DESCRIPTION | 1000 |
| TRANSLATED_CUSTOMER_NAME | 360 |
| Each other one of the 87 input fields | 255 |

The last row comes from the default for delimited CHAR fields with no explicit
length or position; it is not inferred from staging column widths. Generated
expressions/constants in the control file do not add input columns. The CSV END
trailer remains separate from the 87 business fields.

Oracle documents [delimited field lengths](https://docs.oracle.com/en/database/oracle/oracle-database/26/sutil/oracle-sql-loader-field-list-contents.html)
and [control-file length semantics](https://docs.oracle.com/en/database/oracle/oracle-database/26/sutil/oracle-sql-loader-control-file-contents.html).
Field length semantics and database column character semantics are independent.
The retained 26D test rejected a 1000-character / 3000-byte description at the
SQL*Loader stage; the staging database column was independently 1000 CHAR.
This resolved the former AR-ADDRESS-LENGTH gap. It does not establish all
field boundaries or compatibility with other releases.

Reject an overlong value before preview or candidate acceptance. Preserve valid
Unicode values exactly; never truncate, transliterate or silently trim them.
CSV enclosure and escaped quote syntax are not additional decoded field bytes.
Direct ZIP inspection enforces the same rules as business-input preparation.
Loader-validation acceptance cannot waive a confirmed length violation. A
contract change requires a fresh preview and candidate-bound approval.

For a different delivered control file, review its encoding and field semantics
before adapting these limits; do not generalize the 255-byte default to every
FBDI product or override explicit character semantics.
