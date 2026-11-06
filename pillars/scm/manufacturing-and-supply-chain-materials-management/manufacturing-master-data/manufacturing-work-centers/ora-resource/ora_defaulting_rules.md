# Defaulting Boundary

The **Server-managed create reconciliation** contract in ora_design_enforcement.md is the single owner of create eligibility, immutable expectations, post-load completion, and GET-only recovery.

## No Local Defaults

| Situation | What Happens |
|---|---|
| A WorkCenterSubinventory source includes a nonblank WorkCenterSubInvType | Do not change or default the supplied value. Use validate_work_center_subinventory_type_metadata and WC.RECON.TYPE in ora_design_enforcement.md to select writable retention or immutable server-output expectation. |
| A WorkCenterSubinventory source omits WorkCenterSubInvType or leaves it blank | Omit the field from the source; do not substitute a REST default or another value. |
| The exact live Data Loader template does not expose a requested WorkCenterSubInvType as writable | Apply WC.RECON.TYPE in ora_design_enforcement.md only for an eligible create. Otherwise stop as catalog_or_metadata_mismatch; do not silently omit, replace, or default the value. |
| Calendar route or persisted calendar identity is needed | Use the value returned by the documented lookup; do not treat current-state resolution as a local default. |
| A work-center create needs WorkAreaId or WorkAreaName | Use only the values returned by verify_active_work_area for the supplied OrganizationCode and WorkAreaCode. This is payload enrichment, not a local default; retain WorkAreaCode, WorkAreaId, and WorkAreaName together in the workCenters source and do not override the resolver result. |
| A REST Data Loader WorkCenterResource source supplies Available24HoursFlag | Do not default the flag or preserve a title-case Boolean literal. Apply the REST input-validation serialization rule before source preparation so the field is the exact lowercase text true or false. |
| A native FSM CSV package supplies resource availability flags | Follow Native FSM CSV contract in ora_input_validation.md. Preserve exported Y/N values and optional blanks without defaulting or REST Boolean conversion. This does not waive applicable calendar or resource business protections. |
