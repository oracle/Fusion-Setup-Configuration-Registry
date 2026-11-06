"""Evaluate supplied role sets against the generated JSON rules, never the tree.

Usage: python3 scripts/evaluate_roles.py --input REQUEST.json --rules RULES.json [--output RESULT.json]
Only supplied access points are evaluated. No API calls or role expansion occur.
"""
import argparse
from collections import Counter
import json
import uuid
from pathlib import Path

def text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{label} must be a nonempty string')
    return value

def validate_request(request):
    if not isinstance(request, dict):
        raise ValueError('Request must be an object')
    request = dict(request)
    request_id = request.get('requestId')
    if request_id is None or (isinstance(request_id, str) and not request_id.strip()):
        request['requestId'] = 'RSC-' + str(uuid.uuid4())
    if 'applicationUser' in request:
        raise ValueError('applicationUser is not an assessment input; authentication belongs to FSCR core services')
    context = {k: text(request.get(k), k) for k in ('requestId', 'environment')}
    sets = request.get('roleSets')
    if not isinstance(sets, list) or not sets:
        raise ValueError('roleSets must be a nonempty array')
    prepared = []
    seen_sets = set()
    # Validate the entire request before evaluating any role set.
    for role_set in sets:
        if not isinstance(role_set, dict):
            raise ValueError('Each role set must be an object')
        set_id = text(role_set.get('roleSetId'), 'roleSetId')
        if set_id in seen_sets:
            raise ValueError('Duplicate roleSetId')
        seen_sets.add(set_id)
        if 'subjectUser' in role_set:
            text(role_set['subjectUser'], 'subjectUser')
        roles = role_set.get('roles')
        if not isinstance(roles, list):
            raise ValueError(f'{set_id}: roles must be an array')
        contributors = {}
        role_order = []
        seen_roles = set()
        for role in roles:
            if not isinstance(role, dict):
                raise ValueError(f'{set_id}: each role must be an object')
            role_code = text(role.get('roleCode'), 'roleCode')
            role_name = text(role.get('roleName'), 'roleName')
            if role_code in seen_roles:
                raise ValueError(f'{set_id}: duplicate roleCode {role_code}')
            seen_roles.add(role_code)
            points = role.get('accessPoints')
            if not isinstance(points, list):
                raise ValueError(f'{set_id}/{role_code}: accessPoints must be explicitly supplied as an array')
            identity = {'roleCode': role_code, 'roleName': role_name}
            role_order.append(identity)
            for point in points:
                if not isinstance(point, dict):
                    raise ValueError('Each input access point must be an object with code')
                point_code = text(point.get('code'), 'accessPoints.code')
                origins = contributors.setdefault(point_code, [])
                if identity not in origins:
                    origins.append(identity)
        prepared.append((role_set, contributors, role_order))
    return request, context, prepared

def evaluate(request, catalog):
    request, context, prepared = validate_request(request)
    if catalog.get('schemaVersion') != '1.0' or catalog.get('evaluationPolicy', {}).get('roleHierarchyExpansion') is not False:
        raise ValueError('Unsupported rules catalog')
    rules = catalog['rules']
    if not rules or len({r['ruleId'] for r in rules}) != len(rules):
        raise ValueError('Expected nonempty unique runtime checks')
    if catalog.get('source', {}).get('environment') != context['environment']:
        raise ValueError('Runtime catalog environment does not match the FSCR-bound request')
    if any(r['ruleType'] not in {'sensitive_access', 'toxic_combination'} for r in rules):
        raise ValueError('Invalid runtime rule type')
    known = set()
    for rule in rules:
        points = rule['match']['accessPoints']
        if rule['match']['operator'] != 'all' or len(points) != (1 if rule['ruleType'] == 'sensitive_access' else 2):
            raise ValueError('Unsupported rule predicate')
        known.update(text(p['code'], 'rule access-point code') for p in points)
    summary = catalog['summary']
    types = Counter(r['ruleType'] for r in rules)
    if summary['checksPerRoleSet'] != len(rules) or summary['uniqueAccessPoints'] != len(known) or summary['sensitiveAccessChecks'] != types['sensitive_access'] or summary['toxicCombinationChecks'] != types['toxic_combination']:
        raise ValueError('Runtime catalog summary does not match rules')
    results = []
    for role_set, contributors, role_order in prepared:
        findings = []
        for rule in rules:
            points = rule['match']['accessPoints']
            if not all(p['code'] in contributors for p in points):
                continue
            evidence = [dict(p, contributingRoles=contributors[p['code']]) for p in points]
            involved = {r['roleCode'] for p in points for r in contributors[p['code']]}
            findings.append({
                'ruleId': rule['ruleId'], 'ruleName': rule['ruleName'],
                'riskCategory': rule['ruleType'], 'severity': rule['severity'],
                'sourceAlgorithm': rule['sourceAlgorithm'],
                'offendingRoles': [r for r in role_order if r['roleCode'] in involved],
                'offendingAccessPoints': evidence,
                'rationale': rule['rationale'], 'recommendation': rule['recommendation'],
            })
        result = {
            'roleSetId': role_set['roleSetId'],
            'overallResult': 'risk_found' if findings else 'no_risk_found',
            'recommendationStatus': 'remediation_or_documented_risk_acceptance_required' if findings else 'no_catalog_risk_identified',
            'checksEvaluated': len(rules), 'rolesEvaluated': len(role_order),
            'uniqueInputAccessPoints': len(contributors),
            'accessPointsOutsideCatalog': [c for c in contributors if c not in known],
            'sensitiveAccessFindings': sum(f['riskCategory'] == 'sensitive_access' for f in findings),
            'toxicCombinationFindings': sum(f['riskCategory'] == 'toxic_combination' for f in findings),
            'findings': findings,
        }
        if result['accessPointsOutsideCatalog']:
            result['securityCheckupMessage'] = catalog['evaluationPolicy']['accessPointsOutsideCatalogMessage']
        if 'subjectUser' in role_set:
            result['subjectUser'] = text(role_set['subjectUser'], 'subjectUser')
        results.append(result)
    return dict(context, rulesName=catalog['name'], rulesSchemaVersion=catalog['schemaVersion'],
                evaluationScope=catalog['evaluationPolicy']['scope'], roleHierarchyExpansion=False,
                noRiskMeaning=catalog['evaluationPolicy']['noRiskMeaning'],
                roleSetsEvaluated=len(results), totalChecksEvaluated=len(rules) * len(results),
                roleSetResults=results)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--rules', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--properties', type=Path, help='Selected FSCR properties; defaults to core/auth/fusionEnv.properties')
    args = parser.parse_args()
    if args.output and args.output.resolve() in {args.input.resolve(), args.rules.resolve()}:
        raise ValueError('Result output must not overwrite an input or catalog')
    if args.output and args.output.exists():
        raise ValueError('Output already exists; preserve it and select a new destination')
    from fscr_context import bind_request
    request = bind_request(json.loads(args.input.read_text(encoding='utf-8')), args.properties)
    from fscr_context import REPOSITORY
    from workspace_paths import validate_project_artifact
    validate_project_artifact(args.input, request['requestId'], repository=REPOSITORY)
    validate_project_artifact(args.rules, request['requestId'], repository=REPOSITORY)
    if args.output:
        validate_project_artifact(args.output, request['requestId'], repository=REPOSITORY)
    result = evaluate(request, json.loads(args.rules.read_text(encoding='utf-8')))
    serialized = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        # Do not replace a destination created after the preflight check.
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(serialized)
    else:
        print(serialized, end='')

if __name__ == '__main__':
    main()
