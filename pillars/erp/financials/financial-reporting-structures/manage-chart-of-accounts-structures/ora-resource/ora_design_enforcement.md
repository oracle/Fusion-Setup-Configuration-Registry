# Design Enforcement

## Enforcement Order

| Sequence | Step | What Must Happen |
|---|---|---|
| 1 | Validate | Enforce mandatory COA and task field rules |
| 2 | Default | Apply only documented values and record source |
| 3 | Lookup | Compare existing object before create |
| 4 | Readiness | Block package with unresolved technical values |

## Design Rules

| Rule ID | Applies When | Severity | Required Lookup | Blocking Condition | Recommendation | Fix Allowed? |
|---|---|---|---|---|---|---|
| COASTR.001 | Always | Error | find_chart_of_accounts, get_chart_of_accounts | Equivalent object differs | Obtain update-or-new decision | No |
| COASTR.002 | Structure | Error | FSM label metadata | Primary Balancing or Natural Account label absent | Use valid exported code | Yes |
| COASTR.003 | Future-use segment | Error | FSM export | Required, Displayed, or default absent | Correct design | Yes |
| COASTR.005 | Always | Error | Complete same-task FSM export | Populated CSV files or ASM_SETUP_CSV_METADATA.xml are absent | Run complete export before defaulting or package generation; use template-only only as a supplement | Yes |
| COASTR.006 | New COA design | Error | none | A segment duplicates another segment's business meaning or a future/reserved segment is proposed without approved exception | Remove the duplicate or future segment; obtain an approved exception | No |
| COASTR.007 | Intercompany segment is requested | Error | Company and intercompany value-set design | Intercompany value design is incompatible with company values | Align values before preview | Yes |
| COASTR.008 | Defaulted segment positions | Error | Complete same-task FSM export | A defaulted segment sequence number does not equal the ordinal in its SEGMENTn column, or a defaulted position is duplicated or skipped | Correct the defaulted column/sequence mapping before preview | Yes |
| COASTR.010 | Explicit segment positions | Warning | User/workbook source evidence | The user or workbook explicitly supplies ColumnName and SequenceNumber values that do not match the default SEGMENTn ordinal rule, or explicitly supplies duplicated/skipped positions | Preserve explicit values, show the mismatch in readiness, and require user approval before package generation | No |
| COASTR.009 | Segment labels are assigned | Error | Same-task segment-label export or documented qualified-label mapping | A UI label is used where an internal SegmentLabelCode is required | Resolve the internal code before preview | Yes |
| COASTR.011 | User requests COA creation without structural details | Error | none | COA identity or user confirmation of the proposed Company, Cost Center, Account, and Intercompany baseline is absent | Present the basic set as a proposal; ask for COA Name, confirmation or revision, and any additional user-designed segments | No |
| COASTR.012 | Configuration is supplied without identifying a COA | Error | none | COA Name and StructureCode are both absent | Ask which COA owns the configuration; never derive identity from segments, value sets, files, environment context, or prior conversation | No |
| COASTR.013 | Additional segments are not explicitly supplied | Error | none | A runtime attempts to infer, invent, reserve, or append segments beyond the user-confirmed design | Use only the confirmed basic set plus additional segments supplied by the user or an approved design source | No |
| COASTR.014 | Segment names are supplied | Error | none | A segment name has a leading or trailing space | Remove the leading or trailing space before preview | Yes |
| COASTR.015 | Segment names are supplied | Error | none | A segment name starts with @, backslash, {, }, comma, =, <, (, ), period, +, pipe, space, hyphen, apostrophe, or underscore, or contains comma, ampersand, or forward slash | Correct the segment name before preview | Yes |
| COASTR.016 | Segment values are supplied or already exist for the COA | Error | Same-COA segment names and segment values | A segment name exactly matches any segment value in the same COA without regard to case | Change the segment name or conflicting value before preview | No |
| COASTR.017 | More than one label is assigned to a segment | Error | none | GL_BALANCING or GL_ACCOUNT is combined with any other label; GL_SECONDARY_TRACKING is combined with GL_BALANCING, GL_BALANCING_3, GL_ACCOUNT, GL_INTERCOMPANY, or GL_REVAL_GAIN_LOSS_TRACK; GL_BALANCING_3 is combined with GL_BALANCING, GL_SECONDARY_TRACKING, GL_ACCOUNT, GL_INTERCOMPANY, or GL_REVAL_GAIN_LOSS_TRACK; FA_COST_CTR is combined with GL_BALANCING, GL_ACCOUNT, or GL_INTERCOMPANY; GL_INTERCOMPANY is combined with GL_BALANCING, GL_SECONDARY_TRACKING, GL_BALANCING_3, FA_COST_CTR, GL_ACCOUNT, or GL_REVAL_GAIN_LOSS_TRACK; GL_REVAL_GAIN_LOSS_TRACK is combined with GL_BALANCING, GL_SECONDARY_TRACKING, GL_BALANCING_3, GL_ACCOUNT, or GL_INTERCOMPANY; or GL_LOCAL_USE or a custom label is combined with GL_BALANCING or GL_ACCOUNT | Remove the incompatible label assignment before preview | Yes |
| COASTR.018 | Qualified labels are assigned across the structure | Error | none | GL_BALANCING, GL_SECONDARY_TRACKING, GL_BALANCING_3, GL_ACCOUNT, FA_COST_CTR, GL_INTERCOMPANY, or GL_LOCAL_USE is assigned more than once in the same COA | Retain exactly one assignment for each affected qualified label | Yes |
| COASTR.019 | GL_BALANCING_3 is assigned | Error | none | GL_SECONDARY_TRACKING is not assigned anywhere in the same COA | Assign GL_SECONDARY_TRACKING or remove GL_BALANCING_3 | Yes |
| COASTR.020 | Balancing or revaluation-tracking labels are assigned | Error | none | The total number of assignments for GL_BALANCING, GL_SECONDARY_TRACKING, GL_BALANCING_3, and GL_REVAL_GAIN_LOSS_TRACK exceeds 5 | Reduce the tracking-label assignments to 5 or fewer | Yes |
| COASTR.021 | Segment labels are assigned | Error | resolve_segment_label_code | An assigned label has GlobalFlag other than N, equals GL_GLOBAL, is absent from the allowed domain, or is ambiguous from the given input data | Select a unique nonglobal COA-qualified label from the given input data | Yes |
| COASTR.022 | TreeCode or TreeStructureCode is supplied | Error | verify_segment_tree | One tree field is blank, TreeStructureCode is not GL_ACCT_FLEX, the tree is absent or ambiguous, or the tree is not associated with DefaultValueSetCode | Select a GL_ACCT_FLEX tree associated with the segment value set or remove the optional default hierarchy | Yes |
| COASTR.023 | A requested structure segment has an unresolved value set | Error | find_value_set | DefaultValueSetCode is absent, unverified, incompatible with the requested length or format, or ambiguous for any requested segment | Treat an absent candidate as value-set creation readiness without asking the user for a separate creation confirmation. Stop the structure package only until compatible value-set evidence is available; differing or ambiguous definitions require a decision. | Yes |
| COASTR.024 | Any live import | Critical | none | A direct FSM endpoint or another import adapter is selected instead of core.data-loader | Submit the approved immutable FSM ZIP through core.data-loader only. | Yes |

## Design Lookup Requirements

| Rule ID | Resolver | When Required | Values Needed | Source File |
|---|---|---|---|---|
| COASTR.016 | compare_coa_segment_names_and_values | Before structure readiness when segment values are supplied or available | All segment names and all segment values associated with the same COA | Developer-provided gl_detect_essbase_conf_pkg.pkb |
| COASTR.021 | resolve_segment_label_code | Before preview when any segment label is assigned | SegmentLabelCode, GlobalFlag, and allowed-domain result | KFFLabeledSegmentVO.xml and complete same-task segment-label export |
| COASTR.022 | verify_segment_tree | Before preview when TreeCode or TreeStructureCode is supplied | TreeCode, TreeStructureCode, DefaultValueSetCode, and value-set association | KFFSegmentVO.xml, FND_TREE_VL, and value-set-filtered tree metadata |
