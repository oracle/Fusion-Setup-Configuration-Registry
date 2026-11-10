# Inbound Virtual Card Contract Source

These extracts define the exact element names consumed after provider-specific transformation. The Java parsers use namespace-agnostic `local-name()` XPath expressions, but generated normalized output should still use the canonical bundled XSD root and sequence.

## Acknowledgment

Source: `FDBatchAckParser.java`, revision `/st_fusionapps_pt-v2mibfphdev/6`.

Header XPath fields:

```java
//*[local-name() = 'PmtHeader']/*[local-name() = 'MsgId']/text()
//*[local-name() = 'PmtHeader']/*[local-name() = 'MsgSts']/text()
//*[local-name() = 'PmtHeader']/*[local-name() = 'MsgStsCd']/text()
//*[local-name() = 'PmtHeader']/*[local-name() = 'MsgErrCd']/text()
//*[local-name() = 'PmtHeader']/*[local-name() = 'MsgErrDet']/text()
```

Repeating payment XPath fields:

```java
//*[local-name() = 'PmtDetls']
*[local-name() = 'PmtRef']/text()
*[local-name() = 'PmtSts']/text()
*[local-name() = 'PmtStsCd']/text()
*[local-name() = 'PmtMsgErrCd']/text()
*[local-name() = 'PmtMsgErrDet']/text()
*[local-name() = 'PmtClearingNum']/text()
*[local-name() = 'InvHoldCd']/text()
```

`MsgErrDet` and `PmtMsgErrDet` are shortened to 254 characters when their input length exceeds 255. `PmtClearingNum` is passed as the provider transaction response identifier. `MsgStsCd` and `PmtStsCd` are the Oracle application statuses; the provider raw statuses belong in `MsgSts` and `PmtSts`.

## Payment Response

Source: `FDAckProcessing.java`, revision `/st_fusionapps_pt-v2mibfphdev/44`, method `parseAndUpdatePaymentResponse`.

The parser selects every `record` and consumes:

```java
*[local-name() = 'paymentRefNum']/text()
*[local-name() = 'bepStatus']/text()
*[local-name() = 'bepTrxnResponseId']/text()
*[local-name() = 'bepErrorCode']/text()
*[local-name() = 'bepErrorMessage']/text()
*[local-name() = 'invHoldCode']/text()
```

It calls `iby_disburse_ui_api_pub_pkg.vc_pmt_response_update` with parallel arrays for those six fields. When present, `bepErrorCode` is shortened to 29 characters if its input length exceeds 30; `bepErrorMessage` is shortened to 254 characters if its input length exceeds 255. The implementation counts case-insensitive `Success` and `Failure` values, but templates should use provider-to-Oracle status mappings supported by the target flow rather than infer values from those counters.

## Reconciliation

Source: `VirtualCardPaymentReconciliation.java`, revision `/st_fusionapps_pt-v2mibfphdev/4`.

The parser selects every `reconDetls` and consumes:

```java
*[local-name() = 'authCode']/text()
*[local-name() = 'paymentRef']/text()
*[local-name() = 'settlmntDate']/text()
*[local-name() = 'acquirerRef']/text()
*[local-name() = 'settlmntCurr']/text()
*[local-name() = 'transactionAmt']/text()
*[local-name() = 'transactionDate']/text()
*[local-name() = 'transactionId']/text()
```

The arrays are passed to `ap_reconciliation_pkg.vc_pmt_reconciliation_update`; authorization code, payment reference, settlement date, and acquirer reference are also passed to the IBY payment-status update. This makes provider correlation and transaction uniqueness mandatory generation gates even though the Java parser itself does not reject an empty text node before calling the downstream APIs.

## Generation Consequences

- Emit the exact case-sensitive element names above.
- Preserve one normalized record per provider payment or reconciliation transaction.
- Use canonical roots `AckResponse`, `records`, and `reconRcrd` so the result validates against the bundled XSDs.
- Do not rely on namespace differences to distinguish fields; the consumers use `local-name()`.
- Apply documented provider limits before Oracle truncation would occur, and report any possible identifier or diagnostic loss.
- Never invent payment references, clearing references, authorization codes, or transaction IDs.
