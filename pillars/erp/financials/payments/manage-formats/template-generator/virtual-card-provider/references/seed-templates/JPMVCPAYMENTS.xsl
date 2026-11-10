<?xml version="1.0" encoding="UTF-8"?>
<!-- $Header: fusionapps/fin/iby/bipub/shared/runFormat/reports/DisbursementPaymentFileFormats/JPMVCPAYMENTS.xsl /st_fusionapps_pt-v2mibfphdev/4 2025/04/08 21:46:32 konkisho Exp $ -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
<xsl:key name="contacts-by-LogicalGroupReference" match="OutboundPayment" use="LogicalGrouping/LogicalGroupReference"/>
<xsl:template match="OutboundPaymentInstruction">
	<xsl:variable name="lower" select="&#39;abcdefghijklmnopqrstuvwxyz&#39;"/>
	<xsl:variable name="upper" select="&#39;ABCDEFGHIJKLMNOPQRSTUVWXYZ&#39;"/>
	<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
		<xsl:variable name="instrid" select="PaymentInstructionInfo/InstructionReferenceNumber"/>
		<CstmrCdtTrfInitn>
			<GrpHdr>
				<MsgId>
					<xsl:value-of select="$instrid"/>
				</MsgId>
				<CreDtTm>
					<xsl:choose>
						<xsl:when test="contains(PaymentInstructionInfo/InstructionCreationDate , '+')">
							<xsl:value-of select="substring(PaymentInstructionInfo/InstructionCreationDate , 1,	string-length(PaymentInstructionInfo/InstructionCreationDate)-6)"/>
						</xsl:when>
						<xsl:otherwise>
							<xsl:value-of select="PaymentInstructionInfo/InstructionCreationDate"/>
						</xsl:otherwise>
					</xsl:choose>
				</CreDtTm>
				<xsl:if test="not(string(InstructionTotals/PaymentCount)='')">
					<NbOfTxs>
						<xsl:value-of select="InstructionTotals/PaymentCount"/>
					</NbOfTxs>
				</xsl:if>
				<xsl:if test="not(string(OutboundPayment/PaymentAmount/Value)='')">
					<CtrlSum>
						<xsl:value-of select="format-number(sum(OutboundPayment/PaymentAmount/Value), '##0.00')"/>
					</CtrlSum>
				</xsl:if>
				<InitgPty>
					<Nm>
						<xsl:choose>
							<xsl:when test="(PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,'ISO20022_IP_NAME')]/Value) and (PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,'ISO20022_IP_NAME')]/Value) != ''">
								<xsl:value-of select="substring(PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,&#39;ISO20022_IP_NAME&#39;)]/Value,1,140)"/>
							</xsl:when>
							<xsl:when test="(PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,'CGI_INITIATING_PARTY_NAME')]/Value) and (PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[contains(Name,'CGI_INITIATING_PARTY_NAME')]/Value) != ''">
								<xsl:value-of select="substring(PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[Name=&#39;CGI_INITIATING_PARTY_NAME&#39;]/Value,1,140)"/>
							</xsl:when>
							<xsl:otherwise>
								<xsl:value-of select="substring(InstructionGrouping/Payer/LegalEntityName,1,140)"/>
							</xsl:otherwise>
						</xsl:choose>
					</Nm>
					<Id>
						<OrgId>
							<Othr>
								<Id>
									<xsl:value-of select="OutboundPayment/CardProgramDetails/ExtCompanyId"/>
								</Id>
								<SchmeNm>
									<Cd>CUST</Cd>
								</SchmeNm>
							</Othr>
						</OrgId>
					</Id>
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
					<PmtMtd>
						<xsl:value-of select="PaymentMethod/PaymentMethodFormatValue"/>
					</PmtMtd>
					<PmtTpInf>
						<SvcLvl>
							<Cd>
								<xsl:value-of select="ServiceLevel/FormatValue"/>
							</Cd>
						</SvcLvl>
						<LclInstrm>
							<Prtry>
								<xsl:value-of select="CardProgramDetails/ExtMCCGroupCode"/>
							</Prtry>
						</LclInstrm>
						<CtgyPurp>
							<Cd>CCRD</Cd>
						</CtgyPurp>
					</PmtTpInf>
					<ReqdExctnDt>
						<xsl:value-of select="PaymentDate"/>
					</ReqdExctnDt>
					<Dbtr>
						<xsl:choose>
							<xsl:when test="(/OutboundPaymentInstruction/PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[Name=&#39;DEBTOR_NAME&#39;]/Value  != &#39;&#39;)">
								<Nm>
									<xsl:value-of select="substring(/OutboundPaymentInstruction/PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[Name=&#39;DEBTOR_NAME&#39;]/Value,1,140)"/>
								</Nm>
							</xsl:when>
							<xsl:otherwise>
								<xsl:if test="not(string(Payer/Name)=&#39;&#39;)">
									<Nm>
										<xsl:value-of select="substring(Payer/Name,1,140)"/>
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
					</Dbtr>
					<DbtrAcct>
						<Id>
							<Othr>
								<Id>
									<xsl:value-of select="substring(PaymentInstrument/NetworkInstrumentIdentifier,1,25)"/>
								</Id>
							</Othr>
						</Id>
						<Tp>
							<Prtry>Yes</Prtry>
						</Tp>
						<Ccy>
							<xsl:value-of select="PaymentInstrument/PaymentInstrumentCurrency/Code"/>
						</Ccy>
					</DbtrAcct>
					<DbtrAgt>
						<FinInstnId>
							<BIC>CHASUS33</BIC>
							<PstlAdr>
								<Ctry>
									<xsl:value-of select="PaymentInstrument/BankDetails/BankCountry"/>
								</Ctry>
							</PstlAdr>
						</FinInstnId>
					</DbtrAgt>
					<xsl:for-each select="key(&#39;contacts-by-LogicalGroupReference&#39;, LogicalGrouping/LogicalGroupReference)">
						<CdtTrfTxInf>
							<PmtId>
								<EndToEndId>
									<xsl:value-of select="PaymentNumber/PaymentReferenceNumber"/>
								</EndToEndId>
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
							<xsl:choose>
								<xsl:when test="(DigitalPaymentAccount/PayeeVCAttributes/VCRegisteredSupplier= 'REGISTERED') or (DigitalPaymentAccount/PayeeVCAttributes/VCRegisteredSupplier= 'REGISTERED_STP')">
									<Cdtr>
										<Nm>
											<xsl:value-of select="substring(Payee/Name,1,70)"/>
										</Nm>
										<Id>
											<OrgId>
												<Othr>
													<Id>
														<xsl:value-of select="DigitalPaymentAccount/PayeeVCAttributes/VendorId"/>
													</Id>
													<SchmeNm>
														<Prtry>1</Prtry>
													</SchmeNm>
												</Othr>
												<Othr>
													<Id>
														<xsl:value-of select="DigitalPaymentAccount/PayeeVCAttributes/PartySiteId"/>
													</Id>
													<SchmeNm>
														<Prtry>2</Prtry>
													</SchmeNm>
												</Othr>
												<Othr>
													<Id>
														<xsl:value-of select="DigitalPaymentAccount/PayeeVCAttributes/SiteId"/>
													</Id>
													<SchmeNm>
														<Prtry>3</Prtry>
													</SchmeNm>
												</Othr>
											</OrgId>
										</Id>
									</Cdtr>
								</xsl:when>
								<xsl:otherwise>
									<Cdtr>
										<Nm>
											<xsl:value-of select="substring(Payee/Name,1,70)"/>
										</Nm>
										<PstlAdr>
											<Ctry>
												<xsl:value-of select="Payee/Address/Country"/>
											</Ctry>
										</PstlAdr>
										<xsl:variable name="EmailSeparator" select="';'"/>
										<xsl:variable name="SupplierEmail1">
											<xsl:if test="not(DigitalPaymentAccount/Alias=&#39;&#39;)">
												<xsl:value-of select="DigitalPaymentAccount/Alias"/>
											</xsl:if>
										</xsl:variable>
										<xsl:variable name="SupplierEmail2">
											<xsl:choose>
												<xsl:when test="not(DigitalPaymentAccount/PayeeVCAttributes/Alias2=&#39;&#39;)">
													<xsl:value-of select="concat($EmailSeparator,DigitalPaymentAccount/PayeeVCAttributes/Alias2)"/>
												</xsl:when>
												<xsl:otherwise>
													<xsl:value-of select="&#39;&#39;"/>
												</xsl:otherwise>
											</xsl:choose>
										</xsl:variable>
										<xsl:variable name="SupplierEmail3">
											<xsl:choose>
												<xsl:when test="not(DigitalPaymentAccount/PayeeVCAttributes/Alias3=&#39;&#39;)">
													<xsl:value-of select="concat($EmailSeparator,DigitalPaymentAccount/PayeeVCAttributes/Alias3)"/>
												</xsl:when>
												<xsl:otherwise>
													<xsl:value-of select="&#39;&#39;"/>
												</xsl:otherwise>
											</xsl:choose>
										</xsl:variable>
										<xsl:variable name="SupplierEmail4">
											<xsl:choose>
												<xsl:when test="not(DigitalPaymentAccount/PayeeVCAttributes/Alias4=&#39;&#39;)">
													<xsl:value-of select="concat($EmailSeparator,DigitalPaymentAccount/PayeeVCAttributes/Alias4)"/>
												</xsl:when>
												<xsl:otherwise>
													<xsl:value-of select="&#39;&#39;"/>
												</xsl:otherwise>
											</xsl:choose>
										</xsl:variable>
										<xsl:variable name="SupplierEmail5">
											<xsl:choose>
												<xsl:when test="not(DigitalPaymentAccount/PayeeVCAttributes/Alias5=&#39;&#39;)">
													<xsl:value-of select="concat($EmailSeparator,DigitalPaymentAccount/PayeeVCAttributes/Alias5)"/>
												</xsl:when>
												<xsl:otherwise>
													<xsl:value-of select="&#39;&#39;"/>
												</xsl:otherwise>
											</xsl:choose>
										</xsl:variable>
										<CtctDtls>
											<EmailAdr>
												<xsl:value-of select="concat($SupplierEmail1,$SupplierEmail2,$SupplierEmail3,$SupplierEmail4,$SupplierEmail5)"/>
											</EmailAdr>
										</CtctDtls>
									</Cdtr>
								</xsl:otherwise>
							</xsl:choose>
							<RmtInf>
								<xsl:variable name="customdatafieldname" select="concat('PAYMENT_REF_NUM','|')"/>
								<xsl:variable name="customdatafieldvalue" select="PaymentNumber/PaymentReferenceNumber"/>
								<xsl:variable name="customdatastring" select="concat('CFT','|')"/>
								<xsl:variable name="customdatastring2">
									<xsl:value-of select="concat($customdatastring,$customdatafieldname)"/>
								</xsl:variable>
								<xsl:variable name="customdatastring3">
									<xsl:value-of select="concat($customdatastring2,$customdatafieldvalue)"/>
								</xsl:variable>
								<Ustrd>
									<xsl:value-of select="$customdatastring3"/>
								</Ustrd>
								<xsl:for-each select="DocumentPayable">
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
													<xsl:value-of select="format-number(TotalDocumentAmount/Value, '##0.00')"/>
												</DuePyblAmt>
											</xsl:if>
											<xsl:if test="DiscountTaken/Amount/Value &gt; 0">
												<DscntApldAmt>
													<xsl:attribute name="Ccy">
														<xsl:value-of select="DiscountTaken/Amount/Currency/Code"/>
													</xsl:attribute>
													<xsl:value-of select="format-number(DiscountTaken/Amount/Value, '##0.00')"/>
												</DscntApldAmt>
											</xsl:if>
											<xsl:if test="TotalDocumentAmount/Value &lt; 0">
												<CdtNoteAmt>
													<xsl:attribute name="Ccy">
														<xsl:value-of select="TotalDocumentAmount/Currency/Code"/>
													</xsl:attribute>
													<xsl:value-of select="translate(format-number(TotalDocumentAmount/Value, '##0.00'),'-','')"/>
												</CdtNoteAmt>
											</xsl:if>
											<RmtdAmt>
												<xsl:attribute name="Ccy">
													<xsl:value-of select="PaymentAmount/Currency/Code"/>
												</xsl:attribute>
												<xsl:value-of select="translate(format-number(PaymentAmount/Value,'##0.00'),'-','')"/>
											</RmtdAmt>
										</RfrdDocAmt>
										<xsl:if test="not(DocumentPayableLine/PONumber=&#39;&#39;)">
											<CdtrRefInf>
												<Tp>
													<CdOrPrtry>
														<Cd>PUOR</Cd>
													</CdOrPrtry>
												</Tp>
												<Ref>
													<xsl:value-of select="substring(DocumentPayableLine/PONumber,1,35)"/>
												</Ref>
											</CdtrRefInf>
										</xsl:if>
										<xsl:if test="not(RemittanceMessage[1] = &#39;&#39;)">
											<AddtlRmtInf>
												<xsl:value-of select="substring(RemittanceMessage[1],1,140)"/>
											</AddtlRmtInf>
										</xsl:if>
										<xsl:if test="not(RemittanceMessage[2] = &#39;&#39;)">
											<AddtlRmtInf>
												<xsl:value-of select="substring(RemittanceMessage[2],1,140)"/>
											</AddtlRmtInf>
										</xsl:if>
										<xsl:if test="not(RemittanceMessage[3] = &#39;&#39;)">
											<AddtlRmtInf>
												<xsl:value-of select="substring(RemittanceMessage[3],1,140)"/>
											</AddtlRmtInf>
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
