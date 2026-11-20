# FSM UI parity and language contract

Reviewed 2026-10-31 for EXM_MANAGE_AUDIT_LOOKUP_TYPES, fixed CodeSearch branch
SOURCE-SNAPSHOT-147cfa7f931f The colleague workbook is a layout reference,
not an operation contract or import approval.

| Admin action | Source-backed behavior | Workbook behavior |
|---|---|---|
| Create a lookup type | Parent Create unconditionally disabled | Reject unknown types; never create parents |
| Edit type Meaning / Description | Editable UI inputs, writable EO and FSM VO | Optional Lookup Types sheet; existing parent update |
| Change module/configuration/reference group | Module/configuration disabled via DeleteLookupType for ordinary UI users; reference group enabled only for view 2 | Preserve values; no general permission to change them |
| Add code | InsertLookupCode false for System, true for Extension/User | Configuration-level preflight |
| Edit code Meaning / Description / sequence | UI inputs and EO setters | Existing code workflow; retained-row/language gates apply |
| Edit Enabled / dates / Tag | UpdateStartDate true for User, or Extension code CreatedBy other than SEED_DATA_FROM_APPLICATION | Apply the same check before preparation, even though FSM AM bypasses some checks |
| Delete a type/code | Conditional UI controls; distinct from end dating | Gap: no verified CSV deletion contract; omission never means delete |
| Clear a value | UI may allow null subject to validation | Gap: explicit CSV null serialization not verified; blank preserves |
| Independent translations | Language-dependent type/code text and TL entities exist | Gap: independent translation input sheets not implemented; reject rather than discard them |
| DFF/rekey/set changes | Separate context/lifecycle contracts | Preserve; no implicit delete/create |

This is partial parity, not a claim that every UI action is qualified in Excel.

## Implementation evidence

All CodeSearch paths below use the fixed branch and the prefix
`fusionapps/fin/components/financialCommon/fun/appsLookups/`.

- `SearchGenericLookups.jsff`: Create line 19; editable type text 39–48; conditional module/configuration/reference-group 34–58; code controls below 70.
- `LookupTypeEO.xml`: Meaning required/80, Description optional/240; OA_TL_ENTITIES association 367–373.
- `LookupTypeEOImpl.java`: text setters; insertLookupCode 643–653; deleteLookupType and skipValidationFromJava distinguish UI and service permissions.
- `LookupTypeGenericVO.xml`: writable text, type/view keys, translation accessor 250–254.
- `LookupGenericEOImpl.java`: UpdateStartDate uses code CreatedBy, not name/prefix. Service AM bypass does not authorize exceeding UI permissions.
- `LookupTypeGenericTranslationVO.xml`: FND_LOOKUP_TYPES_TL, Language, SourceLang, Meaning, Description.
- `LookupTypeTranslationEO.xml`: type/view/language key; Language/SourceLang precision 4.
- FSM AM SRC-006 in evidence.md, importData 412–460: type migration through MigratorHelper.readXML. No alternate write route is introduced.

## Language and preservation

Type and code text is language-dependent; the package includes both translation
CSV members. This does not install languages, authorize arbitrary language codes,
or translate identifiers. Lookup Types rows edit current-language parent text.
Require snapshot `text_context` with `language`, equal `export_language` and
`import_language`, and a reviewed `source_ref`. Each changed type/view also needs
one complete `type_translation_scopes` entry with `complete=true` and `source_ref`.
Obtain evidence only through a declared supported workflow. Never default language
from the workstation or seed files.

The preparer updates selected parents and leaves type-translation CSV header-only
so stale TL rows cannot overwrite new parent text. The primary EO's OA_TL_ENTITIES
framework owns session-language handling. Live qualification must verify imported
text, SourceLang/fallback behavior, independent translations, retained type fields
and all codes. Offline tests do not prove those runtime results.

Modified-only exports can omit a seeded parent. If omitted, obtain a fresh,
schema-complete selected-parent row via a declared supported readback. Supply it
under `preservation_rows["ORA_FINANCIALS_GENERIC_LOOKUP_TYPE.csv"]`: each entry has
`source_ref` and a `row` containing every exact package header. Compare with fresh
type Meaning, Description, module and configuration evidence. Never fill missing
current values from Oracle seed definitions. Missing readback blocks preparation.
