"""Validate and describe this skill's durable project workspace paths."""
import hashlib
import json
from pathlib import Path

from fscr_context import REPOSITORY


ARTIFACT_SUFFIX = Path('artifacts/shared/common/security/risk-and-security-checkup')
NORMALIZATION_MARKER = 'normalization-complete.json'


def validate_project_artifact(path, request_id=None, *, repository=None, expected_name=None):
    """Return a resolved artifact path in the exact project/request layout."""
    repository = Path(repository or REPOSITORY).resolve()
    path = Path(path)
    lexical = path.absolute()
    resolved = path.resolve()
    project_root = (repository / 'project').resolve()
    try:
        relative = resolved.relative_to(project_root)
    except ValueError as error:
        raise ValueError('Artifact must be inside the selected FSCR project workspace') from error
    if len(relative.parts) < 8:
        raise ValueError('Artifact must use the risk-and-security-checkup request directory')
    project_id = relative.parts[0]
    if project_id == '_template':
        raise ValueError('The project template is not an execution workspace')
    expected_prefix = (project_id, *ARTIFACT_SUFFIX.parts)
    if tuple(relative.parts[:len(expected_prefix)]) != expected_prefix:
        raise ValueError('Artifact must use project/{project_id}/artifacts/shared/common/security/'
                         'risk-and-security-checkup/{request_id}/')
    run_request_id = relative.parts[len(expected_prefix)]
    if not run_request_id or run_request_id in {'.', '..'}:
        raise ValueError('Request directory requires a valid request ID')
    if len(relative.parts) != len(expected_prefix) + 2:
        raise ValueError('Artifacts must be direct files in the request directory')
    if request_id is not None and run_request_id != request_id:
        raise ValueError('Request ID does not match the project request directory')
    if expected_name is not None and resolved.name != expected_name:
        raise ValueError(f'Expected artifact filename {expected_name}')

    project = project_root / project_id
    state_path = project / 'state/project-state.json'
    if not state_path.is_file() or state_path.is_symlink():
        raise ValueError('Selected project has no regular project-state.json')
    state = json.loads(state_path.read_text(encoding='utf-8'))
    if not isinstance(state, dict) or state.get('project_id') != project_id:
        raise ValueError('Selected project state does not match its workspace directory')

    # Existing symlink components can redirect a lexical project path elsewhere.
    try:
        lexical_relative = lexical.relative_to(project_root)
    except ValueError as error:
        raise ValueError('Artifact lexical path must remain inside the project workspace') from error
    current = project_root
    for part in lexical_relative.parts[:-1]:
        current /= part
        if current.is_symlink():
            raise ValueError('Symlinks are not allowed in durable artifact paths')
    if path.is_symlink():
        raise ValueError('Artifact path cannot be a symlink')
    return resolved


def project_reference(path, *, repository=None):
    """Return a non-sensitive project-relative reference, or a bare library filename."""
    repository = Path(repository or REPOSITORY).resolve()
    resolved = Path(path).resolve()
    try:
        return resolved.relative_to(repository).as_posix()
    except ValueError:
        # Library calls may use temporary directories; never persist their absolute path.
        return resolved.name


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def require_complete_normalization(request_path, request_id=None):
    """Reject a normalized request unless its last-published marker verifies all files."""
    request_path = Path(request_path).resolve()
    directory = request_path.parent
    marker_path = directory / NORMALIZATION_MARKER
    normalization_signals = [directory / 'normalization_summary.json',
                             directory / 'source_csvs', marker_path]
    if not any(path.exists() or path.is_symlink() for path in normalization_signals):
        return
    if not marker_path.is_file() or marker_path.is_symlink():
        raise ValueError('Normalized input is incomplete; completion marker is missing')
    marker = json.loads(marker_path.read_text(encoding='utf-8'))
    if not isinstance(marker, dict) or marker.get('status') != 'complete':
        raise ValueError('Normalized input completion marker is invalid')
    if request_id is not None and marker.get('requestId') != request_id:
        raise ValueError('Normalized input completion marker belongs to a different request')
    artifacts = marker.get('artifacts')
    if not isinstance(artifacts, dict) or request_path.name not in artifacts:
        raise ValueError('Normalized input completion marker has no request digest')
    for relative, expected in artifacts.items():
        candidate = (directory / relative).resolve()
        if not candidate.is_relative_to(directory) or not candidate.is_file() or candidate.is_symlink():
            raise ValueError('Normalized input marker contains an unsafe or missing artifact')
        if _sha256(candidate) != expected:
            raise ValueError(f'Normalized input artifact digest mismatch: {relative}')

