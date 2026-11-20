"""Explicit account business-validation waivers; never a valid CCID or import approval."""
from __future__ import annotations
import copy
import re
from interest_account_validation import parse_segments

RESOLVER = 'submit_interest_account_with_user_override'


def business_rejection(result):
    if not isinstance(result, dict):
        return False
    failure, request = result.get('validationFailure'), result.get('request')
    return (isinstance(failure, dict) and isinstance(request, dict)
        and result.get('status') == 'RESPONSE_RECEIVED'
        and type(result.get('httpStatus')) is int and 200 <= result['httpStatus'] < 300
        and result.get('valid') is False and not result.get('soapFault')
        and isinstance(result.get('responseFields'), dict)
        and result['responseFields'].get('Status') == ['Invalid']
        and type(result.get('readOnly')) is bool
        and failure.get('classification') == 'invalid_account'
        and bool(failure.get('errorCodes') or failure.get('message'))
        and request.get('operation') == 'validateAndCreateAccounts'
        and request.get('endpointPath') == '/fscmService/AccountCombinationService')


def eligible_record(record):
    return (isinstance(record, dict) and record.get('status') == 'blocked'
        and business_rejection(record.get('accountValidationResult'))
        and isinstance(record.get('accountResolution'), dict)
        and record['accountResolution'].get('classification') not in
            ('account_check_incomplete', 'account_evidence_conflict', 'validation_unavailable')
        and isinstance(record.get('candidateDesign'), dict)
        and isinstance(record.get('account'), str) and bool(record['account'])
        and isinstance(record.get('ledger'), str) and bool(record['ledger']))


def warning(item):
    return (f"Operation {item['operationId']}: account validation was explicitly overridden: "
        f"{item['approval']['reason']} Submit the account unchanged. FSM may reject or accept it; "
        'verify the saved account and its usability. The import may attempt account creation; '
        'any created GL combination remains. Include this override in the final import approval.')


def make_override(record, decision, review):
    if not eligible_record(record):
        raise ValueError('Only a completed account business rejection can use this override; resolve service/context failures first.')
    choice = decision['records'][record['operationId']]
    if (not isinstance(choice, dict) or choice.get('action') != 'override'
            or not isinstance(choice.get('reason'), str) or not choice['reason'].strip()):
        raise ValueError('Submit unchanged requires an explicit per-record override reason.')
    item = {'resolver': RESOLVER, 'status': 'overridden', 'field': 'InterestSegments',
        'operationId': record['operationId'], 'entity': 'AP_SYSTEM_PARAMETER',
        'targetKey': copy.deepcopy(record['targetKey']), 'requestedValue': record['account'],
        'ledgerName': record['ledger'], 'baselineSha256': review['baselineSha256'],
        'provenance': copy.deepcopy(record['provenance']),
        'approval': {'approved': True, 'approvalId': decision['approvalId'],
                     'reviewSha256': decision['reviewSha256'], 'reason': choice['reason'].strip()},
        'evidence': {'originalFailure': copy.deepcopy(record['accountValidationResult']),
                     'accountResolution': copy.deepcopy(record['accountResolution'])}}
    operation = next(op for op in record['candidateDesign']['operations'] if op['id'] == record['operationId'])
    if not validate_override(item, operation=operation, account=record['account'],
                             ledger=record['ledger'], baseline_sha256=review['baselineSha256']):
        raise ValueError('Override evidence does not match the exact requested account and context.')
    return item


def validate_override(item, *, operation, account, ledger, baseline_sha256):
    if not isinstance(item, dict):
        return False
    try:
        approval, evidence = item['approval'], item['evidence']
        result = evidence['originalFailure']; request = result['request']
        mode = 'No' if result.get('readOnly') is True else 'Yes'
        return (item.get('resolver') == RESOLVER and item.get('status') == 'overridden'
            and item.get('field') == 'InterestSegments' and 'ccid' not in item and 'valid' not in item
            and item.get('operationId') == operation['id'] and item.get('entity') == operation['entity']
            and item.get('targetKey') == operation['targetKey'] and item.get('requestedValue') == account
            and item.get('ledgerName') == ledger and item.get('baselineSha256') == baseline_sha256
            and isinstance(approval, dict) and approval.get('approved') is True
            and isinstance(approval.get('approvalId'), str) and bool(approval['approvalId'].strip())
            and isinstance(approval.get('reason'), str) and bool(approval['reason'].strip())
            and isinstance(approval.get('reviewSha256'), str)
            and re.fullmatch(r'[0-9a-f]{64}', approval['reviewSha256']) is not None
            and business_rejection(result) and result.get('dynamicInsertion') == mode
            and request.get('readOnly') == result.get('readOnly')
            and request.get('baseUrl') == item['provenance']['baseUrl']
            and request.get('businessContext') == {'ledgerName': ledger,
                'segments': parse_segments(account), 'dynamicInsertion': mode})
    except (KeyError, TypeError, ValueError, AttributeError):
        return False


def creation_rejection_matches(item, *, operation, account, ledger, baseline_sha256, base_url):
    if not isinstance(item, dict) or item.get('schemaVersion') != 'invoice-account-creation-rejection-v1':
        return False
    try:
        result, binding = item['creationReceipt'], item['taskContext']
        return (business_rejection(result) and result.get('readOnly') is False
            and result.get('dynamicInsertion') == 'Yes'
            and bool(result.get('approval', {}).get('approvalId'))
            and binding.get('operationId') == operation['id']
            and binding.get('targetKey') == operation['targetKey']
            and binding.get('baselineSha256') == baseline_sha256
            and result['request'].get('baseUrl') == base_url
            and result['request'].get('businessContext') == {'ledgerName': ledger,
                'segments': parse_segments(account), 'dynamicInsertion': 'Yes'})
    except (KeyError, TypeError, ValueError, AttributeError):
        return False
