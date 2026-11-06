Source: developer-provided creation requirements and follow-up organization, transaction-selection and signature-update steps. Only supplied contracts are resolved; remaining TBD fields block execution.

# Error Handling and Execution Gate

Reviewers: SCM pillar development lead and FSCR QA.

## Error Situations

| Situation | What Should Happen |
|---|---|
| Workflow failure or preflight blocker | Classify the failure using governance/error-handling-guidelines.md. Stop on invalid inputs, catalog mismatch, missing privileges, missing source or approval blockers |
| Cache-managed token rejected during an eligible read-only request | Delegate authentication handling to core; refresh the rejected token once only under the core read-only recovery workflow |
| Data Loader polling timeout | Use core.data-loader's bounded wait and polling policy. Stop and report the operation, environment, external request/job ID, last status, elapsed wait and next-check path |
| Any supplied or derived SignatureTypeCode other than ORA_INLINE or ORA_DEFERRED | Stop before preview or submission with input_validation; return exactly: Invalid Signature Type |
| Prepared signature boolean is capitalized or is a quoted JSON string | Stop before preview with input_validation. Creation applies the per-transaction enablement rule in ora_defaulting_rules.md; enablement passes lowercase true and disablement or unspecified creation enablement passes lowercase false. Validate both signature boolean fields against ora_input_validation.md; correct the source and start fresh validation, rather than changing an approved captured load |
| Fusion rejects SignatureEnabledFlag with value False | Preserve the failed load and its diagnostic; no successful creation or enablement may be claimed. Correct the source's boolean representation to lowercase true or false as appropriate, revalidate in a fresh Data Loader session, and obtain its approval before any resubmission; do not automatically retry the failed load |
| Missing runtime contract | Stop if Data Loader preflight cannot validate registered hierarchy, attributes, lossless identifier serialization or required access; input authority is explicitly developer-confirmed and business verification is defined below. Do not invent metadata or substitute direct REST writes |
| Prohibited lifecycle operation | Classify input_validation; disclose the violated design rule before preview |
| Attempt to create the All organizations / -1 parent or add, upsert, replace or redefine its transaction types | Stop before preview or submission with input_validation. Disclose that the protected parent cannot be created and its transaction-type set cannot be extended or redefined. A missing child is not permission to create it; only signature-setting updates on verified existing children with EnabledForAllOrgsFlag true are eligible |
| Protected child update has EnabledForAllOrgsFlag false, or ordinary creation/update requests a true transaction | Stop before preview or submission with input_validation. Identify the scope mismatch: All organizations / -1 permits signature-setting updates only on existing true children; ordinary organizations permit creation and updates only for false transaction types. Refuse enablement and Deferred/Inline changes alike; do not change the eligibility flag or silently omit an explicitly requested ineligible transaction |
| Existing child update eligibility flag is missing, null or nonboolean | Stop with catalog_or_metadata_mismatch; obtain authoritative child REST evidence before a fresh validation. Never assume eligibility from existing membership or convert strings to booleans |
| Request changes EnabledForAllOrgsFlag | Stop before preview with input_validation; eligibility is read-only and cannot be changed to bypass organization-scope restrictions |
| Missing or ambiguous reference | Stop with catalog_or_metadata_mismatch; do not choose the first parent or child |
| Uncertain mutation outcome | Stop; reconcile prior side effects through routed read-only verification before any approved resubmission. Do not replay an uncertain write or automatically compensate by deletion |
| Supplied ordinary OrganizationId fails LOV validation, or supplied OrganizationCode/OrganizationName cannot yield a unique OrganizationId | Stop with input_validation and return exactly: Invalid Organization |
| Child type update has current SignatureModeEditableFlag false, or a creation request asks for a type different from the catalog with derived SignatureModeEditableFlag false | Stop with input_validation and return exactly: You can not update the SignatureType. |
| Signature type label lookup fails or child editability is absent/ambiguous | Stop; do not guess a code or assume the child is editable |
| Create transaction selection is incomplete | Stop before preparing a combined create; do not submit a parent-only create or silently drop eligible children |
| Public API lists a task-prohibited operation | Preserve the developer prohibition; do not enable parent PATCH or independent child POST/DELETE |

## Disclosure Rules

| Gate | What Must Be Shown |
|---|---|
| Resource read order | Read the task-local ora_rule_registry.json and its source anchors in this order: ora_input_validation.md, ora_reference_lookups.md, ora_defaulting_rules.md, ora_design_enforcement.md, then ora_error_handling.md before preview or execution |
| Authoring readiness | Require the registry planner to return planned with readiness ready, without a readiness override. Missing, inconsistent or incomplete resource contracts block implementation. Authoring readiness and generated REST routing metadata do not establish live privileges, BO registration, supported operations, registered metadata or serialization; require the separate Data Loader runtime preflight below |
| Before Data Loader handoff | Task identity, target environment, organization scope, operation, exact immutable artifact and affected parent/children; core.data-loader artifact preparation and registered metadata own the write payload and serialization. Use its approval workflow once; direct business-resource REST calls are read-only derivation/validation only |
| Delete preview | Ordinary parent deletion includes all dependent transaction types; protected -1 parent and standalone child deletes must be refused |
| Data Loader scope | Route every setup-data write only through core.data-loader. Use top BO electronicSignaturePreferences, UI name Electronic Signature Preferences, and its child electronicSignatureTransactionTypes, UI name Electronic Signature Transaction Types. Limit registration and operation support to this hierarchy, combined creation, parent-referenced child updates and parent deletion; preserve all lifecycle restrictions. Other REST calls may only derive or validate attribute values and references; never use them as a write fallback |
| Runtime contract | Before handoff, require the routed preflight to validate project/workspace paths, environment identity, privileges, catalog flags, BO registration, nested payload shape, record keys and operation-specific policy. Read-only parent/child lookup paths and key resolution are documented in ora_reference_lookups.md; Data Loader hierarchy is electronicSignaturePreferences (Electronic Signature Preferences) with child electronicSignatureTransactionTypes (Electronic Signature Transaction Types); support is limited to hierarchy registration, combined create, parent-referenced child update and parent delete. Business verification is defined below. The chat request and Data Loader captured records are authoritative local inputs; core.data-loader owns registered-metadata, serialization and privilege preflight; failed checks block preview and execution |
| Diagnostic persistence | Persist redacted diagnostics, partial successes and errors in the active project's artifacts and state/runs; record token usage according to the task skill manifest |


## Business Verification

These are post-load result checks. They do not execute in the pre-load Task Hook,
replace Data Loader approval, or authorize a write. Data Loader initiation alone
is not completed creation, update or deletion. Apply the corresponding read-only
resolver only after the routed workflow confirms the operation completed without
error. Do not add automatic polling to Data Loader initiation; use its existing
status workflow when completion needs to be established.

| Situation | What Should Happen |
|---|---|
| Combined create completed without error | Use verify_electronic_signature_created_preferences. Confirm all selected transactions were created under the given organization with each final submitted SignatureTypeCode and SignatureEnabledFlag after creation defaults and permitted explicit requests. Report creation as verified only when every comparison passes |
| SignatureType and/or SignatureEnabled update completed without error | Use verify_electronic_signature_updated_transaction. Confirm each requested value matches the given input for the selected transaction under the given organization; only compare fields requested for update |
| Ordinary organization preferences delete completed without error | Use verify_electronic_signature_deleted_preferences. Recheck the same organization; zero existing parent rows confirms successful deletion. An existing row or a failed read does not confirm deletion |
| Business verification fails or is inconclusive | Disclose the mismatch or read failure and retain the successful load outcome separately from business verification. Do not mark the task verified or automatically repeat the write |

Lookup requests, matching and response mapping are owned by
ora_reference_lookups.md. The validation graph returns to Data Loader before any
write; these post-load contracts do not add write nodes or a direct REST route.

## Refusal Rules

| Situation | What Must Not Happen |
|---|---|
| Missing endpoint or authority, or missing/unsupported registered operation capability | Stop; if the adapter cannot express an allowed operation, record a workflow gap. Do not execute a write, infer local authority, hand-build business-resource write requests, use a direct REST write or browser fallback, or register the child BO as an independent create/delete route; keep REST attribute-derivation calls read-only |
| Mutation or import failure | Do not automatically retry POST, PATCH, DELETE or import without idempotency or explicit approval through the active workflow |
| Credential or sensitive runtime data | Do not print or persist credentials, tokens, private keys, sensitive payloads or customer identifiers in repository guidance |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| ESIGN.CHECK_HANDOFF | decision | 10 | execution_gate | ready->ESIGN.DONE_VALIDATION;blocked->ESIGN.ISSUES | ESIGN.ENFORCE_POLICY | stop | Only after contract completion; authorizes no mutation |
| ESIGN.DONE_VALIDATION | terminal | 11 | terminal | none | ESIGN.CHECK_HANDOFF | stop | Validation gates satisfied; return to core.data-loader for its preview and approval workflow |
| ESIGN.ISSUES | terminal | 12 | terminal | none | none | stop | Unsupported request or unresolved authoring/runtime contract; return blockers |
