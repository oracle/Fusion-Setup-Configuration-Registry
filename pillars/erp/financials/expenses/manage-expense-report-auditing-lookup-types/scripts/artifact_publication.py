"""Publish local Expenses artifacts through pinned, no-follow directories.

This canonical implementation is co-shipped in each task's scripts directory so
standalone offline task bundles keep the same boundary without a new provider
dependency. Copies are checked by the Expenses publication regression suite.
Callers retain their task/project/input validation and approval responsibilities.
"""
from contextlib import ExitStack
import argparse
import base64
import json
import os
from pathlib import Path
import secrets
import sys

SUPPORTED = (all(hasattr(os, x) for x in ('O_DIRECTORY', 'O_NOFOLLOW'))
             and all(f in os.supports_dir_fd for f in (os.open, os.mkdir, os.link, os.stat, os.unlink)))
MAX_STDIN = 256 * 1024 * 1024


def _path(value):
    value = Path(value)
    if '..' in value.parts or '\0' in str(value):
        raise OSError('Artifact paths must not traverse directories.')
    value = value.absolute()
    if not value.name:
        raise OSError('Select an artifact filename.')
    return value


def _directory(path, *, create):
    """Open every component without resolving or following a substituted link."""
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    descriptor = os.open(path.anchor, flags)
    try:
        for part in path.parts[1:]:
            if create:
                try:
                    os.mkdir(part, 0o700, dir_fd=descriptor)
                except FileExistsError:
                    pass
            child = os.open(part, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _identity(info):
    return info.st_dev, info.st_ino


def _verify_directory(path, descriptor):
    current = _directory(path, create=False)
    try:
        if _identity(os.fstat(current)) != _identity(os.fstat(descriptor)):
            raise OSError('Artifact parent changed during publication.')
    finally:
        os.close(current)


def _remove_owned(descriptor, name, identity):
    try:
        current = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
        if _identity(current) == identity:
            os.unlink(name, dir_fd=descriptor)
    except FileNotFoundError:
        pass


def publish_files(files, *, mode=0o600):
    """Stage complete private bytes, then link new names; rollback only our files.

The original lexical paths are retained. Reopening a resolved absolute output
name would lose the selected directory boundary when an ancestor is replaced.
"""
    if not SUPPORTED:
        raise OSError('Safe directory-relative artifact publication is unavailable.')
    if mode not in (0o600, 0o400):
        raise ValueError("Artifact mode must be private writable or private read-only.")
    prepared = {}
    for name, content in files.items():
        path = _path(name)
        if path in prepared:
            raise OSError('Artifact destinations must be distinct.')
        if not isinstance(content, (bytes, bytearray, memoryview)):
            raise TypeError('Artifact content must be bytes.')
        prepared[path] = bytes(content)
    with ExitStack() as stack:
        directories = {}
        for path in prepared:
            if path.parent not in directories:
                fd = _directory(path.parent, create=True)
                stack.callback(os.close, fd)
                directories[path.parent] = fd
        staged, published = [], []
        try:
            for path, content in prepared.items():
                directory = directories[path.parent]
                try:
                    os.stat(path.name, dir_fd=directory, follow_symlinks=False)
                except FileNotFoundError:
                    pass
                else:
                    raise FileExistsError('Artifact destination already exists.')
                temporary = '.expense-artifact-' + secrets.token_hex(16) + '.tmp'
                fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                             0o600, dir_fd=directory)
                identity = _identity(os.fstat(fd))
                staged.append((directory, temporary, identity, path))
                try:
                    remaining = memoryview(content)
                    while remaining:
                        count = os.write(fd, remaining)
                        if count <= 0:
                            raise OSError('Incomplete artifact write.')
                        remaining = remaining[count:]
                    os.fchmod(fd, mode)
                    os.fsync(fd)
                finally:
                    os.close(fd)
            for parent, fd in directories.items():
                _verify_directory(parent, fd)
            for directory, temporary, identity, path in staged:
                os.link(temporary, path.name, src_dir_fd=directory, dst_dir_fd=directory,
                        follow_symlinks=False)
                published.append((directory, path.name, identity))
            for parent, fd in directories.items():
                _verify_directory(parent, fd)
        except BaseException:
            for directory, name, identity in reversed(published):
                _remove_owned(directory, name, identity)
            raise
        finally:
            for directory, name, identity, _ in reversed(staged):
                _remove_owned(directory, name, identity)


def publish_json(path, value, *, indent=2, sort_keys=False, ensure_ascii=True, newline=True):
    text = json.dumps(value, indent=indent, sort_keys=sort_keys, ensure_ascii=ensure_ascii)
    publish_files({path: (text + ('\n' if newline else '')).encode('utf-8')})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish-stdin', action='store_true', required=True)
    parser.parse_args()
    try:
        data = sys.stdin.buffer.read(MAX_STDIN + 1)
        if len(data) > MAX_STDIN:
            raise ValueError('Artifact publication exceeds the supported size.')
        payload = json.loads(data)
        if not isinstance(payload, dict) or set(payload) != {'files'} or not isinstance(payload['files'], list):
            raise ValueError('Expected an artifact file list.')
        files = {}
        for item in payload['files']:
            if not isinstance(item, dict) or set(item) != {'path', 'data'}:
                raise ValueError('Invalid artifact entry.')
            path = _path(item['path'])
            if path in files:
                raise ValueError('Artifact destinations must be distinct.')
            files[path] = base64.b64decode(item['data'], validate=True)
        publish_files(files)
        print(json.dumps({'status': 'published', 'files': len(files)}))
        return 0
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(json.dumps({'status': 'failed', 'failure_class': 'artifact_persistence',
                          'message': 'Artifact publication refused; use new paths under unchanged unlinked parents.'}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
