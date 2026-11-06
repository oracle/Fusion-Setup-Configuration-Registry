Source: developer-provided creation requirements and follow-up organization, transaction-selection and signature-update steps. Only supplied contracts are resolved; remaining TBD fields block execution.

# Design Enforcement

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Establish evaluation authority | Use the developer-confirmed chat request and Data Loader captured records for operation and requested values; use verified REST references for persisted identity |
| 2 | Apply organization scope | All organizations and OrganizationId -1 are equivalent; enforce the protected-parent rules and transaction eligibility: native EnabledForAllOrgsFlag true for protected updates, false for ordinary creation and updates |
| 3 | Select create transaction types | Apply the create-selection rule using select_electronic_signature_create_transactions before preview |
| 4 | Gate signature type changes | For creation, derive child editability before applying requested type overrides; for existing-child updates, read current child editability before resolving or accepting a type code |
| 5 | Enforce parent/child lifecycle | Apply every applicable rule below before Data Loader preview |

## Design Rules

| Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|
| Create for an ordinary organization | Blocking |  | Parent-only create or standalone child create | Create electronicSignaturePreferences with electronicSignatureTransactionTypes together in one parent request | Yes: revise combined request |
| Create for All organizations or OrganizationId -1 | Blocking |  | Any attempted parent create, including a combined create | Only update existing transaction types with native EnabledForAllOrgsFlag true through the existing protected parent reference | No: cannot create this parent |
| Add or redefine a transaction type for All organizations or OrganizationId -1 | Blocking | resolve_electronic_signature_parent_child | Request adds a child, upserts a missing child, replaces or renames an existing transaction type, or changes its transaction code or parent/child identity rather than using those values as verified references | The protected transaction-type set is limited to rows already present in the system under the existing -1 parent. Only update signature settings on a uniquely verified existing child; never create a missing row or alter its transaction identity | No: cannot add or redefine protected transaction types |
| Update an existing child for All organizations or OrganizationId -1 | Blocking | resolve_electronic_signature_parent_child | Selected existing child EnabledForAllOrgsFlag is false | Refuse both SignatureEnabledFlag and SignatureType/SignatureTypeCode changes, including Deferred or Inline. Existing membership alone is insufficient; only native true children are eligible, subject to all other gates | No: transaction is ineligible for this scope |
| Create transaction types for an ordinary organization | Blocking | select_electronic_signature_create_transactions | An explicitly requested creation transaction has catalog EnabledForAllOrgsFlag true | Create all and only catalog false transactions in the combined parent request; refuse explicitly requested excluded transactions rather than silently dropping them. Never add a true transaction for an ordinary organization | No: transaction is ineligible for this scope |
| Update transaction types for an ordinary organization | Blocking | resolve_electronic_signature_parent_child | Selected existing child EnabledForAllOrgsFlag is true | Refuse both SignatureEnabledFlag and SignatureType/SignatureTypeCode changes, including Deferred or Inline. Only native false children are eligible for ordinary organizations, subject to all other gates | No: transaction is ineligible for this scope |
| Evaluate child update eligibility | Blocking | resolve_electronic_signature_parent_child | Selected existing child EnabledForAllOrgsFlag is missing, null or nonboolean | Stop; do not infer eligibility from membership, organization, display name or signature editability | No: verified eligibility is required |
| Attempt to change EnabledForAllOrgsFlag | Blocking |  | Request treats the eligibility flag as a writable attribute or changes it to bypass scope restrictions | Use the catalog flag for creation selection and the existing child flag for update eligibility as read-only evidence; never include it as a requested mutation | No: eligibility is read-only |
| Update electronicSignaturePreferences | Blocking |  | Any parent data update for any organization | Update only electronicSignatureTransactionTypes through the parent reference; do not PATCH parent attributes | Yes: change scope to child update |
| Update electronicSignatureTransactionTypes | Blocking | resolve_electronic_signature_parent_child | Missing verified parent or child reference | Update existing child data through its parent reference, including the existing All organizations parent | Yes: resolve references |
| Delete an ordinary electronicSignaturePreferences parent | Blocking | resolve_electronic_signature_parent_child | Delete plan omits its dependent transaction types | Delete the parent only; deletion must cascade to its electronicSignatureTransactionTypes data and be verified afterward | Yes: include cascading effect in preview |
| Delete electronicSignatureTransactionTypes alone | Blocking |  | Any standalone child delete | Child data may be removed only by deleting its eligible parent | No: standalone child deletion prohibited |
| Delete All organizations or OrganizationId -1 parent | Blocking |  | Any attempt to delete the protected parent | Keep the parent and update existing child transaction types through its reference | No: protected parent cannot be deleted |
| Combined create for an ordinary organization | Blocking | select_electronic_signature_create_transactions | The nested child set omits eligible transaction types or includes types excluded by the resolver | Include all and only transaction types selected by the create resolver in the same parent create | Yes: rebuild the child set |
| Combined create with an explicit transaction signature type request | Blocking | read_electronic_signature_create_editability | Requested type differs from the catalog type and the derived SignatureModeEditableFlag is false | Refuse the incompatible type request using the noneditable-type message in ora_error_handling.md; retain the derived flag and never change it to permit an override | No: cannot override noneditable type |
| Combined create with explicit enablement or permitted type requests | Blocking |  | Prepared child values do not follow ora_defaulting_rules.md, or the plan splits these creation-time requests into a separate update load | Include final enablement and permitted type values in the same combined parent and eligible-child creation | Yes: rebuild the combined creation before preview |
| Update child SignatureType or SignatureTypeCode | Blocking | read_electronic_signature_child_editability | Current selected child has SignatureModeEditableFlag false | Refuse the type change with the message defined in ora_error_handling.md; a direct code does not bypass editability | No: cannot override noneditable type |
| Update child type after editability is true | Blocking | resolve_electronic_signature_type_code | An unsupported direct code is supplied, or the supplied label cannot resolve uniquely | Use ORA_DEFERRED or ORA_INLINE directly, or the lookup-derived code for Deferred or In-line; lookup required only for label input | Yes: correct the input or resolver result |
| Update child SignatureEnabledFlag only | Blocking | resolve_electronic_signature_parent_child | Existing parent/child references cannot be verified | Allow true or false only after EnabledForAllOrgsFlag passes organization-scope eligibility through the existing parent reference; SignatureModeEditableFlag restricts type changes, not this flag-only update | Yes: correct references or the boolean |

Review coverage: [synthetic editability, scope and lifecycle scenarios](#synthetic-review-scenarios).

## Design Lookup Requirements

| Resolver | When Required | Values Needed | Source File |
|---|---|---|---|
| resolve_electronic_signature_parent_child | Before child update or ordinary parent delete; also before evaluating protected transaction-type membership | Verified parent reference and, for updates, verified child reference with its existing TransactionTypeCode and native EnabledForAllOrgsFlag for scope eligibility, including enablement-only updates; no new or replacement child identity | ora_reference_lookups.md |
| select_electronic_signature_create_transactions | Before ordinary combined create | Complete eligible transaction-type set | ora_reference_lookups.md |
| read_electronic_signature_create_editability | Before accepting a user-requested creation type different from the catalog | Each selected child derived SignatureModeEditableFlag | ora_reference_lookups.md |
| read_electronic_signature_child_editability | Before any child type update | Current selected child SignatureModeEditableFlag | ora_reference_lookups.md |
| resolve_electronic_signature_type_code | Before a label-based child type update after editability passes | Uniquely resolved SignatureTypeCode | ora_reference_lookups.md |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| ESIGN.ENFORCE_POLICY | decision | 9 | design_enforcement | compliant->ESIGN.CHECK_HANDOFF;blocked->ESIGN.ISSUES | ESIGN.RESOLVE_SIGNATURE_TYPE | stop | Every request; developer-confirmed chat request and Data Loader captured records supply local evaluation authority |

Oracle publishes parent PATCH and standalone child POST/DELETE, but they remain prohibited by the developer-defined task policy. Endpoint availability is not task authorization. Source: [parent endpoints](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/api-manufacturing-electronic-signature-preferences.html), [child endpoints](https://docs.oracle.com/en/cloud/saas/supply-chain-and-manufacturing/26c/fasrp/api-manufacturing-electronic-signature-preferences-electronic-signature-transaction-types.html).

## Synthetic Review Scenarios

These review fixtures exercise [Design Rules](#design-rules). Use synthetic
ordinary OrganizationId 100000000000001 and transaction TEST_TXN_A; protected
scope variants are All organizations, numeric -1 and string "-1". No live parent
or child key is supplied. Assume unique verified references and all other gates
pass unless stated otherwise. Eligibility evidence is the catalog flag for
creation and the selected existing child REST flag for updates. Evaluate each
listed operation and value independently. Eligible outcomes still require Data
Loader preflight and approval; these fixtures are not execution results.

| Scenario | Input and supplied facts | Expected outcome |
|---|---|---|
| ESIGN-POLICY-01 | Ordinary create: catalog mode ORA_DEFERRED, derived editability false; request Inline or ORA_INLINE | Refuse before preview with exactly: You can not update the SignatureType. Preserve derived editability; do not change it to permit the override |
| ESIGN-POLICY-02 | Ordinary create: catalog mode ORA_DEFERRED, derived editability false; explicitly request ORA_DEFERRED | Retain the catalog type; no different-type override is attempted |
| ESIGN-POLICY-03 | Scope-eligible existing child: current editability false; request a different type by label or supported direct code | Refuse with exactly: You can not update the SignatureType. Direct codes do not bypass current editability |
| ESIGN-POLICY-04 | Protected existing child: EnabledForAllOrgsFlag false, editability true; request enabled true, enabled false, Deferred or In-line | Refuse every signature-setting change before preview despite existing membership and editable mode |
| ESIGN-POLICY-05 | Protected existing child: EnabledForAllOrgsFlag true, editability true; request enabled true, enabled false, ORA_DEFERRED or ORA_INLINE | Eligible through its verified parent/child reference; preserve transaction identity and the existing transaction-type set |
| ESIGN-POLICY-06 | Protected scope: attempt parent creation or deletion, or add/upsert a transaction absent from the existing children | Refuse before preview for every protected scope variant; neither parent creation nor a missing-child upsert is permitted |
| ESIGN-POLICY-07 | Ordinary create: catalog A has EnabledForAllOrgsFlag true and B has false; first explicitly request A, then evaluate a separate request without A | Refuse the explicit A request rather than silently dropping it. In the separate request, exclude A and include eligible B in the complete combined child set |
| ESIGN-POLICY-08 | Ordinary existing child: EnabledForAllOrgsFlag true, editability true; request enabled true, enabled false, Deferred or In-line | Refuse every signature-setting change before preview |
| ESIGN-POLICY-09 | Ordinary create with catalog flag false, or ordinary existing-child update with child flag false | Eligible subject to lifecycle, defaults, type editability and remaining gates; update eligibility comes from the child, not catalog membership |
| ESIGN-POLICY-10 | Existing-child update in either scope: eligibility is missing, null, string "true" or string "false" | Block before preview for each variant; require native boolean evidence from the selected child |
| ESIGN-POLICY-11 | Request mutates EnabledForAllOrgsFlag to obtain eligibility; alternatively, a protected request renames/replaces a transaction or changes its code or parent/child identity | Refuse; eligibility and transaction identity remain read-only selection evidence |
| ESIGN-POLICY-12 | Ordinary creation derives editability from a matching protected child whose EnabledForAllOrgsFlag is false | Permit the documented read-only derivation; it authorizes no update to that protected child |
| ESIGN-POLICY-13 | Ordinary parent-only create, standalone child create/delete, parent update, or combined creation omitting an eligible child | Refuse before preview; preserve the combined lifecycle and complete eligible-child set |
| ESIGN-POLICY-14 | Ordinary parent deletion with verified reference | Eligible only when preview includes dependent children and post-load verification follows the Business Verification contract; no standalone child deletion |

Related coverage: [creation defaults and update preservation](ora_defaulting_rules.md#synthetic-review-scenarios)
and [literal rejection](ora_input_validation.md#synthetic-review-scenarios).
Diagnostics and post-load checks remain owned by
[Error Handling](ora_error_handling.md#error-situations) and
[Business Verification](ora_error_handling.md#business-verification).
