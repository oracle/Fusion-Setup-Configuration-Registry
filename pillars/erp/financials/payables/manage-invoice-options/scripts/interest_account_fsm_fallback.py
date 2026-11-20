"""Narrow Invoice Options FSM creation eligibility; never submits an import."""
from __future__ import annotations
import hashlib
import json

RESOLVER = 'create_missing_interest_account_during_fsm'


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def eligible_creation_failure(receipt):
    if not isinstance(receipt, dict):
        return False
    failure = receipt.get('validationFailure') or {}
    request = receipt.get('request') or {}
    approval = receipt.get('approval') or {}
    if not all(isinstance(value, dict) for value in (failure, request, approval)):
        return False
    return (receipt.get('status') == 'RESPONSE_RECEIVED'
            and type(receipt.get('httpStatus')) is int and 200 <= receipt['httpStatus'] < 300
            and receipt.get('valid') is False and receipt.get('readOnly') is False
            and receipt.get('dynamicInsertion') == 'Yes' and not receipt.get('soapFault')
            and receipt.get('responseFields') == {'Status': ['Invalid']}
            and failure.get('classification') == 'invalid_account'
            and failure.get('errorCodes') == ['GL_ASM_ACCOUNT_DYN_INSERT']
            and failure.get('returnedCcId') == '-1'
            and request.get('readOnly') is False
            and request.get('operation') == 'validateAndCreateAccounts'
            and request.get('endpointPath') == '/fscmService/AccountCombinationService'
            and bool(approval.get('approvalId')) and bool(approval.get('approvalRecordSha256')))


def make_deferral(receipt, decision, binding, *, operation, account, ledger, provenance):
    """A current missing/enabled lookup plus the specific approved SOAP failure."""
    if not all(isinstance(value, dict) for value in (decision, binding, operation, provenance)):
        raise ValueError('Complete object-shaped creation and lookup evidence is required.')
    if not eligible_creation_failure(receipt):
        raise ValueError('Only a confirmed GL_ASM_ACCOUNT_DYN_INSERT creation rejection can use FSM creation.')
    if (decision.get('classification') != 'missing_creation_available'
            or decision.get('creationAllowed') is not True
            or decision.get('lookupComplete') is not True or decision.get('exactMatches') != []
            or decision.get('dynamicCombinationCreationAllowed') != 'Y'
            or decision.get('configurationSha256') != binding.get('configurationSha256')):
        raise ValueError('FSM creation requires a fresh complete missing-account check and enabled COA configuration.')
    from interest_account_creation import creation_envelope
    from interest_account_validation import parse_segments
    request = receipt['request']
    segments = parse_segments(account)
    if (request.get('baseUrl') != provenance['baseUrl']
            or request.get('businessContext') != {'ledgerName': ledger, 'segments': segments, 'dynamicInsertion': 'Yes'}
            or request.get('payloadSha256') != hashlib.sha256(creation_envelope(ledger, segments)).hexdigest()
            or binding.get('operationId') != operation['id'] or binding.get('targetKey') != operation['targetKey']):
        raise ValueError('Creation receipt does not match this account, ledger, target or payload.')
    return {'operationId': operation['id'], 'entity': operation['entity'], 'field': 'InterestSegments',
            'resolver': RESOLVER, 'status': 'deferred_to_fsm', 'targetKey': operation['targetKey'],
            'requestedValue': account, 'ledgerName': ledger, 'baselineSha256': binding['baselineSha256'],
            'provenance': provenance, 'evidence': {'creationReceipt': receipt, 'accountResolution': decision,
                                                'taskContext': binding},
            'creationEffect': 'The import will attempt to create this missing account combination while saving Invoice Options.'}


def validate_deferral(item, *, operation, account, ledger, baseline_sha256):
    """Offline binding check, at the same trust boundary as ordinary lookup receipts."""
    if (not isinstance(item, dict) or item.get('resolver') != RESOLVER
            or item.get('status') != 'deferred_to_fsm' or item.get('field') != 'InterestSegments'
            or item.get('operationId') != operation['id'] or item.get('entity') != operation['entity']
            or item.get('targetKey') != operation['targetKey'] or item.get('ledgerName') != ledger
            or item.get('requestedValue') != account or item.get('baselineSha256') != baseline_sha256):
        return False
    evidence = item.get('evidence') or {}
    if not isinstance(evidence, dict):
        return False
    binding = evidence.get('taskContext') or {}
    if not isinstance(binding, dict):
        return False
    if binding.get('baselineSha256') != baseline_sha256:
        return False
    try:
        rebuilt = make_deferral(evidence.get('creationReceipt'), evidence.get('accountResolution') or {},
                                binding, operation=operation, account=account, ledger=ledger,
                                provenance=item['provenance'])
        return rebuilt == item
    except (KeyError, TypeError, ValueError, RuntimeError):
        return False
