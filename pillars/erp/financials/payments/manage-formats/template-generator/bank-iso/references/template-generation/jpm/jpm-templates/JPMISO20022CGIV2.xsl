<?xml version="1.0" encoding="UTF-8"?>
<!-- $Header: fusionapps/fin/iby/bipub/shared/runFormat/reports/DisbursementPaymentFileFormats/JPMISO20022CGIV2.xsl /st_fusionapps_pt-v2mibfphdev/4 2025/08/19 23:45:18 subachu Exp $ -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
	<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
	<xsl:key name="contacts-by-LogicalGroupReference" match="OutboundPayment" use="LogicalGrouping/LogicalGroupReference"/>
	<xsl:template match="OutboundPaymentInstruction">
		<xsl:variable name="lower" select="&#39;abcdefghijklmnopqrstuvwxyz&#39;"/>
		<xsl:variable name="upper" select="&#39;ABCDEFGHIJKLMNOPQRSTUVWXYZ&#39;"/>
		<xsl:variable name="leintid" select="substring(InstructionGrouping/Payer/LegalEntityInternalID,(string-length(InstructionGrouping/Payer/LegalEntityInternalID)-4)+1,4)"/>
		<xsl:variable name="endtoend" select="&#39;N&#39;"/>
		<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
			<xsl:variable name="instrid" select="PaymentInstructionInfo/InstructionReferenceNumber"/>
			<xsl:variable name="dateNow" select="substring-before(PaymentInstructionInfo/InstructionCreationDate,&#39;T&#39;)"/>
			<xsl:variable name="NURGBankCdToMMBID">|HK|JP|NZ|KR|TW|TH|MX|SA|CH|ZA|BR|CZ|DK|SE|NO|</xsl:variable>
			<xsl:variable name="NURGBankCdBranchNuToMMBID">|AU|SG|</xsl:variable>
			<xsl:variable name="NURGBranchNuToBranchId">|HK|JP|NZ|TW|TH|BR|</xsl:variable>
			<xsl:variable name="URGPDOMBankCdToMMBID">|JP|SA|CH|BR|KR|MX|ZA|</xsl:variable>
			<xsl:variable name="URGPDOMBankCdBranchNuToMMBID">|AU|TW|NL|ES|</xsl:variable>
			<xsl:variable name="URGPDOMBranchNuToBranchId">|JP|BR|</xsl:variable>
			<xsl:variable name="URGPXBordBankCdToMMBID">|KR|MX|SA|CH|ZA|CZ|DK|SE|NO|</xsl:variable>
			<xsl:variable name="URGPXBordBankCdBranchNuToMMBID">|HK|JP|NZ|TW|TH|BR|</xsl:variable>
			<xsl:variable name="URGPXBordBranchNuToBranchId">|##|</xsl:variable>
			<xsl:variable name="BKTRBankCdToMMBID">|MX|BR|</xsl:variable>
			<xsl:variable name="BKTRBranchNuToMMBID">|CA|US|</xsl:variable>
			<xsl:variable name="BKTRBankCdBranchNuToMMBID">|##|</xsl:variable>
			<xsl:variable name="BKTRBranchNuToBranchId">|BR|</xsl:variable>
			<xsl:variable name="URNSBankCdToMMBID">|##|</xsl:variable>
			<xsl:variable name="URNSBankCdBranchNuToMMBID">|##|</xsl:variable>
			<xsl:variable name="URNSBranchNuToBranchId">|##|</xsl:variable>
			<xsl:variable name="StrdInvchk" select="&#39;Y&#39;"/>
			<xsl:variable name="year" select="substring(PaymentDate,3,2)"/>
			<xsl:variable name="MYNBPSCRDID" select="Payee/LegalEntityRegistrationNumber"/>
			<xsl:variable name="TWGIRCRDID" select="Payee/LegalEntityRegistrationNumber"/>
			<xsl:variable name="MXTRFCRDID" select="Payee/TaxRegistrationNumber"/>
			<xsl:variable name="BRTRFCRDID" select="Payee/TaxRegistrationNumber"/>
			<xsl:variable name="CLTRFCRDID" select="Payee/TaxRegistrationNumber"/>
			<xsl:variable name="ARTRFCRDID" select="Payee/TaxRegistrationNumber"/>
			<xsl:variable name="endtoend" select="&#39;N&#39;"/>
			<xsl:variable name="CNTRFNURG" select="&#39;Y&#39;"/>
			<xsl:variable name="CNTRFURGP" select="&#39;Y&#39;"/>
			<xsl:variable name="TWTRFURGP" select="&#39;Y&#39;"/>
			<xsl:variable name="JPTRFNURG" select="&#39;Y&#39;"/>
			<xsl:variable name="KRTRFNURG" select="&#39;Y&#39;"/>
			<xsl:variable name="TWTRFNURG" select="&#39;Y&#39;"/>
			<xsl:variable name="THTRFNURG" select="&#39;Y&#39;"/>
			<xsl:variable name="TWCHKBCHQ" select="&#39;Y&#39;"/>
			<xsl:variable name="THCHKBCHQ" select="&#39;Y&#39;"/>
			<xsl:variable name="HKCHKCCHQ" select="&#39;Y&#39;"/>
			<xsl:variable name="TWCHKCCHQ" select="&#39;Y&#39;"/>
			<xsl:variable name="THCHKCCHQ" select="&#39;Y&#39;"/>
			<xsl:variable name="PayerBankCountry" select="BankAccount/BankAddress/Country"/>
			<xsl:variable name="PrtLctnDff" select="&#39;&#39;"/>
			<xsl:variable name="RgnlClrnZnDff" select="&#39;&#39;"/>
			<xsl:variable name="CdtrIdDff" select="&#39;&#39;"/>
			<xsl:variable name="CtryOfResDff" select="&#39;&#39;"/>
			<xsl:variable name="Actualsuplrtaxdff" select="&#39;&#39;"/>
			<xsl:variable name="Actualsuplrnmdff" select="&#39;&#39;"/>
			<xsl:variable name="Admstnzndff" select="&#39;&#39;"/>
			<xsl:variable name="Seqnodff" select="&#39;&#39;"/>
			<xsl:variable name="Wthtaxtpdff" select="&#39;&#39;"/>
			<xsl:variable name="Wthtaxctgrydff" select="&#39;&#39;"/>
			<xsl:variable name="Taxctgrydtlsdff" select="&#39;&#39;"/>
			<xsl:variable name="Taxfrmscddff" select="&#39;&#39;"/>
			<xsl:variable name="Taxratedff" select="&#39;&#39;"/>
			<xsl:variable name="WHTTaxAmount">
				<xsl:value-of select="translate(format-number(sum(DocumentPayable/DocumentPayableLine[LineType/Code =&#39;AWT&#39;]/LineGrossAmount/Value), &#39;##0.00&#39;),&#39;-&#39;,&#39;&#39;)"/>
			</xsl:variable>
			<xsl:variable name="ActualsuplAdd1dff" select="DocumentPayable[1]/Extend/XX_TH_WHT_ALT_ADD1"/>
			<xsl:variable name="ActualsuplAdd2dff" select="DocumentPayable[1]/Extend/XX_TH_WHT_ALT_ADD2"/>
			<xsl:variable name="Taxaddtnlinfdff" select="DocumentPayable[1]/Extend/XX_TH_WHT_TAX_ADDNL_INFO"/>
			<xsl:variable name="BridJP" select="&#39;&#39;"/>
			<xsl:variable name="BridHK" select="&#39;&#39;"/>
			<xsl:variable name="BridNZ" select="&#39;&#39;"/>
			<xsl:variable name="BridTW" select="&#39;&#39;"/>
			<xsl:variable name="BridTH" select="&#39;&#39;"/>
			<xsl:variable name="BridBR" select="&#39;&#39;"/>
			<xsl:variable name="FFCACCOUNT" select="&#39;&#39;"/>
			<xsl:variable name="rrdetyp" select="&#39;corporation&#39;"/>
			<!--Start of Tags-->
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
					<!--Start of Variables-->
					<xsl:variable name="pmthd2" select="PaymentMethod/PaymentMethodFormatValue"/>
					<xsl:variable name="pmthd">
						<xsl:choose>
							<xsl:when test="$pmthd2=&#39;TRF&#39;">TRF</xsl:when>
							<xsl:when test="$pmthd2=&#39;CHK&#39;">CHK</xsl:when>
						</xsl:choose>
					</xsl:variable>
					<xsl:variable name="dlvrchnlcodeh">
						<xsl:choose>
							<xsl:when test="not(string(DeliveryChannel/FormatValue)=&#39;&#39;)">
								<xsl:value-of select="DeliveryChannel/FormatValue"/>
							</xsl:when>
							<xsl:otherwise>
								<xsl:choose>
									<xsl:when test="not(string(DocumentPayable[1]/DeliveryChannel/FormatValue)=&#39;&#39;)">
										<xsl:value-of select="DocumentPayable[1]/DeliveryChannel/FormatValue"/>
									</xsl:when>
									<xsl:otherwise>
										<xsl:if test="not(string(DeliveryChannel/Code)=&#39;&#39;)">
											<xsl:value-of select="DeliveryChannel/Code"/>
										</xsl:if>
									</xsl:otherwise>
								</xsl:choose>
							</xsl:otherwise>
						</xsl:choose>
					</xsl:variable>
					<xsl:variable name="svlvl">
						<xsl:choose>
							<xsl:when test="not(string(ServiceLevel/FormatValue)=&#39;&#39;) ">
								<xsl:value-of select="ServiceLevel/FormatValue"/>
							</xsl:when>
							<xsl:otherwise>
								<xsl:choose>
									<xsl:when test="not(string(ServiceLevel/Code)=&#39;&#39;) ">
										<xsl:value-of select="ServiceLevel/Code"/>
									</xsl:when>
									<xsl:otherwise>
										<xsl:if test="$pmthd2=&#39;TRF&#39; and PayeeBankAccount/SwiftCode=BankAccount/SwiftCode ">BKTR
	</xsl:if>
									</xsl:otherwise>
								</xsl:choose>
							</xsl:otherwise>
						</xsl:choose>
					</xsl:variable>
					<xsl:variable name="dlvrchnlcodemeaning">
						<xsl:choose>
							<xsl:when test="not(string(DeliveryChannel/Meaning)=&#39;&#39;)">
								<xsl:value-of select="DeliveryChannel/Meaning"/>
							</xsl:when>
							<xsl:otherwise>
								<xsl:if test="not(string(DocumentPayable[1]/DeliveryChannel/Meaning)=&#39;&#39;)">
									<xsl:value-of select="DocumentPayable[1]/DeliveryChannel/Meaning"/>
								</xsl:if>
							</xsl:otherwise>
						</xsl:choose>
					</xsl:variable>
					<xsl:variable name="SUALclInstrPrtry">
						<xsl:if test="(not($dlvrchnlcodeh =&#39;&#39;) and contains($dlvrchnlcodeh, &#39;-&#39;) and BankAccount/BankAddress/Country = &#39;US&#39;)">
							<xsl:value-of select="translate(substring-before($dlvrchnlcodeh,&#39;-&#39;),&#39;SUA&#39;,&#39;&#39;)"/>
						</xsl:if>
					</xsl:variable>
					<xsl:variable name="chqtp">
						<xsl:choose>
							<xsl:when test="$svlvl=&#39;CCHQ&#39;">CCHQ</xsl:when>
							<xsl:when test="$svlvl=&#39;DRFT&#39;">DRFT</xsl:when>
							<xsl:when test="$svlvl=&#39;BCHQ&#39;">BCHQ</xsl:when>
						</xsl:choose>
					</xsl:variable>
					<xsl:variable name="dbtrcntrysd">
						<xsl:if test="not(string(Payer/Address/County)=&#39;&#39;)">
							<xsl:value-of select="Payer/Address/County"/>
							<xsl:if test="not(string(Payer/Address/State)=&#39;&#39;) or not(string(Payer/Address/Province)=&#39;&#39;)">
								<xsl:value-of select="&#39; &#39;"/>
							</xsl:if>
						</xsl:if>
						<xsl:if test="not(string(Payer/Address/State)=&#39;&#39;)">
							<xsl:value-of select="Payer/Address/State"/>
							<xsl:if test="not(string(Payer/Address/Province)=&#39;&#39;)">
								<xsl:value-of select="&#39; &#39;"/>
							</xsl:if>
						</xsl:if>
						<xsl:if test="not(string(Payer/Address/Province)=&#39;&#39;)">
							<xsl:value-of select="Payer/Address/Province"/>
						</xsl:if>
					</xsl:variable>
					<xsl:variable name="SUAPoolId">
						<xsl:if test="(not($dlvrchnlcodeh =&#39;&#39;) and contains($dlvrchnlcodeh, &#39;-&#39;) and BankAccount/BankAddress/Country = &#39;US&#39;)">
							<xsl:value-of select="translate(substring-after($dlvrchnlcodeh,&#39;-&#39;),&#39;SUA&#39;,&#39;&#39;)"/>
						</xsl:if>
					</xsl:variable>
					<xsl:variable name="SUAAuthInd">
						<xsl:choose>
							<xsl:when test="(not($dlvrchnlcodemeaning =&#39;&#39;) and (translate($dlvrchnlcodemeaning,$lower,$upper) = &#39;SUA SINGLE&#39;) and BankAccount/BankAddress/Country = &#39;US&#39;)">
								<xsl:value-of select="&#39;YES&#39;"/>
							</xsl:when>
							<xsl:when test="(not($dlvrchnlcodemeaning =&#39;&#39;) and (translate($dlvrchnlcodemeaning,$lower,$upper) = &#39;SUA MULTIPLE&#39;) and BankAccount/BankAddress/Country = &#39;US&#39;)">
								<xsl:value-of select="&#39;NO&#39;"/>
							</xsl:when>
						</xsl:choose>
					</xsl:variable>
					<xsl:variable name="ultdbtrcntrysd">
						<xsl:if test="not(string(InvoicingLegalEntity/Address/County)=&#39;&#39;)">
							<xsl:value-of select="InvoicingLegalEntity/Address/County"/>
							<xsl:if test="not(string(InvoicingLegalEntity/Address/State)=&#39;&#39;) or not(string(InvoicingLegalEntity/Address/Province)=&#39;&#39;)">
								<xsl:value-of select="&#39; &#39;"/>
							</xsl:if>
						</xsl:if>
						<xsl:if test="not(string(InvoicingLegalEntity/Address/State)=&#39;&#39;)">
							<xsl:value-of select="InvoicingLegalEntity/Address/State"/>
							<xsl:if test="not(string(InvoicingLegalEntity/Address/Province)=&#39;&#39;)">
								<xsl:value-of select="&#39; &#39;"/>
							</xsl:if>
						</xsl:if>
						<xsl:if test="not(string(InvoicingLegalEntity/Address/Province)=&#39;&#39;)">
							<xsl:value-of select="InvoicingLegalEntity/Address/Province"/>
						</xsl:if>
					</xsl:variable>
					<!--Start of Payment Info-->
					<PmtInf>
						<xsl:if test="not(LogicalGrouping/LogicalGroupReference=&#39;&#39;)">
							<PmtInfId>
								<xsl:value-of select="LogicalGrouping/LogicalGroupReference"/>
							</PmtInfId>
						</xsl:if>
						<xsl:if test="not($pmthd=&#39;&#39;)">
							<PmtMtd>
								<xsl:value-of select="$pmthd"/>
							</PmtMtd>
						</xsl:if>
						<BtchBookg>
							<xsl:choose>
								<xsl:when test="contains(/OutboundPaymentInstruction/PaymentProcessProfile/BatchBookingFlag,&#39;N&#39;)">
									<xsl:text>false</xsl:text>
								</xsl:when>
								<xsl:otherwise>
									<xsl:text>true</xsl:text>
								</xsl:otherwise>
							</xsl:choose>
						</BtchBookg>
						<NbOfTxs>
							<xsl:value-of select="LogicalGrouping/PaymentInformationTotal"/>
						</NbOfTxs>
						<CtrlSum>
							<xsl:value-of select="format-number(LogicalGrouping/PaymentInformationAmountTotal, &#39;##0.00&#39;)"/>
						</CtrlSum>
						<xsl:if test=" starts-with($dlvrchnlcodeh,&#39;SUA&#39;) ">
							<PmtTpInf>
								<SvcLvl>
									<Cd>
										<xsl:value-of select="$svlvl"/>
									</Cd>
								</SvcLvl>
								<xsl:if test="not($SUALclInstrPrtry=&#39;&#39;)">
									<LclInstrm>
										<Prtry>
											<xsl:value-of select="$SUALclInstrPrtry"/>
										</Prtry>
									</LclInstrm>
								</xsl:if>
								<CtgyPurp>
									<Cd>CCRD</Cd>
								</CtgyPurp>
							</PmtTpInf>
						</xsl:if>
						<xsl:choose>
							<xsl:when test="(BankAccount/BankAddress/Country=&#39;HK&#39;
	or BankAccount/BankAddress/Country=&#39;IN&#39;
	or BankAccount/BankAddress/Country=&#39;ID&#39;
	or BankAccount/BankAddress/Country=&#39;JP&#39;
	or BankAccount/BankAddress/Country=&#39;KR&#39;
	or BankAccount/BankAddress/Country=&#39;NZ&#39;
	or BankAccount/BankAddress/Country=&#39;AU&#39;
	or BankAccount/BankAddress/Country=&#39;SG&#39;
	or BankAccount/BankAddress/Country=&#39;TH&#39;
	or BankAccount/BankAddress/Country=&#39;TW&#39;
	or BankAccount/BankAddress/Country=&#39;VN&#39;
	or BankAccount/BankAddress/Country=&#39;MY&#39;
	or BankAccount/BankAddress/Country=&#39;PH&#39;
	or BankAccount/BankAddress/Country=&#39;CN&#39;)">
								<xsl:choose>
									<xsl:when test="$pmthd=&#39;CHK&#39; and $chqtp=&#39;CCHQ&#39; and PaymentDate &gt; $dateNow ">
										<ReqdExctnDt>
											<xsl:value-of select="$dateNow"/>
										</ReqdExctnDt>
									</xsl:when>
									<xsl:otherwise>
										<ReqdExctnDt>
											<xsl:value-of select="PaymentDate"/>
										</ReqdExctnDt>
									</xsl:otherwise>
								</xsl:choose>
							</xsl:when>
							<xsl:otherwise>
								<ReqdExctnDt>
									<xsl:value-of select="PaymentDate"/>
								</ReqdExctnDt>
							</xsl:otherwise>
						</xsl:choose>
						<!--Start of Dbtr-->
						<Dbtr>
							<xsl:choose>
								<xsl:when test="not(count(/OutboundPaymentInstruction/PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[Name=&#39;DEBTOR_NAME&#39;])=0) and (/OutboundPaymentInstruction/PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[Name=&#39;DEBTOR_NAME&#39;]/Value  != &#39;&#39;) and not(translate(/OutboundPaymentInstruction/PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[Name=&#39;DEBTOR_NAME&#39;]/Value,$lower,$upper) = &#39;NA&#39;) ">
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
									<xsl:if test="not(string(Payer/Address/AddressLine1)=&#39;&#39;)">
										<StrtNm>
											<xsl:value-of select="substring(Payer/Address/AddressLine1,1,70)"/>
										</StrtNm>
									</xsl:if>
									<xsl:if test="not(string(Payer/Address/PostalCode)=&#39;&#39;)">
										<PstCd>
											<xsl:value-of select="Payer/Address/PostalCode"/>
										</PstCd>
									</xsl:if>
									<xsl:if test="not(string(Payer/Address/City)=&#39;&#39;)">
										<TwnNm>
											<xsl:value-of select="Payer/Address/City"/>
										</TwnNm>
									</xsl:if>
									<xsl:if test="not(string(Payer/Address/County)=&#39;&#39;) or not(string(Payer/Address/State)=&#39;&#39;) or not(string(Payer/Address/Province)=&#39;&#39;)">
										<CtrySubDvsn>
											<xsl:value-of select="substring($dbtrcntrysd,1,35)"/>
										</CtrySubDvsn>
									</xsl:if>
									<xsl:if test="not(Payer/Address/Country=&#39;&#39;)">
										<Ctry>
											<xsl:value-of select="Payer/Address/Country"/>
										</Ctry>
									</xsl:if>
								</PstlAdr>
							</xsl:if>
							<!-- Changes as per the Company-Id uptake -->
							<xsl:if test="($svlvl='NURG') and not(string(BankAccount/EFTUserNumber/EFTRequesterId)=&#39;&#39;) and $pmthd2='TRF' ">
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
						<!--End of Dbtr-->
						<!--Start of DbtrAcct-->
						<DbtrAcct>
							<xsl:if test="not(starts-with($dlvrchnlcodeh,&#39;SUA&#39;))">
								<Id>
									<xsl:if test="not(BankAccount/IBANNumber=&#39;&#39;)">
										<IBAN>
											<xsl:value-of select="BankAccount/IBANNumber"/>
										</IBAN>
									</xsl:if>
									<xsl:if test="not(BankAccount/BankAccountNumber=&#39;&#39;) and BankAccount/IBANNumber=&#39;&#39;">
										<Othr>
											<Id>
												<xsl:value-of select="BankAccount/BankAccountNumber"/>
											</Id>
										</Othr>
									</xsl:if>
								</Id>
							</xsl:if>
							<xsl:if test="(starts-with($dlvrchnlcodeh,&#39;SUA&#39;)) and not($SUAPoolId=&#39;&#39;)">
								<Id>
									<Othr>
										<Id>
											<xsl:value-of select="$SUAPoolId"/>
										</Id>
									</Othr>
								</Id>
							</xsl:if>
							<xsl:if test="(starts-with($dlvrchnlcodeh,&#39;SUA&#39;)) and not($SUAAuthInd=&#39;&#39;)">
								<Tp>
									<Prtry>
										<xsl:value-of select="$SUAAuthInd"/>
									</Prtry>
								</Tp>
							</xsl:if>
							<xsl:if test="not(string(BankAccount/BankAccountCurrency/Code)=&#39;&#39;) ">
								<Ccy>
									<xsl:value-of select="BankAccount/BankAccountCurrency/Code"/>
								</Ccy>
							</xsl:if>
						</DbtrAcct>
						<!--End of DbtrAcct-->
						<!--Start of DbtrAgt-->
						<xsl:if test="not(string(BankAccount/SwiftCode)=&#39;&#39;) or not(string(BankAccount/BranchNumber)=&#39;&#39;)">
							<DbtrAgt>
								<FinInstnId>
									<xsl:if test="not(BankAccount/SwiftCode=&#39;&#39;)">
										<BIC>
											<xsl:value-of select="BankAccount/SwiftCode"/>
										</BIC>
									</xsl:if>
									<xsl:if test="(BankAccount/SwiftCode='')">
										<xsl:if test="not(BankAccount/BranchNumber='')">
											<ClrSysMmbId>
												<MmbId>
													<xsl:value-of select="BankAccount/BranchNumber"/>
												</MmbId>
											</ClrSysMmbId>
										</xsl:if>
									</xsl:if>
									<xsl:if test="$dlvrchnlcodeh=&#39;IAT&#39; and $svlvl=&#39;NURG&#39;">
										<Nm>
											<xsl:value-of select="BankAccount/BranchName"/>
										</Nm>
									</xsl:if>
									<xsl:if test="not(BankAccount/BankAddress/Country=&#39;&#39;)">
										<PstlAdr>
											<Ctry>
												<xsl:value-of select="BankAccount/BankAddress/Country"/>
											</Ctry>
										</PstlAdr>
									</xsl:if>
								</FinInstnId>
							</DbtrAgt>
						</xsl:if>
						<!--End of DbtrAgt-->
						<!--Start of UltmtDbtr-->
						<xsl:if test="not(/OutboundPaymentInstruction/PaymentProcessProfile/LogicalGrouping/GroupByUltimateDebtor=&#39;N&#39;)
	and not(string(InvoicingLegalEntity/Address/Country)=&#39;&#39;) and not(InvoicingLegalEntity/LegalEntityId=&#39;&#39;) and (InvoicingLegalEntity/LegalEntityId != Payer/LegalEntityInternalID)">
							<UltmtDbtr>
								<Nm>
									<xsl:value-of select="InvoicingLegalEntity/Name"/>
								</Nm>
								<PstlAdr>
									<xsl:if test="not(string(InvoicingLegalEntity/Address/AddressLine2)=&#39;&#39;)">
										<StrtNm>
											<xsl:value-of select="substring(InvoicingLegalEntity/Address/AddressLine2,1,70)"/>
										</StrtNm>
									</xsl:if>
									<xsl:if test="not(string(InvoicingLegalEntity/Address/AddressLine1)=&#39;&#39;)">
										<BldgNb>
											<xsl:value-of select="substring(InvoicingLegalEntity/Address/AddressLine1,1,16)"/>
										</BldgNb>
									</xsl:if>
									<xsl:if test="not(string(InvoicingLegalEntity/Address/PostalCode)=&#39;&#39;)">
										<PstCd>
											<xsl:value-of select="InvoicingLegalEntity/Address/PostalCode"/>
										</PstCd>
									</xsl:if>
									<xsl:if test="not(string(InvoicingLegalEntity/Address/City)=&#39;&#39;)">
										<TwnNm>
											<xsl:value-of select="InvoicingLegalEntity/Address/City"/>
										</TwnNm>
									</xsl:if>
									<xsl:if test="not(string(InvoicingLegalEntity/Address/County)=&#39;&#39;) or not(string(InvoicingLegalEntity/Address/State)=&#39;&#39;) or not(string(InvoicingLegalEntity/Address/Province)=&#39;&#39;)">
										<CtrySubDvsn>
											<xsl:value-of select="substring($ultdbtrcntrysd,1,35)"/>
										</CtrySubDvsn>
									</xsl:if>
									<Ctry>
										<xsl:value-of select="InvoicingLegalEntity/Address/Country"/>
									</Ctry>
									<xsl:if test="not(string(InvoicingLegalEntity/Address/AddressLine1)=&#39;&#39;)">
										<AdrLine>
											<xsl:value-of select="InvoicingLegalEntity/Address/AddressLine1"/>
										</AdrLine>
									</xsl:if>
								</PstlAdr>
								<xsl:if test="not(string(InvoicingLegalEntity/LegalEntityRegistrationNumber)=&#39;&#39;)">
									<Id>
										<OrgId>
											<Othr>
												<Id>
													<xsl:value-of select="InvoicingLegalEntity/LegalEntityRegistrationNumber"/>
												</Id>
											</Othr>
										</OrgId>
									</Id>
								</xsl:if>
							</UltmtDbtr>
						</xsl:if>
						<!--End of UltmtDbtr-->
						<xsl:for-each select="key(&#39;contacts-by-LogicalGroupReference&#39;, LogicalGrouping/LogicalGroupReference)">
							<xsl:choose>
								<xsl:when test="PaymentMethod/PaymentMethodFormatValue=$pmthd2">
									<xsl:variable name="pmthd1">
										<xsl:choose>
											<xsl:when test="$pmthd2=&#39;TRF&#39;">TRF</xsl:when>
											<xsl:when test="$pmthd2=&#39;CHK&#39;">CHK</xsl:when>
										</xsl:choose>
									</xsl:variable>
									<xsl:variable name="year" select="substring(PaymentDate,3,2)"/>
									<xsl:variable name="svlvl1">
										<xsl:choose>
											<xsl:when test="not(string(ServiceLevel/FormatValue)=&#39;&#39;) ">
												<xsl:value-of select="ServiceLevel/FormatValue"/>
											</xsl:when>
											<xsl:otherwise>
												<xsl:choose>
													<xsl:when test="not(string(ServiceLevel/Code)=&#39;&#39;) ">
														<xsl:value-of select="ServiceLevel/Code"/>
													</xsl:when>
													<xsl:otherwise>
														<xsl:if test="$pmthd2=&#39;TRF&#39; and PayeeBankAccount/SwiftCode=BankAccount/SwiftCode ">BKTR
	</xsl:if>
													</xsl:otherwise>
												</xsl:choose>
											</xsl:otherwise>
										</xsl:choose>
									</xsl:variable>
									<xsl:variable name="chqtp1">
										<xsl:choose>
											<xsl:when test="$svlvl1=&#39;CCHQ&#39;">CCHQ</xsl:when>
											<xsl:when test="$svlvl1=&#39;DRFT&#39;">DRFT</xsl:when>
											<xsl:when test="$svlvl1=&#39;BCHQ&#39;">BCHQ</xsl:when>
										</xsl:choose>
									</xsl:variable>
									<xsl:variable name="USExchDff" select="&#39;&#39;"/>
									<xsl:variable name="bnkinstr2">
										<xsl:choose>
											<xsl:when test="not(string(BankInstruction[2]/Meaning)=&#39;&#39;)">
												<xsl:value-of select="BankInstruction[2]/Meaning"/>
											</xsl:when>
											<xsl:otherwise>
												<xsl:if test="not(string(/OutboundPaymentInstruction/PaymentInstructionInfo/BankInstruction[2]/Meaning)=&#39;&#39;)">
													<xsl:value-of select="/OutboundPaymentInstruction/PaymentInstructionInfo/BankInstruction[2]/Meaning"/>
												</xsl:if>
											</xsl:otherwise>
										</xsl:choose>
									</xsl:variable>
									<xsl:variable name="bnkinstr1">
										<xsl:choose>
											<xsl:when test="not(string(BankInstruction[1]/Meaning)=&#39;&#39;)">
												<xsl:value-of select="BankInstruction[1]/Meaning"/>
											</xsl:when>
											<xsl:otherwise>
												<xsl:if test="not(string(/OutboundPaymentInstruction/PaymentInstructionInfo/BankInstruction[1]/Meaning)=&#39;&#39;)">
													<xsl:value-of select="/OutboundPaymentInstruction/PaymentInstructionInfo/BankInstruction[1]/Meaning"/>
												</xsl:if>
											</xsl:otherwise>
										</xsl:choose>
									</xsl:variable>
									<xsl:variable name="Strdnull" select="&#39;&#39;"/>
									<xsl:variable name="bnkinstr3">
										<xsl:choose>
											<xsl:when test="$svlvl=&#39;URGP&#39; and not(BankAccount/BankAddress/Country=PayeeBankAccount/BankAddress/Country) and not(Payee/ContactInfo/ContactLocators[1]/PhoneNumber=&#39;&#39;)">
												<xsl:value-of select="concat(&#39;/ACC/BENETEL&#39; ,&#39; &#39;)"/>
												<xsl:value-of select="normalize-space(translate(Payee/ContactInfo/ContactLocators[1]/PhoneNumber,&#39;)(+Telephone&#39;,&#39; &#39;))"/>
											</xsl:when>
											<xsl:otherwise>
												<xsl:value-of select="$Strdnull"/>
											</xsl:otherwise>
										</xsl:choose>
									</xsl:variable>
									<xsl:variable name="BoletoBR">
										<xsl:choose>
											<xsl:when test="not(DocumentPayable/BrazilExtend/JLBR_BAR_CODE=&#39;&#39;)">
												<xsl:value-of select="DocumentPayable/BrazilExtend/JLBR_BAR_CODE"/>
											</xsl:when>
											<xsl:otherwise>
												<xsl:value-of select="&#39;&#39;"/>
											</xsl:otherwise>
										</xsl:choose>
									</xsl:variable>
									<xsl:variable name="DKGIKFIKREF" select="&#39;&#39;"/>
									<xsl:variable name="dlvrchnlcode">
										<xsl:choose>
											<xsl:when test="not(string(DeliveryChannel/FormatValue)=&#39;&#39;)">
												<xsl:value-of select="DeliveryChannel/FormatValue"/>
											</xsl:when>
											<xsl:otherwise>
												<xsl:choose>
													<xsl:when test="not(string(DocumentPayable[1]/DeliveryChannel/FormatValue)=&#39;&#39;)">
														<xsl:value-of select="DocumentPayable[1]/DeliveryChannel/FormatValue"/>
													</xsl:when>
													<xsl:otherwise>
														<xsl:if test="not(string(DeliveryChannel/Code)=&#39;&#39;)">
															<xsl:value-of select="DeliveryChannel/Code"/>
														</xsl:if>
													</xsl:otherwise>
												</xsl:choose>
											</xsl:otherwise>
										</xsl:choose>
									</xsl:variable>
									<xsl:variable name="DKGIKFIKREF1">
										<xsl:choose>
											<xsl:when test="($dlvrchnlcode=&#39;01&#39; or $dlvrchnlcode=&#39;73&#39; )">
												<xsl:value-of select="concat($dlvrchnlcode,&#39;/&#39;)"/>
											</xsl:when>
											<xsl:otherwise>
												<xsl:value-of select="concat($dlvrchnlcode,&#39;/&#39;,$DKGIKFIKREF)"/>
											</xsl:otherwise>
										</xsl:choose>
									</xsl:variable>
									<xsl:variable name="PrtLctnDff" select="&#39;&#39;"/>
									<xsl:variable name="RgnlClrnZnDff" select="&#39;&#39;"/>
									<xsl:variable name="CdtrIdDff" select="&#39;&#39;"/>
									<xsl:variable name="CtryOfResDff" select="&#39;&#39;"/>
									<xsl:variable name="AUBCHQPAYABLE" select="&#39;&#39;"/>
									<xsl:variable name="AUCCHQPAYABLE" select="&#39;&#39;"/>
									<xsl:variable name="AUDRFTPAYABLE" select="&#39;&#39;"/>
									<xsl:variable name="HKBCHQPAYABLE" select="&#39;&#39;"/>
									<xsl:variable name="HKCCHQPAYABLE" select="&#39;&#39;"/>
									<xsl:variable name="HKDRFTPAYABLE" select="&#39;&#39;"/>
									<xsl:variable name="INDRFTPAYABLE" select="&#39;&#39;"/>
									<xsl:variable name="IDBCHQPAYABLE" select="&#39;&#39;"/>
									<xsl:variable name="IDCCHQPAYABLE" select="&#39;&#39;"/>
									<xsl:variable name="IDDRFTPAYABLE" select="&#39;&#39;"/>
									<xsl:variable name="MYBCHQPAYABLE" select="&#39;&#39;"/>
									<xsl:variable name="MYCCHQPAYABLE" select="&#39;&#39;"/>
									<xsl:variable name="MYDRFTPAYABLE" select="&#39;&#39;"/>
									<xsl:variable name="NZBCHQPAYABLE" select="&#39;&#39;"/>
									<xsl:variable name="NZDRFTPAYABLE" select="&#39;&#39;"/>
									<xsl:variable name="PHBCHQPAYABLE" select="&#39;&#39;"/>
									<xsl:variable name="PHCCHQPAYABLE" select="&#39;&#39;"/>
									<xsl:variable name="PHDRFTPAYABLE" select="&#39;&#39;"/>
									<xsl:variable name="SGBCHQPAYABLE" select="&#39;&#39;"/>
									<xsl:variable name="SGCCHQPAYABLE" select="&#39;&#39;"/>
									<xsl:variable name="SGDRFTPAYABLE" select="&#39;&#39;"/>
									<xsl:variable name="TWBCHQPAYABLE" select="&#39;&#39;"/>
									<xsl:variable name="TWCCHQPAYABLE" select="&#39;&#39;"/>
									<xsl:variable name="TWDRFTPAYABLE" select="&#39;&#39;"/>
									<xsl:variable name="THBCHQPAYABLE" select="&#39;&#39;"/>
									<xsl:variable name="THCCHQPAYABLE" select="&#39;&#39;"/>
									<xsl:variable name="THDRFTPAYABLE" select="&#39;&#39;"/>
									<xsl:variable name="dlvrchnlcodeUnStrd">
										<xsl:choose>
											<xsl:when test="not(string(DeliveryChannel/Code)=&#39;&#39;)">
												<xsl:value-of select="DeliveryChannel/Code"/>
											</xsl:when>
										</xsl:choose>
									</xsl:variable>
									<xsl:variable name="Actualsuplrnmdff" select="&#39;&#39;"/>
									<xsl:variable name="WHTTaxAmount">
										<xsl:value-of select="translate(format-number(sum(DocumentPayable/DocumentPayableLine[LineType/Code =&#39;AWT&#39;]/LineGrossAmount/Value), &#39;##0.00&#39;),&#39;-&#39;,&#39;&#39;)"/>
									</xsl:variable>
									<xsl:variable name="Taxblamtdff">
										<xsl:choose>
											<xsl:when test="not($WHTTaxAmount)=&#39;&#39; and not(string($WHTTaxAmount)=&#39;0.00&#39;)">
												<xsl:value-of select="$WHTTaxAmount"/>
											</xsl:when>
											<xsl:otherwise>
												<xsl:value-of select="&#39;&#39;"/>
											</xsl:otherwise>
										</xsl:choose>
									</xsl:variable>
									<xsl:variable name="printloc">
										<xsl:choose>
											<xsl:when test="Payer/Address/Country=&#39;IN&#39; and not($PrtLctnDff=&#39;&#39;)">
												<xsl:value-of select="$PrtLctnDff"/>
											</xsl:when>
											<xsl:when test="Payer/Address/Country=&#39;IN&#39; and $PrtLctnDff=&#39;&#39;">MUMBAI</xsl:when>
										</xsl:choose>
									</xsl:variable>
									<xsl:variable name="pmtrsncode">
										<xsl:choose>
											<xsl:when test="not(string(PaymentReason/FormatValue)=&#39;&#39;)">
												<xsl:value-of select="PaymentReason/FormatValue"/>
											</xsl:when>
											<xsl:otherwise>
												<xsl:choose>
													<xsl:when test="not(string(DocumentPayable[1]/PaymentReason/FormatValue)=&#39;&#39;)">
														<xsl:value-of select="DocumentPayable[1]/PaymentReason/FormatValue"/>
													</xsl:when>
													<xsl:otherwise>
														<xsl:choose>
															<xsl:when test="not(string(PaymentReason/Code)=&#39;&#39;)">
																<xsl:value-of select="PaymentReason/Code"/>
															</xsl:when>
															<xsl:otherwise>
																<xsl:if test="not(string(DocumentPayable[1]/PaymentReason/Code)=&#39;&#39;)">
																	<xsl:value-of select="DocumentPayable[1]/PaymentReason/Code"/>
																</xsl:if>
															</xsl:otherwise>
														</xsl:choose>
													</xsl:otherwise>
												</xsl:choose>
											</xsl:otherwise>
										</xsl:choose>
									</xsl:variable>
									<xsl:variable name="DeliveryMtd">
										<xsl:choose>
											<xsl:when test="not(string(DeliveryChannel/FormatValue)=&#39;&#39;)">
												<xsl:value-of select="DeliveryChannel/FormatValue"/>
											</xsl:when>
											<xsl:otherwise>
												<xsl:value-of select="&#39;00000&#39;"/>
											</xsl:otherwise>
										</xsl:choose>
									</xsl:variable>
									<xsl:variable name="pmtrsndesc">
										<xsl:choose>
											<xsl:when test="not(string(PaymentReason/Meaning)=&#39;&#39;)">
												<xsl:value-of select="PaymentReason/Meaning"/>
											</xsl:when>
											<xsl:otherwise>
												<xsl:if test="not(string(DocumentPayable[1]/PaymentReason/Meaning)=&#39;&#39;)">
													<xsl:value-of select="DocumentPayable[1]/PaymentReason/Meaning"/>
												</xsl:if>
											</xsl:otherwise>
										</xsl:choose>
									</xsl:variable>
									<xsl:variable name="FormsCd">
										<xsl:choose>
											<xsl:when test="not(string(DeliveryChannel/Code)='')">
												<xsl:choose>
													<xsl:when test="contains(DeliveryChannel/Code, '-')">
														<xsl:value-of select="substring-before(DeliveryChannel/Code,'-')"/>
													</xsl:when>
													<xsl:otherwise>
														<xsl:value-of select="DeliveryChannel/Code"/>
													</xsl:otherwise>
												</xsl:choose>
											</xsl:when>
										</xsl:choose>
									</xsl:variable>
									<xsl:variable name="chrgbrcode">
										<xsl:choose>
											<xsl:when test="not(string(DocumentPayable/BankCharges/BankChargeBearer/Code[1])=&#39;&#39;)">
												<xsl:value-of select="DocumentPayable/BankCharges/BankChargeBearer/Code[1]"/>
											</xsl:when>
											<xsl:otherwise>
												<xsl:if test="not(string(BankCharges/BankChargeBearer/Code)=&#39;&#39;)">
													<xsl:value-of select="BankCharges/BankChargeBearer/Code"/>
												</xsl:if>
											</xsl:otherwise>
										</xsl:choose>
									</xsl:variable>
									<xsl:variable name="cdtrcntrysd">
										<xsl:if test="not(string(Payee/Address/County)=&#39;&#39;)">
											<xsl:value-of select="Payee/Address/County"/>
											<xsl:if test="not(string(Payee/Address/State)=&#39;&#39;) or not(string(Payee/Address/Province)=&#39;&#39;)">
												<xsl:value-of select="&#39; &#39;"/>
											</xsl:if>
										</xsl:if>
										<xsl:if test="not(string(Payee/Address/State)=&#39;&#39;)">
											<xsl:value-of select="Payee/Address/State"/>
											<xsl:if test="not(string(Payee/Address/Province)=&#39;&#39;)">
												<xsl:value-of select="&#39; &#39;"/>
											</xsl:if>
										</xsl:if>
										<xsl:if test="not(string(Payee/Address/Province)=&#39;&#39;)">
											<xsl:value-of select="Payee/Address/Province"/>
										</xsl:if>
									</xsl:variable>
									<xsl:variable name="cdtragntcntrysd">
										<xsl:if test="not(string(PayeeBankAccount/BankAddress/County)=&#39;&#39;)">
											<xsl:value-of select="PayeeBankAccount/BankAddress/County"/>
											<xsl:if test="not(string(PayeeBankAccount/BankAddress/State)=&#39;&#39;) or not(string(PayeeBankAccount/BankAddress/Province)=&#39;&#39;) ">
												<xsl:value-of select="&#39; &#39;"/>
											</xsl:if>
										</xsl:if>
										<xsl:if test="not(string(PayeeBankAccount/BankAddress/State)=&#39;&#39;)">
											<xsl:value-of select="PayeeBankAccount/BankAddress/State"/>
											<xsl:if test="not(string(PayeeBankAccount/BankAddress/Province)=&#39;&#39;) ">
												<xsl:value-of select="&#39; &#39;"/>
											</xsl:if>
										</xsl:if>
										<xsl:if test="not(string(PayeeBankAccount/BankAddress/Province)=&#39;&#39;)">
											<xsl:value-of select="PayeeBankAccount/BankAddress/Province"/>
										</xsl:if>
									</xsl:variable>
									<xsl:variable name="DocDescrptn" select="DocumentPayable/DocumentDescription[1]"/>
									<xsl:variable name="AutoDealerVT" select="&#39;AutoDealerVT&#39;"/>
									<xsl:variable name="AutoDealerIV" select="&#39;AutoDealerIV&#39;"/>
									<xsl:variable name="AutoDealerIT" select="&#39;AutoDealerIT&#39;"/>
									<xsl:variable name="MmbIdG">
										<xsl:if test="$pmthd2=&#39;TRF&#39;">
											<xsl:choose>
												<xsl:when test="$svlvl1 = &#39;NURG&#39;">
													<xsl:choose>
														<xsl:when test="contains($NURGBankCdToMMBID, string(PayeeBankAccount/BankAddress/Country)) and not(PayeeBankAccount/BankNumber = &#39;&#39;) ">
															<xsl:value-of select="(PayeeBankAccount/BankNumber)"/>
														</xsl:when>
														<xsl:when test="contains($NURGBankCdBranchNuToMMBID, string(PayeeBankAccount/BankAddress/Country)) and not(PayeeBankAccount/BranchNumber = &#39;&#39;)">
															<xsl:value-of select="concat(PayeeBankAccount/BankNumber,PayeeBankAccount/BranchNumber)"/>
														</xsl:when>
														<xsl:otherwise>
															<xsl:if test="not(PayeeBankAccount/BranchNumber = &#39;&#39;)">
																<xsl:value-of select="(PayeeBankAccount/BranchNumber)"/>
															</xsl:if>
														</xsl:otherwise>
													</xsl:choose>
												</xsl:when>
												<xsl:when test="$svlvl1 = &#39;URGP&#39; and (BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country)">
													<xsl:choose>
														<xsl:when test="contains($URGPDOMBankCdToMMBID, string(PayeeBankAccount/BankAddress/Country)) and not(PayeeBankAccount/BankNumber = &#39;&#39;) ">
															<xsl:value-of select="(PayeeBankAccount/BankNumber)"/>
														</xsl:when>
														<xsl:when test="contains($URGPDOMBankCdBranchNuToMMBID, string(PayeeBankAccount/BankAddress/Country)) and not(PayeeBankAccount/BranchNumber = &#39;&#39;)">
															<xsl:value-of select="concat(PayeeBankAccount/BankNumber,PayeeBankAccount/BranchNumber)"/>
														</xsl:when>
														<xsl:otherwise>
															<xsl:if test="not(PayeeBankAccount/BranchNumber = &#39;&#39;)">
																<xsl:value-of select="(PayeeBankAccount/BranchNumber)"/>
															</xsl:if>
														</xsl:otherwise>
													</xsl:choose>
												</xsl:when>
												<xsl:when test="$svlvl1 = &#39;URGP&#39; and not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country)">
													<xsl:choose>
														<xsl:when test="contains($URGPXBordBankCdToMMBID, string(PayeeBankAccount/BankAddress/Country)) and not(PayeeBankAccount/BankNumber = &#39;&#39;) ">
															<xsl:value-of select="(PayeeBankAccount/BankNumber)"/>
														</xsl:when>
														<xsl:when test="contains($URGPXBordBankCdBranchNuToMMBID, string(PayeeBankAccount/BankAddress/Country)) and not(PayeeBankAccount/BranchNumber = &#39;&#39;)">
															<xsl:value-of select="concat(PayeeBankAccount/BankNumber,PayeeBankAccount/BranchNumber)"/>
														</xsl:when>
														<xsl:when test="not(PayeeBankAccount/BankNumber = &#39;&#39;) and (PayeeBankAccount/BankNumber = PayeeBankAccount/BranchNumber)">
															<xsl:value-of select="(PayeeBankAccount/BankNumber)"/>
														</xsl:when>
														<xsl:when test="(PayeeBankAccount/BankNumber != PayeeBankAccount/BranchNumber) and not(PayeeBankAccount/BranchNumber = &#39;&#39;)">
															<xsl:value-of select="concat(PayeeBankAccount/BankNumber,PayeeBankAccount/BranchNumber)"/>
														</xsl:when>
														<xsl:otherwise>
															<xsl:if test="not(PayeeBankAccount/BranchNumber = &#39;&#39;)">
																<xsl:value-of select="(PayeeBankAccount/BranchNumber)"/>
															</xsl:if>
														</xsl:otherwise>
													</xsl:choose>
												</xsl:when>
												<xsl:when test="$svlvl1 = &#39;BKTR&#39;">
													<xsl:choose>
														<xsl:when test="contains($BKTRBankCdToMMBID, string(PayeeBankAccount/BankAddress/Country)) and not(PayeeBankAccount/BankNumber = &#39;&#39;) ">
															<xsl:value-of select="(PayeeBankAccount/BankNumber)"/>
														</xsl:when>
														<xsl:when test="contains($BKTRBranchNuToMMBID, string(PayeeBankAccount/BankAddress/Country)) and not(PayeeBankAccount/BranchNumber = &#39;&#39;)">
															<xsl:value-of select="(PayeeBankAccount/BranchNumber)"/>
														</xsl:when>
														<xsl:when test="contains($BKTRBankCdBranchNuToMMBID, string(PayeeBankAccount/BankAddress/Country)) and not(PayeeBankAccount/BranchNumber = &#39;&#39;)">
															<xsl:value-of select="concat(PayeeBankAccount/BankNumber,PayeeBankAccount/BranchNumber)"/>
														</xsl:when>
														<xsl:otherwise>
															<xsl:if test="not(PayeeBankAccount/BranchNumber = &#39;&#39;)">
																<xsl:value-of select="(PayeeBankAccount/BranchNumber)"/>
															</xsl:if>
														</xsl:otherwise>
													</xsl:choose>
												</xsl:when>
												<xsl:when test="$svlvl1 = &#39;URNS&#39;">
													<xsl:choose>
														<xsl:when test="contains($URNSBankCdToMMBID, string(PayeeBankAccount/BankAddress/Country)) and not(PayeeBankAccount/BankNumber = &#39;&#39;) ">
															<xsl:value-of select="(PayeeBankAccount/BankNumber)"/>
														</xsl:when>
														<xsl:when test="contains($URNSBankCdBranchNuToMMBID, string(PayeeBankAccount/BankAddress/Country)) and not(PayeeBankAccount/BranchNumber = &#39;&#39;)">
															<xsl:value-of select="concat(PayeeBankAccount/BankNumber,PayeeBankAccount/BranchNumber)"/>
														</xsl:when>
														<xsl:otherwise>
															<xsl:if test="not(PayeeBankAccount/BranchNumber = &#39;&#39;)">
																<xsl:value-of select="(PayeeBankAccount/BranchNumber)"/>
															</xsl:if>
														</xsl:otherwise>
													</xsl:choose>
												</xsl:when>
												<xsl:otherwise>
													<xsl:value-of select="&#39;&#39;"/>
												</xsl:otherwise>
											</xsl:choose>
										</xsl:if>
									</xsl:variable>
									<xsl:variable name="BridG">
										<xsl:if test="$pmthd2=&#39;TRF&#39;">
											<xsl:choose>
												<xsl:when test="$svlvl1 = &#39;NURG&#39; and contains($NURGBranchNuToBranchId, string(PayeeBankAccount/BankAddress/Country)) and not(PayeeBankAccount/BranchNumber = &#39;&#39;)">
													<xsl:value-of select="(PayeeBankAccount/BranchNumber)"/>
												</xsl:when>
												<xsl:when test="$svlvl1 = &#39;URGP&#39; and contains($URGPDOMBranchNuToBranchId, string(PayeeBankAccount/BankAddress/Country)) and BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country and not(PayeeBankAccount/BranchNumber = &#39;&#39;)">
													<xsl:value-of select="(PayeeBankAccount/BranchNumber)"/>
												</xsl:when>
												<xsl:when test="$svlvl1 = &#39;URGP&#39; and contains($URGPXBordBranchNuToBranchId, string(PayeeBankAccount/BankAddress/Country)) and (BankAccount/BankAddress/Country != PayeeBankAccount/BankAddress/Country) and not(PayeeBankAccount/BranchNumber = &#39;&#39;)">
													<xsl:value-of select="(PayeeBankAccount/BranchNumber)"/>
												</xsl:when>
												<xsl:when test="$svlvl1 = &#39;BKTR&#39; and contains($BKTRBranchNuToBranchId, string(PayeeBankAccount/BankAddress/Country)) and not(PayeeBankAccount/BranchNumber = &#39;&#39;)">
													<xsl:value-of select="(PayeeBankAccount/BranchNumber)"/>
												</xsl:when>
												<xsl:otherwise>
													<xsl:value-of select="&#39;&#39;"/>
												</xsl:otherwise>
											</xsl:choose>
										</xsl:if>
									</xsl:variable>
									<CdtTrfTxInf>
										<xsl:variable name="paymentdetails" select="PaymentDetails"/>
										<PmtId>
											<xsl:if test="not(string(PaymentNumber/CheckNumber)=&#39;&#39;) ">
												<InstrId>
													<xsl:value-of select="PaymentNumber/CheckNumber"/>
												</InstrId>
											</xsl:if>
											<xsl:choose>
												<xsl:when test="$endtoend=&#39;N&#39;">
													<EndToEndId>
														<xsl:value-of select="PaymentNumber/PaymentReferenceNumber"/>
													</EndToEndId>
												</xsl:when>
												<xsl:when test="not($endtoend=&#39;N&#39;) and not($leintid=&#39;&#39;)">
													<EndToEndId>
														<xsl:value-of select="PaymentNumber/PaymentReferenceNumber"/>
														<xsl:value-of select="$leintid"/>
														<xsl:value-of select="$year"/>
													</EndToEndId>
												</xsl:when>
											</xsl:choose>
										</PmtId>
										<xsl:if test="$pmthd1=&#39;TRF&#39; and not(starts-with($dlvrchnlcodeh,&#39;SUA&#39;))">
											<PmtTpInf>
												<xsl:if test="not($svlvl1=&#39;&#39;)">
													<SvcLvl>
														<Cd>
															<xsl:value-of select="$svlvl1"/>
														</Cd>
													</SvcLvl>
												</xsl:if>
												<xsl:if test="((BankAccount/BankAddress/Country=&#39;ZA&#39; and $svlvl1=&#39;NURG&#39;) or (BankAccount/BankAddress/Country=&#39;US&#39; and (not(translate ($dlvrchnlcode,$lower,$upper)=&#39;CQP&#39;)) and $svlvl1=&#39;NURG&#39;) or (BankAccount/BankAddress/Country=&#39;IN&#39; and translate($dlvrchnlcode,$lower,$upper)=&#39;ECS&#39; and $svlvl1=&#39;NURG&#39;) or (BankAccount/BankAddress/Country=&#39;KR&#39; and $svlvl1=&#39;URGP&#39; and PayeeBankAccount/BankAddress/Country=&#39;KR&#39; and PaymentAmount/Currency/Code=&#39;KRW&#39; )) and not($dlvrchnlcode=&#39;&#39;)">
													<LclInstrm>
														<Cd>
															<xsl:value-of select="$dlvrchnlcode"/>
														</Cd>
													</LclInstrm>
												</xsl:if>
												<xsl:if test="((BankAccount/BankAddress/Country=&#39;MY&#39; and translate($dlvrchnlcode,$lower,$upper)=&#39;NBPS&#39; and $pmthd1=&#39;TRF&#39;) or (BankAccount/BankAddress/Country=&#39;BR&#39; and $svlvl1=&#39;NURG&#39;) or (BankAccount/BankAddress/Country=&#39;CH&#39;) or(BankAccount/BankAddress/Country=&#39;US&#39; and translate ($dlvrchnlcode,$lower,$upper)=&#39;CQP&#39; and $svlvl1=&#39;NURG&#39;)) and not($dlvrchnlcode=&#39;&#39;)">
													<LclInstrm>
														<Prtry>
															<xsl:value-of select="$dlvrchnlcode"/>
														</Prtry>
													</LclInstrm>
												</xsl:if>
												<xsl:if test="BankAccount/BankAddress/Country=&#39;IN&#39; and $pmthd1=&#39;TRF&#39; and $svlvl1=&#39;URGP&#39;  and PaymentAmount/Currency/Code=&#39;INR&#39; and  PayeeBankAccount/BankAddress/Country=&#39;IN&#39; and  not($pmtrsncode=&#39;&#39;)">
													<CtgyPurp>
														<Cd>
															<xsl:value-of select="$pmtrsncode"/>
														</Cd>
													</CtgyPurp>
												</xsl:if>
												<xsl:if test="Payer/Address/Country=&#39;CZ&#39; and $pmthd1=&#39;TRF&#39; and $svlvl1=&#39;URGP&#39;">
													<CtgyPurp>
														<Cd>SDVA</Cd>
													</CtgyPurp>
												</xsl:if>
												<xsl:if test="translate ($pmtrsncode,$lower,$upper)=&#39;AUTO DEALER TRANSACTION&#39;">
													<CtgyPurp>
														<Prtry>Auto Dealer Transaction</Prtry>
													</CtgyPurp>
												</xsl:if>
												<xsl:if test="Payer/Address/Country=&#39;PL&#39; and $pmtrsncode=&#39;TAXS&#39; ">
													<CtgyPurp>
														<Cd>TAXS</Cd>
													</CtgyPurp>
												</xsl:if>
											</PmtTpInf>
										</xsl:if>
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
										<xsl:if test="BankAccount/BankAddress/Country=&#39;US&#39; and ($svlvl1=&#39;URGP&#39; or $chqtp1=&#39;DRFT&#39;) and not($USExchDff=&#39;&#39;) and $USExchDff">
											<XchgRateInf>
												<RateTp>AGRD</RateTp>
											</XchgRateInf>
										</xsl:if>
										<xsl:if test="not($pmthd1=&#39;CHK&#39;)">
											<xsl:if test="not($chrgbrcode=&#39;&#39;)">
												<ChrgBr>
													<xsl:choose>
														<xsl:when test="($chrgbrcode=&#39;BEN&#39;) or ($chrgbrcode=&#39;PAYEE_PAYS_EXPRESS&#39;)">
															<xsl:text>CRED</xsl:text>
														</xsl:when>
														<xsl:when test="($chrgbrcode=&#39;OUR&#39;)">
															<xsl:text>DEBT</xsl:text>
														</xsl:when>
														<xsl:when test="($chrgbrcode=&#39;SHA&#39;)">
															<xsl:text>SHAR</xsl:text>
														</xsl:when>
														<xsl:otherwise>SHAR</xsl:otherwise>
													</xsl:choose>
												</ChrgBr>
											</xsl:if>
										</xsl:if>
										<xsl:choose>
											<xsl:when test="$pmthd1=&#39;CHK&#39;">
												<ChqInstr>
													<xsl:if test="(translate($chqtp1,$lower,$upper)='DFRT')">
														<ChqTp>DFRT</ChqTp>
													</xsl:if>
													<xsl:if test="not(string(PaymentNumber/CheckNumber)=&#39;&#39;)">
														<ChqNb>
															<xsl:value-of select="PaymentNumber/CheckNumber"/>
														</ChqNb>
													</xsl:if>
													<xsl:choose>
														<xsl:when test="(translate($dlvrchnlcode,$lower,$upper)=&#39;MLDB&#39;
	or translate($dlvrchnlcode,$lower,$upper)=&#39;MLCD&#39;
	or translate($dlvrchnlcode,$lower,$upper)=&#39;MLFA&#39;
	or translate($dlvrchnlcode,$lower,$upper)=&#39;CRDB&#39;
	or translate($dlvrchnlcode,$lower,$upper)=&#39;CRCD&#39;
	or translate($dlvrchnlcode,$lower,$upper)=&#39;CRFA&#39;
	or translate($dlvrchnlcode,$lower,$upper)=&#39;PUDB&#39;
	or translate($dlvrchnlcode,$lower,$upper)=&#39;PUCD&#39;
	or translate($dlvrchnlcode,$lower,$upper)=&#39;PUFA&#39;
	or translate($dlvrchnlcode,$lower,$upper)=&#39;RGDB&#39;
	or translate($dlvrchnlcode,$lower,$upper)=&#39;RGCD&#39;
	or translate($dlvrchnlcode,$lower,$upper)=&#39;RGFA&#39;)">
															<DlvryMtd>
																<Cd>
																	<xsl:value-of select="$dlvrchnlcode"/>
																</Cd>
															</DlvryMtd>
														</xsl:when>
														<xsl:otherwise>
															<xsl:if test="not($dlvrchnlcode=&#39;&#39;)">
																<DlvryMtd>
																	<Prtry>
																		<xsl:value-of select="$DeliveryMtd"/>
																	</Prtry>
																</DlvryMtd>
															</xsl:if>
														</xsl:otherwise>
													</xsl:choose>
													<xsl:if test="$chqtp1=&#39;CCHQ&#39; and (BankAccount/BankAddress/Country=&#39;HK&#39;
	or BankAccount/BankAddress/Country=&#39;IN&#39;
	or BankAccount/BankAddress/Country=&#39;ID&#39;
	or BankAccount/BankAddress/Country=&#39;JP&#39;
	or BankAccount/BankAddress/Country=&#39;KR&#39;
	or BankAccount/BankAddress/Country=&#39;NZ&#39;
	or BankAccount/BankAddress/Country=&#39;AU&#39;
	or BankAccount/BankAddress/Country=&#39;SG&#39;
	or BankAccount/BankAddress/Country=&#39;TH&#39;
	or BankAccount/BankAddress/Country=&#39;TW&#39;
	or BankAccount/BankAddress/Country=&#39;VN&#39;
	or BankAccount/BankAddress/Country=&#39;MY&#39;
	or BankAccount/BankAddress/Country=&#39;PH&#39;
	or BankAccount/BankAddress/Country=&#39;CN&#39;) ">
														<ChqMtrtyDt>
															<xsl:value-of select="PaymentDate"/>
														</ChqMtrtyDt>
													</xsl:if>
													<xsl:if test="(BankAccount/BankAddress/Country=&#39;US&#39; or BankAccount/BankAddress/Country=&#39;CA&#39;) and not($FormsCd=&#39;&#39;)">
														<FrmsCd>
															<xsl:value-of select="$FormsCd"/>
														</FrmsCd>
													</xsl:if>
													<xsl:choose>
														<xsl:when test="BankAccount/BankAddress/Country=&#39;IN&#39;">
															<xsl:choose>
																<xsl:when test="(translate($printloc,$lower,$upper)=&#39;MUMBAI&#39;
	or translate($printloc,$lower,$upper)=&#39;DEVANAHALLI&#39;
	or translate($printloc,$lower,$upper)=&#39;PARANUR&#39;
	or translate($printloc,$lower,$upper)=&#39;NEW DELHI&#39;
	or translate($printloc,$lower,$upper)=&#39;BANGALORE&#39;
	or translate($printloc,$lower,$upper)=&#39;DELHI&#39;
	or translate($printloc,$lower,$upper)=&#39;CHENNAI&#39;
	or translate($printloc,$lower,$upper)=&#39;GURGAON&#39;
	or translate($printloc,$lower,$upper)=&#39;GURUGRAM&#39;
	or translate($printloc,$lower,$upper)=&#39;BENGALURU&#39;)">
																	<xsl:choose>
																		<xsl:when test="(translate(Payee/Address/City,$lower,$upper)=&#39;MUMBAI&#39;
	or translate(Payee/Address/City,$lower,$upper)=&#39;DEVANAHALLI&#39;
	or translate(Payee/Address/City,$lower,$upper)=&#39;PARANUR&#39;
	or translate(Payee/Address/City,$lower,$upper)=&#39;NEW DELHI&#39;
	or translate(Payee/Address/City,$lower,$upper)=&#39;BANGALORE&#39;
	or translate(Payee/Address/City,$lower,$upper)=&#39;DELHI&#39;
	or translate(Payee/Address/City,$lower,$upper)=&#39;CHENNAI&#39;
	or translate(Payee/Address/City,$lower,$upper)=&#39;GURGAON&#39;
	or translate(Payee/Address/City,$lower,$upper)=&#39;GURUGRAM&#39;
	or translate(Payee/Address/City,$lower,$upper)=&#39;BENGALURU&#39;)">
																			<RgnlClrZone>JPM PAP</RgnlClrZone>
																		</xsl:when>
																		<xsl:otherwise>
																			<xsl:choose>
																				<xsl:when test="$chqtp1=&#39;CCHQ&#39;">
																					<RgnlClrZone>MSP PAP</RgnlClrZone>
																				</xsl:when>
																				<xsl:when test="$chqtp1=&#39;BCHQ&#39;">
																					<RgnlClrZone>PARDD</RgnlClrZone>
																				</xsl:when>
																			</xsl:choose>
																		</xsl:otherwise>
																	</xsl:choose>
																</xsl:when>
																<xsl:otherwise>
																	<xsl:choose>
																		<xsl:when test="$chqtp1=&#39;CCHQ&#39;">
																			<RgnlClrZone>MSP PAP</RgnlClrZone>
																		</xsl:when>
																		<xsl:when test="$chqtp1=&#39;BCHQ&#39;">
																			<RgnlClrZone>PARDD</RgnlClrZone>
																		</xsl:when>
																		<xsl:when test="$chqtp1=&#39;DRFT&#39; and (not($RgnlClrnZnDff=&#39;&#39;) or not($INDRFTPAYABLE=&#39;&#39;))">
																			<xsl:choose>
																				<xsl:when test="$RgnlClrnZnDff=&#39;&#39; and not($INDRFTPAYABLE=&#39;&#39;)">
																					<RgnlClrZone>
																						<xsl:value-of select="$INDRFTPAYABLE"/>
																					</RgnlClrZone>
																				</xsl:when>
																				<xsl:when test="$INDRFTPAYABLE=&#39;&#39; and not($RgnlClrnZnDff=&#39;&#39;)">
																					<RgnlClrZone>
																						<xsl:value-of select="$RgnlClrnZnDff"/>
																					</RgnlClrZone>
																				</xsl:when>
																			</xsl:choose>
																		</xsl:when>
																	</xsl:choose>
																</xsl:otherwise>
															</xsl:choose>
														</xsl:when>
														<xsl:when test="BankAccount/BankAddress/Country=&#39;AU&#39;">
															<xsl:choose>
																<xsl:when test="$chqtp1=&#39;BCHQ&#39; and (not($RgnlClrnZnDff=&#39;&#39;) or not($AUBCHQPAYABLE=&#39;&#39;))">
																	<xsl:choose>
																		<xsl:when test="$RgnlClrnZnDff=&#39;&#39; and not($AUBCHQPAYABLE=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$AUBCHQPAYABLE"/>
																			</RgnlClrZone>
																		</xsl:when>
																		<xsl:when test="$AUBCHQPAYABLE=&#39;&#39; and not($RgnlClrnZnDff=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$RgnlClrnZnDff"/>
																			</RgnlClrZone>
																		</xsl:when>
																	</xsl:choose>
																</xsl:when>
																<xsl:when test="$chqtp1=&#39;CCHQ&#39; and (not($RgnlClrnZnDff=&#39;&#39;) or not($AUCCHQPAYABLE=&#39;&#39;))">
																	<xsl:choose>
																		<xsl:when test="$RgnlClrnZnDff=&#39;&#39; and not($AUCCHQPAYABLE=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$AUCCHQPAYABLE"/>
																			</RgnlClrZone>
																		</xsl:when>
																		<xsl:when test="$AUCCHQPAYABLE=&#39;&#39; and not($RgnlClrnZnDff=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$RgnlClrnZnDff"/>
																			</RgnlClrZone>
																		</xsl:when>
																	</xsl:choose>
																</xsl:when>
																<xsl:when test="$chqtp1=&#39;DRFT&#39; and (not($RgnlClrnZnDff=&#39;&#39;) or not($AUDRFTPAYABLE=&#39;&#39;))">
																	<xsl:choose>
																		<xsl:when test="$RgnlClrnZnDff=&#39;&#39; and not($AUDRFTPAYABLE=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$AUDRFTPAYABLE"/>
																			</RgnlClrZone>
																		</xsl:when>
																		<xsl:when test="$AUDRFTPAYABLE=&#39;&#39; and not($RgnlClrnZnDff=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$RgnlClrnZnDff"/>
																			</RgnlClrZone>
																		</xsl:when>
																	</xsl:choose>
																</xsl:when>
															</xsl:choose>
														</xsl:when>
														<xsl:when test="BankAccount/BankAddress/Country=&#39;SG&#39;">
															<xsl:choose>
																<xsl:when test="$chqtp1=&#39;BCHQ&#39; and (not($RgnlClrnZnDff=&#39;&#39;) or not($SGBCHQPAYABLE=&#39;&#39;))">
																	<xsl:choose>
																		<xsl:when test="$RgnlClrnZnDff=&#39;&#39; and not($SGBCHQPAYABLE=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$SGBCHQPAYABLE"/>
																			</RgnlClrZone>
																		</xsl:when>
																		<xsl:when test="$SGBCHQPAYABLE=&#39;&#39; and not($RgnlClrnZnDff=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$RgnlClrnZnDff"/>
																			</RgnlClrZone>
																		</xsl:when>
																	</xsl:choose>
																</xsl:when>
																<xsl:when test="$chqtp1=&#39;CCHQ&#39; and (not($RgnlClrnZnDff=&#39;&#39;) or not($SGCCHQPAYABLE=&#39;&#39;))">
																	<xsl:choose>
																		<xsl:when test="$RgnlClrnZnDff=&#39;&#39; and not($SGCCHQPAYABLE=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$SGCCHQPAYABLE"/>
																			</RgnlClrZone>
																		</xsl:when>
																		<xsl:when test="$SGCCHQPAYABLE=&#39;&#39; and not($RgnlClrnZnDff=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$RgnlClrnZnDff"/>
																			</RgnlClrZone>
																		</xsl:when>
																	</xsl:choose>
																</xsl:when>
																<xsl:when test="$chqtp1=&#39;DRFT&#39; and (not($RgnlClrnZnDff=&#39;&#39;) or not($SGDRFTPAYABLE=&#39;&#39;))">
																	<xsl:choose>
																		<xsl:when test="$RgnlClrnZnDff=&#39;&#39; and not($SGDRFTPAYABLE=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$SGDRFTPAYABLE"/>
																			</RgnlClrZone>
																		</xsl:when>
																		<xsl:when test="$SGDRFTPAYABLE=&#39;&#39; and not($RgnlClrnZnDff=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$RgnlClrnZnDff"/>
																			</RgnlClrZone>
																		</xsl:when>
																	</xsl:choose>
																</xsl:when>
															</xsl:choose>
														</xsl:when>
														<xsl:when test="BankAccount/BankAddress/Country=&#39;HK&#39;">
															<xsl:choose>
																<xsl:when test="$chqtp1=&#39;BCHQ&#39; and (not($RgnlClrnZnDff=&#39;&#39;) or not($HKBCHQPAYABLE=&#39;&#39;))">
																	<xsl:choose>
																		<xsl:when test="$RgnlClrnZnDff=&#39;&#39; and not($HKBCHQPAYABLE=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$HKBCHQPAYABLE"/>
																			</RgnlClrZone>
																		</xsl:when>
																		<xsl:when test="$HKBCHQPAYABLE=&#39;&#39; and not($RgnlClrnZnDff=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$RgnlClrnZnDff"/>
																			</RgnlClrZone>
																		</xsl:when>
																	</xsl:choose>
																</xsl:when>
																<xsl:when test="$chqtp1=&#39;CCHQ&#39; and (not($RgnlClrnZnDff=&#39;&#39;) or not($HKCCHQPAYABLE=&#39;&#39;))">
																	<xsl:choose>
																		<xsl:when test="$RgnlClrnZnDff=&#39;&#39; and not($HKCCHQPAYABLE=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$HKCCHQPAYABLE"/>
																			</RgnlClrZone>
																		</xsl:when>
																		<xsl:when test="$HKCCHQPAYABLE=&#39;&#39; and not($RgnlClrnZnDff=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$RgnlClrnZnDff"/>
																			</RgnlClrZone>
																		</xsl:when>
																	</xsl:choose>
																</xsl:when>
																<xsl:when test="$chqtp1=&#39;DRFT&#39; and (not($RgnlClrnZnDff=&#39;&#39;) or not($HKDRFTPAYABLE=&#39;&#39;))">
																	<xsl:choose>
																		<xsl:when test="$RgnlClrnZnDff=&#39;&#39; and not($HKDRFTPAYABLE=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$HKDRFTPAYABLE"/>
																			</RgnlClrZone>
																		</xsl:when>
																		<xsl:when test="$HKDRFTPAYABLE=&#39;&#39; and not($RgnlClrnZnDff=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$RgnlClrnZnDff"/>
																			</RgnlClrZone>
																		</xsl:when>
																	</xsl:choose>
																</xsl:when>
															</xsl:choose>
														</xsl:when>
														<xsl:when test="BankAccount/BankAddress/Country=&#39;ID&#39;">
															<xsl:choose>
																<xsl:when test="$chqtp1=&#39;BCHQ&#39; and (not($RgnlClrnZnDff=&#39;&#39;) or not($IDBCHQPAYABLE=&#39;&#39;))">
																	<xsl:choose>
																		<xsl:when test="$RgnlClrnZnDff=&#39;&#39; and not($IDBCHQPAYABLE=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$IDBCHQPAYABLE"/>
																			</RgnlClrZone>
																		</xsl:when>
																		<xsl:when test="$IDBCHQPAYABLE=&#39;&#39; and not($RgnlClrnZnDff=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$RgnlClrnZnDff"/>
																			</RgnlClrZone>
																		</xsl:when>
																	</xsl:choose>
																</xsl:when>
																<xsl:when test="$chqtp1=&#39;CCHQ&#39; and (not($RgnlClrnZnDff=&#39;&#39;) or not($IDCCHQPAYABLE=&#39;&#39;))">
																	<xsl:choose>
																		<xsl:when test="$RgnlClrnZnDff=&#39;&#39; and not($IDCCHQPAYABLE=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$IDCCHQPAYABLE"/>
																			</RgnlClrZone>
																		</xsl:when>
																		<xsl:when test="$IDCCHQPAYABLE=&#39;&#39; and not($RgnlClrnZnDff=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$RgnlClrnZnDff"/>
																			</RgnlClrZone>
																		</xsl:when>
																	</xsl:choose>
																</xsl:when>
																<xsl:when test="$chqtp1=&#39;DRFT&#39; and (not($RgnlClrnZnDff=&#39;&#39;) or not($IDDRFTPAYABLE=&#39;&#39;))">
																	<xsl:choose>
																		<xsl:when test="$RgnlClrnZnDff=&#39;&#39; and not($IDDRFTPAYABLE=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$IDDRFTPAYABLE"/>
																			</RgnlClrZone>
																		</xsl:when>
																		<xsl:when test="$IDDRFTPAYABLE=&#39;&#39; and not($RgnlClrnZnDff=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$RgnlClrnZnDff"/>
																			</RgnlClrZone>
																		</xsl:when>
																	</xsl:choose>
																</xsl:when>
															</xsl:choose>
														</xsl:when>
														<xsl:when test="BankAccount/BankAddress/Country=&#39;MY&#39;">
															<xsl:choose>
																<xsl:when test="$chqtp1=&#39;BCHQ&#39; and (not($RgnlClrnZnDff=&#39;&#39;) or not($MYBCHQPAYABLE=&#39;&#39;))">
																	<xsl:choose>
																		<xsl:when test="$RgnlClrnZnDff=&#39;&#39; and not($MYBCHQPAYABLE=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$MYBCHQPAYABLE"/>
																			</RgnlClrZone>
																		</xsl:when>
																		<xsl:when test="$MYBCHQPAYABLE=&#39;&#39; and not($RgnlClrnZnDff=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$RgnlClrnZnDff"/>
																			</RgnlClrZone>
																		</xsl:when>
																	</xsl:choose>
																</xsl:when>
																<xsl:when test="$chqtp1=&#39;CCHQ&#39; and (not($RgnlClrnZnDff=&#39;&#39;) or not($MYCCHQPAYABLE=&#39;&#39;))">
																	<xsl:choose>
																		<xsl:when test="$RgnlClrnZnDff=&#39;&#39; and not($MYCCHQPAYABLE=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$MYCCHQPAYABLE"/>
																			</RgnlClrZone>
																		</xsl:when>
																		<xsl:when test="$MYCCHQPAYABLE=&#39;&#39; and not($RgnlClrnZnDff=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$RgnlClrnZnDff"/>
																			</RgnlClrZone>
																		</xsl:when>
																	</xsl:choose>
																</xsl:when>
																<xsl:when test="$chqtp1=&#39;DRFT&#39; and (not($RgnlClrnZnDff=&#39;&#39;) or not($MYDRFTPAYABLE=&#39;&#39;))">
																	<xsl:choose>
																		<xsl:when test="$RgnlClrnZnDff=&#39;&#39; and not($MYDRFTPAYABLE=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$MYDRFTPAYABLE"/>
																			</RgnlClrZone>
																		</xsl:when>
																		<xsl:when test="$MYDRFTPAYABLE=&#39;&#39; and not($RgnlClrnZnDff=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$RgnlClrnZnDff"/>
																			</RgnlClrZone>
																		</xsl:when>
																	</xsl:choose>
																</xsl:when>
															</xsl:choose>
														</xsl:when>
														<xsl:when test="BankAccount/BankAddress/Country=&#39;NZ&#39;">
															<xsl:choose>
																<xsl:when test="$chqtp1=&#39;BCHQ&#39; and (not($RgnlClrnZnDff=&#39;&#39;) or not($NZBCHQPAYABLE=&#39;&#39;))">
																	<xsl:choose>
																		<xsl:when test="$RgnlClrnZnDff=&#39;&#39; and not($NZBCHQPAYABLE=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$NZBCHQPAYABLE"/>
																			</RgnlClrZone>
																		</xsl:when>
																		<xsl:when test="$NZBCHQPAYABLE=&#39;&#39; and not($RgnlClrnZnDff=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$RgnlClrnZnDff"/>
																			</RgnlClrZone>
																		</xsl:when>
																	</xsl:choose>
																</xsl:when>
																<xsl:when test="$chqtp1=&#39;DRFT&#39; and (not($RgnlClrnZnDff=&#39;&#39;) or not($NZDRFTPAYABLE=&#39;&#39;))">
																	<xsl:choose>
																		<xsl:when test="$RgnlClrnZnDff=&#39;&#39; and not($NZDRFTPAYABLE=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$NZDRFTPAYABLE"/>
																			</RgnlClrZone>
																		</xsl:when>
																		<xsl:when test="$NZDRFTPAYABLE=&#39;&#39; and not($RgnlClrnZnDff=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$RgnlClrnZnDff"/>
																			</RgnlClrZone>
																		</xsl:when>
																	</xsl:choose>
																</xsl:when>
															</xsl:choose>
														</xsl:when>
														<xsl:when test="BankAccount/BankAddress/Country=&#39;PH&#39;">
															<xsl:choose>
																<xsl:when test="$chqtp1=&#39;BCHQ&#39; and (not($RgnlClrnZnDff=&#39;&#39;) or not($PHBCHQPAYABLE=&#39;&#39;))">
																	<xsl:choose>
																		<xsl:when test="$RgnlClrnZnDff=&#39;&#39; and not($PHBCHQPAYABLE=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$PHBCHQPAYABLE"/>
																			</RgnlClrZone>
																		</xsl:when>
																		<xsl:when test="$PHBCHQPAYABLE=&#39;&#39; and not($RgnlClrnZnDff=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$RgnlClrnZnDff"/>
																			</RgnlClrZone>
																		</xsl:when>
																	</xsl:choose>
																</xsl:when>
																<xsl:when test="$chqtp1=&#39;CCHQ&#39; and (not($RgnlClrnZnDff=&#39;&#39;) or not($PHCCHQPAYABLE=&#39;&#39;))">
																	<xsl:choose>
																		<xsl:when test="$RgnlClrnZnDff=&#39;&#39; and not($PHCCHQPAYABLE=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$PHCCHQPAYABLE"/>
																			</RgnlClrZone>
																		</xsl:when>
																		<xsl:when test="$PHCCHQPAYABLE=&#39;&#39; and not($RgnlClrnZnDff=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$RgnlClrnZnDff"/>
																			</RgnlClrZone>
																		</xsl:when>
																	</xsl:choose>
																</xsl:when>
																<xsl:when test="$chqtp1=&#39;DRFT&#39; and (not($RgnlClrnZnDff=&#39;&#39;) or not($PHDRFTPAYABLE=&#39;&#39;))">
																	<xsl:choose>
																		<xsl:when test="$RgnlClrnZnDff=&#39;&#39; and not($PHDRFTPAYABLE=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$PHDRFTPAYABLE"/>
																			</RgnlClrZone>
																		</xsl:when>
																		<xsl:when test="$PHDRFTPAYABLE=&#39;&#39; and not($RgnlClrnZnDff=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$RgnlClrnZnDff"/>
																			</RgnlClrZone>
																		</xsl:when>
																	</xsl:choose>
																</xsl:when>
															</xsl:choose>
														</xsl:when>
														<xsl:when test="BankAccount/BankAddress/Country=&#39;TW&#39;">
															<xsl:choose>
																<xsl:when test="$chqtp1=&#39;BCHQ&#39; and (not($RgnlClrnZnDff=&#39;&#39;) or not($TWBCHQPAYABLE=&#39;&#39;))">
																	<xsl:choose>
																		<xsl:when test="$RgnlClrnZnDff=&#39;&#39; and not($TWBCHQPAYABLE=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$TWBCHQPAYABLE"/>
																			</RgnlClrZone>
																		</xsl:when>
																		<xsl:when test="$TWBCHQPAYABLE=&#39;&#39; and not($RgnlClrnZnDff=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$RgnlClrnZnDff"/>
																			</RgnlClrZone>
																		</xsl:when>
																	</xsl:choose>
																</xsl:when>
																<xsl:when test="$chqtp1=&#39;CCHQ&#39; and (not($RgnlClrnZnDff=&#39;&#39;) or not($TWCCHQPAYABLE=&#39;&#39;))">
																	<xsl:choose>
																		<xsl:when test="$RgnlClrnZnDff=&#39;&#39; and not($TWCCHQPAYABLE=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$TWCCHQPAYABLE"/>
																			</RgnlClrZone>
																		</xsl:when>
																		<xsl:when test="$TWCCHQPAYABLE=&#39;&#39; and not($RgnlClrnZnDff=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$RgnlClrnZnDff"/>
																			</RgnlClrZone>
																		</xsl:when>
																	</xsl:choose>
																</xsl:when>
																<xsl:when test="$chqtp1=&#39;DRFT&#39; and (not($RgnlClrnZnDff=&#39;&#39;) or not($TWDRFTPAYABLE=&#39;&#39;))">
																	<xsl:choose>
																		<xsl:when test="$RgnlClrnZnDff=&#39;&#39; and not($TWDRFTPAYABLE=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$TWDRFTPAYABLE"/>
																			</RgnlClrZone>
																		</xsl:when>
																		<xsl:when test="$TWDRFTPAYABLE=&#39;&#39; and not($RgnlClrnZnDff=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$RgnlClrnZnDff"/>
																			</RgnlClrZone>
																		</xsl:when>
																	</xsl:choose>
																</xsl:when>
															</xsl:choose>
														</xsl:when>
														<xsl:when test="BankAccount/BankAddress/Country=&#39;TH&#39;">
															<xsl:choose>
																<xsl:when test="$chqtp1=&#39;BCHQ&#39; and (not($RgnlClrnZnDff=&#39;&#39;) or not($THBCHQPAYABLE=&#39;&#39;))">
																	<xsl:choose>
																		<xsl:when test="$RgnlClrnZnDff=&#39;&#39; and not($THBCHQPAYABLE=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$THBCHQPAYABLE"/>
																			</RgnlClrZone>
																		</xsl:when>
																		<xsl:when test="$THBCHQPAYABLE=&#39;&#39; and not($RgnlClrnZnDff=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$RgnlClrnZnDff"/>
																			</RgnlClrZone>
																		</xsl:when>
																	</xsl:choose>
																</xsl:when>
																<xsl:when test="$chqtp1=&#39;CCHQ&#39; and (not($RgnlClrnZnDff=&#39;&#39;) or not($THCCHQPAYABLE=&#39;&#39;))">
																	<xsl:choose>
																		<xsl:when test="$RgnlClrnZnDff=&#39;&#39; and not($THCCHQPAYABLE=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$THCCHQPAYABLE"/>
																			</RgnlClrZone>
																		</xsl:when>
																		<xsl:when test="$THCCHQPAYABLE=&#39;&#39; and not($RgnlClrnZnDff=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$RgnlClrnZnDff"/>
																			</RgnlClrZone>
																		</xsl:when>
																	</xsl:choose>
																</xsl:when>
																<xsl:when test="$chqtp1=&#39;DRFT&#39; and (not($RgnlClrnZnDff=&#39;&#39;) or not($THDRFTPAYABLE=&#39;&#39;))">
																	<xsl:choose>
																		<xsl:when test="$RgnlClrnZnDff=&#39;&#39; and not($THDRFTPAYABLE=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$THDRFTPAYABLE"/>
																			</RgnlClrZone>
																		</xsl:when>
																		<xsl:when test="$THDRFTPAYABLE=&#39;&#39; and not($RgnlClrnZnDff=&#39;&#39;)">
																			<RgnlClrZone>
																				<xsl:value-of select="$RgnlClrnZnDff"/>
																			</RgnlClrZone>
																		</xsl:when>
																	</xsl:choose>
																</xsl:when>
															</xsl:choose>
														</xsl:when>
													</xsl:choose>
													<xsl:choose>
														<xsl:when test="BankAccount/BankAddress/Country=&#39;IN&#39; and not($PrtLctnDff=&#39;&#39;)">
															<PrtLctn>
																<xsl:value-of select="$PrtLctnDff"/>
															</PrtLctn>
														</xsl:when>
														<xsl:when test="BankAccount/BankAddress/Country=&#39;IN&#39;and $PrtLctnDff=&#39;&#39;">
															<PrtLctn>MUMBAI</PrtLctn>
														</xsl:when>
													</xsl:choose>
												</ChqInstr>
											</xsl:when>
										</xsl:choose>
										<xsl:if test="(not(string(PayeeBankAccount/IntermediaryBankAccount[1]/SwiftCode)=&#39;&#39;) or not(string(PayeeBankAccount/IntermediaryBankAccount[1]/BranchNumber)=&#39;&#39;)) and (($dlvrchnlcode=&#39;IAT&#39; and $svlvl=&#39;NURG&#39;) or  $svlvl=&#39;URGP&#39; )">
											<IntrmyAgt1>
												<FinInstnId>
													<xsl:choose>
														<xsl:when test="$dlvrchnlcode=&#39;IAT&#39; and $svlvl=&#39;NURG&#39; and not(string(PayeeBankAccount/IntermediaryBankAccount/SwiftCode)=&#39;&#39;)">
															<BIC>
																<xsl:value-of select="PayeeBankAccount/IntermediaryBankAccount/SwiftCode"/>
															</BIC>
														</xsl:when>
														<xsl:when test="$svlvl=&#39;URGP&#39; and not(string(IntermediaryBankAccount/SwiftCode)=&#39;&#39;)">
															<BIC>
																<xsl:value-of select="PayeeBankAccount/IntermediaryBankAccount/SwiftCode"/>
															</BIC>
														</xsl:when>
													</xsl:choose>
													<xsl:if test="not(PayeeBankAccount/IntermediaryBankAccount[1]/BranchNumber=&#39;&#39;)">
														<ClrSysMmbId>
															<xsl:choose>
																<xsl:when test="$dlvrchnlcode=&#39;IAT&#39; and $svlvl=&#39;NURG&#39; and not(string(PayeeBankAccount/IntermediaryBankAccount/BranchNumber)=&#39;&#39;)">
																	<MmbId>
																		<xsl:value-of select="PayeeBankAccount/IntermediaryBankAccount/BranchNumber"/>
																	</MmbId>
																</xsl:when>
																<xsl:when test="$svlvl=&#39;URGP&#39; and not(string(PayeeBankAccount/IntermediaryBankAccount/BranchNumber)=&#39;&#39;)">
																	<MmbId>
																		<xsl:value-of select="PayeeBankAccount/IntermediaryBankAccount/BranchNumber"/>
																	</MmbId>
																</xsl:when>
															</xsl:choose>
														</ClrSysMmbId>
													</xsl:if>
													<xsl:choose>
														<xsl:when test="$dlvrchnlcode=&#39;IAT&#39; and $svlvl=&#39;NURG&#39; and not(string(PayeeBankAccount/IntermediaryBankAccount/BankName)=&#39;&#39;)">
															<Nm>
																<xsl:value-of select="PayeeBankAccount/IntermediaryBankAccount/BankName"/>
															</Nm>
														</xsl:when>
														<xsl:when test="$svlvl=&#39;URGP&#39; and not(string(PayeeBankAccount/IntermediaryBankAccount/BankName)=&#39;&#39;)">
															<Nm>
																<xsl:value-of select="PayeeBankAccount/IntermediaryBankAccount/BankName"/>
															</Nm>
														</xsl:when>
													</xsl:choose>
													<PstlAdr>
														<xsl:choose>
															<xsl:when test="$dlvrchnlcode=&#39;IAT&#39; and $svlvl=&#39;NURG&#39; and not(string(PayeeBankAccount/IntermediaryBankAccount[1]/Country)=&#39;&#39;)">
																<Ctry>
																	<xsl:value-of select="PayeeBankAccount/IntermediaryBankAccount[1]/Country"/>
																</Ctry>
															</xsl:when>
															<xsl:when test="$svlvl=&#39;URGP&#39; and not(string(PayeeBankAccount/IntermediaryBankAccount[1]/Country)=&#39;&#39;)">
																<Ctry>
																	<xsl:value-of select="PayeeBankAccount/IntermediaryBankAccount[1]/Country"/>
																</Ctry>
															</xsl:when>
														</xsl:choose>
													</PstlAdr>
												</FinInstnId>
											</IntrmyAgt1>
										</xsl:if>
										<!--ROW Change-->
										<xsl:if test="$dlvrchnlcode=&#39;IAT&#39; and $svlvl=&#39;NURG&#39; and not(PayeeBankAccount/IntermediaryBankAccount/IBANNumber=&#39;&#39;) and (PayeeBankAccount/IntermediaryBankAccount/IBANNumber)">
											<IntrmyAgt1Acct>
												<Id>
													<IBAN>
														<xsl:value-of select="PayeeBankAccount/IntermediaryBankAccount/IBANNumber"/>
													</IBAN>
												</Id>
											</IntrmyAgt1Acct>
										</xsl:if>
										<xsl:if test="not(string(PayeeBankAccount/BankAddress/Country)=&#39;&#39;) and $pmthd1=&#39;TRF&#39; and not(starts-with($dlvrchnlcodeh,&#39;SUA&#39;)) and not(translate ($dlvrchnlcode,$lower,$upper)=&#39;CQP&#39;)">
											<CdtrAgt>
												<FinInstnId>
												    <xsl:choose>
													 <xsl:when test="$svlvl = 'URGP' and PayeeBankAccount/BankAddress/Country = 'ZA' and not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country) and not(PayeeBankAccount/SwiftCode=&#39;&#39;) ">
													   <BIC>
															<xsl:value-of select="PayeeBankAccount/SwiftCode"/>
														</BIC>
													 </xsl:when>
													 <xsl:otherwise>
													   <xsl:if test="not(PayeeBankAccount/SwiftCode=&#39;&#39;) and not(BankAccount/BankAddress/Country = &#39;HK&#39; and PayeeBankAccount/BankAddress/Country = &#39;CN&#39; and PaymentAmount/Currency/Code=&#39;CNY&#39;)">
														<BIC>
															<xsl:value-of select="PayeeBankAccount/SwiftCode"/>
														</BIC>
													   </xsl:if>
													</xsl:otherwise>
													</xsl:choose>
													<xsl:choose>
													<xsl:when test="$svlvl = 'URGP' and PayeeBankAccount/BankAddress/Country = 'ZA' and not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country) and not($MmbIdG=&#39;&#39;) ">
														<ClrSysMmbId>
														<MmbId>
														<xsl:value-of select="concat('ZA',$MmbIdG)"/>
														</MmbId>
													    </ClrSysMmbId>
													</xsl:when>
													<xsl:when test="$pmthd1=&#39;TRF&#39; and not($MmbIdG=&#39;&#39;) and not(BankAccount/BankAddress/Country = &#39;HK&#39; and PayeeBankAccount/BankAddress/Country = &#39;CN&#39; and PaymentAmount/Currency/Code=&#39;CNY&#39;) ">
														<ClrSysMmbId>
															<MmbId>
																<xsl:value-of select="$MmbIdG"/>
															</MmbId>
														</ClrSysMmbId>
												     </xsl:when>
													<xsl:when test="$pmthd1=&#39;TRF&#39; and not($MmbIdG=&#39;&#39;) and (BankAccount/BankAddress/Country = &#39;HK&#39; and PayeeBankAccount/BankAddress/Country = &#39;CN&#39; and PaymentAmount/Currency/Code=&#39;CNY&#39;) ">
														<ClrSysMmbId>
															<MmbId>
																<xsl:value-of select="concat(&#39;CN/&#39;,$MmbIdG)"/>
															</MmbId>
														</ClrSysMmbId>
											        </xsl:when>
											    </xsl:choose>
												<!--ROW Change-->
												<xsl:choose>
													<xsl:when test="$dlvrchnlcode=&#39;IAT&#39; and $svlvl=&#39;NURG&#39; and not(string(PayeeBankAccount/BankName)=&#39;&#39;)">
														<Nm>
															<xsl:value-of select="PayeeBankAccount/BankName"/>
														</Nm>
													</xsl:when>
													<xsl:when test="(PayeeBankAccount/BankName=&#39;&#39;)">
														<Nm>RDFI BANK NAME</Nm>
													</xsl:when>
													<xsl:when test="$svlvl=&#39;URGP&#39; and not(string(PayeeBankAccount/BankName)=&#39;&#39;)">
														<Nm>
															<xsl:value-of select="PayeeBankAccount/BankName"/>
														</Nm>
													</xsl:when>
												</xsl:choose>
													<PstlAdr>
														<xsl:if test="not(string(PayeeBankAccount/BankAddress/AddressLine1)=&#39;&#39;)">
															<StrtNm>
																<xsl:value-of select="substring(PayeeBankAccount/BankAddress/AddressLine1,1,70)"/>
															</StrtNm>
														</xsl:if>
														<xsl:if test="not(string(PayeeBankAccount/BankAddress/PostalCode)=&#39;&#39;)">
															<PstCd>
																<xsl:value-of select="PayeeBankAccount/BankAddress/PostalCode"/>
															</PstCd>
														</xsl:if>
														<xsl:if test="not(string(PayeeBankAccount/BankAddress/City)=&#39;&#39;)">
															<TwnNm>
																<xsl:value-of select="PayeeBankAccount/BankAddress/City"/>
															</TwnNm>
														</xsl:if>
														<xsl:if test="not(string(PayeeBankAccount/BankAddress/County)=&#39;&#39;) or not(string(PayeeBankAccount/BankAddress/State)=&#39;&#39;) or not(string(PayeeBankAccount/BankAddress/Province)=&#39;&#39;)">
															<CtrySubDvsn>
																<xsl:value-of select="substring($cdtragntcntrysd,1,35) "/>
															</CtrySubDvsn>
														</xsl:if>
														<Ctry>
															<xsl:value-of select="PayeeBankAccount/BankAddress/Country"/>
														</Ctry>
													</PstlAdr>
													<xsl:if test="$svlvl1=&#39;SEPA&#39; and PayeeBankAccount/SwiftCode=&#39;&#39;">
														<Othr>
															<Id>NOTPROVIDED</Id>
														</Othr>
													</xsl:if>
												</FinInstnId>
												<xsl:if test="not($BridG=&#39;&#39;)">
													<BrnchId>
														<Id>
															<xsl:value-of select="$BridG"/>
														</Id>
													</BrnchId>
												</xsl:if>
											</CdtrAgt>
										</xsl:if>
										<xsl:if test="not(string(Payee/Name)=&#39;&#39;)">
											<Cdtr>
												<Nm>
													<xsl:value-of select="Payee/Name"/>
												</Nm>
												<xsl:if test="not(string(Payee/Address/Country)=&#39;&#39;)">
													<PstlAdr>
														<xsl:if test="not(string(Payee/Address/AddressLine1)=&#39;&#39;) and not($svlvl1=&#39;NURG&#39; and Payer/Address/Country=&#39;NO&#39;)">
															<StrtNm>
																<xsl:value-of select="substring(Payee/Address/AddressLine1,1,70)"/>
															</StrtNm>
														</xsl:if>
														<xsl:if test="not(string(Payee/Address/PostalCode)=&#39;&#39;)">
															<PstCd>
																<xsl:value-of select="Payee/Address/PostalCode"/>
															</PstCd>
														</xsl:if>
														<xsl:if test="not(string(Payee/Address/City)=&#39;&#39;) and not($svlvl1=&#39;NURG&#39; and Payer/Address/Country=&#39;NO&#39;)">
															<TwnNm>
																<xsl:value-of select="Payee/Address/City"/>
															</TwnNm>
														</xsl:if>
														<xsl:if test="(not(string(Payee/Address/County)=&#39;&#39;) or not(string(Payee/Address/State)=&#39;&#39;) or not(string(Payee/Address/Province)=&#39;&#39;))
	and not($pmthd1=&#39;CHK&#39;) and (not(BankAccount/BankAddress/Country=&#39;US&#39;) and not(BankAccount/BankAddress/Country=&#39;CA&#39;))">
															<CtrySubDvsn>
																<xsl:value-of select="substring($cdtrcntrysd,1,35)"/>
															</CtrySubDvsn>
														</xsl:if>
														<xsl:if test="not(string(Payee/Address/State)=&#39;&#39;) and ($pmthd1=&#39;CHK&#39;)
	and ( BankAccount/BankAddress/Country=&#39;US&#39; or BankAccount/BankAddress/Country=&#39;CA&#39;)">
															<CtrySubDvsn>
																<xsl:value-of select="Payee/Address/State"/>
															</CtrySubDvsn>
														</xsl:if>
														<Ctry>
															<xsl:value-of select="Payee/Address/Country"/>
														</Ctry>
														<xsl:if test="not(string(Payee/Address/AddressLine1)=&#39;&#39;) and ($svlvl1=&#39;NURG&#39; and (Payer/Address/Country=&#39;NO&#39;))">
															<AdrLine>
																<xsl:value-of select="substring(Payee/Address/AddressLine1,1,70)"/>
															</AdrLine>
														</xsl:if>
														<xsl:if test="not(string(Payee/Address/City)=&#39;&#39;) and ($svlvl1=&#39;NURG&#39; and (Payer/Address/Country=&#39;NO&#39;))">
															<AdrLine>
																<xsl:value-of select="Payee/Address/City"/>
															</AdrLine>
														</xsl:if>
														<xsl:if test="($svlvl1=&#39;NURG&#39; and BankAccount/BankAddress/Country=&#39;ZA&#39;)">
															<AdrLine>
																<xsl:value-of select="&#39;South Africa&#39;"/>
															</AdrLine>
														</xsl:if>
														<xsl:if test="($svlvl1=&#39;URGP&#39; and PayeeBankAccount/BankAddress/Country = 'SG' and not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country) and not(Payee/ContactInfo/ContactLocators/PhoneNumber=&#39;&#39;))">
															<AdrLine>
																<xsl:value-of select="Payee/ContactInfo/ContactLocators/PhoneNumber"/>
															</AdrLine>
														</xsl:if>
													</PstlAdr>
												</xsl:if>
												<xsl:if test="$pmthd2='CHK' and not(Payee/SupplierNumber='')">
													<Id>
														<OrgId>
															<Othr>
																<Id>
																	<xsl:value-of select="Payee/SupplierNumber"/>
																</Id>
															</Othr>
														</OrgId>
													</Id>
												</xsl:if>
												<xsl:choose>
													<xsl:when test="BankAccount/BankAddress/Country=&#39;MY&#39; and $svlvl1=&#39;NURG&#39; and $dlvrchnlcode=&#39;NBPS&#39; and not($MYNBPSCRDID=&#39;&#39;)">
														<Id>
															<OrgId>
																<Othr>
																	<Id>
																		<xsl:value-of select="$MYNBPSCRDID"/>
																	</Id>
																</Othr>
															</OrgId>
														</Id>
													</xsl:when>
													<xsl:when test="BankAccount/BankAddress/Country=&#39;TW&#39; and $svlvl1=&#39;NURG&#39; and not($TWGIRCRDID=&#39;&#39;)">
														<Id>
															<OrgId>
																<Othr>
																	<Id>
																		<xsl:value-of select="$TWGIRCRDID"/>
																	</Id>
																	<SchmeNm>
																		<Cd>CUST</Cd>
																	</SchmeNm>
																</Othr>
															</OrgId>
														</Id>
													</xsl:when>
													<xsl:when test="BankAccount/BankAddress/Country=&#39;BR&#39; and not($BRTRFCRDID=&#39;&#39;)">
														<Id>
															<OrgId>
																<Othr>
																	<Id>
																		<xsl:value-of select="$BRTRFCRDID"/>
																	</Id>
																	<SchmeNm>
																		<Cd>TXID</Cd>
																	</SchmeNm>
																</Othr>
															</OrgId>
														</Id>
													</xsl:when>
													<xsl:when test="BankAccount/BankAddress/Country=&#39;MX&#39; and not($MXTRFCRDID=&#39;&#39;)">
														<Id>
															<OrgId>
																<Othr>
																	<Id>
																		<xsl:value-of select="$MXTRFCRDID"/>
																	</Id>
																	<SchmeNm>
																		<Cd>TXID</Cd>
																	</SchmeNm>
																</Othr>
															</OrgId>
														</Id>
													</xsl:when>
													<xsl:when test="BankAccount/BankAddress/Country=&#39;CL&#39; and not($CLTRFCRDID=&#39;&#39;)">
														<Id>
															<OrgId>
																<Othr>
																	<Id>
																		<xsl:value-of select="$CLTRFCRDID"/>
																	</Id>
																	<SchmeNm>
																		<Cd>TXID</Cd>
																	</SchmeNm>
																</Othr>
															</OrgId>
														</Id>
													</xsl:when>
													<xsl:when test="BankAccount/BankAddress/Country=&#39;AR&#39; and not($ARTRFCRDID=&#39;&#39;)">
														<Id>
															<OrgId>
																<Othr>
																	<Id>
																		<xsl:value-of select="$ARTRFCRDID"/>
																	</Id>
																	<SchmeNm>
																		<Cd>TXID</Cd>
																	</SchmeNm>
																</Othr>
															</OrgId>
														</Id>
													</xsl:when>
													<xsl:when test=" (BankAccount/BankAddress/Country=&#39;MY&#39; and $svlvl1=&#39;NURG&#39; and (not($dlvrchnlcode=&#39;NBPS&#39;) or $dlvrchnlcode=&#39;&#39;) )">
														<xsl:choose>
															<xsl:when test="not($CdtrIdDff=&#39;&#39;)">
																<Id>
																	<OrgId>
																		<Othr>
																			<Id>
																				<xsl:value-of select="substring($CdtrIdDff,1,1)"/>
																			</Id>
																			<SchmeNm>
																				<Prtry>RESIDENT</Prtry>
																			</SchmeNm>
																		</Othr>
																	</OrgId>
																</Id>
															</xsl:when>
															<xsl:otherwise>
																<xsl:choose>
																	<xsl:when test="(PayeeBankAccount/BankAddress/Country =BankAccount/BankAddress/Country)">
																		<Id>
																			<OrgId>
																				<Othr>
																					<Id>R</Id>
																					<SchmeNm>
																						<Prtry>RESIDENT</Prtry>
																					</SchmeNm>
																				</Othr>
																			</OrgId>
																		</Id>
																	</xsl:when>
																	<xsl:otherwise>
																		<Id>
																			<OrgId>
																				<Othr>
																					<Id>N</Id>
																					<SchmeNm>
																						<Prtry>RESIDENT</Prtry>
																					</SchmeNm>
																				</Othr>
																			</OrgId>
																		</Id>
																	</xsl:otherwise>
																</xsl:choose>
															</xsl:otherwise>
														</xsl:choose>
													</xsl:when>
												</xsl:choose>
												<xsl:choose>
													<xsl:when test="BankAccount/BankAddress/Country=&#39;ID&#39; and $svlvl1=&#39;NURG&#39;">
														<xsl:choose>
															<xsl:when test="not($CtryOfResDff=&#39;&#39;)">
																<xsl:choose>
																	<xsl:when test="$CtryOfResDff=&#39;RESIDENT&#39;or $CtryOfResDff=&#39;Resident&#39;">
																		<CtryOfRes>ID</CtryOfRes>
																	</xsl:when>
																	<xsl:otherwise>
																		<CtryOfRes>XX</CtryOfRes>
																	</xsl:otherwise>
																</xsl:choose>
															</xsl:when>
															<xsl:otherwise>
																<CtryOfRes>
																	<xsl:value-of select="Payee/Address/Country"/>
																</CtryOfRes>
															</xsl:otherwise>
														</xsl:choose>
													</xsl:when>
												</xsl:choose>
												<xsl:choose>
													<xsl:when test="BankAccount/BankAddress/Country=&#39;CN&#39; and $CNTRFNURG=&#39;Y&#39; and $pmthd1=&#39;TRF&#39; and $svlvl1=&#39;NURG&#39; and not(Payee/AlternateName=&#39;&#39;)">
														<CtctDtls>
															<Nm>
																<xsl:value-of select="Payee/AlternateName"/>
															</Nm>
														</CtctDtls>
													</xsl:when>
													<xsl:when test="BankAccount/BankAddress/Country=&#39;CN&#39; and PayeeBankAccount/BankAddress/Country=&#39;CN&#39; and $CNTRFURGP=&#39;Y&#39; and $pmthd1=&#39;TRF&#39; and $svlvl1=&#39;URGP&#39; and not(Payee/AlternateName=&#39;&#39;) and PaymentAmount/Currency/Code=&#39;CNY&#39;">
														<CtctDtls>
															<Nm>
																<xsl:value-of select="Payee/AlternateName"/>
															</Nm>
														</CtctDtls>
													</xsl:when>
													<xsl:when test="BankAccount/BankAddress/Country=&#39;TW&#39; and $TWTRFURGP=&#39;Y&#39; and $pmthd1=&#39;TRF&#39; and $svlvl1=&#39;URGP&#39; and not(Payee/AlternateName=&#39;&#39;) and PaymentAmount/Currency/Code=&#39;TWD&#39;">
														<CtctDtls>
															<Nm>
																<xsl:value-of select="Payee/AlternateName"/>
															</Nm>
														</CtctDtls>
													</xsl:when>
													<xsl:when test="BankAccount/BankAddress/Country=&#39;JP&#39; and $JPTRFNURG=&#39;Y&#39; and $pmthd1=&#39;TRF&#39; and $svlvl1=&#39;NURG&#39; and not(Payee/AlternateName=&#39;&#39;)">
														<CtctDtls>
															<Nm>
																<xsl:value-of select="Payee/AlternateName"/>
															</Nm>
														</CtctDtls>
													</xsl:when>
													<xsl:when test="BankAccount/BankAddress/Country=&#39;KR&#39; and $KRTRFNURG=&#39;Y&#39; and $pmthd1=&#39;TRF&#39; and $svlvl1=&#39;NURG&#39; and not(Payee/AlternateName=&#39;&#39;)">
														<CtctDtls>
															<Nm>
																<xsl:value-of select="Payee/AlternateName"/>
															</Nm>
														</CtctDtls>
													</xsl:when>
													<xsl:when test="BankAccount/BankAddress/Country=&#39;TW&#39; and $TWTRFNURG=&#39;Y&#39; and $pmthd1=&#39;TRF&#39; and $svlvl1=&#39;NURG&#39; and not(Payee/AlternateName=&#39;&#39;)">
														<CtctDtls>
															<Nm>
																<xsl:value-of select="Payee/AlternateName"/>
															</Nm>
														</CtctDtls>
													</xsl:when>
													<xsl:when test="BankAccount/BankAddress/Country=&#39;TH&#39; and $THTRFNURG=&#39;Y&#39; and $pmthd1=&#39;TRF&#39; and $svlvl1=&#39;NURG&#39; and not(Payee/AlternateName=&#39;&#39;)">
														<CtctDtls>
															<Nm>
																<xsl:value-of select="Payee/AlternateName"/>
															</Nm>
														</CtctDtls>
													</xsl:when>
													<xsl:when test="BankAccount/BankAddress/Country=&#39;TW&#39; and $TWCHKBCHQ=&#39;Y&#39; and $pmthd1=&#39;CHK&#39; and $chqtp1=&#39;BCHQ&#39; and not(Payee/AlternateName=&#39;&#39;)">
														<CtctDtls>
															<Nm>
																<xsl:value-of select="Payee/AlternateName"/>
															</Nm>
														</CtctDtls>
													</xsl:when>
													<xsl:when test="BankAccount/BankAddress/Country=&#39;TH&#39; and $THCHKBCHQ=&#39;Y&#39; and $pmthd1=&#39;CHK&#39; and $chqtp1=&#39;BCHQ&#39; and not(Payee/AlternateName=&#39;&#39;)">
														<CtctDtls>
															<Nm>
																<xsl:value-of select="Payee/AlternateName"/>
															</Nm>
														</CtctDtls>
													</xsl:when>
													<xsl:when test="BankAccount/BankAddress/Country=&#39;HK&#39; and $HKCHKCCHQ=&#39;Y&#39; and $pmthd1=&#39;CHK&#39; and $chqtp1=&#39;CCHQ&#39; and not(Payee/AlternateName=&#39;&#39;)">
														<CtctDtls>
															<Nm>
																<xsl:value-of select="Payee/AlternateName"/>
															</Nm>
														</CtctDtls>
													</xsl:when>
													<xsl:when test="BankAccount/BankAddress/Country=&#39;TW&#39; and $TWCHKCCHQ=&#39;Y&#39; and $pmthd1=&#39;CHK&#39; and $chqtp1=&#39;CCHQ&#39; and not(Payee/AlternateName=&#39;&#39;)">
														<CtctDtls>
															<Nm>
																<xsl:value-of select="Payee/AlternateName"/>
															</Nm>
														</CtctDtls>
													</xsl:when>
													<xsl:when test="BankAccount/BankAddress/Country=&#39;TH&#39; and $THCHKCCHQ=&#39;Y&#39; and $pmthd1=&#39;CHK&#39; and $chqtp1=&#39;CCHQ&#39; and not(Payee/AlternateName=&#39;&#39;)">
														<CtctDtls>
															<Nm>
																<xsl:value-of select="Payee/AlternateName"/>
															</Nm>
														</CtctDtls>
													</xsl:when>
													<xsl:when test="BankAccount/BankAddress/Country=&#39;US&#39; and ( starts-with($dlvrchnlcode,&#39;SUA&#39;) or  translate ($dlvrchnlcode,$lower,$upper)=&#39;CQP&#39;) and not(Payee/ContactInfo/ContactLocators[1]/EmailAddress=&#39;&#39;)  ">
														<CtctDtls>
															<EmailAdr>
																<xsl:value-of select="Payee/ContactInfo/ContactLocators[1]/EmailAddress"/>
															</EmailAdr>
														</CtctDtls>
													</xsl:when>
												</xsl:choose>
											</Cdtr>
										</xsl:if>
										<xsl:if test="(not(string(PayeeBankAccount/BankAccountNumber)=&#39;&#39;) or not(string(PayeeBankAccount/IBANNumber)=&#39;&#39;)) and $pmthd1=&#39;TRF&#39; and not(starts-with($dlvrchnlcode,&#39;SUA&#39;)) and not(translate($dlvrchnlcode,$lower,$upper)=&#39;CQP&#39;)">
											<CdtrAcct>
												<Id>
													<xsl:if test="not(PayeeBankAccount/IBANNumber=&#39;&#39;)">
														<IBAN>
															<xsl:value-of select="PayeeBankAccount/IBANNumber"/>
														</IBAN>
													</xsl:if>
													<xsl:if test="not(PayeeBankAccount/BankAccountNumber=&#39;&#39;) and (PayeeBankAccount/IBANNumber=&#39;&#39;)">
													<xsl:choose>
													 <xsl:when test="$svlvl = 'URGP' and PayeeBankAccount/BankAddress/Country = 'AM' and not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country) and not(PayeeBankAccount/BankNumber = ' ') and not(PayeeBankAccount/BankAccountNumber = ' ') ">
													    <Othr>
															<Id>
																<xsl:value-of select="concat(PayeeBankAccount/BankNumber,PayeeBankAccount/BankAccountNumber)"/>
															</Id>
														</Othr>
													  </xsl:when>
													 <xsl:when test="$svlvl = 'URGP' and PayeeBankAccount/BankAddress/Country = 'JM' and not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country) and not(PayeeBankAccount/SwiftCode = ' ') and not(PayeeBankAccount/BankAccountNumber = ' ') ">
													   <Othr>
															<Id>
																<xsl:value-of select="concat(PayeeBankAccount/SwiftCode,PayeeBankAccount/BankAccountNumber)"/>
															</Id>
														</Othr>
													 </xsl:when>
													 <xsl:otherwise>
													    <Othr>
															<Id>
																<xsl:value-of select="PayeeBankAccount/BankAccountNumber"/>
															</Id>
														</Othr>
													  </xsl:otherwise>
													  </xsl:choose>
													</xsl:if>  
												</Id>
												<!--ROW Change-->
												<xsl:choose>
													<xsl:when test="not(PayeeBankAccount/BankAccountType/Code = &#39;&#39;) and translate(PayeeBankAccount/BankAccountType/Code,$lower,$upper) = &#39;SAVINGS&#39;">
														<Tp>
															<Cd>SVGS</Cd>
														</Tp>
													</xsl:when>
													<xsl:when test="not(PayeeBankAccount/BankAccountType/Code = &#39;&#39;) and translate(PayeeBankAccount/BankAccountType/Code,$lower,$upper) = &#39;LOAN&#39;">
														<Tp>
															<Cd>LOAN</Cd>
														</Tp>
													</xsl:when>
													<xsl:when test="not(PayeeBankAccount/BankAccountType/Code = &#39;&#39;) and translate(PayeeBankAccount/BankAccountType/Code,$lower,$upper) = &#39;DEMAND DEPOSIT&#39;">
														<Tp>
															<Cd>CASH</Cd>
														</Tp>
													</xsl:when>
												</xsl:choose>
											</CdtrAcct>
										</xsl:if>
										<xsl:if test="starts-with(PayeeBankAccount/AlternateBankAccountName,&#39;FFC&#39;)">
											<UltmtCdtr>
												<xsl:if test="not(PayeeBankAccount/AlternateBankAccountName = '')">
													<xsl:variable name="afterSecondAsterisk" select="substring-after(substring-after(PayeeBankAccount/AlternateBankAccountName, '*'), '*')"/>
													<Nm>
														<xsl:value-of select="$afterSecondAsterisk"/>
													</Nm>
												</xsl:if>
												<xsl:if test="not(PayeeBankAccount/AlternateBankAccountName = '')">
													<xsl:variable name="betweenAsterisks" select="substring-before(substring-after(PayeeBankAccount/AlternateBankAccountName, '*'), '*')"/>
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
										<xsl:variable name="Countries_5" select="'BR,CL,CO,AR'"/>
										<xsl:choose>
											<xsl:when test="(not(PayeeBankAccount/BankAddress/Country = '') and  $svlvl = 'URGP' and contains($Countries_5,PayeeBankAccount/BankAddress/Country) and not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country) and not(string(Payee/ContactInfo/ContactLocators/EmailAddress) = ''))">
												<InstrForDbtrAgt>
												  <xsl:variable name="emailAddressBeforeAtSign">
												    <xsl:value-of select="substring-before(Payee/ContactInfo/ContactLocators/EmailAddress,'@')"/>
												  </xsl:variable>
												  <xsl:variable name="emailAddressAfterAtSign">
												   <xsl:value-of select="substring-after(Payee/ContactInfo/ContactLocators/EmailAddress,'@')"/>
												  </xsl:variable>
												  <xsl:value-of select="substring(concat($emailAddressBeforeAtSign,'_AT_',$emailAddressAfterAtSign),1,140)"/>
												</InstrForDbtrAgt>
											</xsl:when>
											<xsl:when test="(not(PayeeBankAccount/BankAddress/Country = '') and  $svlvl = 'URGP' and (PayeeBankAccount/BankAddress/Country = 'KR') and not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country) and not(string(PaymentReason/Code) = ''))"> 
												<InstrForDbtrAgt>
													<xsl:value-of select="substring(concat('/ACC/PURPOSE/',PaymentReason/Code),1,140)"/>
												</InstrForDbtrAgt>
										    </xsl:when>
										    <xsl:when test="(not(PayeeBankAccount/BankAddress/Country = '') and  $svlvl = 'URGP' and (PayeeBankAccount/BankAddress/Country = 'IN') and not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country) and not(string(PaymentReason/Code) = ''))"> 
												<InstrForDbtrAgt>
													<xsl:value-of select="substring(concat('/ACC/PURPOSE/IN,',PaymentReason/Code,',',BankAccount/BankAddress/Country),1,140)"/>
												</InstrForDbtrAgt>
										    </xsl:when>
											<xsl:when test="($svlvl=&#39;URGP&#39; and not(Payee/ContactInfo/ContactLocators/PhoneNumber=&#39;&#39;))">
												<InstrForDbtrAgt>
													<xsl:value-of select="substring((Payee/ContactInfo/ContactLocators/PhoneNumber),1,140)"/>
												</InstrForDbtrAgt>
											</xsl:when>
										</xsl:choose>
										<xsl:choose>
											<xsl:when test="$pmthd1=&#39;TRF&#39; and $svlvl1=&#39;NURG&#39;">
												<xsl:choose>
													<xsl:when test="BankAccount/BankAddress/Country=&#39;US&#39; and translate($dlvrchnlcode,$lower,$upper)=&#39;CCD+&#39; and ($pmtrsncode=&#39;TAXS&#39; or $pmtrsncode=&#39;BECH&#39;) ">
														<Purp>
															<Cd>
																<xsl:value-of select="$pmtrsncode"/>
															</Cd>
														</Purp>
													</xsl:when>
												</xsl:choose>
											</xsl:when>
										</xsl:choose>
										<xsl:choose>
											<xsl:when test="BankAccount/BankAddress/Country=&#39;ID&#39; and $svlvl1=&#39;NURG&#39; and translate($rrdetyp,$upper,$lower)=&#39;case(individual)&#39; ">
												<RgltryRptg>
													<Dtls>
														<Tp>1</Tp>
													</Dtls>
												</RgltryRptg>
											</xsl:when>
											<xsl:when test="BankAccount/BankAddress/Country=&#39;ID&#39; and $svlvl1=&#39;NURG&#39; and translate($rrdetyp,$upper,$lower)=&#39;corporation&#39; ">
												<RgltryRptg>
													<Dtls>
														<Tp>2</Tp>
													</Dtls>
												</RgltryRptg>
											</xsl:when>
											<xsl:when test="BankAccount/BankAddress/Country=&#39;ID&#39; and $svlvl1=&#39;NURG&#39; and translate($rrdetyp,$upper,$lower)=&#39;company&#39; ">
												<RgltryRptg>
													<Dtls>
														<Tp>2</Tp>
													</Dtls>
												</RgltryRptg>
											</xsl:when>
											<xsl:when test="BankAccount/BankAddress/Country=&#39;ID&#39; and $svlvl1=&#39;NURG&#39; and translate($rrdetyp,$upper,$lower)=&#39;goverment&#39; ">
												<RgltryRptg>
													<Dtls>
														<Tp>3</Tp>
													</Dtls>
												</RgltryRptg>
											</xsl:when>
										</xsl:choose>
										<xsl:if test="((BankAccount/BankAddress/Country=&#39;MY&#39; and ($svlvl1=&#39;NURG&#39; or $pmthd1=&#39;CHK&#39;)) or (Payer/Address/Country =&#39;NO&#39; and Payer/Address/Country!=PayeeBankAccount/BankAddress/Country)) and not($pmtrsncode=&#39;&#39;)">
											<RgltryRptg>
												<Dtls>
													<Cd>
														<xsl:value-of select="$pmtrsncode"/>
													</Cd>
												</Dtls>
											</RgltryRptg>
										</xsl:if>
										<xsl:if test="$svlvl1=&#39;URGP&#39; and $pmthd1=&#39;TRF&#39; and not(PaymentTextMessage[3]=&#39;&#39;) ">
											<RgltryRptg>
												<Dtls>
													<Inf>
														<xsl:value-of select="PaymentTextMessage[3]"/>
													</Inf>
												</Dtls>
											</RgltryRptg>
										</xsl:if>
										<xsl:if test="BankAccount/BankAddress/Country=&#39;MX&#39; and (format-number(sum(DocumentPayable/DocumentPayableLine[contains(Tax/TaxCode ,&#39;VAT&#39;)]/LineGrossAmount/Value), &#39;##0.00&#39;) &gt; 0)">
											<Tax>
												<Rcrd>
													<Tp>VATX</Tp>
													<TaxAmt>
														<TtlAmt>
															<xsl:attribute name="Ccy">
																<xsl:value-of select="DocumentPayable/TotalDocumentTaxAmount/Currency/Code[1]"/>
															</xsl:attribute>
															<xsl:value-of select="format-number(sum(DocumentPayable/DocumentPayableLine[contains(Tax/TaxCode ,&#39;VAT&#39;)]/LineGrossAmount/Value), &#39;##0.00&#39;)"/>
														</TtlAmt>
													</TaxAmt>
												</Rcrd>
											</Tax>
										</xsl:if>
										<xsl:variable name="RemittanceName">
											<xsl:choose>
												<xsl:when test="not(Payee/AlternateName=&#39;&#39;)">
													<xsl:value-of select="Payee/AlternateName"/>
												</xsl:when>
												<xsl:otherwise>
													<xsl:value-of select="Payee/Name"/>
												</xsl:otherwise>
											</xsl:choose>
										</xsl:variable>
										<RmtInf>
											<!-- 
	<xsl:variable name="Unstr4">
	<xsl:if test="not(string(PaymentDetails)=&#39;&#39;)">
	<xsl:value-of select="substring(PaymentDetails,1,140)"/>
	</xsl:if>
	</xsl:variable>  -->
											<xsl:variable name="Unstr4">
												<xsl:for-each select="DocumentPayable">
													<xsl:value-of select="DocumentNumber/ReferenceNumber"/>
													<xsl:if test="not(position() = last())">,</xsl:if>
												</xsl:for-each>
											</xsl:variable>
											<!-- ROW Changes -->
											<xsl:variable name="Unstr6">
												<xsl:value-of select="PaymentReason/Meaning"/>
											</xsl:variable>
											<xsl:variable name="Unstr7">
												<xsl:value-of select="PaymentReason/Code"/>
											</xsl:variable>
											<xsl:variable name="Countries_1" select="'AF,DZ,AD,AO,AI,AG,AU,AT,AZ,BD,BB,BE,BJ,BM,BO,BW,BN,BF,BI,KH,CM,CA,CV,KY,CF,TD,CO,HR,CY,CZ,DK,DJ,DM,EG,GQ,ER,EE,ET,FJ,FI,FR,GA,GM,GE,DE,GH,GR,GD,GT,GN,GW,HT,HK,HU,IS,IN,IL,IE,IQ,IT,CI,JM,JP,KE,KW,LA,LV,LS,LB,LI,LT,LU,MO,MW,MV,ML,MT,MU,MC,MN,ME,MS,MA,NP,NL,AN,NZ,NI,NE,NG,NO,PG,PY,PT,QA,CG,RO,RW,KN,LC,VC,WS,SM,ST,SA,SN,RS,SC,SL,SG,SK,SI,SB,ES,SR,SZ,SE,CH,PF,TZ,TG,TO,TT,TN,TW,US,UK,VU,VN,ZM'"/>
											<xsl:variable name="Countries_2" select="'BH,CN,KG,MX,OM,TR'"/>
											<xsl:variable name="Countries_3" select="'JO,MY'"/>
											<xsl:variable name="Countries_4" select="'CR,DO,TH'"/>
											<xsl:choose>
												<xsl:when test="(not(PayeeBankAccount/BankAddress/Country = '') and $svlvl = 'URGP') and
	              (contains($Countries_1,PayeeBankAccount/BankAddress/Country)) and 
	               not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country) and
	               not(string(PaymentReason/Meaning) = '')">
													<Ustrd>
														<xsl:value-of select="substring($Unstr6,1,140)"/>
													</Ustrd>
												</xsl:when>
												<xsl:when test="(not(PayeeBankAccount/BankAddress/Country = '') and $svlvl = 'URGP') and
	              (contains($Countries_2,PayeeBankAccount/BankAddress/Country)) and 
	               not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country) and
	               not(string(PaymentReason/Code) = '')">
													<Ustrd>
														<xsl:value-of select="substring($Unstr7,1,140)"/>
													</Ustrd>
												</xsl:when>
												<xsl:when test="(not(PayeeBankAccount/BankAddress/Country = '') and $svlvl = 'URGP') and
	              (contains($Countries_3,PayeeBankAccount/BankAddress/Country)) and 
	               not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country) and
	               not(string(PaymentReason/Code) = '') and not(string(PaymentReason/Meaning) = '')">
													<Ustrd>
														<xsl:value-of select="substring(concat($Unstr7,'/',$Unstr6),1,140)"/>
													</Ustrd>
												</xsl:when>
												<xsl:when test="(not(PayeeBankAccount/BankAddress/Country = '') and $svlvl = 'URGP') and
	              (contains(PayeeBankAccount/BankAddress/Country,'AR')) and 
	               not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country) and
	               not(string(Payee/TaxRegistrationNumber) = '') and not(string(PaymentReason/Meaning) = '')">
													<Ustrd>
														<xsl:value-of select="substring($Unstr6,1,140)"/>
													</Ustrd>
													<xsl:if test="string(Payee/TaxOrganizationType/Code) = 'CORPORATION'">
														<Ustrd>
															<xsl:value-of select="concat('CUIT' ,' ',Payee/TaxRegistrationNumber)"/>
														</Ustrd>
													</xsl:if>
													<xsl:if test="string(Payee/TaxOrganizationType/Code) = 'INDIVIDUAL'">
														<Ustrd>
															<xsl:value-of select="concat('CUIL',' ', Payee/TaxRegistrationNumber)"/>
														</Ustrd>
													</xsl:if>
												</xsl:when>
												<xsl:when test="(not(PayeeBankAccount/BankAddress/Country = '') and $svlvl = 'URGP') and
	              (contains(PayeeBankAccount/BankAddress/Country,'BS')) and 
	               not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country) and
	               not(string(PayeeBankAccount/SwiftCode) = '') and not(string(PaymentReason/Meaning) = '') and string(PayeeBankAccount/BankName) = 'RBC Bahamas'">
													<Ustrd>
														<xsl:value-of select="substring(concat($Unstr6,' / ',PayeeBankAccount/SwiftCode),1,140)"/>
													</Ustrd>
												</xsl:when>
												<xsl:when test="(not(PayeeBankAccount/BankAddress/Country = '') and $svlvl = 'URGP') and
	              (contains(PayeeBankAccount/BankAddress/Country,'BY')) and 
	               not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country) and
	               not(string(Payee/TaxRegistrationNumber) = '') and not(string(PaymentReason/Meaning) = '') and not(string(PayeeBankAccount/BankCode) = '')">
													<Ustrd>
														<xsl:value-of select="substring(concat($Unstr6,',',PayeeBankAccount/BankCode,',','Tax ID',' ',Payee/TaxRegistrationNumber),1,140)"/>
													</Ustrd>
												</xsl:when>
												<xsl:when test="(not(PayeeBankAccount/BankAddress/Country = '') and $svlvl = 'URGP') and
	              (contains(PayeeBankAccount/BankAddress/Country,'BZ')) and 
	               not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country) and
	               not(string(PayeeBankAccount/BranchNumber) = '') and not(string(PaymentReason/Meaning) = '') and string(PayeeBankAccount/BankName) = 'Scotia Bank'">
													<Ustrd>
														<xsl:value-of select="substring(concat($Unstr6,' ',PayeeBankAccount/BranchNumber),1,140)"/>
													</Ustrd>
												</xsl:when>
												<xsl:when test="(not(PayeeBankAccount/BankAddress/Country = '') and $svlvl = 'URGP') and
	              (contains(PayeeBankAccount/BankAddress/Country,'BR')) and 
	               not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country) and
	               not(string(Payee/TaxRegistrationNumber) = '') and not(string(PaymentReason/Meaning) = '') and not(string(Payee/ContactInfo/ContactLocators/PhoneNumber) = '')">
													<Ustrd>
														<xsl:value-of select="substring(concat($Unstr6,',','Tax ID',' ',Payee/TaxRegistrationNumber,',' ,Payee/ContactInfo/ContactLocators/PhoneNumber),1,140)"/>
													</Ustrd>
												</xsl:when>
												<xsl:when test="(not(PayeeBankAccount/BankAddress/Country = '') and $svlvl = 'URGP') and
	              (contains(PayeeBankAccount/BankAddress/Country,'CL')) and 
	               not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country) and
	               not(string(Payee/TaxRegistrationNumber) = '') and not(string(PaymentReason/Meaning) = '') and not(string(Payee/ContactInfo/ContactLocators/PhoneNumber) = '')">
													<Ustrd>
														<xsl:value-of select="substring(concat($Unstr6,',','RUT',' ',Payee/TaxRegistrationNumber,',', Payee/ContactInfo/ContactLocators/PhoneNumber),1,140)"/>
													</Ustrd>
												</xsl:when>
												<xsl:when test="(not(PayeeBankAccount/BankAddress/Country = '') and $svlvl = 'URGP') and
	              (contains($Countries_4,PayeeBankAccount/BankAddress/Country)) and 
	               not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country) and
	               not(string(Payee/TaxRegistrationNumber) = '') and not(string(PaymentReason/Meaning) = '')">
													<Ustrd>
														<xsl:value-of select="substring(concat($Unstr6,',','Tax ID',' ',Payee/TaxRegistrationNumber),1,140)"/>
													</Ustrd>
												</xsl:when>
												<xsl:when test="(not(PayeeBankAccount/BankAddress/Country = '') and $svlvl = 'URGP') and
	              (contains(PayeeBankAccount/BankAddress/Country,'PE')) and (string(Payee/TaxOrganizationType/Code) = 'CORPORATION')and not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country) and not(string(Payee/TaxRegistrationNumber) = '') and not(string(PaymentReason/Meaning) = '')">
													<Ustrd>
														<xsl:value-of select="substring(concat($Unstr6,',','Tax ID',' ',Payee/TaxRegistrationNumber),1,140)"/>
													</Ustrd>
												</xsl:when>
												<xsl:when test="(not(PayeeBankAccount/BankAddress/Country = '') and $svlvl = 'URGP') and
	              (contains(PayeeBankAccount/BankAddress/Country,'AE')) and (string(Payee/TaxOrganizationType/Code)= 'CORPORATION') and not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country) and not(string(Payee/TaxRegistrationNumber) = '') and not(string(PaymentReason/Code) = '')">
													<Ustrd>
														<xsl:value-of select="substring(concat(PaymentReason/Code,',','Tax ID',' ',Payee/TaxRegistrationNumber),1,140)"/>
													</Ustrd>
												</xsl:when>
												<xsl:when test="(not(PayeeBankAccount/BankAddress/Country = '') and $svlvl = 'URGP') and
	              (contains(PayeeBankAccount/BankAddress/Country,'GY')) and 
	               not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country) and
	               not(string(PayeeBankAccount/SwiftCode) = '') and not(string(PaymentReason/Meaning) = '')">
													<Ustrd>
														<xsl:value-of select="substring(PayeeBankAccount/SwiftCode,1,140)"/>
													</Ustrd>
													<Ustrd>
														<xsl:value-of select="substring(PaymentReason/Meaning,1,140)"/>
													</Ustrd>
												</xsl:when>
												<xsl:when test="(not(PayeeBankAccount/BankAddress/Country = '') and $svlvl = 'URGP') and
	              (contains(PayeeBankAccount/BankAddress/Country,'HN')) and 
	               not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country) and
	               not(string(Payee/TaxRegistrationNumber) = '') and not(string(PaymentReason/Meaning) = '')
	               and not(string(PayeeBankAccount/BankAccountType/Code) = '')">
													<Ustrd>
														<xsl:value-of select="substring(concat($Unstr6,',','Tax ID',' ',Payee/TaxRegistrationNumber,',',PayeeBankAccount/BankAccountType/Code),1,140)"/>
													</Ustrd>
												</xsl:when>
												<xsl:when test="(not(PayeeBankAccount/BankAddress/Country = '') and $svlvl = 'URGP') and
	              (contains(PayeeBankAccount/BankAddress/Country,'ID')) and 
	               not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country) and
	               (string(PaymentReason/Code) = '1011' or string(PaymentReason/Code) = '1012') and not(string(PaymentReason/Meaning) = '') and PaymentAmount/Value &gt; 10000">
													<Ustrd>
													   <xsl:variable name="ustrdDocReferenceNumber">
													   <xsl:for-each select="DocumentPayable">
													   <xsl:value-of select="DocumentNumber/ReferenceNumber"/>
													   </xsl:for-each> 
													   </xsl:variable>
													   <xsl:variable name="ustrdDocTotalValue">
													   <xsl:for-each select="DocumentPayable">
													   <xsl:value-of select="TotalDocumentAmount/Value"/>
													   </xsl:for-each> 
													   </xsl:variable>
														<xsl:value-of select="substring(concat('//',$Unstr6,'//','[ ',$ustrdDocReferenceNumber,' ',$ustrdDocTotalValue,' ]','//'),1,140)"/>
													</Ustrd>
												</xsl:when>
												<xsl:when test="(not(PayeeBankAccount/BankAddress/Country = '') and $svlvl = 'URGP') and
	              (contains(PayeeBankAccount/BankAddress/Country,'MG')) and 
	               not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country) and
	               not(string(Payee/ContactInfo/ContactLocators/PhoneNumber) = '') and not(string(PaymentReason/Meaning) = '')">
													<Ustrd>
														<xsl:value-of select="substring(concat($Unstr6,', ',Payee/ContactInfo/ContactLocators/PhoneNumber),1,140)"/>
													</Ustrd>
												</xsl:when>
												<xsl:when test="(not(PayeeBankAccount/BankAddress/Country = '') and $svlvl = 'URGP') and
	              (contains(PayeeBankAccount/BankAddress/Country,'MZ')) and 
	               not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country) and
	               not(string(Payee/TaxRegistrationNumber) = '') and not(string(PaymentReason/Meaning) = '')">
													<Ustrd>
														<xsl:value-of select="substring(PaymentReason/Meaning,1,140)"/>
													</Ustrd>
													<Ustrd>
														<xsl:value-of select="substring(Payee/TaxRegistrationNumber,1,140)"/>
													</Ustrd>
												</xsl:when>
												<xsl:when test="(not(PayeeBankAccount/BankAddress/Country = '') and $svlvl = 'URGP') and
	              (contains(PayeeBankAccount/BankAddress/Country,'MM')) and 
	               not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country) and
	               not(string(PaymentReason/Code) = '') and not(string(PaymentReason/Meaning) = '') and PaymentAmount/Currency/Code = 'MMK' ">
													<Ustrd>
														<xsl:value-of select="substring(concat($Unstr6,', ','ITRS ',PaymentReason/Code),1,140)"/>
													</Ustrd>
												</xsl:when>
												<xsl:when test="(not(PayeeBankAccount/BankAddress/Country = '') and $svlvl = 'URGP') and
	              (contains(PayeeBankAccount/BankAddress/Country,'PK')) and 
	               not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country) and
	               not(string(Payee/TaxRegistrationNumber) = '') and not(string(PaymentReason/Meaning) = '') and not(string(Payer/TaxRegistrationNumber) = '')">
													<Ustrd>
														<xsl:value-of select="substring(concat($Unstr6,', ',Payer/TaxRegistrationNumber,', ',Payee/TaxRegistrationNumber),1,140)"/>
													</Ustrd>
												</xsl:when>
												<xsl:when test="(not(PayeeBankAccount/BankAddress/Country = '') and $svlvl = 'URGP') and
	              (contains(PayeeBankAccount/BankAddress/Country,'PH')) and 
	               not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country) and not(string(PaymentReason/Code) = '')">
													<Ustrd>
														<xsl:value-of select="substring(PaymentReason/Code,1,140)"/>
													</Ustrd>
												</xsl:when>
												<xsl:when test="(not(PayeeBankAccount/BankAddress/Country = '') and $svlvl = 'URGP') and
	              (contains(PayeeBankAccount/BankAddress/Country,'RU')) and 
	               not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country) and not(string(PaymentReason/Code) = '')">
													<Ustrd>
														<xsl:value-of select="substring(concat('VO',PaymentReason/Code),1,140)"/>
													</Ustrd>
												</xsl:when>
												<xsl:when test="(not(PayeeBankAccount/BankAddress/Country = '') and $svlvl = 'URGP') and
	              (contains(PayeeBankAccount/BankAddress/Country,'VN')) and 
	               not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country) and not(string(PaymentReason/Meaning) = '')">
													<Ustrd>
														<xsl:value-of select="substring(PaymentReason/Meaning,1,140)"/>
													</Ustrd>
												</xsl:when>
											</xsl:choose>
											<xsl:if test="(not($Unstr4=&#39;&#39;) and not($dlvrchnlcodeUnStrd=&#39;CCD&#39;)and not($dlvrchnlcodeUnStrd=&#39;PPD&#39;) and not($dlvrchnlcodeh=&#39;CTX&#39;)) and ($dlvrchnlcodeUnStrd=&#39;CCD+&#39;) or ($dlvrchnlcodeUnStrd=&#39;PPD+&#39;) or ($dlvrchnlcodeUnStrd=&#39;IAT&#39;)">
												<Ustrd>
													<xsl:choose>
														<xsl:when test="($dlvrchnlcodeUnStrd=&#39;CCD+&#39;) or ($dlvrchnlcodeUnStrd=&#39;PPD+&#39;)">
															<xsl:value-of select="substring($Unstr4,1,71)"/>
														</xsl:when>
													</xsl:choose>
													<xsl:choose>
														<xsl:when test="($dlvrchnlcodeUnStrd=&#39;IAT&#39;)">
															<xsl:value-of select="substring($Unstr4,1,140)"/>
														</xsl:when>
													</xsl:choose>
												</Ustrd>
											</xsl:if>
											<xsl:if test="BankAccount/BankAddress/Country=&#39;US&#39; and translate ($dlvrchnlcode,$lower,$upper)=&#39;CQP&#39; and not($DocDescrptn=&#39;&#39;)">
												<Strd>
													<AddtlRmtInf>
														<xsl:value-of select="substring($DocDescrptn,1,140)"/>
													</AddtlRmtInf>
												</Strd>
											</xsl:if>
											<xsl:if test="Payer/Address/Country=&#39;DK&#39; and $svlvl1=&#39;NURG&#39; and not($dlvrchnlcode=&#39;&#39;) ">
												<Strd>
													<xsl:if test="($dlvrchnlcode=&#39;01&#39; or $dlvrchnlcode=&#39;04&#39;
	or $dlvrchnlcode=&#39;15&#39;
	or $dlvrchnlcode=&#39;71&#39;
	or $dlvrchnlcode=&#39;73&#39;
	or $dlvrchnlcode=&#39;75&#39; )">
														<CdtrRefInf>
															<Tp>
																<CdOrPrtry>
																	<Cd>PUOR</Cd>
																</CdOrPrtry>
															</Tp>
															<Ref>
																<xsl:value-of select="$DKGIKFIKREF1"/>
															</Ref>
														</CdtrRefInf>
													</xsl:if>
												</Strd>
											</xsl:if>
											<xsl:if test="BankAccount/BankAddress/Country=&#39;US&#39; and  translate ($pmtrsncode,$lower,$upper)=&#39;AUTO DEALER TRANSACTION&#39;  and (not($AutoDealerVT=&#39;&#39;) or not($AutoDealerIV=&#39;&#39;) or not($AutoDealerIT=&#39;&#39;))">
												<Strd>
													<xsl:if test="not($AutoDealerVT=&#39;&#39;)">
														<RfrdDocInf>
															<Tp>
																<CdOrPrtry>
																	<Prtry>VT</Prtry>
																</CdOrPrtry>
															</Tp>
															<Nb>
																<xsl:value-of select="$AutoDealerVT"/>
															</Nb>
														</RfrdDocInf>
													</xsl:if>
													<xsl:if test="not($AutoDealerIV=&#39;&#39;)">
														<RfrdDocInf>
															<Tp>
																<CdOrPrtry>
																	<Prtry>IV</Prtry>
																</CdOrPrtry>
															</Tp>
															<Nb>
																<xsl:value-of select="$AutoDealerIV"/>
															</Nb>
														</RfrdDocInf>
													</xsl:if>
													<xsl:if test="not($AutoDealerIT=&#39;&#39;)">
														<RfrdDocInf>
															<Tp>
																<CdOrPrtry>
																	<Prtry>IT</Prtry>
																</CdOrPrtry>
															</Tp>
															<Nb>
																<xsl:value-of select="$AutoDealerIT"/>
															</Nb>
														</RfrdDocInf>
													</xsl:if>
												</Strd>
											</xsl:if>
											<xsl:for-each select="DocumentPayable">
												<xsl:if test="not(translate ($dlvrchnlcode,$lower,$upper)=&#39;CQP&#39;) and not(translate ($pmtrsncode,$lower,$upper)=&#39;AUTO DEALER TRANSACTION&#39;) and (translate($dlvrchnlcode,$lower,$upper)='CTX' or translate($dlvrchnlcode,$lower,$upper)='CCD+' or translate($dlvrchnlcode,$lower,$upper)='PPD+' or translate($pmthd1,$lower,$upper) ='CHK')">
													<Strd>
														<RfrdDocInf>
															<Tp>
																<CdOrPrtry>
																	<xsl:choose>
																		<xsl:when test="TotalDocumentAmount/Value &gt;= 0">
																			<Cd>CINV</Cd>
																		</xsl:when>
																		<xsl:otherwise>
																			<Cd>CREN</Cd>
																		</xsl:otherwise>
																	</xsl:choose>
																</CdOrPrtry>
															</Tp>
															<xsl:if test="not(string(DocumentNumber/ReferenceNumber)=&#39;&#39;)">
																<Nb>
																	<xsl:value-of select="substring(DocumentNumber/ReferenceNumber,1,35)"/>
																</Nb>
															</xsl:if>
															<xsl:if test="not(DocumentDate=&#39;&#39;)">
																<RltdDt>
																	<xsl:value-of select="DocumentDate"/>
																</RltdDt>
															</xsl:if>
														</RfrdDocInf>
														<RfrdDocAmt>
															<xsl:if test="TotalDocumentAmount/Value &gt; 0">
																<DuePyblAmt>
																	<xsl:attribute name="Ccy">
																		<xsl:value-of select="TotalDocumentAmount/Currency/Code"/>
																	</xsl:attribute>
																	<xsl:value-of select="format-number(TotalDocumentAmount/Value, &#39;##0.00&#39;)"/>
																</DuePyblAmt>
															</xsl:if>
															<xsl:if test="DiscountTaken/Amount/Value &gt; 0">
																<DscntApldAmt>
																	<xsl:attribute name="Ccy">
																		<xsl:value-of select="DiscountTaken/Amount/Currency/Code[1]"/>
																	</xsl:attribute>
																	<xsl:value-of select="format-number(DiscountTaken/Amount/Value, &#39;##0.00&#39;)"/>
																</DscntApldAmt>
															</xsl:if>
															<xsl:if test="TotalDocumentAmount/Value &lt; 0">
																<CdtNoteAmt>
																	<xsl:attribute name="Ccy">
																		<xsl:value-of select="TotalDocumentAmount/Currency/Code"/>
																	</xsl:attribute>
																	<xsl:value-of select="translate(format-number(TotalDocumentAmount/Value, &#39;##0.00&#39;),&#39;-&#39;,&#39;&#39;)"/>
																</CdtNoteAmt>
															</xsl:if>
                                                            <xsl:if test="AmountWithheld/Value &gt; 0">
															     <TaxAmt>
                                                                   <xsl:attribute name="Ccy">
																	 <xsl:value-of select="AmountWithheld/Currency/Code"/>
																	</xsl:attribute>
																	<xsl:value-of select="translate(format-number(AmountWithheld/Value, &#39;##0.00&#39;),'-','')"/>
																 </TaxAmt>
															</xsl:if>	
															<xsl:if test="PaymentAmount/Value &gt;= 0">
															<RmtdAmt>
																<xsl:attribute name="Ccy">
																	<xsl:value-of select="PaymentAmount/Currency/Code[1]"/>
																</xsl:attribute>
																<xsl:value-of select="translate(format-number(PaymentAmount/Value, &#39;##0.00&#39;),&#39;-&#39;,&#39;&#39;)"/>
															</RmtdAmt>
														</xsl:if>
														</RfrdDocAmt>
														<xsl:choose>
															<xsl:when test="$PayerBankCountry =&#39;US&#39; and not(string(PONumber) = &#39;UNMATCHED&#39;) and (not(string(PONumber)=&#39;&#39;))">
																<xsl:choose>
																	<xsl:when test="not(string(PONumber)=&#39;&#39;) and $dlvrchnlcode=&#39;CTX&#39;">
																		<CdtrRefInf>
																			<Tp>
																				<CdOrPrtry>
																					<Prtry>PO</Prtry>
																				</CdOrPrtry>
																			</Tp>
																			<Ref>
																				<xsl:value-of select="PONumber"/>
																			</Ref>
																		</CdtrRefInf>
																	</xsl:when>
																	<xsl:when test="not(string(PONumber)=&#39;&#39;) and starts-with($dlvrchnlcode,&#39;SUA&#39;) ">
																		<CdtrRefInf>
																			<Tp>
																				<CdOrPrtry>
																					<Cd>PUOR</Cd>
																				</CdOrPrtry>
																			</Tp>
																			<Ref>
																				<xsl:value-of select="PONumber"/>
																			</Ref>
																		</CdtrRefInf>
																	</xsl:when>
																</xsl:choose>
															</xsl:when>
															<xsl:otherwise>
																<CdtrRefInf>
																	<xsl:if test="not(string($pmthd1)='CHK')">
																		<Tp>
																			<CdOrPrtry>
																				<Cd>PUOR</Cd>
																			</CdOrPrtry>
																		</Tp>
																	</xsl:if>
																	<xsl:choose>
																		<xsl:when test="not(DocumentNumber/UniqueRemittanceIdentifier/Number=&#39;&#39;)">
																			<Ref>
																				<xsl:value-of select="DocumentNumber/UniqueRemittanceIdentifier/Number"/>
																			</Ref>
																		</xsl:when>
																		<xsl:otherwise>
																			<Ref>
																				<xsl:value-of select="substring(DocumentNumber/ReferenceNumber,1,35)"/>
																			</Ref>
																		</xsl:otherwise>
																	</xsl:choose>
																</CdtrRefInf>
															</xsl:otherwise>
														</xsl:choose>
														<xsl:variable name="Adjamnt" select="format-number(sum(DocumentPayableLine[(not(LineType/Code =&#39;TAX&#39;) and not(LineType/Code =&#39;ITEM&#39;))]/LineGrossAmount/Value), &#39;##0.00&#39;)"/>
														<xsl:variable name="Adjustment">
															<xsl:choose>
																<xsl:when test="not($Adjamnt = &#39;0.00&#39;) ">
																	<xsl:value-of select="concat(&#39;Other Items &#39;,string($Adjamnt))"/>
																</xsl:when>
																<xsl:otherwise>
																	<xsl:value-of select="&#39;&#39;"/>
																</xsl:otherwise>
															</xsl:choose>
														</xsl:variable>
														<xsl:if test="not(DocumentDescription=&#39;&#39;)">
															<AddtlRmtInf>
																<xsl:value-of select="substring(DocumentDescription,1,140)"/>
															</AddtlRmtInf>
														</xsl:if>
													</Strd>
												</xsl:if>
											</xsl:for-each>
										</RmtInf>
									</CdtTrfTxInf>
								</xsl:when>
							</xsl:choose>
						</xsl:for-each>
					</PmtInf>
				</xsl:for-each>
			</CstmrCdtTrfInitn>
		</Document>
	</xsl:template>
</xsl:stylesheet>	
