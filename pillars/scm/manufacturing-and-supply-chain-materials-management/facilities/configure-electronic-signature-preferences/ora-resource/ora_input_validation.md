Source: developer-provided creation requirements and follow-up organization, transaction-selection and signature-update steps. Only supplied contracts are resolved; remaining TBD fields block execution.

# Input Validation

The developer explicitly confirms the chat request and Data Loader captured
records as the authoritative local source for the operation and requested
values. REST validates organization and transaction references. Literal shape,
boolean, code-set and lifecycle checks need no additional lookup. Data Loader
owns validation of registered attributes and transport serialization.

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Organization identity | OrganizationId, otherwise OrganizationCode or OrganizationName; or the protected label All organizations | Stop before preview | Use resolve_inventory_organization for ordinary identities; All organizations and OrganizationId -1 identify the protected scope | Every operation | resolve_inventory_organization |
| Combined create shape | OrganizationId and electronicSignatureTransactionTypes array in the same parent request | Stop before preview | Check the prepared combined shape after transaction selection; selected children are obtained through select_electronic_signature_create_transactions | Prepared create data after transaction selection |  |
| Child reference | Existing electronicSignaturePreferences reference and electronicSignatureTransactionTypes record reference | Stop before preview | Resolve the parent and child using the documented lookup contract once supplied | Child update | resolve_electronic_signature_parent_child |
| Signature type representation | SignatureTypeCode ORA_DEFERRED or ORA_INLINE; alternatively SignatureType Deferred or In-line; Inline is also accepted for creation | Stop if a requested type change supplies neither supported representation | For creation, use the direct label/code mapping owned by ora_defaulting_rules.md after creation editability derivation; existing-child label updates use resolve_electronic_signature_type_code after editability passes | Creation with a requested type or child type update | |
| Signature enablement value | SignatureEnabledFlag as JSON true or false | Stop when an enablement update has no boolean value | Enable maps to true; disable maps to false. Require a native JSON boolean and lowercase transport representation; false is an explicit value, not missing input | Combined creation or child enablement update |  |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Nested transaction shape | TransactionTypeCode and SignatureTypeCode are strings; SignatureEnabledFlag and SignatureModeEditableFlag are JSON booleans; OrganizationId is required integer int64 in the published create schema; TransactionTypeCode and SignatureTypeCode are strings of maximum length 30. Complete runtime field selection remains subject to the registered adapter | Create or child update |  |
| Parent identifier versus organization | Do not assume OrganizationId is the parent REST record key; SignatureOrganizationId identifies the parent and SignatureDefinitionId identifies its child; resolve both through the documented collection lookup and retain returned item links | Update or delete reference | resolve_electronic_signature_parent_child |
| SignatureEnabledFlag type | Accept native true and false; reject quoted JSON string substitutes; do not default an omitted update field. Always pass lowercase true for enablement and lowercase false for disablement | Combined create or child enablement update |  |
| Signature boolean serialization | Validate SignatureEnabledFlag and SignatureModeEditableFlag after source preparation and before preview: JSON uses native unquoted true or false; boolean values in text-based loader sources use exact lowercase true or false tokens. Reject True, False, TRUE, FALSE and other substitutes; do not approve a source produced by generic language string conversion. Correcting a captured source requires a fresh Data Loader validation session and approval | Every prepared create or child update containing either boolean flag |  |
| Accepted signature codes | Developer-confirmed SignatureTypeCode values are exclusively ORA_INLINE and ORA_DEFERRED. Reject every other code, including INLINE and DEFERRED; validate both direct inputs and label-lookup results against this set. On failure return invalid_signature_type and use the exact message owned by ora_error_handling.md | Create or child type update |  |
| OrganizationId transport type | Published create schema requires integer int64; normalize an accepted numeric intake string without loss of precision before execution, using core.data-loader registered-metadata validation and serialization; block if its type check cannot preserve the exact ID | Prepared combined create |  |
| Read-only display values | SignatureType, Transaction and TransactionTypeId are read-only response fields; do not send them as writable child attributes | Prepared child update |  |

Review coverage: [synthetic literal-validation scenarios](#synthetic-review-scenarios).

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| ESIGN.VALIDATE_INPUT | decision | 1 | validate_input | valid->ESIGN.RESOLVE_ORGANIZATION;invalid->ESIGN.ISSUES | none | stop | Every request; chat request and Data Loader captured records are authoritative local inputs; registered metadata governs transport fields |

Documentation: [26C create schema](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/op-electronicsignaturepreferences-post.html) and [26C child collection schema](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/op-electronicsignaturepreferences-signatureorganizationid-child-electronicsignaturetransactiontypes-get.html).

## Synthetic Review Scenarios

These review fixtures exercise [Field Validation](#field-validation), not live
Fusion operations. Use TEST_TXN_A with all unrelated gates satisfied. Evaluate
each listed value independently, in each stated field and source; acceptance
means only that the tested validation passes. Exact diagnostic text remains
owned by [Error Situations](ora_error_handling.md#error-situations).

| Scenario | Input and supplied facts | Expected outcome |
|---|---|---|
| ESIGN-INPUT-01 | Prepared create: each of SignatureEnabledFlag and SignatureModeEditableFlag uses native JSON true or false, or the exact text token true or false in a text-based loader source | Accept each boolean representation in its stated format; explicit false remains a value |
| ESIGN-INPUT-02 | Either signature boolean field in a text-based loader source contains True, False, TRUE, FALSE, 1 or 0 | Reject every variant before preview; require a corrected source and fresh Data Loader validation and approval |
| ESIGN-INPUT-03 | Either signature boolean field contains quoted JSON "true" or "false", or JSON number 1 or 0 | Reject every variant before preview; neither strings nor numbers are native JSON booleans |
| ESIGN-INPUT-04 | Create or editable child type update: supplied SignatureTypeCode is ORA_INLINE or ORA_DEFERRED | Accept either code unchanged, subject to the remaining scope and editability gates |
| ESIGN-INPUT-05 | Supplied SignatureTypeCode, catalog-derived code or existing-update label-lookup result is INLINE, DEFERRED or TEST_UNSUPPORTED | Reject each code from each source with exactly: Invalid Signature Type. Do not silently rewrite it to an accepted code |

Related coverage: [creation mappings and omitted update fields](ora_defaulting_rules.md#synthetic-review-scenarios)
and [policy eligibility](ora_design_enforcement.md#synthetic-review-scenarios).
