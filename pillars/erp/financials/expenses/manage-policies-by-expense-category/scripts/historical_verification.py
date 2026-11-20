"""Read-only binding of an already validated preparation to historical evidence.

This route never builds a candidate, changes a date, refreshes a receipt or grants
import authority. Current-day candidate admission remains in the ordinary builder.
"""
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
import hashlib
import json

SCHEMA = 'fscr-policy-historical-verification-v1'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def artifact(value):
    if not isinstance(value, dict) or set(value) != {'path', 'sha256'}:
        raise ValueError('Historical evidence requires an exact path/hash artifact')
    path = Path(value['path'])
    if not path.is_absolute() or path.is_symlink() or not path.is_file():
        raise ValueError('Unsafe historical evidence artifact')
    if path.resolve() != path or sha(path) != value['sha256']:
        raise ValueError('Historical evidence artifact changed')
    return path


def timestamp(value):
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except (AttributeError, TypeError, ValueError):
        raise ValueError('Historical evidence requires a timezone-aware timestamp') from None
    if result.tzinfo is None or result > datetime.now(timezone.utc):
        raise ValueError('Historical evidence timestamp is naive or in the future')
    return result.astimezone(timezone.utc)


def verify(api, protocol, baseline, candidate, blueprint_path, requirements_path, proof_path):
    import policy_adapter as policy
    import baseline_evidence
    import currency_receipt

    policy.product_contract(protocol)
    blueprint = api['_read_json'](blueprint_path)
    requirements = api['_read_json'](requirements_path)
    if (not isinstance(blueprint, dict) or not isinstance(requirements, list)
            or not all(isinstance(r, dict) for r in requirements)):
        raise ValueError('Historical blueprint and requirements must use object/list shapes')
    ctx = policy.context(blueprint.get('resolvedScope'))
    proof = api['_read_json'](proof_path)
    expected = {'schemaVersion', 'artifacts', 'sourceSnapshot'}
    if not isinstance(proof, dict) or set(proof) != expected or proof['schemaVersion'] != SCHEMA:
        raise ValueError('Exact historical verification context required')
    refs = proof['artifacts']
    if not isinstance(refs, dict) or set(refs) != {
            'baseline', 'candidate', 'blueprint', 'requirements', 'template', 'validation', 'nativeApproval'}:
        raise ValueError('Incomplete historical preparation evidence')
    paths = {key: artifact(value) for key, value in refs.items()}
    for key, path in [('baseline', baseline), ('candidate', candidate),
                      ('blueprint', blueprint_path), ('requirements', requirements_path)]:
        if paths[key] != Path(path).resolve():
            raise ValueError('Historical evidence identifies different '+key)
    original = blueprint['resolvedScope'].get('inputBindings')
    optional_bindings = policy.lookup_bindings(ctx)
    expected_bindings = ({'baseline', 'taskSources', 'areaSources'}
        | {key for key in policy.FILE_KEYS if ctx[key] is not None}
        | set(optional_bindings))
    if not isinstance(original, dict) or set(original) != expected_bindings:
        raise ValueError('Historical source/input inventory is incomplete')
    if original['baseline'] != sha(baseline):
        raise ValueError('Historical baseline changed')
    for key, actual in optional_bindings.items():
        if original[key] != actual:
            raise ValueError('Historical optional preparation evidence changed: '+key)
    for key in policy.FILE_KEYS:
        actual = None if ctx[key] is None else sha(ctx[key])
        if actual != original.get(key):
            raise ValueError('Historical preparation input changed: '+key)

    snapshot = Path(proof['sourceSnapshot'])
    if not snapshot.is_absolute() or snapshot.resolve() != snapshot or not snapshot.is_dir():
        raise ValueError('Safe archived source snapshot required')
    for kind in ('taskSources', 'areaSources'):
        inventory = original[kind]
        if not isinstance(inventory, dict) or not inventory:
            raise ValueError('Missing historical source inventory')
        observed = {p.relative_to(snapshot/kind).as_posix()
                    for p in (snapshot/kind).rglob('*') if p.is_file()}
        if observed != set(inventory):
            raise ValueError('Historical source inventory differs')
        for name, digest in inventory.items():
            rel = PurePosixPath(name)
            if rel.is_absolute() or '..' in rel.parts or '\\' in name:
                raise ValueError('Unsafe historical source member')
            path = snapshot/kind/name
            if path.resolve() != path or not path.is_file() or sha(path) != digest:
                raise ValueError('Archived historical source changed: '+name)

    canonical = api['_sha256_bytes'](api['_canonical_bytes'](blueprint))
    validation = api['_read_json'](paths['validation'])
    if (not isinstance(validation, dict) or validation.get('status') != 'PASS' or validation.get('errors')
            or validation.get('unresolvedWarnings') or validation.get('task') != protocol['task']
            or validation.get('designSha256') != canonical
            or validation.get('baselineSha256') != sha(baseline)
            or validation.get('candidateSha256') != sha(candidate)
            or validation.get('templateSha256') != sha(paths['template'])
            or validation.get('requirementIds') != [r['id'] for r in requirements]
            or requirements != api['_requirements'](protocol, blueprint)):
        raise ValueError('Original validation is not bound to the exact historical preparation')
    hook = api['_read_json'](paths['nativeApproval'])
    if not isinstance(hook, dict):
        raise ValueError('Original native approval must be an object')
    preview, approval = hook.get('preview', {}), hook.get('approval', {})
    if (not isinstance(preview, dict) or not isinstance(approval, dict)
            or not isinstance(preview.get('finalData'), dict)
            or not isinstance(approval.get('runbookBinding'), dict)
            or approval.get('approved') is not True or approval.get('executionRoute') != 'data-loader'
            or approval.get('taskCode') != protocol['task']['code']
            or preview.get('taskCode') != protocol['task']['code']
            or preview.get('finalData', {}).get('archiveSha256') != sha(candidate)
            or preview.get('runbookBinding') != approval.get('runbookBinding')
            or approval.get('runbookBinding', {}).get('serverUrl') != ctx['target_origin']):
        raise ValueError('Original native approval is not bound to the historical candidate')
    prepared_at = timestamp(preview.get('generatedAt'))
    approved_at = timestamp(approval.get('approvedAt'))
    provenance = baseline_evidence.verify(baseline, ctx['baseline_receipt'],
        ctx['baseline_export_plan'], ctx['baseline_export_approval'],
        ctx['environment'], ctx['baseline_process_id'])
    receipt = api['_read_json'](Path(ctx['baseline_receipt']))
    observed = timestamp(receipt.get('observed_at_utc'))
    if (observed.date().isoformat() != ctx['validation_date']
            or prepared_at.date().isoformat() != ctx['validation_date']
            or not observed <= prepared_at <= approved_at
            or currency_receipt.origin(provenance['origin']) != currency_receipt.origin(ctx['target_origin'])):
        raise ValueError('Historical preparation chronology or target differs')
    references = []
    if ctx['currency_receipt'] is not None:
        binding = currency_receipt.binding(ctx['workbook'], baseline, ctx['runtime_contract'],
            ctx['environment'], ctx['target_origin'], ctx['validation_date'])
        captured = api['_read_json'](Path(ctx['currency_receipt']))
        for operation in captured.get('operations', []):
            references.append(currency_receipt.verify(ctx['currency_receipt'], binding,
                operation['entity'], operation['policy_name'], operation['operation'], operation['currency_code']))
        if not references:
            raise ValueError('Historical currency evidence has no bound operation')
    return ctx, {'schemaVersion': SCHEMA, 'proofSha256': sha(proof_path),
        'verifiedAt': datetime.now(timezone.utc).isoformat(),
        'originalValidationSha256': sha(paths['validation']), 'preparedAt': preview['generatedAt'],
        'designSha256': canonical, 'originalSourceBindings': original,
        'verifierSourceBindings': policy.bindings(ctx, baseline),
        'referenceEvidence': references, 'readOnly': True, 'importApproved': False,
        'boundary': 'Local historical artifact/reference verification only; native process success remains independently required.'}
