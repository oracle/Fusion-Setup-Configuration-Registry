# IDR Defaulting Rules

This task supports updates only.

## Update rule

Apply no defaults. Start from the fresh target export, change only allowed business fields explicitly requested, and preserve every other non-audit value on targeted rows. Leave declared audit cells blank in generated update rows. Include only targeted rows in the import ZIP; verify omitted baseline rows and their non-audit values remain unchanged in target state.

Leaving Override Default Business Unit unselected is an explicit requested change that maps to `BuDerivationBasisCode=N`. If the request omits that field, preserve its exported value. This mapping is defined in `ora_reference_lookups.md`; it is not a default.
