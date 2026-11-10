<?xml version="1.0" encoding="UTF-8"?>
<!-- $Header: fusionapps/fin/iby/bipub/shared/runFormat/reports/DisbursementPaymentFileFormats/JPMISO20022SEPA.xsl /st_fusionapps_pt-v2mibfphdev/9 2025/01/02 22:58:51 subachu Exp $ -->
<!--<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<!--<xsl:output/>-->
<!--<xsl:output method="xml"/>-->
<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
<xsl:key name="contacts-by-LogicalGroupReference" match="OutboundPayment" use="LogicalGrouping/LogicalGroupReference"/>
<xsl:template match="OutboundPaymentInstruction">
<xsl:variable name="lower" select="&#39;abcdefghijklmnopqrstuvwxyz&#39;"/>
<xsl:variable name="upper" select="&#39;ABCDEFGHIJKLMNOPQRSTUVWXYZ&#39;"/>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<xsl:variable name="instrid" select="PaymentInstructionInfo/InstructionReferenceNumber"/>
<CstmrCdtTrfInitn>
<GrpHdr>
<xsl:if test="not(string(PaymentInstructionInfo/InstructionReferenceNumber)=&#39;&#39;)">
<MsgId>
<xsl:value-of select="$instrid"/>
</MsgId>
</xsl:if>
<CreDtTm>
<xsl:choose>
<xsl:when test="contains(PaymentInstructionInfo/InstructionCreationDate , &#39;+&#39;)">
<xsl:value-of select="substring(PaymentInstructionInfo/InstructionCreationDate , 1,	string-length(PaymentInstructionInfo/InstructionCreationDate)-6)"/>
</xsl:when>
<xsl:otherwise>
<xsl:value-of select="PaymentInstructionInfo/InstructionCreationDate"/>
</xsl:otherwise>
</xsl:choose>
</CreDtTm>
<xsl:if test="not(string(InstructionTotals/PaymentCount)=&#39;&#39;)">
<NbOfTxs>
<xsl:value-of select="InstructionTotals/PaymentCount"/>
</NbOfTxs>
</xsl:if>
<xsl:if test="not(string(OutboundPayment/PaymentAmount/Value)=&#39;&#39;)">
<CtrlSum>
<xsl:value-of select="format-number(sum(OutboundPayment/PaymentAmount/Value), &#39;##0.00&#39;)"/>
</CtrlSum>
</xsl:if>
<InitgPty>
<Nm>
<xsl:choose>
<xsl:when test="(PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,&#39;ISO20022_IP_NAME&#39;)]/Value) and (PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,&#39;ISO20022_IP_NAME&#39;)]/Value) != &#39;&#39;">
<xsl:value-of select="PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,&#39;ISO20022_IP_NAME&#39;)]/Value"/>
</xsl:when>
<xsl:when test="not(count(/OutboundPaymentInstruction/PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[Name=&#39;CGI_INITIATING_PARTY_NAME&#39;])=0) and ( /OutboundPaymentInstruction/PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,&#39;CGI_INITIATING_PARTY_NAME&#39;)]/Value != &#39;&#39;) and not(translate(/OutboundPaymentInstruction/PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[Name=&#39;CGI_INITIATING_PARTY_NAME&#39;]/Value,$lower,$upper) = &#39;NA&#39;) ">
<xsl:value-of select="/OutboundPaymentInstruction/PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[Name=&#39;CGI_INITIATING_PARTY_NAME&#39;]/Value"/>
</xsl:when>
<xsl:otherwise>
<xsl:value-of select="InstructionGrouping/Payer/LegalEntityName"/>
</xsl:otherwise>
</xsl:choose>
</Nm>
</InitgPty>
</GrpHdr>
<xsl:for-each select="OutboundPayment[count(. | key(&#39;contacts-by-LogicalGroupReference&#39;, LogicalGrouping/LogicalGroupReference)[1]) = 1]">
<xsl:sort select="LogicalGrouping/LogicalGroupReference"/>
<PmtInf>
<xsl:if test="not(LogicalGrouping/LogicalGroupReference=&#39;&#39;)">
<PmtInfId>
<xsl:value-of select="LogicalGrouping/LogicalGroupReference"/>
</PmtInfId>
</xsl:if>
<PmtMtd>TRF</PmtMtd>
<PmtTpInf>
<SvcLvl>
<Cd>SEPA</Cd>
</SvcLvl>
</PmtTpInf>
<ReqdExctnDt>
<xsl:value-of select="PaymentDate"/>
</ReqdExctnDt>
<Dbtr>
<xsl:choose>
<xsl:when test="(/OutboundPaymentInstruction/PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[Name=&#39;DEBTOR_NAME&#39;]/Value  != &#39;&#39;)">
<Nm>
<xsl:value-of select="/OutboundPaymentInstruction/PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[Name=&#39;DEBTOR_NAME&#39;]/Value"/>
</Nm>
</xsl:when>
<xsl:otherwise>
<xsl:if test="not(string(Payer/Name)=&#39;&#39;)">
<Nm>
<xsl:value-of select="Payer/Name"/>
</Nm>
</xsl:if>
</xsl:otherwise>
</xsl:choose>
<xsl:if test="not(string(Payer/Address/Country)=&#39;&#39;)">
<PstlAdr>
<xsl:if test="not(Payer/Address/Country=&#39;&#39;)">
<Ctry>
<xsl:value-of select="Payer/Address/Country"/>
</Ctry>
</xsl:if>
</PstlAdr>
</xsl:if>

<!-- Changes as per the Company-Id uptake -->
<xsl:if test = "not(string(BankAccount/EFTUserNumber/EFTRequesterId)=&#39;&#39;) ">
<Id>
<OrgId>
<Othr>
<Id>
<xsl:value-of select="BankAccount/EFTUserNumber/EFTRequesterId"/>
</Id>
<SchmeNm>
<Prtry>JPMCOID</Prtry>
</SchmeNm>
</Othr>
</OrgId>
</Id>
</xsl:if>

</Dbtr>
<DbtrAcct>
<xsl:if test="not(BankAccount/IBANNumber=&#39;&#39;)">
<Id>
<IBAN>
<xsl:value-of select="BankAccount/IBANNumber"/>
</IBAN>
</Id>
</xsl:if>
<Ccy>
<xsl:value-of select="BankAccount/BankAccountCurrency/Code"/>
</Ccy>
</DbtrAcct>
<DbtrAgt>
<FinInstnId>
<xsl:if test="not(BankAccount/SwiftCode=&#39;&#39;)">
<BIC>
<xsl:value-of select="BankAccount/SwiftCode"/>
</BIC>
</xsl:if>
<xsl:if test="not(BankAccount/BankAddress/Country=&#39;&#39;)">
<PstlAdr>
<Ctry>
<xsl:value-of select="BankAccount/BankAddress/Country"/>
</Ctry>
</PstlAdr>
</xsl:if>
<xsl:if test="(BankAccount/SwiftCode=&#39;&#39;)">
<Othr>
<Id>NOTPROVIDED</Id>
</Othr>
</xsl:if>
</FinInstnId>
</DbtrAgt>
<xsl:if test="not(/OutboundPaymentInstruction/PaymentProcessProfile/LogicalGrouping/GroupByUltimateDebtor=&#39;N&#39;) and not(InvoicingLegalEntity/LegalEntityId=&#39;&#39;) and (InvoicingLegalEntity/LegalEntityId != Payer/LegalEntityInternalID)">
<UltmtDbtr>
<Nm>
<xsl:value-of select="InvoicingLegalEntity/Name"/>
</Nm>
</UltmtDbtr>
</xsl:if>
<xsl:for-each select="key(&#39;contacts-by-LogicalGroupReference&#39;, LogicalGrouping/LogicalGroupReference)">
<CdtTrfTxInf>
<PmtId>
<xsl:if test="not(string(PaymentNumber/PaymentReferenceNumber)=&#39;&#39;) ">
<InstrId>
<xsl:value-of select="PaymentNumber/PaymentReferenceNumber"/>
</InstrId>
</xsl:if>
<xsl:if test="not(string(PaymentNumber/PaymentReferenceNumber)=&#39;&#39;) ">
<EndToEndId>
<xsl:value-of select="PaymentNumber/PaymentReferenceNumber"/>
</EndToEndId>
</xsl:if>
</PmtId>
<xsl:if test="not(string(PaymentAmount/Value)=&#39;&#39;) and not(string(PaymentAmount/Currency/Code)=&#39;&#39;)">
<Amt>
<InstdAmt>
<xsl:attribute name="Ccy">
<xsl:value-of select="PaymentAmount/Currency/Code"/>
</xsl:attribute>
<xsl:value-of select="format-number(PaymentAmount/Value,&#39;#.00&#39;)"/>
</InstdAmt>
</Amt>
</xsl:if>
<xsl:if test="not(string(Payee/Name)=&#39;&#39;)">
<Cdtr>
<Nm>
<xsl:value-of select="Payee/Name"/>
</Nm>
</Cdtr>
</xsl:if>
<!--<xsl:if test="(not(string(PayeeBankAccount/BankAccountNumber)=&#39;&#39;) or not(string(PayeeBankAccount/IBANNumber)=&#39;&#39;));">-->
<xsl:if test="(not(string(PayeeBankAccount/BankAccountNumber)=&#39;&#39;) or not(string(PayeeBankAccount/IBANNumber)=&#39;&#39;))">
<xsl:if test="not(PayeeBankAccount/IBANNumber=&#39;&#39;)">
<CdtrAcct>
<Id>
<IBAN>
<xsl:value-of select="PayeeBankAccount/IBANNumber"/>
</IBAN>
</Id>
</CdtrAcct>
</xsl:if>
</xsl:if>
<xsl:if test="starts-with(PayeeBankAccount/AlternateBankAccountName,&#39;FFC&#39;)">
<UltmtCdtr>
<xsl:if test="not(PayeeBankAccount/AlternateBankAccountName = '')">
<xsl:variable name="afterSecondAsterisk" 
select="substring-after(substring-after(PayeeBankAccount/AlternateBankAccountName, '*'), '*')"/>
<Nm>
<xsl:value-of select="$afterSecondAsterisk"/>
</Nm>
</xsl:if>
<xsl:if test="not(PayeeBankAccount/AlternateBankAccountName = '')">
<xsl:variable name="betweenAsterisks" 
select="substring-before(substring-after(PayeeBankAccount/AlternateBankAccountName, '*'), '*')"/>
<Id>
<OrgId>
<Othr>
<Id>
<xsl:value-of select="$betweenAsterisks"/>
</Id>
</Othr>
</OrgId>
</Id>
</xsl:if>
</UltmtCdtr>
</xsl:if>
<xsl:variable name="Unstr">
<xsl:for-each select="DocumentPayable">
<xsl:value-of select="DocumentNumber/ReferenceNumber"/>
<xsl:if test="not(position() = last())">,</xsl:if>
</xsl:for-each>
</xsl:variable>
<xsl:if test="(not($Unstr =&#39;&#39;))">
<RmtInf>
<Ustrd>
<xsl:value-of select="substring($Unstr,1,140)"/>
</Ustrd>
</RmtInf>
</xsl:if>
</CdtTrfTxInf>
</xsl:for-each>
</PmtInf>
</xsl:for-each>
</CstmrCdtTrfInitn>
</Document>
</xsl:template>
</xsl:stylesheet>
