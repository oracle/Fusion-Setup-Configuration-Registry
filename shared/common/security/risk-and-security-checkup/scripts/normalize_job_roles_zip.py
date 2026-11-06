"""Normalize a submitted complete SSM/FSM role CSV ZIP; no risk lookup."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import stat
import zipfile

from evaluate_roles import validate_request
from extract_tree import assessment_lock, stage_document, publish_document
from workspace_paths import NORMALIZATION_MARKER, validate_project_artifact

ROLE_FILE = 'ORA_ASE_FUNCTIONAL_SECURITY_CUSTOM_ROLES.csv'
MEMBERSHIP_FILE = 'ORA_ASE_FUNCTIONAL_SECURITY_CUSTOM_ROLE_PRIVILEGE_MEMBERSHIP.csv'
MAX_ARCHIVE_BYTES = 100 * 1024 * 1024
MAX_ARCHIVE_ENTRIES = 1000
MAX_MEMBER_BYTES = 50 * 1024 * 1024
MAX_TOTAL_UNCOMPRESSED_BYTES = 100 * 1024 * 1024
MAX_COMPRESSION_RATIO = 100
READ_CHUNK_BYTES = 1024 * 1024


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(READ_CHUNK_BYTES), b''):
            digest.update(chunk)
    return digest.hexdigest()


def validate_archive_info(info):
    mode = (info.external_attr >> 16) & 0o170000
    if mode == stat.S_IFLNK:
        raise ValueError(f'Archive symlink entries are not allowed: {info.filename}')
    if info.flag_bits & 0x1:
        raise ValueError(f'Encrypted archive entries are not supported: {info.filename}')
    if info.compress_type not in {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED}:
        raise ValueError(f'Unsupported archive compression: {info.filename}')
    if info.file_size > MAX_MEMBER_BYTES:
        raise ValueError(f'Archive member exceeds the size limit: {info.filename}')
    ratio = info.file_size / max(info.compress_size, 1)
    if ratio > MAX_COMPRESSION_RATIO:
        raise ValueError(f'Archive member exceeds the compression-ratio limit: {info.filename}')


def read_member(archive, info):
    content = bytearray()
    with archive.open(info) as stream:
        while True:
            chunk = stream.read(min(READ_CHUNK_BYTES, MAX_MEMBER_BYTES + 1 - len(content)))
            if not chunk:
                break
            content.extend(chunk)
            if len(content) > MAX_MEMBER_BYTES:
                raise ValueError(f'Archive member exceeds the size limit: {info.filename}')
    if len(content) != info.file_size:
        raise ValueError(f'Archive member size changed while reading: {info.filename}')
    return bytes(content)


def read_rows(content, filename, required):
    reader = csv.DictReader(io.StringIO(content.decode('utf-8-sig'), newline=''), strict=True)
    fields = reader.fieldnames or []
    if len(fields) != len(set(fields)) or not required.issubset(fields):
        raise ValueError(f'{filename}: missing required or duplicate CSV columns')
    rows = list(reader)
    for number, row in enumerate(rows, 2):
        if None in row or any(value is None for value in row.values()):
            raise ValueError(f'{filename}, row {number}: malformed CSV row')
        if any(not row[key].strip() for key in required):
            raise ValueError(f'{filename}, row {number}: missing required value')
    return rows


def normalize(source, output, *, environment, complete_privilege_information=True,
              request_id=None):
    if not complete_privilege_information:
        raise ValueError('Explicitly incomplete privilege information cannot be evaluated')
    source, output = Path(source), Path(output)
    summary_path = output.parent / 'normalization_summary.json'
    source_directory = output.parent / 'source_csvs'
    source_paths = {name: source_directory / name for name in (ROLE_FILE, MEMBERSHIP_FILE)}
    destinations = [output, summary_path, *source_paths.values()]
    if len({p.resolve() for p in destinations}) != len(destinations):
        raise ValueError('Output conflicts with a normalization artifact filename')
    if source.resolve() in {p.resolve() for p in destinations}:
        raise ValueError('Output artifacts cannot overwrite the source archive')
    if any(p.exists() for p in destinations):
        raise ValueError('Normalization artifacts already exist; use a separate output directory')
    if source.is_symlink() or not source.is_file():
        raise ValueError('Source archive must be a regular file')
    if source.stat().st_size > MAX_ARCHIVE_BYTES:
        raise ValueError('Source archive exceeds the compressed-size limit')
    archive_digest = file_sha256(source)
    raw, entries = {}, {}
    with zipfile.ZipFile(source) as archive:
        infos = archive.infolist()
        if len(infos) > MAX_ARCHIVE_ENTRIES:
            raise ValueError('Source archive exceeds the entry-count limit')
        total_size = 0
        for info in infos:
            validate_archive_info(info)
            if not info.is_dir():
                total_size += info.file_size
                if total_size > MAX_TOTAL_UNCOMPRESSED_BYTES:
                    raise ValueError('Source archive exceeds the total uncompressed-size limit')
        for name in source_paths:
            matches = [info for info in infos
                       if not info.is_dir() and PurePosixPath(info.filename).name == name]
            if len(matches) != 1:
                raise ValueError(f'Expected exactly one archive entry for {name}; found {len(matches)}')
            raw[name] = read_member(archive, matches[0])
            entries[name] = matches[0].filename
        excluded = [info.filename for info in infos
                    if not info.is_dir() and info.filename not in entries.values()]
    role_rows = read_rows(raw[ROLE_FILE], ROLE_FILE, {'RoleCode', 'RoleName'})
    membership_rows = read_rows(raw[MEMBERSHIP_FILE], MEMBERSHIP_FILE,
                                {'ParentRole', 'MemberPrivilege', 'AddOrRemovePrivilegeMembership'})
    roles = {}
    for row in role_rows:
        code = row['RoleCode']
        if code in roles:
            raise ValueError(f'Duplicate role code: {code}')
        roles[code] = {'roleCode': code, 'roleName': row['RoleName'], 'accessPoints': []}
        if 'RoleCategory' in row:
            roles[code]['sourceRoleCategory'] = row['RoleCategory']
    seen, duplicate_rows = set(), 0
    for row in membership_rows:
        code, privilege = row['ParentRole'], row['MemberPrivilege']
        if code not in roles:
            raise ValueError(f'Membership has no exact role-code match: {code}')
        if row['AddOrRemovePrivilegeMembership'] != 'ADD':
            raise ValueError(f'{code}/{privilege}: membership action requires clarification/baseline')
        pair = (code, privilege)
        if pair in seen:
            duplicate_rows += 1
        else:
            seen.add(pair)
            roles[code]['accessPoints'].append({'code': privilege})
    request = {'requestId': request_id, 'environment': environment,
               'roleSets': [{'roleSetId': code, 'roles': [role]} for code, role in roles.items()]}
    request, _, _ = validate_request(request)
    summary = {
        'requestId': request['requestId'], 'environment': environment,
        'sourceArchiveName': source.name,
        'sourceArchiveSha256': archive_digest,
        'sourceCsvSha256': {name: hashlib.sha256(data).hexdigest() for name, data in raw.items()},
        'sourceArchiveEntries': entries, 'excludedArchiveEntries': excluded,
        'join': 'CUSTOM_ROLES.RoleCode = CUSTOM_ROLE_PRIVILEGE_MEMBERSHIP.ParentRole (left join)',
        'roleSetGrouping': 'One independent role set per exported role across all categories; no user assignments inferred',
        'privilegeCompleteness': 'Submitted membership CSV treated as final and complete under skill input policy; no separate confirmation requested',
        'hierarchyExpansion': False, 'roleCount': len(roles),
        'privilegeMembershipRows': len(membership_rows), 'uniqueRolePrivilegeMemberships': len(seen),
        'uniquePrivilegeCodes': len({privilege for _, privilege in seen}),
        'duplicateMembershipRows': duplicate_rows,
        'rolesWithoutPrivilegeMemberships': [code for code, role in roles.items() if not role['accessPoints']],
        'privilegesPerRole': {code: len(role['accessPoints']) for code, role in roles.items()},
        'validation': 'passed',
    }
    documents = {output: json.dumps(request, ensure_ascii=False, indent=2).encode() + b'\n',
                 summary_path: json.dumps(summary, ensure_ascii=False, indent=2).encode() + b'\n',
                 **{source_paths[name]: data for name, data in raw.items()}}
    marker_path = output.parent / NORMALIZATION_MARKER
    if marker_path.exists() or marker_path.is_symlink():
        raise ValueError('Normalization artifacts already exist; use a separate output directory')
    marker = {'status': 'complete', 'requestId': request['requestId'],
              'artifacts': {str(path.relative_to(output.parent)).replace('\\', '/'):
                            hashlib.sha256(data).hexdigest()
                            for path, data in documents.items()}}
    marker_bytes = json.dumps(marker, ensure_ascii=False, indent=2).encode() + b'\n'
    # Stage everything first, publish data exclusively, and publish completion last.
    staged = []
    published = []
    try:
        for destination, data in documents.items():
            staged.append((stage_document(destination, data), destination))
        staged.append((stage_document(marker_path, marker_bytes), marker_path))
        for temporary, destination in staged:
            publish_document(temporary, destination)
            published.append(destination)
    except BaseException:
        for destination in reversed(published):
            destination.unlink(missing_ok=True)
        for directory in (source_directory, output.parent):
            try:
                directory.rmdir()
            except OSError:
                pass
        raise
    finally:
        for temporary, _ in staged:
            temporary.unlink(missing_ok=True)
    try:
        saved = json.loads(output.read_text(encoding='utf-8'))
        validate_request(saved)
        saved_roles = [group['roles'][0] for group in saved['roleSets']]
        if (saved != request or
            [(r['roleCode'], r['roleName']) for r in saved_roles] !=
            [(r['RoleCode'], r['RoleName']) for r in role_rows] or
            {(r['roleCode'], p['code']) for r in saved_roles for p in r['accessPoints']} != seen):
            raise ValueError('Saved JSON does not reconcile with the source CSVs')
    except BaseException:
        for destination in reversed(published):
            destination.unlink(missing_ok=True)
        for directory in (source_directory, output.parent):
            try:
                directory.rmdir()
            except OSError:
                pass
        raise
    return request, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zip', required=True, type=Path, dest='source')
    parser.add_argument('--properties', type=Path, help='Selected FSCR properties; defaults to core/auth/fusionEnv.properties')
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--request-id')
    parser.add_argument('--complete-privilege-information', action='store_true', default=True,
                        help='Compatibility flag; submitted input is treated as complete by default')
    args = parser.parse_args()
    from fscr_context import environment_from_properties
    request_id = args.request_id or args.output.parent.name
    output = validate_project_artifact(args.output, request_id, expected_name='calling_request.json')
    with assessment_lock(output):
        _, summary = normalize(args.source, output, environment=environment_from_properties(args.properties),
                               complete_privilege_information=args.complete_privilege_information,
                               request_id=request_id)
    # ASCII-safe console JSON also works when Windows redirects a legacy-encoded stdout.
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
