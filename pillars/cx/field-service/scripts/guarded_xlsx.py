"""Bound untrusted XLSX intake before callers build domain-specific records.

Limits are cumulative per open workbook, including repeated member reads. No
archive extraction, network access, or optional spreadsheet dependency is used.
"""
from __future__ import annotations

import os
from pathlib import Path
import re
import time
import xml.etree.ElementTree as ET
import zipfile

MAX_FILE_BYTES = 16 * 1024 * 1024
MAX_MEMBERS = 256
MAX_MEMBER_BYTES = 8 * 1024 * 1024
MAX_EXPANDED_BYTES = 32 * 1024 * 1024
MAX_RATIO = 200
MAX_SHEETS = 64
MAX_ROWS = 20000
MAX_COLUMNS = 512
MAX_CELLS = 100000
MAX_DENSE_CELLS = 1000000
MAX_STRINGS = 20000
MAX_STRING_CHARS = 32768
MAX_NODES = 250000
MAX_DEPTH = 32
MAX_SECONDS = 10
CHUNK_BYTES = 16384
MAIN = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'


def column_index(reference: str) -> int:
    # Bound the reference before regex/integer work or sparse row allocation.
    if len(reference) > 12 or not re.fullmatch(r'[A-Za-z]{1,3}[1-9][0-9]{0,6}', reference):
        raise ValueError('XLSX cell reference is invalid or exceeds coordinate limits.')
    letters = reference.rstrip('0123456789').upper()
    column = 0
    for letter in letters:
        column = column * 26 + ord(letter) - ord('A') + 1
    if column > MAX_COLUMNS or int(reference[len(letters):]) > MAX_ROWS:
        raise ValueError('XLSX coordinate limit exceeded.')
    return column


def shared_string(strings: list[str], raw: str | None) -> str:
    if raw is None or len(raw) > 8 or not re.fullmatch(r'[0-9]+', raw):
        raise ValueError('XLSX shared string index is invalid.')
    index = int(raw)
    if index >= len(strings):
        raise ValueError('XLSX shared string index is out of range.')
    return strings[index]


class _BoundedTree(ET.TreeBuilder):
    def __init__(self, archive):
        super().__init__()
        self.archive = archive
        self.depth = 0
        self.text_sizes = []
        self.tags = []
        self.row_width = 0

    def start(self, tag, attrs):
        a = self.archive
        a.check_time()
        self.depth += 1
        self.text_sizes.append(0)
        self.tags.append(tag)
        a.count('nodes', MAX_NODES)
        if self.depth > MAX_DEPTH:
            raise ValueError('XLSX XML depth limit exceeded.')
        if tag == MAIN + 'sheet':
            a.count('sheets', MAX_SHEETS)
        elif tag == MAIN + 'row':
            # A nested row would reset the outer row's allocation accounting.
            if MAIN + 'row' in self.tags[:-1]:
                raise ValueError('XLSX nested rows are not supported.')
            a.count('rows', MAX_ROWS)
            number = attrs.get('r')
            if number is not None and (len(number) > 7 or not number.isascii() or not number.isdecimal() or not 1 <= int(number) <= MAX_ROWS):
                raise ValueError('XLSX row coordinate limit exceeded.')
            self.row_width = 0
        elif tag == MAIN + 'c':
            a.count('cells', MAX_CELLS)
            self.row_width = max(self.row_width, column_index(attrs.get('r', '')))
        elif tag == MAIN + 'si':
            a.count('strings', MAX_STRINGS)
        elif tag == MAIN + 'dimension':
            for reference in attrs.get('ref', '').split(':'):
                column_index(reference)
        return super().start(tag, attrs)

    def data(self, data):
        # Track text over the whole subtree, including rich-text runs.
        for index in range(len(self.text_sizes)):
            self.text_sizes[index] += len(data)
        # Only string/value nodes have a per-value cap; document totals have
        # the independent expanded-byte and node limits.
        if self.tags and self.tags[-1] in (MAIN + 't', MAIN + 'si', MAIN + 'is', MAIN + 'v') and self.text_sizes[-1] > MAX_STRING_CHARS:
            raise ValueError('XLSX text limit exceeded.')
        return super().data(data)

    def end(self, tag):
        if tag in (MAIN + 'si', MAIN + 'is', MAIN + 'v') and self.text_sizes[-1] > MAX_STRING_CHARS:
            raise ValueError('XLSX string limit exceeded.')
        if tag == MAIN + 'row':
            self.archive.count('dense_cells', MAX_DENSE_CELLS, self.row_width)
        self.depth -= 1
        self.text_sizes.pop()
        self.tags.pop()
        return super().end(tag)

    def doctype(self, name, pubid, system):
        raise ValueError('XLSX DTDs and entities are not supported.')


class GuardedWorkbook:
    def __init__(self, path: Path):
        self.path = path
        self.counts = {}
        self.started = time.monotonic()

    def check_time(self):
        if time.monotonic() - self.started > MAX_SECONDS:
            raise ValueError('XLSX processing time limit exceeded.')

    def count(self, name, limit, amount=1):
        self.counts[name] = self.counts.get(name, 0) + amount
        if self.counts[name] > limit:
            raise ValueError(f'XLSX {name} limit exceeded.')

    def __enter__(self):
        self.source = self.path.open('rb')
        try:
            if os.fstat(self.source.fileno()).st_size > MAX_FILE_BYTES:
                raise ValueError('XLSX file byte limit exceeded.')
            self.archive = zipfile.ZipFile(self.source)
            entries = self.archive.infolist()
            if len(entries) > MAX_MEMBERS:
                raise ValueError('XLSX member count limit exceeded.')
            names = set()
            total = 0
            for entry in entries:
                self.check_time()
                if entry.filename in names:
                    raise ValueError('XLSX duplicate archive member.')
                names.add(entry.filename)
                if entry.flag_bits & 1 or entry.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
                    raise ValueError('XLSX encryption/compression is unsupported.')
                total += entry.file_size
                if entry.file_size > MAX_MEMBER_BYTES or total > MAX_EXPANDED_BYTES:
                    raise ValueError('XLSX expanded byte limit exceeded.')
                if entry.file_size > MAX_RATIO * max(entry.compress_size, 1):
                    raise ValueError('XLSX compression ratio limit exceeded.')
            return self
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def __exit__(self, *_):
        if hasattr(self, 'archive'):
            self.archive.close()
        self.source.close()

    def namelist(self):
        return self.archive.namelist()

    def xml(self, name):
        if not name.startswith('xl/') or '\\' in name or any(part in ('', '.', '..') for part in name.split('/')):
            raise ValueError('XLSX member path is unsafe.')
        parser = ET.XMLParser(target=_BoundedTree(self))
        member_bytes = 0
        with self.archive.open(name) as member:
            while True:
                self.check_time()
                chunk = member.read(min(CHUNK_BYTES, MAX_MEMBER_BYTES - member_bytes + 1))
                if not chunk:
                    break
                member_bytes += len(chunk)
                if member_bytes > MAX_MEMBER_BYTES:
                    raise ValueError('XLSX actual member byte limit exceeded.')
                self.count('expanded_bytes', MAX_EXPANDED_BYTES, len(chunk))
                parser.feed(chunk)
        self.check_time()
        return parser.close()
