#!/usr/bin/env python3
"""Refresh task-owned references through the existing core GET client; no writes to Fusion."""
import argparse
import datetime as dt
import hashlib
import importlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from build_import_candidate import package, TYPE_MEMBER, CODE
from intake_workbook import TASK, preflight

API = '/fscmRestApi/resources/11.13.18.05/'
TAXONOMY = '/api/boss/data/objects/ora/commonAppsInfra/objects/v1/taxonomyNodes'


def reference_destination(project, destination, area, *, require_new=True):
    """Keep this task's reference outputs under a real project area.

    Inspect the supplied paths before resolving them: resolving both the root
    and destination would make a linked outside root appear contained.
    """
    project, destination = Path(project).absolute(), Path(destination).absolute()
    if area not in {'exports', 'artifacts'} or '..' in project.parts or '..' in destination.parts:
        raise ValueError('Reference destinations require explicit project paths without traversal.')
    root = project / area
    if root not in destination.parents:
        raise ValueError('Reference destination must be inside the selected project ' + area + ' directory.')
    for path in (*reversed(destination.parents), destination):
        if path.is_symlink() or (hasattr(path, 'is_junction') and path.is_junction()):
            raise ValueError('Reference destination roots and ancestors must not be symlinks or junctions.')
        if path.exists() and path != destination and not path.is_dir():
            raise ValueError('Reference destination ancestor must be a directory.')
    if not project.is_dir() or not destination.resolve().is_relative_to(root):
        raise ValueError('Reference destination escapes the selected project.')
    if destination.exists() and (require_new or not destination.is_dir()):
        raise ValueError('Reference destination must be new or an existing capture directory.')
    return destination


def links(row):
    return row.get('links', row.get('@context', {}).get('links', []))


def child(row, name):
    found = [v['href'] for v in links(row) if v.get('rel') == 'child' and v.get('name') == name]
    if len(found) != 1:
        raise ValueError('Missing/ambiguous returned child link: ' + name)
    return found[0]


def identity(value):
    if isinstance(value, bool) or not re.fullmatch(r'\d+', str(value)):
        raise ValueError('Missing/invalid numeric identity; never default a view or set ID.')
    return str(int(value))


def normalize_code(code, lookup_type, dff_rows):
    if len(dff_rows) != 1:
        raise ValueError('Each code needs exactly one unambiguous DFF identity row.')
    full = dff_rows[0]
    for key, expected in [('LookupType', lookup_type['LookupType']), ('LookupCode', code['LookupCode'])]:
        if full.get(key) != expected:
            raise ValueError('DFF identity does not match its parent: ' + key)
    view = identity(lookup_type['ViewApplicationId'])
    if identity(code.get('ViewApplicationId')) != view or identity(full.get('ViewApplicationId')) != view:
        raise ValueError('DFF/code/type application-view mismatch.')
    result = {k: v for k, v in code.items() if k not in {'links', '@context', 'lookupsDFF'}}
    result.update(LookupType=lookup_type['LookupType'], ViewApplicationId=view, SetId=identity(full.get('SetId')))
    return result


def expanded_code(code, lookup_type):
    # A code-only child URL is ambiguous when a code occurs in multiple sets.
    # Expansion retains the originating parent row's set context.
    dff = code.get('lookupsDFF')
    if (not isinstance(dff, dict) or dff.get('hasMore') is not False
            or dff.get('offset') != 0 or not isinstance(dff.get('items'), list)
            or dff.get('count') != len(dff['items'])):
        raise ValueError('Expanded DFF identity must be complete; do not follow an ambiguous code-only child URL.')
    return normalize_code(code, lookup_type, dff['items'])


def module_scope(rows):
    # EXM/APPLICATION is the fixed task parameter, never a customer module ID.
    ids = {r['ModuleId'] for member in (TYPE_MEMBER, CODE) for r in rows[member]
           if r.get('ModuleKey') == 'EXM' and r.get('ModuleType') == 'APPLICATION' and r.get('ModuleId')}
    if len(ids) > 1:
        raise ValueError('Exact-task export has conflicting EXM/APPLICATION module mappings.')
    return sorted(ids)


def resolve_modules(reader, rows):
    modules = module_scope(rows)
    if modules:
        return modules, 'export-confirmed-application-modules'
    # Modified-only exports can be empty while seeded types still exist. Resolve
    # the task's business key independently; never infer ownership from a type.
    nodes = reader.pages(TAXONOMY, ["$filter=moduleType = 'APPLICATION'", '$sortBy=moduleId'])
    if any(n.get('moduleType') != 'APPLICATION' for n in nodes):
        raise ValueError('Taxonomy response violates the APPLICATION module filter.')
    matches = [n for n in nodes if n.get('moduleKey') == 'EXM']
    if len(matches) != 1:
        raise ValueError('Resolve exactly one EXM/APPLICATION taxonomy node; missing or ambiguous module evidence.')
    module = matches[0].get('moduleId')
    if not isinstance(module, str) or not module.strip() or module != module.strip() or len(module) > 32:
        raise ValueError('Taxonomy node requires its documented moduleId; do not substitute alternativeId, moduleGUID or an opaque key.')
    return [module], 'taxonomy-confirmed-application-modules'


def catalog(snapshot):
    if snapshot.get('task_code') != TASK or snapshot.get('complete') is not True or snapshot.get('sets_complete') is not True:
        raise ValueError('A complete environment-bound snapshot is required for customer dropdowns.')
    types = []
    seen = set()
    for row in snapshot['types']:
        if row['LookupType'] in seen:
            raise ValueError('Lookup type has multiple views. Resolve the view before generating an unambiguous dropdown.')
        seen.add(row['LookupType'])
        types.append({'code': row['LookupType'], 'name': row['Meaning'], 'description': row.get('Description') or '',
                      'configuration_level': row['CustomizationLevel'], 'view_application_id': identity(row['ViewApplicationId'])})
    return {'schema_version': '2.0', 'task_code': TASK, 'catalog_kind': 'customer-environment',
            'environment': snapshot['environment'], 'captured_at': snapshot['captured_at'],
            'exhaustive': False, 'scope': 'Verified Expenses application modules; unverified descendants are not inferred.',
            'source': 'Selected customer environment ' + snapshot['environment'] + '; captured ' + snapshot['captured_at'],
            'lookup_types': sorted(types, key=lambda r: r['code']),
            'reference_sets': [{'code': r['SetCode'], 'name': r.get('SetName') or r['SetCode']} for r in snapshot['sets']],
            'enabled_values': ['Yes', 'No']}


def existing_model(snapshot, selected):
    sets = {identity(r['SetId']): r['SetCode'] for r in snapshot['sets']}
    rows = []
    fields = {'Meaning':'meaning', 'Description':'description', 'DisplaySequence':'display_sequence',
              'StartDateActive':'start_date', 'EndDateActive':'end_date', 'Tag':'tag'}
    for c in snapshot['codes']:
        if c['LookupType'] not in selected:
            continue
        if c.get('EnabledFlag') not in {'Y', 'N'}:
            raise ValueError('Unknown destination EnabledFlag; do not coerce it.')
        r = {'lookup_type': c['LookupType'], 'lookup_code': c['LookupCode'], 'set_code': sets[identity(c['SetId'])],
             'enabled': 'Yes' if c['EnabledFlag'] == 'Y' else 'No'}
        r.update({dst: c[src] for src, dst in fields.items() if c.get(src) is not None})
        rows.append(r)
    return {'schema_version': '3.0', 'task_code': TASK, 'rows': rows,
            'type_rows': [{'lookup_type': t['LookupType'], 'meaning': t['Meaning'], 'description': t.get('Description') or ''}
                          for t in snapshot['types'] if t['LookupType'] in selected], 'source_issues': []}


def _core_modules(repo):
    """Resolve only the selected checkout's public Core providers."""
    paths = {
        'fusion_auth': repo / 'core/auth/fusion-oauth-authentication/scripts/fusion_auth.py',
        'rest_client_common': repo / 'core/fusion-api/rest-api-client/scripts/rest_client_common.py',
    }
    modules = {}
    for name, path in paths.items():
        previous_path = sys.path[:]
        sys.path.insert(0, str(path.parent))
        try:
            module = importlib.import_module(name)
        finally:
            sys.path[:] = previous_path
        if Path(module.__file__).resolve() != path.resolve():
            raise ValueError('Core reference client differs from the selected repository.')
        modules[name] = module
    return modules['fusion_auth'], modules['rest_client_common']


class CoreReader:
    def __init__(self, repo, project, environment, export_dir, properties=None):
        self.project = Path(project).absolute()
        self.repo, self.export_dir, self.sequence = repo, reference_destination(self.project, export_dir, 'exports'), 0
        self.environment = environment
        self.properties = Path(properties).absolute() if properties is not None else repo / 'core/auth/fusionEnv.properties'
        self.profile_hash = hashlib.sha256(self.properties.read_bytes()).hexdigest()
        self.auth, self.common = _core_modules(repo)
        props = self.auth.read_properties(self.properties)
        self.ensure_unchanged()
        if props.get('environment') != environment:
            raise ValueError('Selected environment and configured environment differ.')
        base = urlsplit(props.get('restBaseUrl', ''))
        if base.scheme != 'https' or not base.hostname or base.username or base.password or base.port not in (None, 443):
            raise ValueError('Expected the configured credential-free HTTPS Fusion origin.')
        self.origin = (base.hostname.lower(), base.port or 443)
        # Keep the exact configuration in memory. No subprocess rereads a
        # mutable default profile and no credential-bearing snapshot is saved.
        self.props = self.common.props_with_scope_property(props, 'scope')
        self.profile = props
        self.boss_props = None
        self.boss_token = None
        self.access_token = None
        reference_destination(self.project, self.export_dir, 'exports')
        self.export_dir.mkdir(parents=True, exist_ok=False)

    def ensure_unchanged(self):
        try:
            unchanged = hashlib.sha256(self.properties.read_bytes()).hexdigest() == self.profile_hash
        except OSError:
            unchanged = False
        if not unchanged:
            raise ValueError('Selected reference profile changed; stop and restart under the selected environment.')
        reference_destination(self.project, self.export_dir, 'exports', require_new=False)

    def verify_environment(self, environment):
        self.ensure_unchanged()
        if environment != self.environment:
            raise ValueError('Reference snapshot environment differs from the selected profile.')

    def get(self, endpoint, query):
        self.ensure_unchanged()
        endpoint = self.endpoint(endpoint)
        boss = urlsplit(endpoint).path == TAXONOMY
        if boss and self.boss_props is None:
            self.boss_props = self.common.props_with_scope_property(self.profile, 'boss_scope')
        props = self.boss_props if boss else self.props
        token_attribute = 'boss_token' if boss else 'access_token'
        url = self.common.build_url(props, endpoint, query)
        if getattr(self, token_attribute) is None:
            setattr(self, token_attribute, self.auth.get_access_token(props, token_cache='auto'))
        self.ensure_unchanged()
        for attempt in range(2):
            try:
                content, headers, status = self.common.request_bytes(
                    props, url, method='GET', access_token=getattr(self, token_attribute),
                    headers={} if boss else {'REST-Framework-Version': '9'}, json_body=None, timeout=60)
                break
            except self.auth.FusionHttpError as error:
                if attempt or error.status_code not in (401, 403):
                    raise ValueError('Core reference GET failed with HTTP ' + str(error.status_code)) from None
                self.ensure_unchanged()
                setattr(self, token_attribute, self.auth.get_access_token(props, token_cache='auto', force_login=True))
                self.ensure_unchanged()
        self.ensure_unchanged()
        if status != 200:
            raise ValueError('Core reference GET did not return HTTP 200.')
        return content

    def endpoint(self, url):
        parsed = urlsplit(url)
        if parsed.netloc and not parsed.scheme:
            raise ValueError('Protocol-relative links are not supported.')
        if parsed.scheme:
            if parsed.scheme != 'https' or parsed.username or parsed.password or (parsed.hostname.lower(), parsed.port or 443) != self.origin:
                raise ValueError('Returned link is outside the selected environment origin.')
        standard = parsed.path.startswith(API) and parsed.path[len(API):].split('/')[0] in {'genericLookups', 'setIdSets'}
        if not (standard or parsed.path == TAXONOMY) or parsed.query or parsed.fragment or '..' in parsed.path:
            raise ValueError('Unexpected lookup link or embedded query.')
        return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, '', ''))

    def pages(self, url, query=()):
        endpoint = self.endpoint(url)
        boss = urlsplit(endpoint).path == TAXONOMY
        offset, records, page_hashes = 0, [], set()
        while True:
            if self.sequence >= 2000:
                raise ValueError('Bounded reference read limit reached.')
            self.sequence += 1
            output = self.export_dir / ('read-%04d.json' % self.sequence)
            params = dict(value.split('=', 1) for value in query)
            params.update({'$limit' if boss else 'limit': '500', '$offset' if boss else 'offset': str(offset)})
            content = self.get(endpoint, params)
            data = json.loads(content)
            self.ensure_unchanged()
            with reference_destination(self.project, output, 'exports').open('xb') as stream:
                stream.write(content)
            items = data.get('items')
            # BOSS uses $offset in requests and need not echo an offset. It must
            # still supply an explicit terminal hasMore=false; absence is unsafe.
            if (not isinstance(items, list) or not all(isinstance(item, dict) for item in items)
                    or not isinstance(data.get('hasMore'), bool)
                    or data.get('offset', offset if boss else None) != offset):
                raise ValueError('Incomplete/mismatched collection pagination contract.')
            digest = hashlib.sha256(json.dumps(items, sort_keys=True).encode()).hexdigest()
            if items and digest in page_hashes:
                raise ValueError('Repeated collection page; refusing incomplete evidence.')
            page_hashes.add(digest)
            records.extend(items)
            if data['hasMore'] is False:
                return records
            if not items or self.sequence > 2000:
                raise ValueError('Empty continuing page or bounded read limit reached.')
            offset += len(items)


def collect(reader, baseline_rows, model, environment, template, baseline):
    reader.verify_environment(environment)
    captured_at = dt.datetime.now(dt.timezone.utc).isoformat()
    modules, scope_kind = resolve_modules(reader, baseline_rows)
    types, seen = [], set()
    for module in modules:
        for t in reader.pages(API + 'genericLookups', ["q=ModuleId='" + module.replace("'", "''") + "'"]):
            if t.get('ModuleId') != module:
                raise ValueError('Lookup response violates the selected module filter.')
            key = (t.get('LookupType'), identity(t.get('ViewApplicationId')))
            if key in seen:
                raise ValueError('Duplicate type/view identity in customer inventory.')
            seen.add(key); types.append(t)
    sets = reader.pages(API + 'setIdSets')
    set_ids = {}
    set_codes = set()
    for s in sets:
        sid = identity(s.get('SetId'))
        if sid in set_ids or not s.get('SetCode') or s['SetCode'] in set_codes:
            raise ValueError('Ambiguous customer reference-set inventory.')
        set_ids[sid] = s; set_codes.add(s['SetCode'])
    selected = {r['lookup_type'] for r in model.get('rows', []) + model.get('type_rows', [])}
    codes, scopes = [], []
    for name in sorted(selected):
        matches = [t for t in types if t.get('LookupType') == name]
        if len(matches) != 1:
            raise ValueError('Requested lookup type is missing or has ambiguous views in verified customer scope: ' + name)
        t = matches[0]
        collection = child(t, 'lookupCodes')
        # Require complete expansion in each originating row, not code-only links.
        for c in reader.pages(collection, ['expand=lookupsDFF']):
            full = expanded_code(c, t)
            if full['SetId'] not in set_ids:
                raise ValueError('Code references a set absent from complete customer set inventory.')
            codes.append(full)
        # The unfiltered type child is read across all sets, with full DFF keys.
        # SetIdLookupVO resolves any existing SetCode independently of code usage.
        # An empty population is still complete after the terminal page is checked.
        for sid in set_ids:
            scopes.append({'LookupType': name, 'ViewApplicationId': identity(t['ViewApplicationId']), 'SetId': sid,
                           'complete': True, 'source_ref': str(reader.export_dir) + ': unfiltered fully paginated type-code/DFF GETs across all sets; SetIdLookupVO set resolver'})
    reader.verify_environment(environment)
    snapshot = {'task_code': TASK, 'environment': environment, 'captured_at': captured_at,
                'complete': True, 'codes_complete': True, 'sets_complete': True, 'expenses_module_ids': modules,
                'scope_kind': scope_kind,
                'module_source_ref': str(reader.export_dir) + ': paginated taxonomy EXM/APPLICATION GET' if scope_kind.startswith('taxonomy-') else str(baseline),
                'types': types, 'sets': sets, 'codes': codes, 'code_scopes': scopes,
                'template_sha256': hashlib.sha256(template.read_bytes()).hexdigest(), 'baseline_sha256': hashlib.sha256(baseline.read_bytes()).hexdigest()}
    return snapshot


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for key in ('repo-root', 'project-root', 'input', 'template', 'baseline', 'output-dir', 'read-dir'):
        p.add_argument('--' + key, type=Path, required=True)
    p.add_argument('--environment', required=True)
    p.add_argument('--properties', type=Path, help='Trusted environment profile, including a private profile outside the repository. Defaults to core/auth/fusionEnv.properties.')
    p.add_argument('--live', action='store_true', help='Perform only the declared core GET reference checks.')
    p.add_argument('--dry-run', action='store_true')
    a = p.parse_args()
    project, repo = a.project_root.absolute(), a.repo_root.resolve(strict=True)
    try:
        a.output_dir = reference_destination(project, a.output_dir, 'artifacts')
        a.read_dir = reference_destination(project, a.read_dir, 'exports')
    except ValueError as error:
        p.error(str(error))
    model = json.loads(a.input.read_text())
    from intake_workbook import validate
    checked = validate(model)
    if checked['issues'] or checked['status'] == 'needs_input':
        p.error('Provide validated selected lookup type/code input.')
    from xml.etree import ElementTree as ET
    tm, empty = package(a.template); bm, rows = package(a.baseline)
    if any(empty.values()):
        p.error('Template contains records.')
    tx, bx = ET.fromstring(tm), ET.fromstring(bm)
    if any(x.findtext('.//ProcessEnv') != a.environment for x in (tx, bx)) or tx.findtext('.//ProcessRelease') != bx.findtext('.//ProcessRelease'):
        p.error('Exports do not match selected environment/release.')
    modules = module_scope(rows)
    if a.dry_run:
        print(json.dumps({'status': 'local_plan_valid', 'environment': a.environment, 'operations': 'core GET references only',
                          'module_resolution': 'export' if modules else 'taxonomy GET required with boss_scope',
                          'references_verified': False, 'external_calls': False})); return
    if not a.live:
        p.error('Reference collection requires explicit --live under the active task workflow.')
    reader = CoreReader(repo, project, a.environment, a.read_dir, properties=a.properties)
    snapshot = collect(reader, rows, model, a.environment, a.template, a.baseline)
    choices = catalog(snapshot)
    reader.verify_environment(a.environment)
    reference_destination(project, a.output_dir, 'artifacts').mkdir(parents=True, exist_ok=False)
    for name, value in [('destination.json', snapshot), ('workbook-lovs.json', choices), ('existing-input.json', existing_model(snapshot, {r['lookup_type'] for r in model.get('rows', []) + model.get('type_rows', [])})),
                        ('preflight.json', preflight(model, snapshot, a.environment))]:
        with reference_destination(project, a.output_dir / name, 'artifacts').open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'status': 'references_refreshed', 'types': len(snapshot['types']), 'sets': len(snapshot['sets']), 'codes': len(snapshot['codes']), 'execution_authorized': False}))


if __name__ == '__main__':
    main()
