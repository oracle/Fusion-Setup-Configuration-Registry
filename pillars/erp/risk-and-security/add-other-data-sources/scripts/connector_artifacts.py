"""Contain connector approval artifacts within the selected project workspace."""

from __future__ import annotations

import json
import os
import stat
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


def artifact_path(project_root: str | Path, path: str | Path) -> Path:
    root = Path(project_root).resolve(strict=True)
    candidate = Path(path).absolute()
    if ".." in candidate.parts or not candidate.is_relative_to(root):
        raise ValueError("artifact path must remain inside the selected project workspace")
    current = root
    for part in candidate.relative_to(root).parts:
        current /= part
        if current.is_symlink():
            raise ValueError("artifact path must not contain a symlink")
    if not candidate.resolve().is_relative_to(root):
        raise ValueError("artifact path resolves outside the selected project workspace")
    return candidate


@contextmanager
def artifact_directory(project_root: str | Path, path: Path,
                       *, create: bool = False) -> Iterator[int]:
    """Open every directory component without following links, including at write time."""
    directory = artifact_path(project_root, path)
    root = Path(project_root).resolve(strict=True)
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    fd = os.open(root, flags)
    try:
        for part in directory.relative_to(root).parts:
            if create:
                try:
                    os.mkdir(part, mode=0o700, dir_fd=fd)
                except FileExistsError:
                    pass
            child = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = child
        yield fd
    finally:
        os.close(fd)


def _write_new_text(directory_fd: int, name: str, contents: str) -> None:
    fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                 0o600, dir_fd=directory_fd)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(contents)
        handle.flush()
        os.fsync(handle.fileno())


def write_new_text(path: Path, contents: str, project_root: str | Path) -> None:
    destination = artifact_path(project_root, path)
    with artifact_directory(project_root, destination.parent) as fd:
        _write_new_text(fd, destination.name, contents)


def new_preview_directory(current: Path, project_root: str | Path) -> Path:
    pointer = artifact_path(project_root, current / "latest-approval.json")
    if pointer.exists() and not pointer.is_file():
        raise ValueError("current approval pointer must be a regular file")
    versions = artifact_path(project_root, current / "approvals")
    with artifact_directory(project_root, versions, create=True) as fd:
        name = "preview-" + uuid.uuid4().hex
        os.mkdir(name, mode=0o700, dir_fd=fd)
    return versions / name


def publish_current_pointer(current: Path, value: dict,
                            project_root: str | Path) -> Path:
    pointer = artifact_path(project_root, current / "latest-approval.json")
    with artifact_directory(project_root, current) as fd:
        try:
            existing = os.stat(pointer.name, dir_fd=fd, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            if not stat.S_ISREG(existing.st_mode):
                raise ValueError("current approval pointer must be a regular file")
        temporary = ".latest-approval-" + uuid.uuid4().hex
        created = False
        try:
            _write_new_text(fd, temporary, json.dumps(value, ensure_ascii=False, indent=2) + "\n")
            created = True
            # Replaces the directory entry itself; never follows its target.
            os.replace(temporary, pointer.name, src_dir_fd=fd, dst_dir_fd=fd)
        finally:
            if created:
                try:
                    os.unlink(temporary, dir_fd=fd)
                except FileNotFoundError:
                    pass
    return pointer
