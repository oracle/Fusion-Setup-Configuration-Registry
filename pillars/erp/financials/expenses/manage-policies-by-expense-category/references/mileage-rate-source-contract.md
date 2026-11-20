# Mileage rate validation boundary


The initial workbook excludes Rate Determinants. Its Mileage rate kinds are
MILEAGE, PASSENGER and ADDITIONAL. Resulting-state validation uses the complete
proposed row and resolved parent; an omitted update cell does not clear a stored
calculation method, passenger range or company code.

Reviewed source is the FPH `FUSIONAPPS_PT.V2MIBFPHDEV_LINUX.X64` label
`261028.0600.S`, under `fusionapps/fin/components/payables/exm/policy/`:

- `shared/model/src/oracle/apps/financials/expenses/policy/shared/model/entity/MileagePolLineEO.xml`:
  PassengerThreshold has precision 3, scale 0 and a positive-value validator with
  the explicit -1 exception. AltKey includes owning policy, AdditionalRateCode,
  CalculationMethodCode, CurrencyCode, DistanceThreshold, EndDate, FuelType,
  GeographyId, PassengerThreshold, RoleId, StartDate, TypeOfRateCode,
  VehicleCategory, VehicleType, ZoneCode and GenderCode. Exported parent/role/
  geography references map those internal coordinates through the service schema.
  AltKey_NoStart contains the same coordinates excluding StartDate. Its unique
  validator runs when MigrationFlagType is true. The custom getters in
  MileagePolLineEOImpl.java derive migration mode from the service root; the
  MigrationFlagType getter retains that value for all row kinds. Both uniqueness
  checks therefore remain required for the selected service-import profile.
- `mileage/model/src/oracle/apps/financials/expenses/policy/mileage/uiModel/applicationModule/FinExmPolicyMileageAMImpl.java`,
  `validateRow`: ADDITIONAL requires an additional code; PASSENGER and ADDITIONAL
  require CalculationMethodCode. These are UI upload requirements, not claimed
  independent proof that FSM invokes this validator.
- `mileage/model/src/oracle/apps/financials/expenses/policy/mileage/uiModel/view/MileagePolLinesVO.xml`:
  CalculationMethodCode binds EXM_CALCULATION_METHOD. The existing reviewed
  intake domain maps Amount to AMOUNT and Percentage to PERCENTAGE. RATE is not
  that lookup's Amount code. Domain membership does not replace target lookup
  eligibility checks.

`mileage_rate_profile.py` rejects incompatible add-on fields, missing enabled
parent options, unresolved company lookup type, missing amounts/dates, invalid
date order and determinant-bearing rows. Finite nonnegative amounts and the
single-currency/no-determinant restrictions are the local initial input profile;
they are not presented as unreviewed universal Oracle constraints. Blank child
currency is preserved; parent display currency is not copied into a key field.

Candidate parent resolution invokes the resulting-rate validator. Baseline
identity checks retain the full exported AltKey dimensions; recognizing distinct
determinant-bearing keys does not authorize editing those rows. Workbook and
serialized-input identity projections now include CalculationMethodCode.
The second migration-enabled key, AltKey_NoStart, is also checked; changing only
StartDate does not establish a distinct importable rate.

The own Mileage profile now supplies parent and schedule validation and a
source-matched, operation-bound company-code resolver. Fresh target capture is
required when that branch consumes company codes. Shared XML field-write
behavior for existing business updates retains exact-field conditional preparation.
Wholly new no-determinant groups use the separately reviewed
[Mileage create serialization](mileage-create-serialization.json) and bounded
[DOM proof](fsm-dom-empty-element-contract.json), with explicit choices and
operation-bound references. The base-only SINGLE/MILE create case passed
[live reconciliation](live-verification-scope.md); other shapes and target/build
parity remain unverified by that case;
unqualified generated synchronization and existing-parent/new-company-rate
retained-reference public qualification remain outside that admission.
No default passenger threshold, calculation method, date or company code is
generated. Prior live approvals for other categories do not apply.
