# Outbound Virtual Card Contract Source

These are narrowly scoped extracts from the Oracle implementation. They establish which virtual-card nodes are appended to each `OutboundPayment` and the tables that supply them.

## View Assembly

Source: `IBY_XML_FD_PMT_1_0_V.view`, revision `/st_fusionapps_pt-v2mibfphdev/13`.

The `OutboundPayment` expression appends all three virtual-card fragments:

```sql
iby_fd_extract_gen_pvt.get_payment_instrument(pmt.payment_id),
iby_fd_extract_gen_pvt.get_card_program_details(pmt.payment_id),
iby_fd_extract_gen_pvt.get_digital_payment_acct_det(pmt.payment_id),
XMLElement("DocumentPayableCount",
  IBY_FD_EXTRACT_GEN_PVT.Get_Pmt_DocPayableCount(pmt.payment_id))
```

This confirms that the XSLT source root remains `OutboundPaymentInstruction`, with `PaymentInstrument`, `CardProgramDetails`, and `DigitalPaymentAccount` as children of each `OutboundPayment`.

## Payment Instrument Constructor

Source: `iby_fd_extract_gen_pvt.pkb`, revision `/st_fusionapps_pt-v2mibfphdev/62`, function `get_payment_instrument`.

```sql
XMLElement("PaymentInstrument",
  XMLElement("PaymentInstrumentInternalId", cpi.payment_instrument_id),
  XMLElement("PaymentInstrumentName", cpi.payment_instrument_alias),
  XMLElement("NetworkInstrumentIdentifier", cpi.network_instrument_identifier),
  XMLElement("PaymentInstrumentCurrency",
    XMLElement("Code", cpi.currency_code)),
  XMLElement("BankDetails",
    XMLElement("BankCountry", cib.home_country_code)))
```

Main sources are `CE_PAYMENT_INSTRUMENTS`, `IBY_PAYMENTS_ALL`, and, for the opt-in bank-country branch, `CE_INDEX_BANKS`. Without that branch, `BankDetails/BankCountry` is not constructed.

## Card Program Constructor

Source: `iby_fd_extract_gen_pvt.pkb`, revision `/st_fusionapps_pt-v2mibfphdev/62`, function `get_card_program_details`.

```sql
XMLElement("CardProgramDetails",
  XMLElement("ExtCompanyId", ivcpm.ext_company_id),
  XMLElement("ExtMCCGroupCode", iictb.ext_mcc_group_code),
  XMLElement("CardProgramSetup", XMLAgg(XMLElement("Extend",
    XMLElement("Name", attribute_code), XMLElement("Value", attribute_value)))),
  XMLElement("TemplateSetup", XMLAgg(XMLElement("Extend",
    XMLElement("Name", attribute_code), XMLElement("Value", attribute_value)))),
  XMLElement("TemplateControls", XMLAgg(XMLElement("Extend",
    XMLElement("Name", opts.template_option_code), XMLElement("Value", vals.template_option_value)))),
  XMLElement("AdditionalAttributes", XMLAgg(XMLElement("Extend",
    XMLElement("Name", opts_tl.template_option_name), XMLElement("Value", vals.template_option_value)))))
```

`ExtMCCGroupCode` is emitted only by the opt-in branch. The setup and template extensions come from `IBY_SETUP_EXTENSIBILITY`; controls and additional attributes come from the template option tables.

## Digital Payment Account Constructor

Source: `iby_fd_extract_gen_pvt.pkb`, revision `/st_fusionapps_pt-v2mibfphdev/62`, function `get_digital_payment_acct_det`.

```sql
XMLElement("DigitalPaymentAccount",
  XMLElement("DigitalPaymentAccountInternalId", dpa.digital_payment_account_id),
  XMLElement("Token", dpa.token),
  XMLElement("TokenTypeCode", dpa.token_type_code),
  XMLElement("Alias", dpa.alias),
  XMLElement("AliasTypeCode", dpa.alias_type_code),
  XMLElement("CurrencyCode", dpa.currency_code),
  XMLElement("PaymentModeCode", dpa.payment_mode_code),
  CASE
    WHEN dpa.payment_mode_code = 'VIRTUAL_CARD' AND dpa.token IS NOT NULL
    THEN XMLElement("STPEnabled", 'Y')
    ELSE XMLElement("STPEnabled", 'N')
  END,
  XMLElement("AdditionalAttributes", ...),
  XMLElement("PayeeVCAttributes",
    XMLElement("VCRegisteredSupplier", dpa.digital_acct_provider_ref_code),
    XMLElement("Alias2", dpa.alias2),
    XMLElement("Alias3", dpa.alias3),
    XMLElement("Alias4", dpa.alias4),
    XMLElement("Alias5", dpa.alias5),
    XMLElement("VendorId", ipa.payee_supplier_id),
    XMLElement("PartySiteId", ipa.party_site_id),
    XMLElement("SiteId", ipa.supplier_site_id)))
```

The join is `IBY_PAYMENTS_ALL.DIGITAL_PAYMENT_ACCOUNT_ID` to `IBY_DIGITAL_PAYMENT_ACCOUNTS.DIGITAL_PAYMENT_ACCOUNT_ID`. Multiple-email construction is not limited to the earlier JPM opt-in branch.

## Generation Consequences

- Do not assume `BankCountry` or `ExtMCCGroupCode` exists for every deployment; map it conditionally or require setup evidence.
- `STPEnabled` is source-derived, not a provider default.
- `NetworkInstrumentIdentifier`, `ExtCompanyId`, aliases, and supplier identifiers have distinct source semantics. Do not substitute one for another without the provider specification.
- `Token` is inside the source contract but remains subject to the PCI boundary. Do not emit or persist it unless the provider profile explicitly requires it and the approved runtime boundary permits it.
