# Runtime tree and rules

The six configured algorithm reference codes are extraction identifiers, not cached metadata:

| Reference | Rule type | Required entitlement dimensions |
| --- | --- | --- |
| AL.09361.ORA | Rule-1 sensitive access | 1 |
| AL.09802.ORA | Rule-1 sensitive access | 1 |
| AL.09360.ORA | Rule-2 toxic combination | 2 |
| AL.04571.ORA | Rule-2 toxic combination | 2 |
| AL.05980.ORA | Rule-2 toxic combination | 2 |
| AL.06870.ORA | Rule-2 toxic combination | 2 |

Read names, IDs, entitlement membership, and access-point codes/names exclusively from the requested environment. `AL.09802.ORA` is the configured payment-sensitive reference; do not substitute `AL.09082`.

The UTF-8 JSON tree is an ordered array of algorithms, each with `referenceCode`, `id`, `name`, and `entitlements`. Each entitlement has `id`, `name`, and `accessPoints`; each point has exact `code` and `name`. Retain occurrences across algorithms and entitlement dimensions. Never globally deduplicate the tree or edit it during generation.

Rule-1 generates one check for every point in each sensitive algorithm's entitlement. Rule-2 generates the Cartesian product of points from the two entitlements for each toxic algorithm. Both codes must occur in the same role set, in one or multiple roles. A code present in both dimensions satisfies both dimensions if supplied. Keep entitlement evidence distinct in rule identities. Reject duplicate codes within one entitlement and duplicate entitlement IDs within one algorithm as ambiguous metadata.

Compute counts from the tree: sensitive checks are the sum of sensitive entitlement sizes; toxic checks are the sum of products of each toxic algorithm's two sizes. Unique codes and occurrences are runtime summary values. No fixed counts are assumed. Missing algorithms, invalid dimensions, or empty entitlement accesses fail the run.

Match exact case-sensitive codes. Deduplicate input codes for matching while preserving contributors. Assess sets independently, retaining sensitive and toxic findings sharing codes. Recommendations do not constitute approval; `high` is the implementation severity default.
