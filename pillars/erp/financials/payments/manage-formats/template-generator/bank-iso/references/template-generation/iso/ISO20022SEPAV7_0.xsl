<?xml version="1.0" encoding="UTF-8" ?> 
 <!--   $Header: fusionapps/fin/iby/bipub/shared/runFormat/reports/DisbursementPaymentFileFormats/ISO20022SEPAV7_0.xsl /st_fusionapps_pt-v2mibfphgold/1 2018/02/09 04:03:30 savamara Exp $   
  --> 
 <!--   dbdrv: exec java oracle/apps/xdo/oa/util XDOLoader.class java &phase=dat 
checkfile:~PROD:patch/115/publisher/templates:fin_IBY_SEPA_CT.xsl UPLOAD -DB_USERNAME &un_apps -DB_PASSWORD &pw_apps -JDBC_CONNECTION 
&jdbc_db_addr -LOB_TYPE TEMPLATE -APPS_SHORT_NAME IBY -LOB_CODE IBY_SEPA_CREDIT_INIT_TEMPLATE -LANGUAGE en -XDO_FILE_TYPE XSL-XML -FILE_NAME 
&fullpath:~PROD:patch/115/publisher/templates:SEPA.xsl 
  --> 
 <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output omit-xml-declaration="no" /> 
  <xsl:output method="xml" /> 
  <xsl:key name="contacts-by-LogicalGroupReference" match="OutboundPayment" use="LogicalGrouping/LogicalGroupReference" /> 
 <xsl:template match="OutboundPaymentInstruction">
 <Document  xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03"
                  xmlns:xs="http://www.w3.org/2001/XMLSchema"
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
 <BICOrBEI>
  <xsl:value-of select="PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,'ISO20022_IP_BICORBEI')]/Value"/> 
 </BICOrBEI>
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
 <PmtInfId>
  <xsl:value-of select="LogicalGrouping/LogicalGroupReference" /> 
  </PmtInfId>
  <PmtMtd>TRF</PmtMtd> 
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
  <!--better to use attributes from new logical grp table -->
 <NbOfTxs>
  <xsl:value-of select="LogicalGrouping/PaymentInformationTotal" /> 
  </NbOfTxs>
 <CtrlSum>
  <xsl:value-of select="format-number(LogicalGrouping/PaymentInformationAmountTotal, '##0.00')" /> 
  </CtrlSum>
  <xsl:if test="not(/OutboundPaymentInstruction/PaymentProcessProfile/LogicalGrouping/GroupByPaymentDateLogical='N') or not
(/OutboundPaymentInstruction/PaymentProcessProfile/LogicalGrouping/GroupByBankAccountLogical='N')">
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
 <SvcLvl>
  <Cd>SEPA</Cd> 
  </SvcLvl>
  <xsl:if test="not(DeliveryChannel/Code='')">
  <LclInstrm>
  <Cd>
  <xsl:value-of select="DeliveryChannel/Code" /> 
  </Cd> 
  </LclInstrm>
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
  <xsl:value-of select="PaymentDate" /> 
  </ReqdExctnDt>
 <Dbtr>
 <Nm>
  <xsl:value-of select="Payer/Name" /> 
  </Nm>
 <xsl:if test="not(Payer/Address/Country='') or not(Payer/Address/AddressLine1='') or not(Payer/Address/AddressLine2='')">
 <PstlAdr>
 <xsl:if test="not(Payer/Address/Country='')">
 <Ctry>
  <xsl:value-of select="Payer/Address/Country" /> 
  </Ctry>
 </xsl:if>
 <xsl:if test="not(Payer/Address/AddressLine1='')">
 <AdrLine>
  <xsl:value-of select="Payer/Address/AddressLine1" /> 
  </AdrLine>
 </xsl:if>
 <xsl:if test="not(Payer/Address/AddressLine2='')">
 <AdrLine>
  <xsl:value-of select="Payer/Address/AddressLine2" /> 
  </AdrLine>
  </xsl:if>
  </PstlAdr>
  </xsl:if>
 <Id>
 <OrgId>
 <xsl:if test="/OutboundPaymentInstruction/PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,'ISO20022_DR_BICORBEI')]/Value and /OutboundPaymentInstruction/PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,'ISO20022_DR_BICORBEI')]/Value != ''">
 <BICOrBEI>
  <xsl:value-of select="/OutboundPaymentInstruction/PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,'ISO20022_DR_BICORBEI')]/Value"/> 
 </BICOrBEI>
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
  </Othr>
  </xsl:if>
  </OrgId>
  </Id>
  </Dbtr>
 <DbtrAcct>
 <Id>
 <IBAN>
  <xsl:value-of select="BankAccount/IBANNumber" /> 
  </IBAN>
  </Id>
 <Ccy>
  <xsl:value-of select="BankAccount/BankAccountCurrency/Code" /> 
  </Ccy>
  </DbtrAcct>
 <DbtrAgt>
 <FinInstnId>
  <xsl:if test="not(BankAccount/SwiftCode='')">
	<BIC>
		<xsl:value-of select="BankAccount/SwiftCode" />
	</BIC>
  </xsl:if>
  <xsl:if test="(BankAccount/SwiftCode='')">
	<ClrSysMmbId><MmbId><Othr><Id> NOT PROVIDED</Id></Othr></MmbId></ClrSysMmbId>
  </xsl:if>
  <xsl:if test="not(BankAccount/BankAddress/Country='')"> 
  <PstlAdr> 
  <Ctry> 
  <xsl:value-of select="BankAccount/BankAddress/Country"/> 
  </Ctry> 
  </PstlAdr> 
  </xsl:if> 
  </FinInstnId>
  </DbtrAgt>
  <xsl:if test="not(/OutboundPaymentInstruction/PaymentProcessProfile/LogicalGrouping/GroupByUltimateDebtor='N') and not(InvoicingLegalEntity/LegalEntityId='') and (InvoicingLegalEntity/LegalEntityId != Payer/LegalEntityInternalID)">
 <UltmtDbtr>
 <Nm>
  <xsl:value-of select="InvoicingLegalEntity/Name" /> 
  </Nm>
  <PstlAdr>
  <AdrLine>
  <xsl:value-of select="InvoicingLegalEntity/Address/AddressLine1" /> 
  </AdrLine>
  <xsl:if test="not(InvoicingLegalEntity/Address/AddressLine2='')">
  <AdrLine>
  <xsl:value-of select="InvoicingLegalEntity/Address/AddressLine2" /> 
  </AdrLine>
  </xsl:if>
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
  <ChrgBr>SLEV</ChrgBr> 
  </xsl:if>
  <xsl:variable name="paymentdetails" select="PaymentDetails" /> 
 <xsl:for-each select="key('contacts-by-LogicalGroupReference', LogicalGrouping/LogicalGroupReference)">

<!--Start of credit transaction block-->
 <CdtTrfTxInf>
 <PmtId>
 <InstrId>
  <xsl:value-of select="PaymentNumber/PaymentReferenceNumber"/> 
  </InstrId>
 <EndToEndId>
  <xsl:value-of select="PaymentNumber/PaymentReferenceNumber"/> 
  </EndToEndId>
  </PmtId>
<!--Start of payment type information block-->
  <xsl:if test="(/OutboundPaymentInstruction/PaymentProcessProfile/LogicalGrouping/GroupByPaymentDateLogical='N') and 
(/OutboundPaymentInstruction/PaymentProcessProfile/LogicalGrouping/GroupByBankAccountLogical='N')">
 <PmtTpInf>
  <xsl:if test="(/OutboundPaymentInstruction/PaymentProcessProfile/LogicalGrouping/GroupBySettlementPriority='N')">
 <xsl:choose>
  <xsl:when test="(SettlementPriority/Code='NORMAL')">
    <InstrPrty>NORM</InstrPrty>
  </xsl:when>
  <xsl:when test="(SettlementPriority/Code='EXPRESS')">
    <InstrPrty>HIGH</InstrPrty>
  </xsl:when>
 </xsl:choose>
 </xsl:if>
  <xsl:if test="(/OutboundPaymentInstruction/PaymentProcessProfile/LogicalGrouping/GroupByServiceLevel='N')">
 <SvcLvl>
  <Cd>SEPA</Cd> 
  </SvcLvl>
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
  <xsl:if test="(/OutboundPaymentInstruction/PaymentProcessProfile/LogicalGrouping/GroupByBankChargeBearer='N')">
  <ChrgBr>SLEV</ChrgBr> 
  </xsl:if>
 <CdtrAgt>
 <FinInstnId>
   <BIC>
    <xsl:value-of select="PayeeBankAccount/SwiftCode"/> 
   </BIC>
  <xsl:if test="not(PayeeBankAccount/BankAddress/Country='')"> 
  <PstlAdr> 
   <Ctry> <xsl:value-of select="PayeeBankAccount/BankAddress/Country"/></Ctry> 
  </PstlAdr>
  </xsl:if> 
  </FinInstnId>
  </CdtrAgt>
 <Cdtr>
 <Nm>
  <xsl:value-of select="SupplierorParty/Name" /> 
  </Nm>
 <PstlAdr>
 <Ctry>
  <xsl:value-of select="SupplierorParty/Address/Country" /> 
  </Ctry>
 <AdrLine>
  <xsl:value-of select="SupplierorParty/Address/AddressLine1" /> 
  </AdrLine>
 <xsl:if test="not(SupplierorParty/Address/AddressLine2='')">
 <AdrLine>
  <xsl:value-of select="SupplierorParty/Address/AddressLine2" /> 
  </AdrLine>
  </xsl:if>
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
  <IBAN>
   <xsl:value-of select="PayeeBankAccount/IBANNumber" /> 
  </IBAN>
 </Id>
 <xsl:if test="not(PayeeBankAccount/BankAccountCurrency/Code='')">
 <Ccy>
  <xsl:value-of select="PayeeBankAccount/BankAccountCurrency/Code" />
 </Ccy>
 </xsl:if>
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
 <RmtInf>
<xsl:for-each select="DocumentPayable">
 <Strd>
  <CdtrRefInf>
  <Tp>
  <CdOrPrtry>
  <Cd>SCOR</Cd>
  </CdOrPrtry>
  <Issr>
  <xsl:value-of select="../Payee/Name"/> 
  </Issr>
  </Tp>
    <Ref>
     <xsl:choose>
      <xsl:when test="not(DocumentNumber/UniqueRemittanceIdentifier/Number='')">
      <xsl:value-of select="DocumentNumber/UniqueRemittanceIdentifier/Number" />
      </xsl:when>
      <xsl:otherwise>
      <xsl:value-of select="DocumentNumber/ReferenceNumber" />
      </xsl:otherwise>
      </xsl:choose>
    </Ref>
  </CdtrRefInf>
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
