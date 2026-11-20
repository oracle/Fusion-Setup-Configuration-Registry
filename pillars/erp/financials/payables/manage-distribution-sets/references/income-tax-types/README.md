# Income tax type seed reference


Income tax type reference data for code and description matching. Availability and active status may differ in your environment.

The [JSON reference](income-tax-types.json) preserves all 51 exact codes, descriptions and inactive dates. Codes contain significant spaces, slashes and mixed case; do not remove them. JSON `null` means that the source has no inactive date. It does not establish current environment availability or active status.

Use this list for reference and exact code/description mapping. Require a unique match before resolving a description. `MISC16` and `NEC1D` both have description **Overtime Compensation** and neither is end-dated in this source; ask for the intended code. `MISC13 A` and `MISC13 EPP` are end-dated 2001-04-10; never present them as active choices. A repository miss does not establish that a code is invalid in a different release or environment. Apply the task's [repository-first resolution and unavailable-REST continuation policy](../../ora-resource/ora_reference_lookups.md#income-tax-resolution-policy); this data file does not perform REST calls, grant access, bypass validation, create tax types or authorize imports.

## Seed values

| Income tax type | Description | Inactive date in source |
|---|---|---|
| `AVAN/A` | Fringe Benefits - other | Blank |
| `AVAN/L` | Fringe Benefits - Housing | Blank |
| `AVAN/N` | Fringe Benefits - Food | Blank |
| `AVAN/V` | Fringe Benefits - Car | Blank |
| `COTIS` | Contributions to Pension Funds (to be deducted) | Blank |
| `DAU/AR` | Miscellaneous - Other | Blank |
| `DCO/CO` | Brokerage Fees | Blank |
| `DCOM/C` | Miscellaneous - Commissions | Blank |
| `DDA/DA` | Miscellaneous - Royalties | Blank |
| `DDI/DI` | Miscellaneous - Inventor's Fees | Blank |
| `DHON/H` | Miscellaneous - Fees | Blank |
| `DJE/JP` | Miscellaneous - Director's Fees | Blank |
| `DRIS/R` | Miscellaneous - Rebates | Blank |
| `GOV 1` | Unemployment compensation | Blank |
| `GOV 4` | Federal income tax withheld on government payments | Blank |
| `GOV 6` | Taxable grants | Blank |
| `GOV 6A` | Energy grants | Blank |
| `GOV 7` | Agriculture payments | Blank |
| `GOV8` | Family Leave Benefits | Blank |
| `INDE/F` | Indemnities and Reimbursements - Lump Sum | Blank |
| `INDE/P` | Indemnities and Reimbursements - Payment by the Employer | Blank |
| `INDE/R` | Indemnities and Reimbursements - On Supporting Documents(1) | Blank |
| `INT 1` | Interest income not included in box 3 | Blank |
| `INT 1A` | Financial institution interest income not included in box 3 | Blank |
| `INT 3` | Interest on U.S. Savings Bonds and Treasury obligations | Blank |
| `INT 4` | Federal income tax withheld on interest payments | Blank |
| `INT 8` | Tax exempt interest | Blank |
| `MISC1` | Rent | Blank |
| `MISC10` | Crop Insurance Proceeds. Reported in 1099-MISC Box 9 from 2020. | Blank |
| `MISC11` | Fish purchased for resale | Blank |
| `MISC13` | Excess golden parachute payments. Reported in Box 3 on Form 1099-NEC from 2025. | Blank |
| `MISC13 A` | Gross proceeds paid to an attorney | 2001-04-10 |
| `MISC13 EPP` | Excess golden parachute payment | 2001-04-10 |
| `MISC14` | Gross proceeds paid to an attorney. Reported in 1099-MISC Box 10 from 2020. | Blank |
| `MISC15a NT` | Section 409A non-taxable deferrals. Reported in 1099-MISC Box 12 from 2020. | Blank |
| `MISC15a T` | Section 409A taxable deferrals. Reported in 1099-MISC Box 12 from 2020. | Blank |
| `MISC15b` | Nonqualified deferred compensation. Reported in 1099-MISC Box 15 from 2022. | Blank |
| `MISC16` | Overtime Compensation | Blank |
| `MISC2` | Royalties | Blank |
| `MISC3` | Other Income | Blank |
| `MISC4` | Federal income tax withheld | Blank |
| `MISC5` | Fishing boat proceeds | Blank |
| `MISC6` | Medical and health care payments | Blank |
| `MISC7` | Non-employee compensation. Reported in Form 1099-NEC from 2020. | Blank |
| `MISC8` | Payments in lieu of dividend or interest | Blank |
| `MISC9` | Consumer Products for Resale. Reported in 1099-MISC Box 7 from 2020. | Blank |
| `NEC1D` | Overtime Compensation | Blank |
| `RETE/D` | Withholding Tax Exemption Based on International Conventions | Blank |
| `RETE/R` | Withholding Tax - Reduced Rate | Blank |
| `TVA/47` | VAT on Royalties (to be deducted) | Blank |
| `TVA/55` | VAT on Royalties (to be added) | Blank |
