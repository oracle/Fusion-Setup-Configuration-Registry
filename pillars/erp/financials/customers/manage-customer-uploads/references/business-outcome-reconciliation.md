# Business-outcome reconciliation


Current runtime availability is governed by [governed read routes](governed-read-routes.md).
Exact Customer Upload attempt evidence can be collected through
`scripts/customer_attempt_collect.py` using the unchanged core REST GET client.
Its task-owned evidence schema is distinct from historical core `fbdiDiagnostics`
output. Missing or ambiguous evidence still blocks association; basic logs alone
never establish row lineage or persisted business outcomes.


The functional scope is the complete Customers worksheet, including
ATTRIBUTE_CATEGORY and ATTRIBUTE1–30. Do not silently drop a supplied segment,
restrict support to the three segments used in one test environment, or infer a
physical attribute from a tenant's segment display/API name. Resolve deployed
metadata for the account flexfield and actual context. Other worksheets remain
outside this task's initial delivery scope.

Before preview, `customer_api_dff_review.review_input_limits` checks supplied
string values against explicit deployed `valueFormat.maximumLength` metadata.
A known violation must be corrected, not waived as loader uncertainty. Unexposed
requested mappings require review. Passing this check is not full value-set,
byte-length, requiredness or business validation; retain eligible remaining gaps.

The runtime obligation is to verify the intended target/relationships, all
supplied values and source-backed relevant effects. Inspect omitted values that
supported APIs expose and retain unexpected changes for review. Unused unexposed
storage and unrelated historical versions are disclosed as unobserved, not
unconditional blockers. Unobserved does not mean null, unchanged, preserved or
irrelevant. A concrete wider-effect concern still needs resolution.

`customer_reconciliation_scope.plan` partitions all 87 columns for the exact
candidate. The campaign plan includes it as `runtime_business_outcome_scope`.
`assess_values` recomputes the API comparison for 77 direct/profile/set fields.
Requested unreadable or mismatched values, changed/unresolved owners, unexpected
omitted-field changes and observed metadata changes remain review findings.
Source/identity, receipt, tax and Bill-to fields retain their separate reviewers;
a satisfied value component cannot complete an import by itself.

For DFF updates, compare the before/after context, metadata revision and physical
mapping. A context or deployment change requires a source-backed review of the
affected old/new segments, including values omitted from the request. Do not
treat a matching new value as proof that other context values were preserved.
A new account has no invented pre-import snapshot; creation/reuse and intended
effects are established through the separate target and attempt reviews.

Before execution, establish the supported collection route for requested values
and relevant effects. Eligible business-validation uncertainty may use the
normal explicitly accepted loader-validation path. It cannot authorize guessing
targets, unsupported operations or claiming unreadable outcomes verified.
After the one approved submission, retain per-row outcomes and partial results.
Missing readback means incomplete verification with a next read-only action;
it does not justify automatic resubmission or a successful completion claim.

The detailed supplied-evidence physical comparators remain available for deeper
developer validation. Their full-column/history input shapes are not mandatory
functional prerequisites. SQL/JDBC/Publisher remains developer-only. Review API
capture provenance, binding, visibility and freshness independently; cached
projected summaries are not authenticated evidence. Process status, reconciled
business outcome and Journey synchronization remain separate.

The optional `customer_error_identity.associate_messages` component can map a
complete `FSCR_ROW_V1` JSON identity in a Data Loader error message to the exact
candidate. It accounts for the control file's party/account/account-site number
fallbacks and leaves duplicate identities, legacy messages, malformed JSON,
explicitly omitted long identities and conflicting upload IDs unresolved. The
versioned message format requires a separately qualified registration change;
the existing recipe is not assumed to emit it. Bind the authenticated, complete
message collection to the actual attempt separately. A mapped error is not
proof of rollback or permission to retry, and an unmapped or absent error is
not proof that a candidate row loaded.

`customer_error_identity.associate_attempt` additionally binds the retained
registration recipe and exact attempt, requires complete load-error diagnostics,
distinct effective candidate identities, complete successful interface loading,
terminal product execution, and balanced file/object/error counts. It classifies
the remaining rows as loaded only when all failed rows have unique complete
message identities and the scoped counts establish the entire partition.
This is an explicit count-and-identity derivation, never success inferred from
an absent error alone. Persisted values, side effects and recovery approval
still require their separate reviews.

For explicit new logical targets, `customer_api_new_target_review.analyze`
recomputes the canonical source-key queries and complete retained observations,
compares independent party/account/site numbers, and checks declared entity
intents. Its initially qualified review shapes are all-new entities or an
existing party/account with a new location/site/use hierarchy. Other compositions
need a separate review; this is not a product prohibition. No visible conflict
does not establish global absence or permission to create. Establish business
authority over the exact requested source keys and numbers separately, then use
the normal preview and approval process. A text authority reference is not proof.

After a create or mixed import, `customer_api_creation_review.project` extracts
the direct CreationDate of each exact resolved entity from supported organization,
account and location responses. `review_window` compares those timestamps with
the reviewed attempt interval and per-entity create/reuse/update intent. It does
not substitute profile creation dates, infer actor causality from a timestamp or
framework RequestId, or invent a before snapshot for a new target. Missing dates,
conflicting parents, old targets declared new and changed existing owners need
review. Compose audit times with authenticated raw captures, source/number/parent
matching, exact attempt association, all supplied values and relevant effects;
a timestamp check alone cannot complete an import.
