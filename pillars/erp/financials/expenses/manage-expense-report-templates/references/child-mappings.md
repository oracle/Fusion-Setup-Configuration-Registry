# Child mapping import contract

Read for populated Expense Type Itemizations rows. The current workbook has
three sheets and the candidate builder accepts a top-level `itemizations` array
in a v1.5 design. Use every populated mapping row; never silently omit an
unsupported intent.

## Normalization and scope

Copy the matching parsed section's `rows` into the same-named design array,
using the existing catalog keys. Resolve the mapping operation from the fresh
target export using the full relationship identity: an existing relationship is
an update and an absent relationship is a create. Omit blank optional values on
an update; on a create omit blank itemization end dates or represent them as
null. Do not put an operation in the worksheet-derived design. Retain
source-cell metadata outside the execution design. An explicit `Clear` for
mapping end date is a route gap, not an ordinary blank. Neither relationship
has a nullable identity.

Include every owning Business Unit/template in `templates`. For a mapping-only
request with an existing template, add an identity-only target-resolved template entry;
do not require the implementor to add otherwise unnecessary template/type rows.
The owning type can be an existing baseline row or a type created in the same
candidate. Types are built first, so workbook row ordering is immaterial.

```json
{
  "schema_version": "1.5",
  "itemizations": [{
    "business_unit": "Example Operations",
    "template_name": "Travel",
    "parent_type_name": "Hotel",
    "child_type_name": "Meals",
    "include": "Yes"
  }]
}
```

These arrays supplement the existing baseline-bound design. Every parent and
child must resolve uniquely. Selected records must satisfy the cash-only scope.
Never use row position as identity.

## Itemizations

The five dotted parent-reference headers identify the owning template/type.
`BuName`, `ExpTemplateName`, and `Name` identify the itemization child type.
Both types must exist in the resulting same-template, same-Business-Unit scope.
The owner must have Itemization Enabled or Required. Self-itemization and
duplicate requested relationships are rejected.

- A target-absent relationship with Include Yes appends a new relationship.
- A target-existing relationship with blank Include or Yes validates and retains
  the existing relationship.
  It produces no artificial row delta or audit-column changes.
- Include No/removal remains unsupported: omitting a row from a merge import
  does not establish deletion. The itemization CSV has no end-date column, so
  mapping end-dating and Clear remain unsupported as well.
- Newly Enabled/Required types must have an included, resolvable child after
  all requested additions. New parent/child types may be in the same ZIP.

## Projects, accounts, and tax

Project Expenditure Mappings are not part of the current workbook or v1.5
execution design. Every imported expense type has Projects disabled, no default
project expenditure type, and no project receipt requirement. Expense Type
Account is an optional account number mapped to Segment1 with the BU primary
ledger resolved automatically; omitted edit accounts are preserved.
The builder writes `TaxClassificationCode` and `TaxProductCategoryCode` blank.
Do not add a project-mapping array, direct ledger/segment fields, or tax fields
to bypass those defaults.

## Evidence, review and execution

The builder verifies the fresh archive's child headers and XML paths itself.
Changed itemization CSVs appear in preview `delta.mappings`, including field
changes and row hashes. Unchanged members remain byte-identical, including
parent CSVs for itemization-only requests. Preserve unrelated rows in changed
members and all card/policy members.

The existing CSV review and Core Data Loader approval/import route applies to
the combined parent/child ZIP. If all requested target-existing relationships
already exist and no other values change, report no changes needed; do not request
approval for a no-op import. Local fixture tests establish transformation
behavior; live import acceptance must be confirmed by the approved loader result.

## Source boundaries

The fresh target export establishes the CSV column names and XML hierarchy.
Oracle's published [itemization table](https://docs.oracle.com/en/cloud/saas/financials/25d/oedmf/exmexpensetypeitemize-30602.html)
identifies the parent/child key. This is a 25D reference; combine it with the
current target export, and do not infer deletion semantics from it.
