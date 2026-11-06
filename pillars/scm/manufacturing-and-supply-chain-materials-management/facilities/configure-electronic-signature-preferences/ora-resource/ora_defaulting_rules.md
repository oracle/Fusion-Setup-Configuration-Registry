Source: developer-confirmed creation rules: apply explicit transaction enablement and editable signature-type requests in the combined create; use false and the catalog signature mode for transactions without those requests.

# Creation Defaults

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Resolver |
|---|---|---|---|---|
| SignatureEnabledFlag | true for a selected transaction explicitly requested as enabled; otherwise false | Independently for each selected transaction during combined parent creation; match explicit intent to its uniquely resolved TransactionTypeCode; enabling one transaction does not enable others | No: preserve explicit true or false; enable maps to true and disable maps to false. An unspecified transaction defaults to false | |
| SignatureTypeCode | Retain the selected catalog SignatureMode when no type is requested, even if editability is true; otherwise apply a supported requested code for that transaction in the same creation only when its derived SignatureModeEditableFlag is true | Combined create after transaction selection and creation editability derivation | Yes: Deferred maps directly to ORA_DEFERRED; Inline and In-line map directly to ORA_INLINE without a generic lookup; supported direct codes are retained. Do not override a noneditable type; ora_design_enforcement.md owns refusal | |

Review coverage: [synthetic creation and update scenarios](#synthetic-review-scenarios).

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| ESIGN.APPLY_CREATE_DEFAULTS | decision | 6 | apply_default | applied->ESIGN.READ_CHILD_EDITABILITY;not_required->ESIGN.READ_CHILD_EDITABILITY;invalid->ESIGN.ISSUES | ESIGN.RESOLVE_CREATE_EDITABILITY | stop | For combined creation after catalog selection and editability derivation, apply the Standard Defaults independently to each selected transaction using validated request values and Data Loader captured records. Existing updates and deletes return not_required; do not apply creation defaults or populate omitted update fields |

## Synthetic Review Scenarios

These are reusable review fixtures for [Standard Defaults](#standard-defaults)
and this file's update exclusion, not executed test results or import artifacts.
Use synthetic OrganizationId 100000000000001. TEST_TXN_A and TEST_TXN_B are the
complete eligible catalog set, both with native EnabledForAllOrgsFlag false.
Their catalog SignatureMode is ORA_DEFERRED and derived SignatureModeEditableFlag
is true unless a case overrides it. Each case is independent; other gates pass.
For updates, assume uniquely verified existing parent/child references.

| Scenario | Input and supplied facts | Expected outcome |
|---|---|---|
| ESIGN-DEFAULT-01 | Create: explicitly enable TEST_TXN_A; omit enablement and type for TEST_TXN_B | One electronicSignaturePreferences creation for the synthetic organization with both children in electronicSignatureTransactionTypes: A has SignatureEnabledFlag true, B false; both have SignatureTypeCode ORA_DEFERRED and SignatureModeEditableFlag true. Preserve the complete eligible set; no second load solely for enablement |
| ESIGN-DEFAULT-02 | Create: explicitly disable TEST_TXN_A | A receives SignatureEnabledFlag false; explicit false is preserved and is not treated as missing input |
| ESIGN-DEFAULT-03 | Create: request Inline or In-line for TEST_TXN_A | Each label variant maps directly to ORA_INLINE in the same combined creation, without a generic lookup; B retains ORA_DEFERRED. Both signatures remain false when enablement is unspecified |
| ESIGN-DEFAULT-04 | Create: A catalog SignatureMode is ORA_INLINE; request Deferred | A receives ORA_DEFERRED in the combined creation; preserve its derived editability and B's defaults |
| ESIGN-DEFAULT-05 | Create: A catalog SignatureMode is ORA_INLINE and editability is true; omit its type | A retains ORA_INLINE; editability alone does not choose a new type |
| ESIGN-DEFAULT-06 | Update A: current type ORA_DEFERRED, enabled false, editability false; request enabled true only | Submit only SignatureEnabledFlag true through the existing parent/child reference; preserve type and editability. No type-editability or label lookup is required for this flag-only request |
| ESIGN-DEFAULT-07 | Update A: current type ORA_DEFERRED, enabled true, editability true; request ORA_INLINE only | Submit only SignatureTypeCode ORA_INLINE after current editability passes; preserve SignatureEnabledFlag true and apply no creation defaults |
| ESIGN-DEFAULT-08 | Update A: current type ORA_INLINE and enabled true; explicitly request enabled false and omit type | Submit SignatureEnabledFlag false; preserve ORA_INLINE and do not populate the omitted type field |

Related coverage: [input literals](ora_input_validation.md#synthetic-review-scenarios)
and [editability and scope policy](ora_design_enforcement.md#synthetic-review-scenarios).
