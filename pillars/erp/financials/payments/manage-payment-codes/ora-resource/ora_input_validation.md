# Manage Payment Codes — Input Validation

<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: IBY_PAYMENT_CODE::PaymentCodeType, IBY_PAYMENT_CODE::PaymentCode, IBY_PAYMENT_CODE::TerritoryCode, IBY_PAYMENT_CODE::FormatValue, IBY_PAYMENT_CODE::Meaning, IBY_PAYMENT_CODE::StartDate, IBY_PAYMENT_CODE::Description, IBY_PAYMENT_CODE::EndDate, IBY_PAYMENT_CODE::EndDateDsp, IBY_PAYMENT_CODE::Code -->
<!-- fscr-update-fields: IBY_PAYMENT_CODE::TerritoryCode, IBY_PAYMENT_CODE::FormatValue, IBY_PAYMENT_CODE::Meaning, IBY_PAYMENT_CODE::StartDate, IBY_PAYMENT_CODE::Description, IBY_PAYMENT_CODE::EndDate, IBY_PAYMENT_CODE::EndDateDsp -->

Model/UI requiredness is distinct from proven CSV import requiredness. Source-backed create and same-key update scope does not prove null/omission behavior. Run Book owns intake and Data Loader owns package assembly. Neither package membership nor update exposure establishes direct translation ownership.

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Root identity | IBY_PAYMENT_CODE.PaymentCodeType + PaymentCode; source-proven EO primary/alternate key | Stop; never infer identity from row order | Supply canonical type and portable code; SRC-CS-EO, SRC-CS-VO | Create and update | resolve_payment_code_type |
| Root model values | Meaning, StartDate, EndDate and service Code required by reviewed model | Stop before preview when a required serialized value is unresolved | Serialize explicit Meaning and Code equal to PaymentCode, and explicit valid StartDate/EndDate with consistent EndDateDsp. The live FSM converter selects declared metadata/header fields, transforms known date strings and passes XML to the task reader; do not rely on a blank CSV value retaining an EO default; SRC-CS-VO, SRC-CS-EOJAVA, SRC-CS-AMIMPL, SRC-CS-FSM-MIGRATOR, SRC-CS-FSCORE-CSVXML | Create | |
| Translation identity/context | PaymentCode + PaymentCodeType + Language; SourceLang required by TL EO | Stop before preview for a missing parent pair, Language or SourceLang, duplicate child triple, unqualified generated inventory, or direct translation input | Preserve existing child inputs and match the exact parent pair. Root create requires source-qualified framework-generated identities; never infer a missing language or source language. Direct translation writes remain excluded; SRC-CS-TLEO, SRC-CS-TLLINK, SRC-CS-APPLCORE-TL-CREATE | Package contains translations or root create generates children | resolve_payment_code_language |

## Dependency-Aware Validation

| Applies When | Result | Next Action | Resolver |
|---|---|---|---|
| Country supplied | Requires current-environment reference verification | Run the exact public-preflight resolver through the declared native client and require a unique current code/label match; stop on denied or incomplete reads | resolve_payment_code_country |
| Translation rows included or generated | Parent pair must match root and both IBY_PAYMENT_CODE parent-link columns | Preserve existing translation CSV inputs unchanged. Root create submits no new direct child rows and requires a complete fresh installed-language inventory and exact generated-key reconciliation contract. Before preview, derive exact expected effects and qualify the reconciliation contract for root Meaning/Description propagation; otherwise stop. Verify actual effects against the fresh post-import export afterward. Direct translation operations remain excluded; SRC-CS-TLEO, SRC-CS-TLASSOC, SRC-CS-AMIMPL, SRC-CS-APPLCORE-TL-CREATE, SRC-CS-APPLCORE-TL-UPDATE | resolve_payment_code_language |
| Before create/update preview | Existence, no-op and update identity require complete baseline | Obtain a fresh, unfiltered current-data export through shared.setup-export.task-level-export for IBY_MANAGE_PAYMENT_CODES; validate its completed same-environment/task/user manifest and both CSV members, then evaluate the complete root file by exact composite key. Template-only and public LOV results are insufficient; SRC-FSM-CURRENT-20261006, SRC-CS-AMIMPL, SRC-CS-VO | find_payment_code_by_key |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Execution authority | User-declared local authority: reviewed task ora-resource tables. Evaluate Type through resolve_payment_code_type, lengths through this file's String Size Boundaries, and key/seeded restrictions through the Design Rules. This scope does not authorize CSV defaults, reference populations or complete environment baseline claims | Before static Type, length, key and seeded checks | |
| Exact CSV shape | Template owns member names and header order; reject short/extra fields and retain trailing blanks; metadata node paths and entity-specific sequences must match; SRC-FSM-PACKAGE | Package validation | |
| Type domain | Normalize only documented labels/codes through owning resolver; no UI indices or arbitrary strings | Type supplied | resolve_payment_code_type |
| Source lengths | Enforce the exact entity-field maxima below before candidate generation; report actual/max/unit and ask for corrected text; never truncate; SRC-CS-EO, SRC-CS-TLEO | String values supplied | |
| Dates | Root EndDate >= StartDate; FND:::FND_CMN_FRM_ERLY_EQ_TO_DATE. Serialize explicit nonblank StartDate and EndDate as strict valid YYYY/MM/DD; EndDateDsp is blank for EndDate 4712/12/31 and equals the finite EndDate otherwise. The framework maps this format to yyyy-MM-dd before the task XML reader. Reject malformed/locale-ambiguous dates and inconsistent EndDate pairs; keep the template headers. A blank CSV cell is not an instruction to preserve a value or use a default; SRC-CS-EO, SRC-CS-EOJAVA, SRC-FSM-PACKAGE, SRC-CS-FSM-MIGRATOR, SRC-CS-FSCORE-CSVXML, SRC-CS-FSCORE-XMLCONSTANTS | Root date values supplied | |
| Paired transients | Create Code must equal PaymentCode. Existing-row update preserves the exported Code cell and must not populate this insert-only-key setter. EndDateDsp is derived from EndDate: blank for the sentinel, equal for a finite date; SRC-CS-EOJAVA | Root Code or EndDateDsp present | |
| History fields | Retain all template columns. On create serialize empty history cells; on update retain the exported history cells without accepting implementor changes. Both service VOs mark these attributes non-updateable, and the FSM FAQ states readXML ignores non-updateable attributes. Their XML presence does not authorize audit mutation. Exclude history values from business-effect comparison; SRC-CS-VO, SRC-CS-TLVO, SRC-INTERNAL-FSM-FAQ | Create/update | |
| Unknown fields | Reject unsupported field mapping; derived UI Status is outside the CSV package; SRC-CS-UIVO, SRC-FSM-PACKAGE | Intake/package mapping | |

## Complete Attribute Dispositions

| Entity | Field | Create | Update | Boundary | Source IDs |
|---|---|---|---|---|---|
| IBY_PAYMENT_CODE | PaymentCodeType | supported | unsupported | Composite identity; while-insert only | SRC-CS-VO, SRC-CS-EO |
| IBY_PAYMENT_CODE | PaymentCode | supported | unsupported | Composite identity; while-insert only | SRC-CS-VO, SRC-CS-EO |
| IBY_PAYMENT_CODE | TerritoryCode | supported | supported | Seeded Y prohibits change; partial resolver | SRC-CS-EOJAVA, SRC-CS-UIVO |
| IBY_PAYMENT_CODE | FormatValue | supported | supported | Alias; no task default | SRC-CS-VO, SRC-CS-EO |
| IBY_PAYMENT_CODE | CreatedBy | unsupported | unsupported | Read-only framework history | SRC-CS-VO, SRC-CS-EO |
| IBY_PAYMENT_CODE | SeededFlag | unsupported | unsupported | Read-only; EO default N; not a business Boolean | SRC-CS-VO, SRC-CS-EO |
| IBY_PAYMENT_CODE | LastUpdatedBy | unsupported | unsupported | Read-only framework history | SRC-CS-VO, SRC-CS-EO |
| IBY_PAYMENT_CODE | CreationDate | unsupported | unsupported | Read-only framework history | SRC-CS-VO, SRC-CS-EO |
| IBY_PAYMENT_CODE | LastUpdateLogin | unsupported | unsupported | Read-only framework history | SRC-CS-VO, SRC-CS-EO |
| IBY_PAYMENT_CODE | LastUpdateDate | unsupported | unsupported | Read-only framework history | SRC-CS-VO, SRC-CS-EO |
| IBY_PAYMENT_CODE | Meaning | supported | supported | Name; model required; seeded Y prohibits change | SRC-CS-EO, SRC-CS-EOJAVA, SRC-UI-CREATE |
| IBY_PAYMENT_CODE | StartDate | supported | supported | Model required; database-current-date default | SRC-CS-EO, SRC-CS-EOJAVA |
| IBY_PAYMENT_CODE | Description | supported | supported | Optional; seeded Y prohibits change | SRC-CS-EO, SRC-CS-EOJAVA |
| IBY_PAYMENT_CODE | EndDate | supported | supported | Model required; sentinel default; effective dating | SRC-CS-EO, SRC-CS-EOJAVA |
| IBY_PAYMENT_CODE | EndDateDsp | supported | supported | Transient setter affects EndDate | SRC-CS-EOJAVA |
| IBY_PAYMENT_CODE | Code | supported | unsupported | Transient setter changes existing identity; no getter-derived default proven | SRC-CS-VO, SRC-CS-EOJAVA |
| IBY_PAYMENT_CODE_TRANSLATION | PaymentCode | unresolved | unresolved | Triple key and parent pair known; direct lifecycle TBD | SRC-CS-TLEO, SRC-CS-TLLINK |
| IBY_PAYMENT_CODE_TRANSLATION | PaymentCodeType | unresolved | unresolved | Triple key; parent match; type domain known; direct lifecycle TBD | SRC-CS-TLEO, SRC-CS-TLLINK, SRC-CS-TYPESEED |
| IBY_PAYMENT_CODE_TRANSLATION | Language | unresolved | unresolved | Independent direct input remains unqualified/excluded. Preserve existing cells; framework root create uses every installed I/B language | SRC-CS-TLEO, SRC-CS-APPLCORE-TL-CREATE, SRC-CS-APPLCORE-LANGUAGES |
| IBY_PAYMENT_CODE_TRANSLATION | SourceLang | unresolved | unresolved | Independent direct input remains unqualified/excluded. Preserve existing cells; framework-generated value is session-derived, never a hard-coded CSV default | SRC-CS-TLEO, SRC-CS-APPLCORE-TL-CREATE, SRC-CS-APPLCORE-TL-UPDATE |
| IBY_PAYMENT_CODE_TRANSLATION | Meaning | unresolved | unresolved | Direct lifecycle/serialization TBD | SRC-CS-TLEO, SRC-CS-TLVO |
| IBY_PAYMENT_CODE_TRANSLATION | Description | unresolved | unresolved | Direct lifecycle/serialization TBD | SRC-CS-TLEO, SRC-CS-TLVO |
| IBY_PAYMENT_CODE_TRANSLATION | CreatedBy | unsupported | unsupported | Read-only framework history | SRC-CS-TLVO, SRC-CS-TLEO |
| IBY_PAYMENT_CODE_TRANSLATION | CreationDate | unsupported | unsupported | Read-only framework history | SRC-CS-TLVO, SRC-CS-TLEO |
| IBY_PAYMENT_CODE_TRANSLATION | LastUpdatedBy | unsupported | unsupported | Read-only framework history | SRC-CS-TLVO, SRC-CS-TLEO |
| IBY_PAYMENT_CODE_TRANSLATION | LastUpdateDate | unsupported | unsupported | Read-only framework history | SRC-CS-TLVO, SRC-CS-TLEO |
| IBY_PAYMENT_CODE_TRANSLATION | LastUpdateLogin | unsupported | unsupported | Read-only framework history | SRC-CS-TLVO, SRC-CS-TLEO |

## String Size Boundaries

ADF precision and persistence limits are separate evidence. SRC-CS-EO declares root PaymentCodeType precision 100, but SRC-EDM-PC-B-26D and SRC-CS-PC-PEO establish a persistence/public-entity limit of 30. Enforce only the five canonical ASCII Type codes and retain 30 as the effective Type ceiling; do not permit arbitrary 100-character types. The 26D TL table corroborates its 30/4/80/240 lengths and parent keys (SRC-EDM-PC-TL-26D). Database documentation does not state byte-versus-character semantics for arbitrary Unicode; the other entries retain their reviewed ADF character precision. Audit lengths describe model shape, not editable inputs.

| Entity | Field | Maximum | Unit | Source IDs |
|---|---|---|---|---|
| IBY_PAYMENT_CODE | PaymentCodeType | 30 | characters; canonical ASCII Type codes only | SRC-CS-EO, SRC-CS-PC-PEO, SRC-EDM-PC-B-26D |
| IBY_PAYMENT_CODE | PaymentCode | 30 | characters | SRC-CS-EO |
| IBY_PAYMENT_CODE | TerritoryCode | 2 | characters | SRC-CS-EO |
| IBY_PAYMENT_CODE | FormatValue | 80 | characters | SRC-CS-EO |
| IBY_PAYMENT_CODE | Meaning | 80 | characters | SRC-CS-EO |
| IBY_PAYMENT_CODE | Description | 240 | characters | SRC-CS-EO |
| IBY_PAYMENT_CODE | CreatedBy | 64 | characters | SRC-CS-EO |
| IBY_PAYMENT_CODE | LastUpdatedBy | 64 | characters | SRC-CS-EO |
| IBY_PAYMENT_CODE | LastUpdateLogin | 32 | characters | SRC-CS-EO |
| IBY_PAYMENT_CODE | SeededFlag | 1 | characters | SRC-CS-EO |
| IBY_PAYMENT_CODE_TRANSLATION | PaymentCodeType | 30 | characters | SRC-CS-TLEO |
| IBY_PAYMENT_CODE_TRANSLATION | PaymentCode | 30 | characters | SRC-CS-TLEO |
| IBY_PAYMENT_CODE_TRANSLATION | Language | 4 | characters | SRC-CS-TLEO |
| IBY_PAYMENT_CODE_TRANSLATION | SourceLang | 4 | characters | SRC-CS-TLEO |
| IBY_PAYMENT_CODE_TRANSLATION | Meaning | 80 | characters | SRC-CS-TLEO |
| IBY_PAYMENT_CODE_TRANSLATION | Description | 240 | characters | SRC-CS-TLEO |
| IBY_PAYMENT_CODE_TRANSLATION | CreatedBy | 64 | characters | SRC-CS-TLEO |
| IBY_PAYMENT_CODE_TRANSLATION | LastUpdatedBy | 64 | characters | SRC-CS-TLEO |
| IBY_PAYMENT_CODE_TRANSLATION | LastUpdateLogin | 32 | characters | SRC-CS-TLEO |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MPC_VALIDATE_INPUT | step | 10 | validate_input | valid->MPC_DEPENDENCIES;invalid->MPC_HANDLE_ISSUES;missing->MPC_HANDLE_ISSUES | none | stop | Selected task create/update request |
