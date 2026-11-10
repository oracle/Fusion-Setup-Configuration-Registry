# Downstream party and bill-to source findings


Reviewed source series: FUSIONAPPS_11.13.26.10.0_LINUX.X64. This is authoring
evidence, not an observed successful import or a complete business-validation
specification. Source captures and hashes are retained in the developer evidence
bundle; no tenant records or credential material belong in this reference.

## Party values

`fusionapps/crm/hz/db/plsql/hz_cimp_parties_pkg.pkb`, lines 1611–1729,
inserts GSA_INDICATOR_FLAG, JGZZ_FISCAL_CODE and DUNS_NUMBER_C into HZ_PARTIES.
Lines 2648–2727 update those columns using incoming null → existing value,
G_MISS_CHAR → null, otherwise incoming value. The Customer Interface mapping
supplies these from GSA_INDICATOR_FLAG, TAXPAYER_ID_NUM and DUNS_NUMBER.
This does not authorize exposing a sentinel as a supported workbook clear action.

The organization-profile insert and update paths also carry these values.
The update source joins the party's profile where EFFECTIVE_LATEST_CHANGE='Y'
and SYSDATE falls between EFFECTIVE_START_DATE and EFFECTIVE_END_DATE
(lines 2879–2886), with value updates at 2893, 2943–2944. Preserve profile history
and ambiguity; a match on HZ_PARTIES alone cannot certify all profile effects.

TAXPAYER_REGISTRATION_NUM maps into HZ_IMP_PARTIES_T.TAX_REFERENCE in the
Customer Interface package. The downstream consumer is the asynchronous
ZX_NEW_SERVICES_PKG.zx_tca_ptp_callback, which writes the THIRD_PARTY profile's
ZX_PARTY_TAX_PROFILE.REP_REGISTRATION_NUMBER. See [tax evidence](tax-evidence.md)
for source predicates, event routing and the offline comparator. Do not substitute
JGZZ_FISCAL_CODE or HZ_CUST_SITE_USES_ALL.TAX_REFERENCE based on similar names.

## Bill-to reference

`hz_cimp_acctsiteuse_pkg.pkb` lines 403–423 resolve a SHIP_TO row's
BILL_TO_CUST_SITE_REF against a same-batch, same-source-system BILL_TO interface
row with null INTERFACE_STATUS. Lines 436–458 resolve a still-unresolved link
through active HZ_ORIG_SYS_REFERENCES owned by HZ_CUST_SITE_USES_ALL. This fallback
uses status A without a reference effective-date predicate. Keep this loader
predicate distinct from other identity policies.

The resolved ID is persisted as HZ_CUST_SITE_USES_ALL.BILL_TO_SITE_USE_ID. The
update expression at line 916 preserves the existing link for a null incoming
resolved ID, clears for G_MISS_NUM18 and otherwise uses the resolved ID. A blank
workbook input therefore must not be interpreted as a request to clear a link.

`hz_cimp_acctsiteuse_val.pkb` lines 788–863 validate that a supplied bill-to
reference/ID is on a SHIP_TO row. These findings do not establish a universal
same-account restriction. The bill-to comparator retains actual target
account/site/set relationships, distinguish same-batch and pre-existing
resolution, and report missing or ambiguous evidence without inventing policy.

Persisted bill-to comparison and scoped organization-profile/sibling inventories
now have offline helpers and tests, as does taxpayer-registration comparison.
Complete effects acceptance, live asynchronous tax persistence and live
create/update/reuse/recovery cases remain pending.
