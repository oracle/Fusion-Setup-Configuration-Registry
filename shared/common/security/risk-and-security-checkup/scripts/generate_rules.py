"""Generate runtime Rule-1 and Rule-2 checks without modifying the source tree.

Usage: python3 scripts/generate_rules.py --tree PATH --output PATH [--properties PATH]
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
from itertools import product
import json
from pathlib import Path

ALGORITHMS = {'AL.09361.ORA': 1, 'AL.09802.ORA': 1, 'AL.09360.ORA': 2, 'AL.04571.ORA': 2, 'AL.05980.ORA': 2, 'AL.06870.ORA': 2}

def build_catalog(tree_bytes, environment):
    tree = json.loads(tree_bytes.decode('utf-8'))
    if not isinstance(tree, list) or [a['referenceCode'] for a in tree] != list(ALGORITHMS):
        raise ValueError('Expected the six configured algorithms in the established order')
    counts = Counter()
    occurrences = {}
    rules = []
    algorithms = []
    for algorithm in tree:
        code = algorithm['referenceCode']
        entitlements = algorithm['entitlements']
        if len(entitlements) != ALGORITHMS[code] or any(not e['accessPoints'] for e in entitlements):
            raise ValueError(f'{code}: expected {ALGORITHMS[code]} nonempty entitlement dimensions')
        if any(not isinstance(algorithm[k], str) or not algorithm[k].strip() for k in ('id', 'name')):
            raise ValueError(f'{code}: invalid algorithm ID/name')
        points_by_entitlement = []
        seen_entitlements = set()
        for ent in entitlements:
            if any(not isinstance(ent[k], str) or not ent[k].strip() for k in ('id', 'name')):
                raise ValueError(f'{code}: invalid entitlement ID/name')
            if ent['id'] in seen_entitlements:
                raise ValueError(f'{code}: duplicate entitlement ID')
            seen_entitlements.add(ent['id'])
            seen_in_entitlement = set()
            points = []
            for point in ent['accessPoints']:
                if any(not isinstance(point[k], str) or not point[k] for k in ('code', 'name')):
                    raise ValueError(f'{code}: invalid access point')
                if point['code'] in seen_in_entitlement:
                    raise ValueError(f'{code}: duplicate access-point code within entitlement')
                seen_in_entitlement.add(point['code'])
                counts[point['code']] += 1
                occurrences.setdefault(point['code'], []).append(code)
                points.append(dict(point, entitlementId=ent['id'], entitlementName=ent['name']))
            points_by_entitlement.append(points)
        sensitive = len(entitlements) == 1
        combinations = ((p,) for p in points_by_entitlement[0]) if sensitive else product(*points_by_entitlement)
        start = len(rules)
        for combination in combinations:
            key = code + '|' + '|'.join(p['entitlementId'] for p in combination) + '|' + '|'.join(p['code'] for p in combination)
            rule_name = algorithm['name'] + ': ' + ' + '.join(p['name'] for p in combination)
            if sensitive:
                point = combination[0]
                rationale = f'The submitted role set grants {point["name"]}, identified by {algorithm["name"]} as sensitive access.'
                recommendation = (
                    f'Remove {point["name"]} ({point["code"]}) from roles that do not require it. '
                    'Restrict necessary access to authorized responsibilities using least privilege. '
                    'If the access must remain, document the business rationale, risk acceptance, and applicable compensating controls.'
                )
            else:
                left, right = combination
                rationale = (
                    f'The submitted role set combines {left["entitlementName"]} access ({left["name"]}) '
                    f'with {right["entitlementName"]} access ({right["name"]}), violating {algorithm["name"]} separation of duties.'
                )
                recommendation = (
                    f'Remove or reassign {left["name"]} ({left["code"]}) or {right["name"]} ({right["code"]}) '
                    'so the resulting role set no longer grants both conflicting functions. '
                    'Separate the responsibilities between different users; splitting them across roles assigned to the same user does not resolve the conflict. '
                    'If the risk must remain, document the business rationale, risk acceptance, and applicable compensating controls.'
                )
            rules.append({
                'ruleId': 'risk-' + hashlib.sha256(key.encode()).hexdigest()[:20],
                'ruleName': rule_name,
                'ruleType': 'sensitive_access' if sensitive else 'toxic_combination',
                'severity': 'high',
                'sourceAlgorithm': {k: algorithm[k] for k in ('referenceCode', 'id', 'name')},
                'match': {'operator': 'all', 'accessPoints': list(combination)},
                'rationale': rationale,
                'recommendation': recommendation,
            })
        algorithms.append({
            'referenceCode': code, 'name': algorithm['name'],
            'ruleType': 'sensitive_access' if sensitive else 'toxic_combination',
            'accessPointsPerEntitlement': [len(e['accessPoints']) for e in entitlements], 'checks': len(rules) - start,
        })
    types = Counter(r['ruleType'] for r in rules)
    if len({r['ruleId'] for r in rules}) != len(rules):
        raise ValueError('Duplicate generated rule IDs')
    return {
        'schemaVersion': '1.0',
        'name': 'Fusion Risk and Security Checkup Runtime Catalog',
        'source': {
            'environment': environment,
            'retrievedAt': datetime.now(timezone.utc).isoformat(),
            'treeSha256': hashlib.sha256(tree_bytes).hexdigest(),
        },
        'evaluationPolicy': {
            'scope': 'complete_submitted_role_set',
            'roleHierarchyExpansion': False,
            'accessPointMatch': 'exact_case_sensitive_code',
            'roleSetCombination': 'union_of_caller_supplied_access_points',
            'separateRoleSetsEvaluatedIndependently': True,
            'sensitiveAccessMatch': 'one_access_point_is_sufficient',
            'toxicCombinationMatch': 'both_access_points_in_a_pair_must_be_present_in_the_same_role_set',
            'duplicateInputCodes': 'deduplicate_for_matching_preserve_all_contributing_roles',
            'missingRoleAccessPoints': 'reject_request_without_evaluation',
            'unknownAccessPoints': 'report_as_outside_runtime_catalog_do_not_infer_matches',
            'accessPointsOutsideCatalogMessage': 'Some submitted access points are outside the runtime catalog coverage. Review the reported findings and run Risk Management analysis for a complete security analysis at regular intervals before going live.',
            'noRiskMeaning': 'No match within the runtime-derived checks using the supplied access points; this is not approval of a security change or validation of data security.',
            'severityPolicy': 'High is an implementation default for these high-priority checks, not a severity retrieved from the Fusion API.',
            'recommendationPolicy': 'Recommendations are generated remediation guidance; risk acceptance and compensating controls require the applicable organizational process.',
            'authentication': 'Metadata must be freshly retrieved for the selected FSCR environment through routed core services.',
        },
        'inputContract': {
            'requiredFields': ['requestId', 'environment', 'roleSets'],
            'roleSetRequiredFields': ['roleSetId', 'roles'],
            'optionalRoleSetFields': ['subjectUser'],
            'roleRequiredFields': ['roleCode', 'roleName', 'accessPoints'],
            'accessPointRequiredFields': ['code'],
            'accessPointOptionalFields': ['name'],
            'emptyAccessPointList': 'Allowed as an explicit caller declaration of no access points, including no membership rows in a caller-declared complete job-role membership CSV.',
            'callerResponsibility': 'Supply all existing and proposed roles and all their relevant access points for the resulting target set. Resolve any role hierarchies before calling; the evaluator does not fetch roles or privileges.',
        },
        'summary': {
            'algorithms': len(tree), 'entitlements': sum(len(a['entitlements']) for a in tree), 'accessPointOccurrences': sum(counts.values()),
            'uniqueAccessPoints': len(counts), 'sensitiveAccessChecks': types['sensitive_access'],
            'toxicCombinationChecks': types['toxic_combination'], 'checksPerRoleSet': len(rules),
            'sharedAccessPoints': [{'code': c, 'algorithms': occurrences[c]} for c in counts if counts[c] > 1],
            'algorithmChecks': algorithms,
        },
        'rules': rules,
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tree', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--properties', type=Path, help='Selected FSCR properties; defaults to core/auth/fusionEnv.properties')
    args = parser.parse_args()
    from fscr_context import REPOSITORY
    from workspace_paths import validate_project_artifact
    tree = validate_project_artifact(args.tree, repository=REPOSITORY)
    output = validate_project_artifact(args.output, repository=REPOSITORY)
    if tree.parent != output.parent:
        raise ValueError('Tree and generated rules must belong to the same request directory')
    if tree == output:
        raise ValueError('Output must not overwrite the tree')
    if output.exists():
        raise ValueError('Output already exists; preserve it and select a new destination')
    raw = tree.read_bytes()
    from fscr_context import environment_from_properties
    catalog = build_catalog(raw, environment_from_properties(args.properties))
    serialized = json.dumps(catalog, ensure_ascii=False, indent=2) + '\n'
    assert json.loads(serialized) == catalog
    if tree.read_bytes() != raw:
        raise RuntimeError('Source tree changed during generation')
    # Exclusive creation also rejects a destination created after preflight.
    with output.open('x', encoding='utf-8') as stream:
        stream.write(serialized)
    print(json.dumps(catalog['summary']))

if __name__ == '__main__':
    main()
