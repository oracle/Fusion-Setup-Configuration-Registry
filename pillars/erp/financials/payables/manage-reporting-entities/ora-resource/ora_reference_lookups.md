# Reference Lookups

These checks are read-only and run through the approved workflow. Reviewing or editing this guidance does not run them. Fusion performs its own validation during import.

## Live Lookups

| Resolver | Runs When | Source Values | Request Path or URL | Requested Fields | Match Rule | Values to Fill | If No Match or Many Matches |
|---|---|---|---|---|---|---|---|
| validate_reporting_entity_set | SetCode is supplied | Explicit SetCode | /fscmRestApi/resources/11.13.18.05/setIdSetsLOV?onlyData=true&fields=SetCode,SetName,Description&q=SetCode='{SetCode}' | SetCode, SetName, Description | Read all pages; exact code comparison; escape quotes and URL-encode query; preserve explicit code. | No internal SetId; returned label is evidence only. | Zero exact matches stops; malformed response stops; do not select an ID from multiple rows. Availability-only warning cannot derive a missing value. |
| resolve_reporting_entity_bu | BU or enterprise context is supplied | BuName, separately established EnterpriseId | /fscmRestApi/resources/11.13.18.05/finBusinessUnitsLOV?finder=ModuleIdFinder;ModuleId=10,Intent=AP_MANAGE_PAYABLES_TAX_REPORTING_ENTITY_DATA&onlyData=true&fields=BusinessUnitId,BusinessUnitName,ActiveFlag,PrimaryLedgerId&q=BusinessUnitName='{BuName}' | BusinessUnitId, BusinessUnitName, ActiveFlag, PrimaryLedgerId; collection hasMore/offset | Read every page; require one exact active BU. ModuleId 10 selects the PAYABLES_INVOICING_BF business function. Intent applies task data security. Escape name literals and URL-encode query values. Internal FSM still resolves BuName plus EnterpriseId through BuAltKeyByName. | Receipt only; no OrgId in CSV or business intake. This REST response does not establish EnterpriseId. | Stop on ambiguous exact results; distinguish an unavailable/unauthorized lookup from an invalid BU. No match in a secured result is not proof of global absence. Shared helper duplicate semantics remain unqualified; no-match clears OrgId then required/Payables BU validation applies. |
| resolve_reporting_entity_location | Location is supplied or its matching context is needed | InternalLocationCode, SetCode, supplied EffectiveStartDate and EffectiveEndDate | /hcmRestApi/resources/11.13.18.05/locationsLov?q=LocationCode='{InternalLocationCode}';SetCode='{SetCode}'; optional effectiveDate for the selected as-of date. Verify the selected row with finder=PrimaryKey;EffectiveEndDate={end},EffectiveStartDate={start},LocationId={returnedId}. | LocationId, LocationName, LocationCode, SetId, SetCode, EffectiveStartDate, EffectiveEndDate, ActiveStatus; hasMore and offset | Read all pages and require one exact code/set/date record. Map REST LocationCode to CSV InternalLocationCode; compare supplied effective boundaries using strict equivalent date parsing without rewriting CSV fields. Return canonical context from that same selected row only. FSM resolves SetCode then LocationVVOCriteria using code, SetId and dates. | SetCode and location effective boundaries only when needed and uniquely established; LocationId and SetId are internal evidence, not business input. | Zero or multiple exact matches stop for correction/disambiguation; auth/transport failures are not absence. Never default COMMON or silently choose another effective slice. No Common Options bill-to filter or contractBillToLocations fallback is imported. |

## Lookup Execution Rules

| Situation | What Happens |
|---|---|
| Supplemental set GET unavailable | Preserve an explicit code with an unverified warning under the active governed application-validation policy; never fabricate a missing SetCode or SetId. |
| Missing current BU or location evidence | Obtain the documented same-target lookup receipt and preserve exact surfaced FSM validation. Any permitted application-validation choice requires explicit field/candidate acceptance and normal Data Loader approval; no automatic retry. |
| Reference derivation or update target is ambiguous | Stop for disambiguation. An uncertainty choice cannot bypass task/target identity, key/audit boundaries, known invalid values or ownership. |

## Task Nodes

| Rule ID | Node Type | Sequence | Action Type | Transitions | Prerequisites | On Failure | Applies When |
|---|---|---|---|---|---|---|---|
| MRE.LOOKUP | step | 30 | reference_lookup | success->MRE.DEFAULT;failure->MRE.ERROR | MRE.DEP | stop | References require verification or a location context must be derived |

## BU Preflight Qualification

The BU eligibility predicate and REST filter mapping are documented. This is an optional read-only preflight under the routed workflow, not a new import route. A 400, 401 or 403 does not prove business invalidity and cannot trigger a guessed Intent, alternate credential or automatic import. Preserve normal authentication and application-validation policy. The selected identity must have endpoint access and task data access. Obtain a fresh same-target receipt for each operational request; the REST response alone does not prove enterprise membership.

ModuleId is a seeded business-function identifier, not an enterprise ID or the Payables application ID. ModuleId=10 selects Payables Invoicing, not Payables Payment. The Intent matches the AP_MANAGE_PAYABLES_TAX_REPORTING_ENTITY_DATA criterion declared by the Payables view and is mapped by the REST implementation to data security. It can narrow visible BUs; it does not grant access.

The business-unit matching key uses Name plus EnterpriseId, passed in that order. REST still does not establish EnterpriseId, and the shared helper behavior for malformed duplicate rows remains unreviewed. Do not copy Invoice Options EnterpriseId defaults into Reporting Entities without a task-specific derivation decision. A successful payablesOptions GET can corroborate existing setup; do not make an existing options row an inferred Reporting Entities prerequisite.


## Balancing Values: FSM Validation

Accept the supplied BalancingSegmentValue. Before import, require a nonblank value, resolve exactly one parent using the child BU/location references, and reject duplicate child tuples (BU, location, balancing value), including collisions with preserved rows under that parent. Preserve untouched existing children.

FSM validates value-set membership, enabled and summary flags, effectivity, internal GL context and reporting-use eligibility. Do not require ledger/COA discovery, a populated COA export, ValueSetCode, valueSets REST receipts or a BSV-specific exception before normal submission. A missing BSV lookup is not unresolved evidence or a validation failure. This does not change BU and location checks or Data Loader approval.

When FSM rejects the supplied value, report its exact diagnostic, including FND_CMN_INVALID_ATTRB_API_SERV or FND_CMN_REC_COMB_VALS_EXST when returned. Request corrected input; never replace the BSV or retry the import automatically. These application rules remain enforced by Fusion.

## Location API Qualification

Obtain a fresh per-request location match before operational use, using the exact location code, set and effective-date context.

Use the case-sensitive locationsLov resource name. Escape code/set literals and URL-encode query values. Read complete pagination before deciding zero or ambiguity. effectiveDate selects an as-of slice; returned start/end boundaries must still agree with supplied import-matching context. If the caller selects a historical slice, use an explicit date in that slice and verify its exact boundaries. A zero current-date result does not establish historical absence.

Use the location code (`InternalLocationCode`), location set (`SetCode`), and applicable effective dates to identify the location. `LocationName` helps users confirm their selection; do not match by name alone. ActiveStatus is retained as evidence; do not impose an extra status or bill-to eligibility predicate without Reporting Entities-specific support. Do not request BillToSiteFlag or use the bill-to-only FSCM fallback for this task. System-generated location and set IDs are not customer inputs. Location effective dates remain location matching context, not reporting-entity retirement dates.
