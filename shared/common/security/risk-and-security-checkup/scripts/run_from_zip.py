"""Normalize all submitted roles, then run a fresh authenticated assessment."""
import argparse
from pathlib import Path
import subprocess
import sys

from normalize_job_roles_zip import normalize
from extract_tree import assessment_lock
from workspace_paths import validate_project_artifact


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--zip', required=True, type=Path, dest='source')
    parser.add_argument('--properties', type=Path, help='Selected FSCR properties; defaults to core/auth/fusionEnv.properties')
    parser.add_argument('--output-directory', required=True, type=Path)
    parser.add_argument('--request-id')
    parser.add_argument('--normalize-only', action='store_true')
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        parser.error('Python 3.10 or newer is required')
    request_id = args.request_id or args.output_directory.name
    request_path = validate_project_artifact(args.output_directory / 'calling_request.json',
                                             request_id,
                                             expected_name='calling_request.json')
    directory = request_path.parent
    if directory.exists() and any(directory.iterdir()):
        parser.error('Use a new or empty output directory; preserve existing runs. '
                     'For existing validated input use run_checkup.py after checking no assessment is running.')
    result_path = directory / 'security_checkup_result.json'
    from fscr_context import environment_from_properties
    with assessment_lock(request_path):
        _, summary = normalize(args.source, request_path,
                               environment=environment_from_properties(args.properties),
                               request_id=request_id)
    print('Normalized all roles: {}; unique memberships: {}'.format(
        summary['roleCount'], summary['uniqueRolePrivilegeMemberships']), flush=True)
    print('Input: {}'.format(request_path), flush=True)
    if args.normalize_only:
        print('Normalization only; no authentication or risk evaluation performed.', flush=True)
        return 0
    command = [sys.executable, str(Path(__file__).with_name('run_checkup.py')),
               '--input', str(request_path), '--output', str(result_path)]
    if args.properties is not None:
        command.extend(['--properties', str(args.properties)])
    # Display a reviewable resume command without credentials; never execute via a shell.
    quoted = ' '.join('"{}"'.format(value) for value in command)
    print('If runtime evaluation fails, preserve input. After resolving the error and '
          'checking no process is running, resume using:', flush=True)
    print(('& ' if sys.platform == 'win32' else '') + quoted, flush=True)
    return subprocess.run(command, check=False).returncode


if __name__ == '__main__':
    raise SystemExit(main())
