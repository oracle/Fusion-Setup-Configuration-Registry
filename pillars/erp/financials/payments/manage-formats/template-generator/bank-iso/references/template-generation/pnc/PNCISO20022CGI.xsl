<?xml version="1.0" encoding="UTF-8"?>
<!-- $Header: fusionapps/fin/iby/bipub/shared/runFormat/reports/DisbursementPaymentFileFormats/PNCISO20022CGI.xsl /st_fusionapps_pt-v2mibfphdev/5 2025/12/12 15:29:53 subachu Exp $ -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
	<xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>
	<xsl:key name="contacts-by-LogicalGroupReference" match="OutboundPayment" use="LogicalGrouping/LogicalGroupReference"/>
	<xsl:template match="OutboundPaymentInstruction">
		<xsl:variable name="lower" select="&#39;abcdefghijklmnopqrstuvwxyz&#39;"/>
		<xsl:variable name="upper" select="&#39;ABCDEFGHIJKLMNOPQRSTUVWXYZ&#39;"/>
		<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03"
			xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
			<xsl:variable name="instrid" select="PaymentInstructionInfo/InstructionReferenceNumber"/>
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
							<xsl:when test="contains(PaymentInstructionInfo/InstructionCreationDate , '+')">
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
							<xsl:value-of select="format-number(sum(OutboundPayment/PaymentAmount/Value), '##0.00')"/>
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
						<Id>
							<OrgId>
								<Othr>
									<xsl:if test="not(string(InstructionGrouping/BankAccount/EFTUserNumber/EFTRequesterId)=&#39;&#39;)">
										<Id>
											<xsl:value-of select="InstructionGrouping/BankAccount/EFTUserNumber/EFTRequesterId"/>
										</Id>
									</xsl:if>
									<SchmeNm>
										<Prtry>AP0</Prtry>
									</SchmeNm>
								</Othr>
							</OrgId>
						</Id>
					</InitgPty>
				</GrpHdr>
				<xsl:for-each select="OutboundPayment[count(. | key('contacts-by-LogicalGroupReference', LogicalGrouping/LogicalGroupReference)[1]) = 1]">
					<xsl:sort select="LogicalGrouping/LogicalGroupReference"/>
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
								</xsl:choose>
							</xsl:otherwise>
						</xsl:choose>
					</xsl:variable>

					<xsl:variable name="PhoneNumber">
						<xsl:choose>
							<xsl:when test="not(string(Payee/ContactInfo/ContactLocators/PhoneNumber)=&#39;&#39;) ">
								<xsl:value-of select="Payee/ContactInfo/ContactLocators/PhoneNumber"/>
							</xsl:when>
						</xsl:choose>
					</xsl:variable>

					<!--Start of payment information block-->
					<PmtInf>
						<xsl:if test="not(LogicalGrouping/LogicalGroupReference='')">
							<PmtInfId>
								<xsl:value-of select="LogicalGrouping/LogicalGroupReference"/>
							</PmtInfId>
						</xsl:if>
						<xsl:if test="not(PaymentMethod/PaymentMethodFormatValue='')">
							<PmtMtd>
								<xsl:value-of select="PaymentMethod/PaymentMethodFormatValue"/>
							</PmtMtd>
						</xsl:if>
						<!-- get from new logical table instead -->
						<NbOfTxs>
							<xsl:value-of select="LogicalGrouping/PaymentInformationTotal"/>
						</NbOfTxs>
						<CtrlSum>
							<xsl:value-of select="format-number(LogicalGrouping/PaymentInformationAmountTotal, '##0.00')"/>
						</CtrlSum>
						<!--Start of payment type information block-->
						<xsl:if test="not(ServiceLevel/Code='')">
							<PmtTpInf>
								<SvcLvl>
									<Cd>
										<xsl:value-of select="ServiceLevel/Code"/>
									</Cd>
								</SvcLvl>
							</PmtTpInf>
						</xsl:if>
						<!--End of payment type information block-->
						<ReqdExctnDt>
							<xsl:value-of select="PaymentDate"/>
						</ReqdExctnDt>
						<Dbtr>
							<xsl:choose>
								<xsl:when test="(/OutboundPaymentInstruction/PaymentInstructionInfo/PaymentSystemAccount/AccountSettings[Name=&#39;DEBTOR_NAME&#39;]/Value!= &#39;&#39;)">
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
						</Dbtr>
						<DbtrAcct>
							<Id>
								<Othr>
									<Id>
										<xsl:value-of select="BankAccount/BankAccountNumber"/>
									</Id>
								</Othr>
							</Id>
						</DbtrAcct>
						<DbtrAgt>
							<FinInstnId>
								<Nm>
									<xsl:value-of select="BankAccount/BankName"/>
								</Nm>
							</FinInstnId>
						</DbtrAgt>
						<xsl:for-each select="key('contacts-by-LogicalGroupReference', LogicalGrouping/LogicalGroupReference)">
							<!--Start of credit transaction block-->
							<CdtTrfTxInf>
								<PmtId>
									<EndToEndId>
										<xsl:value-of select="PaymentNumber/PaymentReferenceNumber"/>
									</EndToEndId>
								</PmtId>
								<!--Start of payment type information block-->
								<PmtTpInf>
									<xsl:if test="(PaymentMethod/PaymentMethodFormatValue='TRF') and (ServiceLevel/FormatValue='NURG') ">
										<LclInstrm>
											<xsl:choose>
												<xsl:when test="not(DeliveryChannel/FormatValue='')">
													<Cd>
														<xsl:value-of select="DeliveryChannel/FormatValue"/>
													</Cd>
												</xsl:when>
												<xsl:when test="not(DocumentPayable[1]/DeliveryChannel/FormatValue='')">
													<Cd>
														<xsl:value-of select="DocumentPayable[1]/DeliveryChannel/FormatValue"/>
													</Cd>
												</xsl:when>
												<xsl:when test="not(DeliveryChannel/Code='')">
													<Cd>
														<xsl:value-of select="DeliveryChannel/Code"/>
													</Cd>
												</xsl:when>
											</xsl:choose>
										</LclInstrm>
									</xsl:if>
									<xsl:choose>
										<xsl:when test="(PaymentMethod/PaymentMethodFormatValue='CHK')">
											<CtgyPurp>
												<Prtry>X</Prtry>
											</CtgyPurp>
										</xsl:when>
										<xsl:when test="(PaymentMethod/PaymentMethodFormatValue='TRF') and (ServiceLevel/FormatValue='URGP')">
											<CtgyPurp>
												<Prtry>
													<xsl:value-of select="DeliveryChannel/Code"/>
												</Prtry>
											</CtgyPurp>
										</xsl:when>
									</xsl:choose>
								</PmtTpInf>
								<!--End of payment type information block-->
								<Amt>
									<InstdAmt>
										<xsl:attribute name="Ccy">
											<xsl:value-of select="PaymentAmount/Currency/Code"/>
										</xsl:attribute>
										<xsl:value-of select="format-number(PaymentAmount/Value, '##0.00')"/>
									</InstdAmt>
								</Amt>
								<xsl:if test="(PaymentMethod/PaymentMethodFormatValue='CHK')">
									<ChqInstr>
										<xsl:if test="not(PaymentNumber/CheckNumber='')">
											<ChqNb>
												<xsl:value-of select="PaymentNumber/CheckNumber"/>
											</ChqNb>
										</xsl:if>
										<xsl:if test="(PaymentMethod/PaymentMethodFormatValue='CHK')">
											<DlvryMtd>
												<xsl:choose>
													<xsl:when test="(DeliveryChannel/Code='BM')">
														<Prtry>
															<xsl:value-of select="concat(DeliveryChannel/Code, DeliveryChannel/FormatValue)"/>
														</Prtry>
													</xsl:when>
													<xsl:otherwise>
														<Prtry>
															<xsl:value-of select="DeliveryChannel/Code"/>
														</Prtry>
													</xsl:otherwise>
												</xsl:choose>
											</DlvryMtd>
										</xsl:if>
										<xsl:if test="not(PaymentTextMessage[1]= '')">
											<MemoFld>
												<xsl:value-of select="PaymentTextMessage[1]"/>
											</MemoFld>
										</xsl:if>
									</ChqInstr>
								</xsl:if>
								<xsl:if test="(ServiceLevel/FormatValue='URGP') and ((DeliveryChannel/Code='BOP') or (DeliveryChannel/Code='FWT'))and not (string(PayeeBankAccount/IntermediaryBankAccount[1]/Country)=&#39;&#39;)">
									<IntrmyAgt1>
										<FinInstnId>
											<xsl:if test="not(string(PayeeBankAccount/IntermediaryBankAccount[1]/SwiftCode)='') and (DeliveryChannel/Code='BOP') and (ServiceLevel/FormatValue='URGP')">
												<BIC>
													<xsl:value-of select="PayeeBankAccount/IntermediaryBankAccount[1]/SwiftCode"/>
												</BIC>
											</xsl:if>
											<xsl:if test="not(PayeeBankAccount/IntermediaryBankAccount[1]/BranchNumber=&#39;&#39;) and (DeliveryChannel/Code='FWT') and (ServiceLevel/FormatValue='URGP') ">
												<ClrSysMmbId>
													<MmbId>
														<xsl:value-of select="PayeeBankAccount/IntermediaryBankAccount[1]/BranchNumber"/>
													</MmbId>
												</ClrSysMmbId>
											</xsl:if>
											<xsl:if test="not(PayeeBankAccount/IntermediaryBankAccount[1]/BankName=&#39;&#39;)">
												<Nm>
													<xsl:value-of select="PayeeBankAccount/IntermediaryBankAccount[1]/BankName"/>
												</Nm>
											</xsl:if>
											<PstlAdr>
												<xsl:if test="not(PayeeBankAccount/IntermediaryBankAccount[1]/Country=&#39;&#39;)">
													<Ctry>
														<xsl:value-of select="PayeeBankAccount/IntermediaryBankAccount[1]/Country"/>
													</Ctry>
												</xsl:if>
											</PstlAdr>
										</FinInstnId>
									</IntrmyAgt1>
								</xsl:if>
								<xsl:if test="(PaymentMethod/PaymentMethodFormatValue=&#39;TRF&#39;)">
									<CdtrAgt>
										<FinInstnId>
											<xsl:if test="not(PayeeBankAccount/SwiftCode='') and (DeliveryChannel/Code='BOP')">
												<BIC>
													<xsl:value-of select="PayeeBankAccount/SwiftCode"/>
												</BIC>
											</xsl:if>
											<xsl:if test="((DeliveryChannel/Code != 'BOP') and not(PayeeBankAccount/BranchNumber=''))">
												<ClrSysMmbId>
													<MmbId>
														<xsl:value-of select="PayeeBankAccount/BranchNumber"/>
													</MmbId>
												</ClrSysMmbId>
											</xsl:if>
											<xsl:if test="not(PayeeBankAccount/BankName='')">
												<Nm>
													<xsl:value-of select="PayeeBankAccount/BankName"/>
												</Nm>
											</xsl:if>
											<xsl:if test="not(string(PayeeBankAccount/BankAddress/Country)=&#39;&#39;) or not(string(PayeeBankAccount/BankAddress/City)=&#39;&#39;)or not(string(PayeeBankAccount/BankAddress/AddressLine1=&#39;&#39;))">
												<PstlAdr>
													<xsl:if test="not(string(PayeeBankAccount/BankAddress/Country)=&#39;&#39;)">
														<Ctry>
															<xsl:value-of select="PayeeBankAccount/BankAddress/Country"/>
														</Ctry>
													</xsl:if>
													<xsl:if test="not(string(PayeeBankAccount/BankAddress/City)=&#39;&#39;)">
														<TwnNm>
															<xsl:value-of select="PayeeBankAccount/BankAddress/City"/>
														</TwnNm>
													</xsl:if>
													<xsl:if test="not(PayeeBankAccount/BankAddress/AddressLine1=&#39;&#39;)">
														<AdrLine>
															<xsl:value-of select="PayeeBankAccount/BankAddress/AddressLine1"/>
														</AdrLine>
													</xsl:if>
												</PstlAdr>
											</xsl:if>
										</FinInstnId>
									</CdtrAgt>
								</xsl:if>
								<Cdtr>
									<xsl:if test="not(string(Payee/Name)=&#39;&#39;)">
										<Nm>
											<xsl:value-of select="substring(Payee/Name,1,70)"/>
										</Nm>
									</xsl:if>
									<PstlAdr>
										<xsl:if test="not(string(Payee/Address/PostalCode)=&#39;&#39;)">
											<PstCd>
												<xsl:value-of select="Payee/Address/PostalCode"/>
											</PstCd>
										</xsl:if>
										<xsl:if test="not(string(Payee/Address/City)=&#39;&#39;)">
											<TwnNm>
												<xsl:value-of select="Payee/Address/City"/>
											</TwnNm>
										</xsl:if>
										<xsl:if test="not(Payee/Address/State='')">
											<xsl:choose>
												<xsl:when test="(PaymentMethod/PaymentMethodFormatValue=&#39;CHK&#39;)">
													<CtrySubDvsn>
														<xsl:value-of select="substring(Payee/Address/State,1,2)"/>
													</CtrySubDvsn>
												</xsl:when>
												<xsl:when test="(PaymentMethod/PaymentMethodFormatValue=&#39;TRF&#39; and (ServiceLevel/FormatValue='NURG'))">
													<CtrySubDvsn>
														<xsl:value-of select="substring(Payee/Address/State,1,2)"/>
													</CtrySubDvsn>
												</xsl:when>
											</xsl:choose>
										</xsl:if>
										<xsl:if test="not(string(Payee/Address/Country)=&#39;&#39;)">
											<Ctry>
												<xsl:value-of select="Payee/Address/Country"/>
											</Ctry>
										</xsl:if>
										<xsl:if test="not(Payee/Address/AddressLine1=&#39;&#39;)">
											<AdrLine>
												<xsl:value-of select="Payee/Address/AddressLine1"/>
											</AdrLine>
										</xsl:if>
									</PstlAdr>
									<xsl:if test="(PaymentSourceInfo/EmployeePaymentFlag='N') and not(Payee/SupplierNumber='')">
										<Id>
											<OrgId>
												<Othr>
													<Id>
														<xsl:value-of select="Payee/SupplierNumber"/>
													</Id>
													<xsl:if test="(PaymentSourceInfo/EmployeePaymentFlag='N')">
														<SchmeNm>
															<Prtry>VN</Prtry>
														</SchmeNm>
													</xsl:if>
												</Othr>
											</OrgId>
										</Id>
									</xsl:if>
								</Cdtr>
								<xsl:choose>
									<xsl:when test="((ServiceLevel/FormatValue='URGP') and not(PayeeBankAccount/IBANNumber='') and (PaymentMethod/PaymentMethodFormatValue=&#39;TRF&#39;) and (DeliveryChannel/Code='BOP'))">
										<CdtrAcct>
											<Id>
												<IBAN>
													<xsl:value-of select="PayeeBankAccount/IBANNumber"/>
												</IBAN>
											</Id>
										</CdtrAcct>
									</xsl:when>
									<xsl:when test="((ServiceLevel/FormatValue='URGP') and (PayeeBankAccount/IBANNumber='') and (PaymentMethod/PaymentMethodFormatValue=&#39;TRF&#39;) and (DeliveryChannel/Code='BOP'))">
										<CdtrAcct>
											<Id>
												<Othr>
													<Id>
														<xsl:value-of select="PayeeBankAccount/BankAccountNumber"/>
													</Id>
												</Othr>
											</Id>
										</CdtrAcct>
									</xsl:when>
									<!-- if no IBAN, use bank account number-->
									<xsl:when test="((ServiceLevel/FormatValue='URGP')and (PayeeBankAccount/IBANNumber)='' and (PaymentMethod/PaymentMethodFormatValue=&#39;TRF&#39;) and (DeliveryChannel/Code!='BOP'))">
										<CdtrAcct>
											<Id>
												<Othr>
													<Id>
														<xsl:value-of select="PayeeBankAccount/BankAccountNumber"/>
													</Id>
												</Othr>
											</Id>
										</CdtrAcct>
									</xsl:when>
									<xsl:when test="((ServiceLevel/FormatValue='NURG')and(PaymentMethod/PaymentMethodFormatValue=&#39;TRF&#39;))">
										<CdtrAcct>
											<Id>
												<Othr>
													<Id>
														<xsl:value-of select="PayeeBankAccount/BankAccountNumber"/>
													</Id>
												</Othr>
											</Id>
											<Tp>
												<Prtry>22</Prtry>
											</Tp>
										</CdtrAcct>
									</xsl:when>
								</xsl:choose>
								<xsl:variable name="Countries_1" select="'BR,MA,NZ,QA,RO,SA,SG,ZA,SE,CH,TH,TR,UG,ZM,MX'" />
								<xsl:variable name="Countries_2" select="'CN,IN,OM'" />
								<xsl:choose>
									<xsl:when test="not(PaymentReason/Code='') and (PayeeBankAccount/BankAddress/Country='BH')">
										<Purp>
											<Prtry>
												<xsl:value-of select="concat('/ORDERRES/BH/',PaymentReason/Code,'/')" />
											</Prtry>
										</Purp>
									</xsl:when>
									<xsl:when test="not(PaymentReason/Meaning='') and (contains($Countries_1,PayeeBankAccount/BankAddress/Country)) and not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country) and (ServiceLevel/FormatValue='URGP') ">
										<Purp>
											<Prtry>
												<xsl:value-of select="concat('/POP:',PaymentReason/Meaning)" />
											</Prtry>
										</Purp>
									</xsl:when>
									<xsl:when test="not(PaymentReason/Code='') and (contains($Countries_2,PayeeBankAccount/BankAddress/Country)) and not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country) and (ServiceLevel/FormatValue='URGP')">
										<Purp>
											<Prtry>
												<xsl:value-of select="concat('/POP:',PaymentReason/Code)" />
											</Prtry>
										</Purp>
									</xsl:when>
									<xsl:when test="not(PaymentReason/Code='') and (PayeeBankAccount/BankAddress/Country='PH') and not(BankAccount/BankAddress/Country = PayeeBankAccount/BankAddress/Country)">
										<Purp>
											<Prtry>
												<xsl:value-of select="concat('/ACC/PURPOSE/',PaymentReason/Code)" />
											</Prtry>
										</Purp>
									</xsl:when>
									<xsl:when test="not(PaymentReason/Code='') and not(PaymentReason/Meaning='')  and ((PayeeBankAccount/BankAddress/Country='AE')) ">
										<Purp>
											<Prtry>
												<xsl:value-of select="concat('/BENEFRES/AE//',PaymentReason/Code,'/',PaymentReason/Meaning)" />
											</Prtry>
										</Purp>
									</xsl:when>
								</xsl:choose>

								<xsl:variable name="PayeeCountry">
									<xsl:choose>
										<!-- First preference: Payee address country -->
										<xsl:when test="normalize-space(PayeeBankAccount/BankAddress/Country) != ''">
											<xsl:value-of select="PayeeBankAccount/BankAddress/Country"/>
										</xsl:when>
									</xsl:choose>
								</xsl:variable>

								<RmtInf>
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
												<Nb>
													<xsl:value-of select="substring(DocumentNumber/ReferenceNumber,1,35)"/>
												</Nb>
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
												<xsl:if test="DiscountTaken/Amount/Value &gt;= 0">
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
														<xsl:value-of select="translate(format-number(TotalDocumentAmount/Value, '##0.00'), '-', '')"/>
													</CdtNoteAmt>
												</xsl:if>
												<RmtdAmt>
													<xsl:attribute name="Ccy">
														<xsl:value-of select="PaymentAmount/Currency/Code"/>
													</xsl:attribute>
													<xsl:value-of select="translate(format-number(PaymentAmount/Value, '##0.00'), '-', '')"/>
												</RmtdAmt>
											</RfrdDocAmt>
											<xsl:choose>
												<xsl:when test=" ($svlvl='URGP' and not($PhoneNumber='') and ($PayeeCountry='CN'or $PayeeCountry ='JP'))">
													<CdtrRefInf>
														<Ref>
															<xsl:value-of select="concat('/PHON:', $PhoneNumber)" />
														</Ref>
													</CdtrRefInf>
												</xsl:when>
												<xsl:when test="not(DocumentDescription=&#39;&#39;)">
													<CdtrRefInf>
														<Ref>
															<xsl:value-of select="substring(DocumentDescription,1,30)"/>
														</Ref>
													</CdtrRefInf>
												</xsl:when>
											</xsl:choose>
											<xsl:if test="not(RemittanceMessage[1] = &#39;&#39;)">
												<AddtlRmtInf>
													<xsl:value-of select="substring(RemittanceMessage[1],1,140)"/>
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