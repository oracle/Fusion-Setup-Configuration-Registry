"""Validate new artifact destinations inside an initialized FSCR project.

Pure preflight: never creates directories, modifies an index, or calls Fusion.
Call again immediately before persistence. Existing output paths are refused.
"""
import argparse
import json
import os
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[4]
INITIALIZED_STATUSES = frozenset({'initialized', 'in_progress', 'blocked', 'ready_for_review'})


class ArtifactPathError(ValueError):
    pass


def _absolute(value):
    if value is None or not str(value).strip() or '..' in Path(value).parts:
        raise ArtifactPathError('Explicit project and artifact paths without traversal are required')
    return Path(os.path.abspath(value))


def _reject_symlinks(path):
    for item in (*reversed(path.parents), path):
        if item.is_symlink():
            raise ArtifactPathError('Artifact paths must not contain symlinks')
        if item.exists() and item != path and not item.is_dir():
            raise ArtifactPathError('Artifact path ancestor is not a directory')


def validate_artifact_path(destination, project_root, *, repository_root=REPOSITORY_ROOT):
    """Require a new descendant of project/<id>/artifacts, before any writes.

    repository_root is a code-level injection point for isolated core unit tests;
    production callers/CLI always use this module's repository root.
    """
    project, output = _absolute(project_root), _absolute(destination)
    repository = _absolute(repository_root)
    if project.parent != repository/'project' or project.name.startswith('_'):
        raise ArtifactPathError('Project root must identify an initialized project/<project_id> workspace')
    _reject_symlinks(project)
    if not project.is_dir():
        raise ArtifactPathError('Project workspace does not exist')
    state_path = project/'state/project-state.json'
    _reject_symlinks(state_path)
    try:
        if state_path.stat().st_size > 1024*1024:
            raise ArtifactPathError('Project state is too large')
        state = json.loads(state_path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as error:
        raise ArtifactPathError('Initialized project state is required') from error
    if not isinstance(state, dict) or state.get('status') not in INITIALIZED_STATUSES:
        raise ArtifactPathError('Initialized project state is required')
    artifacts = project/'artifacts'
    if artifacts not in output.parents:
        raise ArtifactPathError('Output must be inside the selected project artifacts directory')
    _reject_symlinks(output)
    if output.exists():
        raise ArtifactPathError('Output path already exists')
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        destination = validate_artifact_path(args.output, args.project_root)
        print(json.dumps({'status':'validated_artifact_destination','output':str(destination),'writes':0}))
        return 0
    except (ArtifactPathError, OSError):
        print(json.dumps({'status':'blocked','failure_class':'input_validation',
            'message':'Select a new nonsymlinked artifact destination in an initialized project workspace'}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
