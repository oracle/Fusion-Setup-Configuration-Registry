# Input Validation

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve |
|---|---|---|---|
| Structure identity | COA Name or StructureCode | Block | Ask the user to identify the chart of accounts. Derive StructureCode only after COA Name is supplied; never derive the COA identity from configuration details or prior context. |
| Segment design | User-confirmed Company, Cost Center, Account, and Intercompany baseline or an explicit replacement design; any additional segments must be user-provided | Block | Present the basic segment set as a proposal and ask the user to confirm or revise it and provide any additional segments. Do not derive additional segments. |
| Required structure attributes | KeyFlexfieldCode, ApplicationId, StructureCode, Name, Delimiter, EnabledFlag | Block | Apply workbook constants or derived defaults, then report the source |
| Required segment attributes | KeyFlexfieldCode, ApplicationId, StructureCode, SegmentCode, SegmentIdentifier, ColumnName, Name, Prompt, ShortPrompt, SequenceNumber, EnabledFlag, DisplayWidth, DefaultValueSetCode | Block | Derive SegmentIdentifier from SegmentCode using the documented normalization rule; derive other fields only from the complete export, supported read-only Fusion metadata, workbook, or user input |
| Required structure-instance attributes | KeyFlexfieldCode, ApplicationId, StructureInstanceCode, Name, EnabledFlag, DynamicCombinationCreationAllowed, ShorthandAliasEnabledFlag, StructureCode | Block | Apply workbook constants or derived defaults; do not create an instance until its referenced StructureCode is resolved. |
| Required structure-instance segment attributes | KeyFlexfieldCode, ApplicationId, StructureInstanceCode, SegmentCode, RequiredFlag, DisplayFlag, BIEnabledFlag, QueryRequiredType, ValueSetCode | Block | Resolve ValueSetCode through verified value-set metadata and apply workbook defaults only where the user has not supplied a value. |
| Referenced value-set resolution | One uniquely resolved ValueSetCode with compatible ValidationType, ValueDataType, ValueSubtype, MaximumLength, and flags for every requested segment; ValueSetId is optional metadata | Block | Use find_value_set before structure package generation. Require its unique compatible code-match result; do not require ValueSetId for code-based CSV references. |
| Import contract | Complete same-task FSM CSV export and ASM_SETUP_CSV_METADATA.xml | Block | Obtain complete same-task export; template-only output is supplementary only |

## Field Validation

| Check | What Happens |
|---|---|
| COA name | Reject values longer than 30 characters. |
| StructureCode | Reject values longer than 30 characters, including codes derived from COA Name. |
| Segment name | Reject values longer than 30 characters. Do not modify the supplied name. |
| Segment name whitespace | Reject a segment name with a leading or trailing space. |
| Segment name starting characters | Reject a segment name that starts with @, backslash, {, }, comma, =, <, (, ), period, +, pipe, space, hyphen, apostrophe, or underscore. |
| Segment name contained characters | Reject a segment name that contains a comma, ampersand, or forward slash. |
| SegmentCode | Reject values longer than 30 characters. |
| SegmentIdentifier length | Reject values longer than 30 characters after validating or deriving the identifier. |
| Segment length | If supplied, require the segment value length to be a numeric integer from 1 through 150. If blank, default it to 6 before value-set readiness and package generation. Never replace an explicitly supplied valid length with the default. |
| ValueSetId | Optional metadata only. Retain it when returned; its absence must not block a unique compatible ValueSetCode match or code-based CSV import. Do not derive it from an opaque resource key or add an ID column absent from the target export. |
| DefaultValueSetCode | Require a verified compatible ValueSetCode for every segment. SegmentCode_VS is a lookup candidate only and must not be used in a package without a successful value-set lookup. |
| Delimiter | Allow only exclamation mark, asterisk, plus sign, hyphen, period, colon, equals sign, caret, tilde, or vertical bar. |
| SequenceNumber zero | Reject SequenceNumber 0 before package generation. |
| Segment sequence and column | If ColumnName or SequenceNumber is derived/defaulted, require a one-to-one match: SEGMENT1 uses SequenceNumber 1, SEGMENT2 uses 2, and so on. If the user or workbook explicitly supplies both values, preserve them, record a warning in import readiness, and require explicit approval before package generation. |
| SegmentIdentifier | Require a nonblank identifier for every structure segment. Derive it from SegmentCode by lowercasing the complete code when it contains only letters and digits. When a special character occurs, remove it and uppercase the immediately following letter; lowercase all other letters and preserve digits. Reject the derivation when a special character is not immediately followed by a letter. Validate an explicitly supplied SegmentIdentifier against the same rule before package generation. |
| ShortPrompt | Require a unique short prompt within the structure; derive a distinct prompt or stop for user input when the abbreviation rule collides |
| SegmentLabelCode | Require an internal code from same-task export or the documented qualified-label mapping; reject UI-label text as an import value |
| Segment label allowed domain | Reject GL_GLOBAL and any label whose GlobalFlag is not N. Require every assigned label to resolve through the COA-qualified label domain before preview. |
| Segment tree | When TreeCode or TreeStructureCode is supplied, require both fields, require TreeStructureCode to equal GL_ACCT_FLEX, and verify that TreeCode exists for the segment DefaultValueSetCode. Do not require a tree when no default hierarchy is requested. |
| StructureInstanceIdentifier | When the identifier is blank, derive it from StructureInstanceCode by uppercasing the first letter, lowercasing remaining letters, removing separators, and uppercasing the letter after each separator. Reject a derivation when a separator is not immediately followed by a letter. |
| Instance segment defaults | TreeCode, DefaultType, and DefaultValue must remain blank unless an approved hierarchy or segment-default design supplies them. |
| Instance segment value set | Require the instance ValueSetCode to match a verified compatible value set for the same segment before package generation. |
| Vague create request | Propose Company as Primary Balancing, Cost Center as Cost Center, Account as Natural Account, and Intercompany as Intercompany. Ask for the COA name, confirmation or revision of the proposed set, and any additional user-designed segments. Do not generate artifacts or start Fusion activity before confirmation. |
| Missing COA identity | When configuration is supplied without COA Name or StructureCode, ask which chart of accounts owns it. Do not derive the identity from segment configuration, value-set codes, files, environment context, or a previously discussed COA. |
| Additional segment derivation | Accept additional segments only when explicitly supplied by the user or an approved design source. Never infer, invent, reserve, or append extra segments from the basic set or other configuration. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| COASTR.VALIDATE | step | 2 | validate_input | valid->COASTR.READY | COASTR.COLLECT | stop | Always |
