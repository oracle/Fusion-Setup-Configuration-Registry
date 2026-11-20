# Manage Payment Methods dependency readiness

## Required Dependency Order

| Sequence | Dependency | What Must Happen |
|---|---|---|
| 1 | Payment method parent | Confirm unique code and intended create/update state before child data; SRC-FSM-PACKAGE, SRC-CODE-IBY-SVC-AM-IMPL |
| 2 | Applicability and translation | Bind child values to the selected parent; SRC-CODE-IBY-SVC-CHILD-VOS, SRC-CODE-IBY-SVC-TL-VO |
| 3 | Validation assignment and values | Use configured validation set and parameter context; SRC-CODE-IBY-SVC-ASSIGN-VO, SRC-CODE-IBY-SVC-VALUE-VO |

## Dependency Rules

| Dependency ID | Dependency | Mandatory | Applies When | Status | Value Source | Resolver | Why | User Guidance | Values to Fill |
|---|---|---|---|---|---|---|---|---|---|
| PM-PARENT | Payment method parent | Yes | Every child row | Verify | Fresh same-environment, same-task FSM export plus explicit same-candidate parent creates | resolve_setup_payment_method_by_code | Child graph refers to the setup parent; SRC-CODE-IBY-SVC-AM-IMPL; SRC-REVIEW-PM-LOV-SCOPE | Resolve exactly one immutable PaymentMethodCode in ORA_IBY_FD_PARENT_PAY_MET, or one explicit same-candidate create with no baseline collision. Missing, duplicate, conflicting or stale parent evidence blocks the child. Preserve assignment-context and import-side-effect checks. | PaymentMethodCode |
| PM-BU | Business unit | Conditional | BuName supplied | Verify | Current environment business unit | find_business_unit_by_name | Import resolver uses enterprise context; SRC-CODE-IBY-SVC-AM-IMPL | Resolve one active context-appropriate BU | BusinessUnitId |
| PM-LE | Legal entity | Conditional | LEName supplied | Verify | Current environment legal entity identifier (CSV LEName) | find_legal_entity_by_identifier | Import resolver uses legal entity alternate key; SRC-CODE-IBY-SVC-AM-IMPL | Resolve one context-appropriate identifier; display Name alone is insufficient | LegalEntityIdentifier and LegalEntityId |
| PM-VALIDATION | Validation set and parameter | Conditional | Validation child supplied | Blocked | Configured validation set and parameter supplied by implementor |  | Configured set and parameter acceptance is unverified; SRC-CODE-IBY-SVC-ASSIGN-VO | Review candidate in controlled environment before import | ValidationSetCode and ValidationParameterCode |

## Dependency Classification

| Result Category | When Used | Can Run Lookup/Create? |
|---|---|---|
| Verify | A supported read-only preflight exists | Lookup only |
| Blocked | Resolver or configured value contract is partial | No |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| PM.DEPENDENCIES | step | 20 | resolve_dependency | ok->PM.LOOKUP;blocked->PM.RETURN_ISSUES | PM.VALIDATE | stop | Every request |


## Source-reviewed import side effects

Sources: SRC-DEBUG-IMPORT; SRC-REVIEW-PARENT-IMPL. These rules are source-confirmed; deployed behavior remains separately qualified.

- For a serialized payment-method parent, AP/AR/CE flag N can remove that application's existing usage rows, including a retained N flag on an unrelated parent edit. Inspect the fresh baseline and stop if this would violate preserved-row create/update. Do not treat the deletion as an implicit approved operation.
- Moving PAYER_ORG to blank all-BU scope can consolidate/remove existing specific-BU rows. Stop preserved-row create/update when those rows exist in the same method/application context.
- A seeded parent is removed from the import XML by the source hook; reject a request that would otherwise claim to update it.
- At least one of AP, AR or CE must remain enabled. Do not infer missing enablement flags or serialize defaults to satisfy this rule.
- Source-confirmed lookup mapping is distinct from environment identity/cardinality and live import qualification. A ready orchestration node means it can evaluate these conditional gates; it does not satisfy every resolver for every request.

## Validation assignment package dependencies

A validation parameter create/update package must contain its exact assignment
parent and owning format/payment-method parent. The runtime carries required
existing ancestors from the fresh baseline, preserving business values and
blanking import audit fields. These dependencies are not additional requested
business changes. Explicit parent operations take precedence. Missing or
ambiguous parents, changed dependency content and unrelated rows fail validation.
For Payment Methods, existing parent identity and import-side-effect checks also
apply to included dependencies. Verify the requested parameter and preservation
of all other business values through a fresh export after import.
