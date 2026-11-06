"""Fresh BOSS metadata -> runtime rules -> assessment and reviewable rule exports."""
import argparse
import json
from pathlib import Path
import tempfile
from evaluate_roles import validate_request, evaluate
from generate_rules import build_catalog
from extract_tree import (plan_extraction, prepare, project_path, assessment_lock,
                          stage_document, publish_document)
from fscr_context import REPOSITORY
from workspace_paths import (project_reference, require_complete_normalization,
                             validate_project_artifact)


class CoreResponsesRequired(RuntimeError):
    def __init__(self, plan):
        super().__init__('Execute the emitted reads through core.fusion-api.rest-api-client and resume with Core results')
        self.plan = plan


def run(request, output, extractor=None):
    with assessment_lock(output):
        return _run(request, output, extractor)


def _run(request, output, extractor=None):
    request, _, _ = validate_request(request)
    target = Path(output)
    artifacts = {
        'sensitiveAccessRules': target.parent / 'sensitive_access_rules.json',
        'toxicCombinationRules': target.parent / 'toxic_combination_rules.json',
        'generationSummary': target.parent / 'generation_summary.json',
        'runtimeTree': target.parent / 'runtime_tree.json',
    }
    if target.resolve() in {p.resolve() for p in artifacts.values()}:
        raise ValueError('Assessment output conflicts with a rule export filename')
    if any(p.exists() or p.is_symlink() for p in [target, *artifacts.values()]):
        raise ValueError('Assessment artifacts already exist; use a new request directory')
    with tempfile.TemporaryDirectory(prefix='rsc-runtime-') as directory:
        tree = Path(directory) / 'runtime_tree.json'
        if extractor is None:
            _, plan = plan_extraction(request, str(target.parent.resolve()), {})
            raise CoreResponsesRequired(plan)
        else:
            extractor(request, tree)
        tree_bytes = tree.read_bytes()
        catalog = build_catalog(tree_bytes, request['environment'])
        tree_data = json.loads(tree_bytes.decode('utf-8'))
        tree_summary = {key: catalog['summary'][key] for key in
                        ('algorithms', 'entitlements', 'accessPointOccurrences', 'uniqueAccessPoints')}
        tree_summary['uniqueEntitlements'] = len({e['id'] for a in tree_data for e in a['entitlements']})
        tree_summary['perAlgorithm'] = [
            {'referenceCode': a['referenceCode'], 'name': a['name'],
             'entitlements': len(a['entitlements']),
             'accessPointOccurrences': sum(len(e['accessPoints']) for e in a['entitlements']),
             'uniqueAccessPoints': len({p['code'] for e in a['entitlements'] for p in e['accessPoints']})}
            for a in tree_data]
        counts = {key: catalog['summary'][key] for key in
                  ('sensitiveAccessChecks', 'toxicCombinationChecks', 'checksPerRoleSet')}
        print('Generated checks before evaluation: ' + json.dumps(counts), flush=True)
        result = evaluate(request, catalog)
        result['catalogSource'] = catalog['source']
        result['generatedChecks'] = counts
        result['treeSummary'] = tree_summary
        result['evaluationArtifacts'] = {
            key: project_reference(path, repository=REPOSITORY) for key, path in artifacts.items()
        }
        documents = {artifacts['runtimeTree']: tree_bytes}
        for kind, key in (('sensitive_access', 'sensitiveAccessRules'),
                          ('toxic_combination', 'toxicCombinationRules')):
            rules = [rule for rule in catalog['rules'] if rule['ruleType'] == kind]
            documents[artifacts[key]] = {
                'requestId': result['requestId'], 'schemaVersion': catalog['schemaVersion'],
                'name': catalog['name'], 'source': catalog['source'], 'ruleType': kind,
                'ruleCount': len(rules), 'evaluationPolicy': catalog['evaluationPolicy'], 'rules': rules,
            }
        documents[artifacts['generationSummary']] = {
            'requestId': result['requestId'], 'environment': result['environment'],
            'source': catalog['source'], 'treeSummary': tree_summary, **counts,
        }
        documents[target] = result
        # Stage every document before publishing. Publish the assessment last.
        target.parent.mkdir(parents=True, exist_ok=True)
        staged = []
        published = []
        try:
            for destination, document in documents.items():
                content = document if isinstance(document, bytes) else (
                    json.dumps(document, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
                temporary = stage_document(destination, content)
                staged.append((temporary, destination))
            for temporary, destination in staged:
                publish_document(temporary, destination)
                published.append(destination)
        except BaseException:
            for destination in reversed(published):
                destination.unlink(missing_ok=True)
            raise
        finally:
            for temporary, _ in staged:
                temporary.unlink(missing_ok=True)
        return result


def main():
    # Keep the lock through Core planning and final publication for this invocation.
    args = parse_args()
    with assessment_lock(project_path(args.output), args.dry_run):
        return execute(args)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--properties', type=Path, help='Selected FSCR properties; defaults to core/auth/fusionEnv.properties')
    parser.add_argument('--core-response', action='append', default=[], help='request-id=Core-result.json; repeat for all results')
    parser.add_argument('--request-plan-output', type=Path)
    parser.add_argument('--dry-run', action='store_true', help='Print the next Core read plan without writing artifacts')
    return parser.parse_args()


def execute(args):
    reserved = [args.output.parent / name for name in
                ('sensitive_access_rules.json', 'toxic_combination_rules.json', 'generation_summary.json', 'runtime_tree.json')]
    if args.input.resolve() == args.output.resolve() or args.input.resolve() in {p.resolve() for p in reserved}:
        raise ValueError('Output artifacts cannot overwrite caller input')
    from fscr_context import bind_request
    request = bind_request(json.loads(args.input.read_text(encoding='utf-8')), args.properties)
    validate_project_artifact(args.input, request['requestId'], repository=REPOSITORY)
    validate_project_artifact(args.output, request['requestId'], repository=REPOSITORY,
                              expected_name='security_checkup_result.json')
    require_complete_normalization(args.input, request['requestId'])
    plan_path = args.request_plan_output or args.output.parent / 'core-requests.json'
    validate_project_artifact(plan_path, request['requestId'], repository=REPOSITORY)
    if plan_path.resolve() in {args.input.resolve(), *[p.resolve() for p in reserved]}:
        raise ValueError('Core request plan cannot overwrite input or assessment artifacts')
    if any(p.exists() for p in [args.output, *reserved]):
        raise ValueError('Assessment artifacts already exist; use a new request directory')
    tree, plan = prepare(request, args.output, args.core_response, plan_path,
                         args.dry_run, _lock_held=True)
    if args.dry_run:
        print(json.dumps(plan))
        return 0
    if tree is None:
        print(json.dumps({'status': plan['status'], 'pending_requests': len(plan['requests']),
                          'request_plan': str(plan_path)}))
        return 2
    def extracted(_request, destination):
        destination.write_text(json.dumps(tree, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    result = _run(request, args.output, extracted)
    print(json.dumps({'requestId': result['requestId'], 'totalChecksEvaluated': result['totalChecksEvaluated'],
                      'evaluationArtifacts': result['evaluationArtifacts']}))

if __name__ == '__main__':
    raise SystemExit(main())
