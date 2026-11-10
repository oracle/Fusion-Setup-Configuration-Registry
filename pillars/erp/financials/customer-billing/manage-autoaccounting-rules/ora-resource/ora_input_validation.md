# Manage AutoAccounting Rules Input Validation


<!-- fscr-supported-operations: create, update -->
<!-- fscr-create-fields: AR_AUTO_ACCOUNTING::Attribute1, AR_AUTO_ACCOUNTING::Attribute10, AR_AUTO_ACCOUNTING::Attribute11, AR_AUTO_ACCOUNTING::Attribute12, AR_AUTO_ACCOUNTING::Attribute13, AR_AUTO_ACCOUNTING::Attribute14, AR_AUTO_ACCOUNTING::Attribute15, AR_AUTO_ACCOUNTING::Attribute2, AR_AUTO_ACCOUNTING::Attribute3, AR_AUTO_ACCOUNTING::Attribute4, AR_AUTO_ACCOUNTING::Attribute5, AR_AUTO_ACCOUNTING::Attribute6, AR_AUTO_ACCOUNTING::Attribute7, AR_AUTO_ACCOUNTING::Attribute8, AR_AUTO_ACCOUNTING::Attribute9, AR_AUTO_ACCOUNTING::AttributeCategory, AR_AUTO_ACCOUNTING::BuName, AR_AUTO_ACCOUNTING::Type, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute1, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute10, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute11, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute12, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute13, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute14, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute15, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute2, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute3, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute4, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute5, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute6, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute7, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute8, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute9, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::AttributeCategory, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Constant, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Segment, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::SegmentNum, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::TableName -->
<!-- fscr-update-fields: AR_AUTO_ACCOUNTING::Attribute1, AR_AUTO_ACCOUNTING::Attribute10, AR_AUTO_ACCOUNTING::Attribute11, AR_AUTO_ACCOUNTING::Attribute12, AR_AUTO_ACCOUNTING::Attribute13, AR_AUTO_ACCOUNTING::Attribute14, AR_AUTO_ACCOUNTING::Attribute15, AR_AUTO_ACCOUNTING::Attribute2, AR_AUTO_ACCOUNTING::Attribute3, AR_AUTO_ACCOUNTING::Attribute4, AR_AUTO_ACCOUNTING::Attribute5, AR_AUTO_ACCOUNTING::Attribute6, AR_AUTO_ACCOUNTING::Attribute7, AR_AUTO_ACCOUNTING::Attribute8, AR_AUTO_ACCOUNTING::Attribute9, AR_AUTO_ACCOUNTING::AttributeCategory, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute1, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute10, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute11, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute12, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute13, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute14, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute15, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute2, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute3, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute4, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute5, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute6, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute7, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute8, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Attribute9, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::AttributeCategory, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::Constant, ORA_LE_AR_AUTO_ACCOUNTING_SEGMENT::TableName -->

This contract validates task input only. It does not authorize a Fusion import.

## Required Groups

| Requirement Group | Accepted Fields | If Missing | How to Resolve | Applies When | Resolver |
|---|---|---|---|---|---|
| Business-unit identity | BuName | Block the request | Supply one exact business unit | Create and update | resolve_auto_business_unit |
| Account-type identity | Type | Block the request | Supply one supported account type | Create and update | resolve_auto_account_type |
| Complete segment inventory | Segment, SegmentNum | Block the complete candidate | Supply exactly one rule for every required accounting segment | Create | resolve_auto_segment |
| Segment derivation | TableName or Constant | Block the complete candidate | Supply one compatible source or one valid constant for every segment | Create | resolve_auto_source |
| Exact update target | Segment | Block the request | Identify one exact child segment beneath the resolved parent | Update | resolve_auto_segment |
| DFF deployment | AttributeCategory and mapped Attribute1 through Attribute15 | Block the requested DFF change | Supply exact deployed context, segment mapping, and value evidence | Any DFF input | resolve_auto_dff |

## Field Validation

| Check | What Happens | Applies When | Resolver |
|---|---|---|---|
| Parent key uniqueness | Require exactly one BuName plus Type identity and reject duplicate operations | Create or update | resolve_auto_business_unit |
| Child key uniqueness | Require one Segment plus SegmentNum identity per parent and reject mismatches | Every child row | resolve_auto_segment |
| Derivation exclusivity | Require exactly one of TableName or Constant | Every child row | resolve_auto_source |
| Fixed account type | Normalize only an evidenced label/code; reject off-domain values | Type is supplied | resolve_auto_account_type |
| Fixed source | Normalize only an evidenced source compatible with the account type | TableName is supplied | resolve_auto_source |
| Constant value | Preserve exact value and require target value-set validation | Constant is supplied | resolve_auto_constant |
| Service-owned audit fields | Reject populated LastUpdateDate, LastUpdatedBy, CreationDate, CreatedBy, or LastUpdateLogin and serialize blank | Create and update | |
| Identity changes | Reject updates to BuName, Type, Segment, or SegmentNum | Update | |
| DFF boundary | Accept only explicitly deployed mappings; otherwise keep blank or preserve baseline | Any DFF input | resolve_auto_dff |
| No-op update | Generate no candidate and report the state already exists | Update produces no change | |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| AAR.VALIDATE_INPUT | decision | 1 | validate_input | valid->AAR.RESOLVE_DEPENDENCIES;invalid->AAR.RETURN_ISSUES | none | stop | Every normalized create, update, or validation request |

## Source Anchors

| Source IDs | Use |
|---|---|
| SRC-FSM-PACKAGE; SRC-CODE-TASK-BO; SRC-CODE-BO-DEFINITION | Exact entities, fields, hierarchy, and FSM task mapping |
| SRC-CODE-HEADER-EO; SRC-CODE-SEGMENT-EO | Portable identities, persistence, and audit boundaries |
| SRC-CODE-AUTOGL-LOOKUP; SRC-CODE-VALUE-SOURCE-VVO | Fixed account-type and source domains |
| SRC-DOC-AUTOACCOUNTING-26D | Complete segment design and source-or-constant behavior |
