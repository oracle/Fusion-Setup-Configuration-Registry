# Defaulting Rules

## Source Register

These developer-supplied sources were inspected for this authoring update. Identify the exact files by basename and SHA-256; retain originals in the authorized source location, outside the reusable skill package. Source documents supply design evidence, not execution authorization or verified current-release Oracle API contracts.

| Source ID | Source | Locator | SHA-256 |
|---|---|---|---|
| COA-DESIGN-2026-05 | COA Design Considerations_May2026.docx | Segment Considerations; Intercompany Segment; Future Segment; Appendix: Design Steps | edccf5b13ddc17a9f6c70ec70f190a0669a8e880ebf1102aef5463a9674f32b4 |
| COA-ATTRIBUTES | CoaAttributes.xlsx | Structures; Structure Segments; Instances; Instance Segments; Segment Labels sheets | 23824c063c2ea6d8f0d21aa010696b540d7cb5e565c29488c7c002b6954e93d6 |

## Guidance Sources

| Source Mode | Allowed Sources | When Used |
|---|---|---|
| Implementation design | COA-DESIGN-2026-05, exact section locators below | Design considerations; do not treat recommendations as mandatory Oracle product behavior |
| Attribute authoring | COA-ATTRIBUTES, exact sheet and row locators below | Requiredness, constants, references, and derivation notes actually populated in the workbook |
| Task policy | Existing rules in ora_input_validation.md, ora_defaulting_rules.md, and ora_design_enforcement.md | Preserve previously authored task policy; distinguish it from supplied-document evidence |
| Target metadata | Complete same-task export and the declared read-only lookup contracts | Target-specific shape and identifiers; these source documents do not establish API support or release currency |

## Source Mapping

| Rule or Decision | Source Evidence |
|---|---|
| Export-first default derivation and source order | Existing task policy below#source-precedence; target export is runtime evidence, not an attached source document |
| Structure attributes and requiredness | COA-ATTRIBUTES: Structures rows 2-8; Structure Segments rows 2-14 and 21; Instances rows 2-10 and 16; Instance Segments rows 2-13 and 19 |
| Segment-label import codes and target metadata | Existing ora_reference_lookups.md contracts and target export; COA-ATTRIBUTES Segment Labels row 6 identifies a derived field but does not specify the accepted internal codes |
| Value-set references | COA-ATTRIBUTES: Structure Segments row 21; Instance Segments row 19. Value-set creation belongs to its separate task. |
| Design review and segment distinctness | COA-DESIGN-2026-05: Segment Considerations / Segment Design and Segment Design Considerations |
| Basic segment proposal | COA-DESIGN-2026-05: Appendix: Design Steps / Step Two recommends the starting business dimensions. The skill's confirmation requirement and label assignments remain task policy. |
| Segment order and delimiter | Existing task policy below; COA-ATTRIBUTES Structures row 7 supplies the hyphen default. The design document does not establish a mandatory order or a delimiter whitelist. |
| Future segments | COA-DESIGN-2026-05: Future Segment treats reserved segments as a context-dependent design choice requiring governance. COASTR.006 remains the task policy requiring an approved exception; do not attribute a universal prohibition to the document. |
| Intercompany design | COA-DESIGN-2026-05: Intercompany Segment / Consistency of Values and Considerations: One v. Two Balancing Segments and Intercompany. Exact company/intercompany value compatibility remains the task's design check, not a claim that the document mandates identical sets. |
| Additional segments and missing COA identity | Existing task policy in ora_input_validation.md and ora_design_enforcement.md; do not infer approval to add segments from examples in COA-DESIGN-2026-05 |

## Evidence Boundaries

| Evidence Boundary | Required Handling |
|---|---|
| Original Oracle page list | Not supplied by the developer; the former references to listed Oracle pages and EDM pages are not evidence. Do not claim current-release Oracle verification from these two files. |
| Technical behavior absent from supplied files | Use only the existing documented task contract and qualified target evidence. Mark any newly required undocumented contract TBD and block that operation until an authorized source resolves it. |
| Workbook blank or Derived cells without an algorithm | Do not claim that the workbook specifies the skill's algorithm. Preserve the explicit task policy and report its separate provenance below. |
| Source distribution | Reference source identities and concise mappings only; the original documents are not packaged or cleared for publication by this authoring run. |

## Historical Advisory Source Corrections

The source register, mappings, and evidence boundaries above supersede the unlocated source attributions in the preserved legacy ora_design_advisory.md. In particular, its future-segment prohibition attribution is not supported by COA-DESIGN-2026-05; the existing approved-exception policy is a task policy. Its references to attached COA Best Practices and COA Attributes mean the exact files identified above, not separate unavailable attachments. Its generic listed Oracle or EDM pages are not supplied evidence.

## Source Precedence

| Sequence | Source | Use |
|---|---|---|
| 1 | Complete same-task FSM CSV export and ASM_SETUP_CSV_METADATA.xml | Reuse populated technical values, internal codes, column names, and accepted value forms |
| 2 | Supported read-only Fusion metadata | Resolve target-specific identifiers or lookups absent from the full export |
| 3 | COA-ATTRIBUTES: CoaAttributes.xlsx, identified in ora_defaulting_rules.md#source-register | Apply only populated workbook rules; do not infer algorithms from blank cells or Derived markers |
| 4 | Qualified Oracle functional and EDM documentation, when supplied through authorized documentation lookup | Resolve documented semantics only; no original Oracle page list was supplied with COA-ATTRIBUTES or COA-DESIGN-2026-05 |

Template-only exports may supplement the complete export for file shape, but must not replace the complete export.

## Source Interpretation

COA-ATTRIBUTES is the exact workbook identified by filename and hash in [the source register](#source-register). Sheet and row citations below refer to that file. Its blank cells and Derived markers do not specify every implementation algorithm. The following crosswalk separates workbook evidence from existing task policy without changing the current default values or approval gates.

| Field or Rule | Workbook Evidence | Task Policy Boundary |
|---|---|---|
| Name and Description | Structures rows 5-6 mark derivation but do not define the expression | Existing name and description derivations are authored task policy |
| SegmentCode, Name, Prompt | Structure Segments row 5 uses a COA-name placeholder; row 8 supplies no expression; row 10 references Name | The existing segment-name derivation is task policy, not a literal transcription of row 5; retain distinct user-confirmed segment identities |
| SegmentIdentifier | Structure Segments row 6 has no derivation algorithm | Use the existing user-provided derivation rule, not an inferred workbook rule |
| ColumnName and SequenceNumber | Structure Segments rows 7 and 12 mark derivation without an expression | SEGMENTn ordinal alignment and explicit-value warning/approval behavior are existing task policy |
| StructureInstanceIdentifier | Instances row 5 has no derivation algorithm | Existing identifier normalization is authored task policy |
| Optional instance segment fields | Instance Segments row 6 is blank; rows 9-10 mark derivation without a concrete default | Blank-unless-approved handling is existing task policy |
| SegmentLabelCode | Segment Labels row 6 marks derivation without internal code values | Resolve from qualified target metadata through ora_reference_lookups.md; the workbook does not prove internal label codes |

## Standard Defaults

| Field | Default Value | Applies When | Override User Value? | Source |
|---|---|---|---|---|
| KeyFlexfieldCode | GL# | User leaves it blank | No | COA-ATTRIBUTES: Structures row 2 |
| ApplicationId | 101 | User leaves it blank | No | COA-ATTRIBUTES: Structures row 3 |
| StructureCode | COA name with spaces replaced by underscores | User leaves it blank | No | COA-ATTRIBUTES: Structures row 4 |
| Name | COA name | User leaves it blank | Yes | COA-ATTRIBUTES: Structures row 5 |
| Description | Derived COA description | User leaves it blank | Yes | COA-ATTRIBUTES: Structures row 6 |
| Delimiter | - | User leaves it blank | Yes | COA-ATTRIBUTES: Structures row 7 |
| EnabledFlag | Y | User leaves it blank | Yes | COA-ATTRIBUTES: Structures row 8 |
| SegmentCode, Name, Prompt | User-provided segment name | Segment field is blank | No | Existing segment-name task policy; COA-ATTRIBUTES: Structure Segments rows 5, 8, and 10 have the limitations recorded above |
| SegmentIdentifier | Derive from SegmentCode: lowercase the complete code when it contains only letters and digits; otherwise remove each special character and uppercase its immediately following letter while lowercasing all other letters and preserving digits | Segment identifier is blank and every special character in SegmentCode is immediately followed by a letter | No | User-provided SegmentIdentifier derivation rule |
| ColumnName | Same-task full export; otherwise SEGMENT plus the user-supplied ordinal position | User leaves it blank | No | Complete FSM export first; existing ordinal task policy; COA-ATTRIBUTES: Structure Segments row 7 does not specify the expression |
| SequenceNumber | The ordinal in ColumnName: SEGMENT1 → 1, SEGMENT2 → 2, SEGMENT3 → 3, and so on | User leaves it blank | No | User direction; enforce one-to-one column and sequence alignment only for defaulted values |
| Explicit ColumnName and SequenceNumber | Preserve explicit user or workbook values even when they do not match the default ordinal rule | Both fields are supplied explicitly | No | User direction; readiness report must flag the mismatch and require approval |
| ShortPrompt | First three letters with initial capital for one word; initials for multiple words | User leaves it blank | Yes | COA-ATTRIBUTES: Structure Segments row 11 |
| EnabledFlag | Y | Segment enabled flag is blank | Yes | COA-ATTRIBUTES: Structure Segments row 13 |
| DisplayWidth | 6 | User leaves it blank | Yes | COA-ATTRIBUTES: Structure Segments row 14 |
| Segment value length | 6 | User leaves segment length blank | No | User-provided default-length rule; pass the resolved length to the referenced value set as MaximumLength |
| DefaultValueSetCode | Verified referenced ValueSetCode | User leaves it blank after a successful value-set lookup | No | Read-only value-set metadata; COA-ATTRIBUTES: Structure Segments row 21 |
| SegmentLabelCode | GL_BALANCING for Primary Balancing, FA_COST_CTR for Cost Center, GL_ACCOUNT for Natural Account, GL_INTERCOMPANY for Intercompany | User supplies the business classification but not an internal code | No | Same-task export first; ora_reference_lookups.md qualified-label resolver. COA-ATTRIBUTES does not specify the internal codes; unresolved code evidence blocks preview |
| StructureInstanceCode | COA name with spaces replaced by underscores | User leaves it blank | No | COA-ATTRIBUTES: Instances row 4 |
| StructureInstanceIdentifier | Uppercase the first letter, lowercase remaining letters, remove separators, and uppercase the following letter | User leaves it blank and every separator is immediately followed by a letter | No | Existing identifier task policy; COA-ATTRIBUTES: Instances row 5 has no algorithm |
| Structure instance Name | Structure Name | User leaves it blank | No | COA-ATTRIBUTES: Instances row 6 |
| Structure instance Description | Blank | User leaves it blank | Yes | COA-ATTRIBUTES: Instances row 7 does not provide a concrete default |
| Structure instance EnabledFlag | Y | User leaves it blank | Yes | COA-ATTRIBUTES: Instances row 8 |
| DynamicCombinationCreationAllowed | Y | User leaves it blank | Yes | COA-ATTRIBUTES: Instances row 9 |
| ShorthandAliasEnabledFlag | N | User leaves it blank | Yes | COA-ATTRIBUTES: Instances row 10 |
| Structure instance StructureCode | Resolved StructureCode | User leaves it blank | No | COA-ATTRIBUTES: Instances row 16 |
| Instance segment TreeCode | Blank | No approved hierarchy or tree design is supplied | Yes | COA-ATTRIBUTES: Instance Segments row 6 |
| Instance segment RequiredFlag | Y | User leaves it blank | Yes | COA-ATTRIBUTES: Instance Segments row 7 |
| Instance segment DisplayFlag | Y | User leaves it blank | Yes | COA-ATTRIBUTES: Instance Segments row 8 |
| Instance segment DefaultType and DefaultValue | Blank | No approved segment default is supplied | Yes | COA-ATTRIBUTES: Instance Segments rows 9 and 10 |
| Instance segment BIEnabledFlag | N | User leaves it blank | Yes | COA-ATTRIBUTES: Instance Segments row 12 |
| Instance segment QueryRequiredType | OPTIONAL | User leaves it blank | Yes | COA-ATTRIBUTES: Instance Segments row 13 |
| Instance segment ValueSetCode | Verified referenced ValueSetCode | User leaves it blank after successful value-set lookup | No | COA-ATTRIBUTES: Instance Segments row 19 |
| Basic segment design | Company as Primary Balancing, Cost Center as Cost Center, Account as Natural Account, and Intercompany as Intercompany | User makes a vague create request with no structural details; present as a proposal and wait for confirmation | No | User-provided vague-request rule |
| Additional segments | No default | Always | No | User-provided design boundary; additional segments must come from the user or an approved design source |
| COA identity | No default | COA Name and StructureCode are both absent | No | User-provided design boundary; ask the user to identify the chart of accounts |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| COASTR.DEFAULT | step | 5 | apply_default | complete->COASTR.BULK | COASTR.LOOKUP | stop | Object absent |
