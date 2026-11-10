<?xml version='1.0' encoding='utf-8'?>
<!--   $Header: fusionapps/fin/iby/bipub/shared/runFormat/reports/DisbursementPaymentFileFormats/ISO20022CGI2019.xsl /st_fusionapps_pt-v2mibfphdev/1 2023/03/29 12:54:52 bsharan Exp $
-->
<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output omit-xml-declaration="no" />
<xsl:output method="xml" />
<xsl:key name="contacts-by-LogicalGroupReference" match="OutboundPayment" use="LogicalGrouping/LogicalGroupReference" />
<xsl:template match="OutboundPaymentInstruction">
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.09"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<xsl:variable name="instrid" select="PaymentInstructionInfo/InstructionReferenceNumber" />
<CstmrCdtTrfInitn>
<GrpHdr>
<MsgId>
<xsl:value-of select="$instrid" />
</MsgId>
<CreDtTm>
<xsl:choose>
<xsl:when test="contains(PaymentInstructionInfo/InstructionCreationDate , '+')">
<xsl:value-of select="substring(PaymentInstructionInfo/InstructionCreationDate , 1,	string-length(PaymentInstructionInfo/InstructionCreationDate)-6)"/>
</xsl:when>
<xsl:otherwise>
<xsl:value-of select="PaymentInstructionInfo/InstructionCreationDate" />
</xsl:otherwise>
</xsl:choose>
</CreDtTm>
<NbOfTxs>
<xsl:value-of select="InstructionTotals/PaymentCount" />
</NbOfTxs>
<CtrlSum>
<xsl:value-of select="format-number(sum(OutboundPayment/PaymentAmount/Value), '##0.00')"/>
</CtrlSum>
<InitgPty>
<Nm>
<xsl:choose>
<xsl:when test="(PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,'ISO20022_IP_NAME')]/Value) and (PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,'ISO20022_IP_NAME')]/Value) != ''">
<xsl:value-of select="PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,'ISO20022_IP_NAME')]/Value"/>
</xsl:when>
<xsl:otherwise>
<xsl:value-of select="InstructionGrouping/Payer/LegalEntityName" />
</xsl:otherwise>
</xsl:choose>
</Nm>
<Id>
<OrgId>
<xsl:if test="PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,'ISO20022_IP_BICORBEI')]/Value and PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,'ISO20022_IP_BICORBEI')]/Value != ''">
<AnyBIC>
<xsl:value-of select="PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,'ISO20022_IP_BICORBEI')]/Value"/>
</AnyBIC>
</xsl:if>
<xsl:if test="not(PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,'ISO20022_IP_BICORBEI')]/Value) or (PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,'ISO20022_IP_BICORBEI')]/Value='')">
<Othr>
<Id>
<xsl:choose>
<xsl:when test="PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,'ISO20022_IP_OTHERID')]/Value and PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,'ISO20022_IP_OTHERID')]/Value !=''">
<xsl:value-of select="PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,'ISO20022_IP_OTHERID')]/Value"/>
</xsl:when>
<xsl:otherwise>
<xsl:value-of select="/OutboundPaymentInstruction/InstructionGrouping/Payer/LegalEntityRegistrationNumber" />
</xsl:otherwise>
</xsl:choose>
</Id>
</Othr>
</xsl:if>
</OrgId>
</Id>
</InitgPty>
</GrpHdr>
<xsl:for-each select="OutboundPayment[count(. | key('contacts-by-LogicalGroupReference', LogicalGrouping/LogicalGroupReference)[1]) = 1]">
<xsl:sort select="LogicalGrouping/LogicalGroupReference" />
<!--Start of payment information block-->
<PmtInf>
<xsl:if test="not(LogicalGrouping/LogicalGroupReference='')">
<PmtInfId>
<xsl:value-of select="LogicalGrouping/LogicalGroupReference" />
</PmtInfId>
</xsl:if>
<PmtMtd>
<xsl:value-of select="PaymentMethod/PaymentMethodFormatValue" />
</PmtMtd>
<xsl:if test="not(/OutboundPaymentInstruction/PaymentProcessProfile/BatchBookingFlag='')">
<BtchBookg>
<xsl:choose>
<xsl:when test="(/OutboundPaymentInstruction/PaymentProcessProfile/BatchBookingFlag='N')">
<xsl:text>false</xsl:text>
</xsl:when>
<xsl:otherwise>
<xsl:text>true</xsl:text>
</xsl:otherwise>
</xsl:choose>
</BtchBookg>
</xsl:if>
<!-- get from new logical table instead -->
<NbOfTxs>
<xsl:value-of select="LogicalGrouping/PaymentInformationTotal" />
</NbOfTxs>
<CtrlSum>
<xsl:value-of select="format-number(LogicalGrouping/PaymentInformationAmountTotal, '##0.00')" />
</CtrlSum>
<xsl:if test="not(/OutboundPaymentInstruction/PaymentProcessProfile/LogicalGrouping/GroupByPaymentDateLogical='N') or not (/OutboundPaymentInstruction/PaymentProcessProfile/LogicalGrouping/GroupByBankAccountLogical='N')">
<!--Start of payment type information block-->
<PmtTpInf>
<xsl:if test="(/OutboundPaymentInstruction/PaymentProcessProfile/LogicalGrouping/GroupBySettlementPriority='Y')">
<xsl:choose>
<xsl:when test="(SettlementPriority/Code='NORMAL')">
<InstrPrty>NORM</InstrPrty>
</xsl:when>
<xsl:when test="(SettlementPriority/Code='EXPRESS')">
<InstrPrty>HIGH</InstrPrty>
</xsl:when>
</xsl:choose>
</xsl:if>
<xsl:if test="not(/OutboundPaymentInstruction/PaymentProcessProfile/LogicalGrouping/GroupByServiceLevel='N')">
<xsl:if test="not(PaymentMethod/PaymentMethodFormatValue='CHK')">
<xsl:if test="not(ServiceLevel/Code='')">
<SvcLvl>
<Cd>
<xsl:value-of select="ServiceLevel/Code" />
</Cd>
</SvcLvl>
</xsl:if>
<xsl:if test="not(DeliveryChannel/Code='')">
<LclInstrm>
<Cd>
<xsl:value-of select="DeliveryChannel/Code" />
</Cd>
</LclInstrm>
</xsl:if>
</xsl:if>
</xsl:if>
<xsl:if test="(/OutboundPaymentInstruction/PaymentProcessProfile/LogicalGrouping/GroupByCategoryPurpose='Y')">
<CtgyPurp>
<Cd>SUPP</Cd>
</CtgyPurp>
</xsl:if>
</PmtTpInf>
<!--End of payment type information block-->
</xsl:if>
<ReqdExctnDt>
<Dt>
<xsl:value-of select="PaymentDate" />
</Dt>
</ReqdExctnDt>
<Dbtr>
<Nm>
<xsl:value-of select="Payer/Name" />
</Nm>
<PstlAdr>
<StrtNm>
<xsl:value-of select="Payer/Address/AddressLine1" />
</StrtNm>
<PstCd>
<xsl:value-of select="Payer/Address/PostalCode" />
</PstCd>
<TwnNm>
<xsl:value-of select="Payer/Address/City" />
</TwnNm>
<xsl:if test="not(Payer/Address/County='') or not(Payer/Address/State='') or not(Payer/Address/Province='')">
<CtrySubDvsn>
<xsl:value-of select="Payer/Address/County" />
<xsl:value-of select="Payer/Address/State" />
<xsl:value-of select="Payer/Address/Province" />
</CtrySubDvsn>
</xsl:if>
<xsl:if test="not(Payer/Address/Country='')">
<Ctry>
<xsl:value-of select="Payer/Address/Country" />
</Ctry>
</xsl:if>
</PstlAdr>
<Id>
<OrgId>
<xsl:if test="/OutboundPaymentInstruction/PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,'ISO20022_DR_BICORBEI')]/Value and /OutboundPaymentInstruction/PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,'ISO20022_DR_BICORBEI')]/Value != ''">
<AnyBIC>
<xsl:value-of select="/OutboundPaymentInstruction/PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,'ISO20022_DR_BICORBEI')]/Value"/>
</AnyBIC>
</xsl:if>
<xsl:if test="not(/OutboundPaymentInstruction/PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,'ISO20022_DR_BICORBEI')]/Value) or /OutboundPaymentInstruction/PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,'ISO20022_DR_BICORBEI')]/Value = ''">
<Othr>
<Id>
<xsl:choose>
<xsl:when test="/OutboundPaymentInstruction/PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,'ISO20022_DR_OTHERID')]/Value and /OutboundPaymentInstruction/PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,'ISO20022_DR_OTHERID')]/Value != ''">
<xsl:value-of select="/OutboundPaymentInstruction/PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,'ISO20022_DR_OTHERID')]/Value"/>
</xsl:when>
<xsl:otherwise>
<xsl:value-of select="/OutboundPaymentInstruction/InstructionGrouping/Payer/LegalEntityRegistrationNumber" />
</xsl:otherwise>
</xsl:choose>
</Id>
<xsl:if test="/OutboundPaymentInstruction/PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,'ISO20022_DR_ID_SCHME_NAME')]/Value and /OutboundPaymentInstruction/PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,'ISO20022_DR_ID_SCHME_NAME')]/Value!=''">
<SchmeNm>
<Cd>
<xsl:value-of select="/OutboundPaymentInstruction/PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,'ISO20022_DR_ID_SCHME_NAME')]/Value"/>
</Cd>
</SchmeNm>
</xsl:if>
</Othr>
</xsl:if>
</OrgId>
</Id>
</Dbtr>
<DbtrAcct>
<Id>
<xsl:if test="not(BankAccount/IBANNumber='')">
<IBAN>
<xsl:value-of select="BankAccount/IBANNumber" />
</IBAN>
</xsl:if>
<!-- if no IBAN, use bank account number-->
<xsl:if test="(BankAccount/IBANNumber='')">
<Othr>
<Id>
<xsl:value-of select="BankAccount/BankAccountNumber" />
</Id>
</Othr>
</xsl:if>
</Id>
<xsl:if test="not(BankAccount/BankAccountType/Code='')">
<Tp>
<Cd>
<xsl:value-of select="BankAccount/BankAccountType/Code" />
</Cd>
</Tp>
</xsl:if>
<Ccy>
<xsl:value-of select="BankAccount/BankAccountCurrency/Code" />
</Ccy>
</DbtrAcct>
<DbtrAgt>
<FinInstnId>
<xsl:if test="not(BankAccount/SwiftCode='')">
<BICFI>
<xsl:value-of select="BankAccount/SwiftCode" />
</BICFI>
</xsl:if>
<xsl:if test="(BankAccount/SwiftCode='')">
<xsl:if test="not(BankAccount/BranchNumber='')">
<ClrSysMmbId>
<MmbId>
<xsl:value-of select="BankAccount/BranchNumber" />
</MmbId>
</ClrSysMmbId>
</xsl:if>
</xsl:if>
<xsl:if test="not(BankAccount/BankAddress/Country='')">
<PstlAdr>
<Ctry>
<xsl:value-of select="BankAccount/BankAddress/Country" />
</Ctry>
</PstlAdr>
</xsl:if>
</FinInstnId>
<xsl:if test="not(BankAccount/BranchNumber='')">
<BrnchId>
<Id>
<xsl:value-of select="BankAccount/BranchNumber" />
</Id>
</BrnchId>
</xsl:if>
</DbtrAgt>
<xsl:if test="not(/OutboundPaymentInstruction/PaymentProcessProfile/LogicalGrouping/GroupByUltimateDebtor='N')  and not(InvoicingLegalEntity/LegalEntityId='') and (InvoicingLegalEntity/LegalEntityId != Payer/LegalEntityInternalID)">
<UltmtDbtr>
<Nm>
<xsl:value-of select="InvoicingLegalEntity/Name" />
</Nm>
<PstlAdr>
<PstCd>
<xsl:value-of select="InvoicingLegalEntity/Address/PostalCode" />
</PstCd>
<TwnNm>
<xsl:value-of select="InvoicingLegalEntity/Address/City" />
</TwnNm>
<CtrySubDvsn>
<xsl:value-of select="InvoicingLegalEntity/Address/County" />
<xsl:value-of select="InvoicingLegalEntity/Address/State" />
<xsl:value-of select="InvoicingLegalEntity/Address/Province" />
</CtrySubDvsn>
<Ctry>
<xsl:value-of select="InvoicingLegalEntity/Address/Country" />
</Ctry>
</PstlAdr>
<Id>
<OrgId>
<Othr>
<Id>
<xsl:value-of select="InvoicingLegalEntity/LegalEntityRegistrationNumber" />
</Id>
</Othr>
</OrgId>
</Id>

</UltmtDbtr>
</xsl:if>
<xsl:if test="not(/OutboundPaymentInstruction/PaymentProcessProfile/LogicalGrouping/GroupByBankChargeBearer='N')">
<xsl:if test="not(PaymentMethod/PaymentMethodFormatValue='CHK')">
<xsl:if test="not(BankCharges/BankChargeBearer/Code='')">
<ChrgBr>
<xsl:choose>
<xsl:when test="(BankCharges/BankChargeBearer/Code='BEN') or (BankCharges/BankChargeBearer/Code='PAYEE_PAYS_EXPRESS')">
<xsl:text>CRED</xsl:text>
</xsl:when>
<xsl:when test="(BankCharges/BankChargeBearer/Code='OUR')">
<xsl:text>DEBT</xsl:text>
</xsl:when>
<xsl:when test="(BankCharges/BankChargeBearer/Code='SHA')">
<xsl:text>SHAR</xsl:text>
</xsl:when>
<xsl:otherwise>SLEV</xsl:otherwise>
</xsl:choose>
</ChrgBr>
</xsl:if>
</xsl:if>
</xsl:if>
<xsl:variable name="paymentdetails" select="PaymentDetails" />
<xsl:for-each select="key('contacts-by-LogicalGroupReference', LogicalGrouping/LogicalGroupReference)">

<!--Start of credit transaction block-->
<CdtTrfTxInf>
<PmtId>
<InstrId>
<xsl:value-of select="PaymentNumber/PaymentReferenceNumber" />
</InstrId>
<EndToEndId>
<xsl:value-of select="PaymentNumber/PaymentReferenceNumber" />
</EndToEndId>
</PmtId>

<!--Start of payment type information block-->
<xsl:if test="(/OutboundPaymentInstruction/PaymentProcessProfile/LogicalGrouping/GroupByPaymentDateLogical='N') and (/OutboundPaymentInstruction/PaymentProcessProfile/LogicalGrouping/GroupByBankAccountLogical='N')">
<PmtTpInf>
<xsl:if test="not(PaymentMethod/PaymentMethodFormatValue='CHK')">
<xsl:if test="((/OutboundPaymentInstruction/PaymentProcessProfile/LogicalGrouping/GroupBySettlementPriority='N') and not(SettlementPriority/Code=''))">
<xsl:choose>
<xsl:when test="(SettlementPriority/Code='NORMAL')">
<InstrPrty>NORM</InstrPrty>
</xsl:when>
<xsl:when test="(SettlementPriority/Code='EXPRESS')">
<InstrPrty>HIGH</InstrPrty>
</xsl:when>
</xsl:choose>
</xsl:if>
</xsl:if>
<xsl:if test="not(PaymentMethod/PaymentMethodFormatValue='CHK')">
<xsl:if test="(/OutboundPaymentInstruction/PaymentProcessProfile/LogicalGrouping/GroupByServiceLevel='N')">
<SvcLvl>
<Cd>
<xsl:value-of select="ServiceLevel/Code" />
</Cd>
</SvcLvl>
<LclInstrm>
<Cd>
<xsl:value-of select="DeliveryChannel/Code" />
</Cd>
</LclInstrm>
</xsl:if>
</xsl:if>
<xsl:if test="not(/OutboundPaymentInstruction/PaymentProcessProfile/LogicalGrouping/GroupByCategoryPurpose='Y')">
<CtgyPurp>
<Cd>SUPP</Cd>
</CtgyPurp>
</xsl:if>
</PmtTpInf>
<!--End of payment type information block-->
</xsl:if>
<Amt>
<InstdAmt>
<xsl:attribute name="Ccy">
<xsl:value-of select="PaymentAmount/Currency/Code" />
</xsl:attribute>
<xsl:value-of select="format-number(PaymentAmount/Value, '##0.00')" />
</InstdAmt>
</Amt>
<xsl:if test="not(PaymentMethod/PaymentMethodFormatValue='CHK')">
<xsl:if test="(/OutboundPaymentInstruction/PaymentProcessProfile/LogicalGrouping/GroupByBankChargeBearer='N')">
<xsl:if test="not(BankCharges/BankChargeBearer/Code='')">
<ChrgBr>
<xsl:choose>
<xsl:when test="(BankCharges/BankChargeBearer/Code='BEN') or (BankCharges/BankChargeBearer/Code='PAYEE_PAYS_EXPRESS')">
<xsl:text>CRED</xsl:text>
</xsl:when>
<xsl:when test="(BankCharges/BankChargeBearer/Code='OUR')">
<xsl:text>DEBT</xsl:text>
</xsl:when>
<xsl:when test="(BankCharges/BankChargeBearer/Code='SHA')">
<xsl:text>SHAR</xsl:text>
</xsl:when>
<xsl:otherwise>SLEV</xsl:otherwise>
</xsl:choose>
</ChrgBr>
</xsl:if>
</xsl:if>
</xsl:if>
<CdtrAgt>
<FinInstnId>
<xsl:if test="not(PayeeBankAccount/SwiftCode='')">
<BICFI>
<xsl:value-of select="PayeeBankAccount/SwiftCode" />
</BICFI>
</xsl:if>
<xsl:if test="(PayeeBankAccount/SwiftCode='')">
<xsl:if test="not(PayeeBankAccount/BranchNumber='')">
<ClrSysMmbId>
<MmbId>
<xsl:value-of select="PayeeBankAccount/BranchNumber" />
</MmbId>
</ClrSysMmbId>
</xsl:if>
</xsl:if>
<xsl:if test="not(PayeeBankAccount/BankName='')">
<Nm>
<xsl:value-of select="PayeeBankAccount/BankName" />
</Nm>
</xsl:if>
<xsl:if test="not(PayeeBankAccount/BankAddress/Country='')">
<PstlAdr>
<Ctry>
<xsl:value-of select="PayeeBankAccount/BankAddress/Country" />
</Ctry>
</PstlAdr>
</xsl:if>
</FinInstnId>
<xsl:if test="not(PayeeBankAccount/BranchNumber='')">
<BrnchId>
<Id>
<xsl:value-of select="PayeeBankAccount/BranchNumber" />
</Id>
</BrnchId>
</xsl:if>
</CdtrAgt>
<Cdtr>
<Nm>
<xsl:value-of select="SupplierorParty/Name" />
</Nm>
<PstlAdr>
<StrtNm>
<xsl:value-of select="SupplierorParty/Address/AddressLine1" />
</StrtNm>
<PstCd>
<xsl:value-of select="SupplierorParty/Address/PostalCode" />
</PstCd>
<TwnNm>
<xsl:value-of select="SupplierorParty/Address/City" />
</TwnNm>
<xsl:if test="not(SupplierorParty/Address/County='') or not(SupplierorParty/Address/State='') or not(SupplierorParty/Address/Province='')">
<CtrySubDvsn>
<xsl:value-of select="SupplierorParty/Address/County" />
<xsl:value-of select="SupplierorParty/Address/State" />
<xsl:value-of select="SupplierorParty/Address/Province" />
</CtrySubDvsn>
</xsl:if>
<Ctry>
<xsl:value-of select="SupplierorParty/Address/Country" />
</Ctry>
</PstlAdr>
<xsl:if test="(PaymentSourceInfo/EmployeePaymentFlag='N')">
<Id>
<OrgId>
<xsl:if test="not(SupplierorParty/TaxRegistrationNumber='')">
<Othr>
<Id>
<xsl:value-of select="SupplierorParty/TaxRegistrationNumber" />
</Id>
</Othr>
</xsl:if>
<xsl:if test="(SupplierorParty/TaxRegistrationNumber='')">
<xsl:if test="not(SupplierorParty/LegalEntityRegistrationNumber='')">
<Othr>
<Id>
<xsl:value-of select="SupplierorParty/LegalEntityRegistrationNumber" />
</Id>
</Othr>
</xsl:if>
<xsl:if test="(SupplierorParty/LegalEntityRegistrationNumber='')">
<xsl:if test="not(SupplierorParty/SupplierNumber='')">
<Othr>
<Id>
<xsl:value-of select="SupplierorParty/SupplierNumber" />
</Id>
</Othr>
</xsl:if>
<xsl:if test="(SupplierorParty/SupplierNumber='')">
<xsl:if test="not(SupplierorParty/PartyNumber='')">
<Othr>
<Id>
<xsl:value-of select="SupplierorParty/PartyNumber" />
</Id>
</Othr>
</xsl:if>
<xsl:if test="(SupplierorParty/PartyNumber='')">
<Othr>
<Id>
<xsl:value-of select="SupplierorParty/FirstPartyReference" />
</Id>
</Othr>
</xsl:if>
</xsl:if>
</xsl:if>
</xsl:if>
</OrgId>
</Id>
</xsl:if>
<!--employee payments-->
<xsl:if test="(PaymentSourceInfo/EmployeePaymentFlag='Y')">
<Id>
<PrvtId>
<DtAndPlcOfBirth>
<BirthDt>
<xsl:value-of select="substring(Payee/PersonInfo/BirthDate, 0, 11)" />
</BirthDt>
<CityOfBirth>
<xsl:value-of select="Payee/PersonInfo/TownOfBirth" />
</CityOfBirth>
<CtryOfBirth>
<xsl:value-of select="Payee/PersonInfo/CountryOfBirth" />
</CtryOfBirth>
</DtAndPlcOfBirth>
<!-- <SchemeNm>
<Cd>NIDL</Cd>
</SchemeNm>-->
</PrvtId>
</Id>
</xsl:if>
</Cdtr>
<CdtrAcct>
<Id>
<xsl:if test="not(PayeeBankAccount/IBANNumber='')">
<IBAN>
<xsl:value-of select="PayeeBankAccount/IBANNumber" />
</IBAN>
</xsl:if>
<!-- if no IBAN, use bank account number-->
<xsl:if test="(PayeeBankAccount/IBANNumber='')">
<Othr>
<Id>
<xsl:value-of select="PayeeBankAccount/BankAccountNumber" />
</Id>
</Othr>
</xsl:if>
</Id>
<xsl:if test="not(PayeeBankAccount/BankAccountName='')">
<Nm>
<xsl:value-of select="PayeeBankAccount/BankAccountName" />
</Nm>
</xsl:if>
</CdtrAcct>
<xsl:if test="(Payee/PartyInternalID!= SupplierorParty/PartyInternalID)">
<UltmtCdtr>
<Nm>
<xsl:value-of select="Payee/Name" />
</Nm>
<PstlAdr>
<StrtNm>
<xsl:value-of select="Payee/Address/AddressLine1" />
</StrtNm>
<PstCd>
<xsl:value-of select="Payee/Address/PostalCode" />
</PstCd>
<TwnNm>
<xsl:value-of select="Payee/Address/City" />
</TwnNm>
<xsl:if test="not(Payee/Address/County='') or not(Payee/Address/State='') or not(Payee/Address/Province='')">
<CtrySubDvsn>
<xsl:value-of select="Payee/Address/County" />
<xsl:value-of select="Payee/Address/State" />
<xsl:value-of select="Payee/Address/Province" />
</CtrySubDvsn>
</xsl:if>
<Ctry>
<xsl:value-of select="Payee/Address/Country" />
</Ctry>
</PstlAdr>
<Id>
<OrgId>
<xsl:if test="not(Payee/TaxRegistrationNumber='')">
<Othr>
<Id>
<xsl:value-of select="Payee/TaxRegistrationNumber" />
</Id>
</Othr>
</xsl:if>
<xsl:if test="(Payee/TaxRegistrationNumber='')">
<xsl:if test="not(Payee/LegalEntityRegistrationNumber='')">
<Othr>
<Id>
<xsl:value-of select="Payee/LegalEntityRegistrationNumber" />
</Id>
</Othr>
</xsl:if>
<xsl:if test="(Payee/LegalEntityRegistrationNumber='')">
<xsl:if test="not(Payee/SupplierNumber='')">
<Othr>
<Id>
<xsl:value-of select="Payee/SupplierNumber" />
</Id>
</Othr>
</xsl:if>
<xsl:if test="(Payee/SupplierNumber='')">
<xsl:if test="not(Payee/PartyNumber='')">
<Othr>
<Id>
<xsl:value-of select="Payee/PartyNumber" />
</Id>
</Othr>
</xsl:if>
<xsl:if test="(Payee/PartyNumber='')">
<Othr>
<Id>
<xsl:value-of select="Payee/FirstPartyReference" />
</Id>
</Othr>

</xsl:if>
</xsl:if>
</xsl:if>
</xsl:if>
</OrgId>

</Id>
</UltmtCdtr>
</xsl:if>
<xsl:if test="(PaymentMethod/PaymentMethodFormatValue='TRF') and (not(/OutboundPaymentInstruction/PaymentInstructionInfo/BankInstruction[2]/Meaning='') or not(/OutboundPaymentInstruction/PaymentInstructionInfo/BankInstructionDetails=''))">
<InstrForCdtrAgt>
<xsl:if test="not(/OutboundPaymentInstruction/PaymentInstructionInfo/BankInstruction[2]/Meaning='')">
<Cd>
<xsl:value-of select="/OutboundPaymentInstruction/PaymentInstructionInfo/BankInstruction[2]/Meaning" />
</Cd>
</xsl:if>
<xsl:if test="not(/OutboundPaymentInstruction/PaymentInstructionInfo/BankInstructionDetails='')">
<InstrInf>
<xsl:value-of select="/OutboundPaymentInstruction/PaymentInstructionInfo/BankInstructionDetails"/>
</InstrInf>
</xsl:if>
</InstrForCdtrAgt>
</xsl:if>
<xsl:if test="(PaymentMethod/PaymentMethodFormatValue='TRF') and not(/OutboundPaymentInstruction/PaymentInstructionInfo/BankInstruction[1]/Meaning='')">
<InstrForDbtrAgt>
<xsl:value-of select="/OutboundPaymentInstruction/PaymentInstructionInfo/BankInstruction[1]/Meaning" />
</InstrForDbtrAgt>
</xsl:if>
<xsl:if test="not(PaymentReason/Code = '')">
<Purp>
<Cd>
<xsl:value-of select="PaymentReason/Code" />
</Cd>
</Purp>
</xsl:if>
<xsl:if test="not(Payee/TaxRegistrationNumber='') or not(Payer/TaxRegistrationNumber='')">
<Tax>
<xsl:if test="not(Payee/TaxRegistrationNumber='')">
<Cdtr>
<TaxId>
<xsl:value-of select="Payee/TaxRegistrationNumber" />
</TaxId>
</Cdtr>
</xsl:if>
<xsl:if test="not(Payer/TaxRegistrationNumber='')">
<Dbtr>
<TaxId>
<xsl:value-of select="Payer/TaxRegistrationNumber" />
</TaxId>
</Dbtr>
</xsl:if>
</Tax>
</xsl:if>
<RmtInf>
<xsl:for-each select="DocumentPayable">
<Strd>
<RfrdDocInf>
<Tp>
<CdOrPrtry>
<Cd>
<xsl:choose>
<xsl:when test="(DocumentType/Code='STANDARD') or (DocumentType/Code='INTEREST')">
<xsl:text>CINV</xsl:text>
</xsl:when>
<xsl:when test="(DocumentType/Code='CREDIT')">
<xsl:text>CREN</xsl:text>
</xsl:when>
<xsl:when test="(DocumentType/Code='DEBIT')">
<xsl:text>DEBN</xsl:text>
</xsl:when>
</xsl:choose>
</Cd>
</CdOrPrtry>
<Issr>
<xsl:value-of select="../Payee/Name" />
</Issr>
</Tp>
<Nb>
<xsl:value-of select="DocumentNumber/ReferenceNumber" />
</Nb>
<RltdDt>
<xsl:value-of select="DocumentDate" />
</RltdDt>
</RfrdDocInf>
<RfrdDocAmt>
<xsl:if test="not(TotalDocumentAmount/Value = 0)">
<DuePyblAmt>
<xsl:attribute name="Ccy">
<xsl:value-of select="TotalDocumentAmount/Currency/Code" />
</xsl:attribute>
<xsl:value-of select="format-number(TotalDocumentAmount/Value, '##0.00')" />
</DuePyblAmt>
</xsl:if>
<xsl:if test="not(DiscountTaken/Amount/Value = 0)">
<DscntApldAmt>
<xsl:attribute name="Ccy">
<xsl:value-of select="DiscountTaken/Amount/Currency/Code" />
</xsl:attribute>
<xsl:value-of select="format-number(DiscountTaken/Amount/Value, '##0.00')" />
</DscntApldAmt>
</xsl:if>
<xsl:if test="not(TotalDocumentTaxAmount/Value = 0)">
<TaxAmt>
<xsl:attribute name="Ccy">
<xsl:value-of select="TotalDocumentTaxAmount/Currency/Code" />
</xsl:attribute>
<xsl:value-of select="format-number(TotalDocumentTaxAmount/Value, '##0.00')" />
</TaxAmt>
</xsl:if>
</RfrdDocAmt>
<xsl:if test="not(DocumentNumber/UniqueRemittanceIdentifier/Number='')">
<CdtrRefInf>
<Tp>
<CdOrPrtry>
<Cd>SCOR</Cd>
</CdOrPrtry>
<Issr>
<xsl:value-of select="../Payee/Name" />
</Issr>
</Tp>
<Ref>
<xsl:value-of select="DocumentNumber/UniqueRemittanceIdentifier/Number" />
</Ref>
</CdtrRefInf>
</xsl:if>
</Strd>
</xsl:for-each>
</RmtInf>
</CdtTrfTxInf>
</xsl:for-each>
</PmtInf>
</xsl:for-each>
</CstmrCdtTrfInitn>
</Document>
</xsl:template>
</xsl:stylesheet>
