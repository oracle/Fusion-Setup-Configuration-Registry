# Defaulting Rules

## Defaults

| Field(s) | Default value | Applies when | Explicit request | Handling |
|---|---|---|---|---|
| TermsDateBasis | `Invoice` | Fusion initializes a new record | Preserved; never replaced | Fusion default behavior |
| GlDateFromReceiptFlag | `INVOICE` (Invoice date) | Fusion initializes a new record | Preserved; never replaced | Fusion default behavior |
| PayDateBasisLookupCode | `DISCOUNT` | Fusion initializes a new record | Preserved; never replaced | Fusion default behavior |
| BudgetDateBasis | `ACC` | Fusion initializes a new record | Preserved; never replaced | Fusion default behavior |
| DiscountDistributionMethod | `SYSTEM` (Single distribution) | Fusion initializes a new record | Preserved; never replaced | Fusion default behavior |
| AutoCalculateInterestFlag; ProrateIntInvAcrossDists | `N`; `N` (Single distribution) | Fusion initializes a new record; setting AutoCalculateInterestFlag to `Y` also defaults proration to `N` | Preserved; never replaced | Fusion default behavior |
| ApprovalWorkflowFlag; AllowForceApprovalFlag; ValidateBeforeApprovalFlag | `N`; `N`; `N` | Fusion initializes a new record | Preserved; never replaced | Fusion default behavior |
| AlwaysTakeDiscFlag; DiscIsInvLessTaxFlag; ExcludeFreightFromDiscount | `N`; `N`; `N` | Fusion initializes a new record | Preserved; never replaced | Fusion default behavior |
| AllowFinalMatchFlag; AllowFlexOverrideFlag; AllowPaidInvoiceAdjust; InvDocCategoryOverride; TransferDescFlexFlag | `N`; `N`; `N`; `N`; `N` | Fusion initializes a new record | Preserved; never replaced | Fusion default behavior |
| BuildPrepaymentAccountsFlag; PrepaymentAvailableMesgFlag; RecalcPayScheduleFlag | `N`; `N`; `N` | Fusion initializes a new record | Preserved; never replaced | Fusion default behavior |
| AllowInvThirdPartyOvrd; RoutingFlag; AttachmentMandatorySsFlag; DisallowAttachmentDelFlag | `N`; `N`; `N`; `N` | Fusion initializes a new record | Preserved; never replaced | Fusion default behavior |

## Defaulting Boundary

These are Fusion initialization defaults. For a create candidate, apply the
required Terms Date Basis, Accounting Date Basis, Pay Date Basis, and Budget
Date Basis values when omitted. For an existing business-unit record, preserve
exported values during unrelated updates. When the request explicitly sets
`AutoCalculateInterestFlag=Y` and omits `ProrateIntInvAcrossDists`, the adapter
writes `N` (Single distribution), matching the UI enable action. Disclose this
in the preview's effective values and requirements. Preserve explicit `N`, `Y`,
or blank choices; omission alone triggers this default. Do not ask for an
allocation method unless the user wants a choice other than the disclosed
default. Disabling interest continues to clear the dependent fields.

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| DEFAULT.APPLY | step | 30 | apply_default | success->DESIGN.ENFORCE;failure->ERROR.BLOCK | DEP.CHECK | stop | Always; apply documented create defaults and omitted interest allocation when explicitly enabling interest; preserve explicit choices and unrelated update values |
