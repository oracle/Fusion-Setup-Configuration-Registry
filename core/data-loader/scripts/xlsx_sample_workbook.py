"""Create and parse editable Data Loader sample workbooks without third-party packages."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import posixpath
import re
import stat
import subprocess
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Iterable
from xml.etree import ElementTree as ET

try:
    import data_loader_metadata as metadata
except ModuleNotFoundError:
    from scripts import data_loader_metadata as metadata


MAX_SHEET_NAME_LENGTH = 30
_MAX_XLSX_ROW = 1_048_576
_MAX_XLSX_COLUMN = 16_384
# Bound rectangular output even when a legal, very wide header is supplied.
_MAX_SHEET_OUTPUT_CELLS = 1_000_000
_ILLEGAL_SHEET_NAME_CHARACTERS = re.compile(r"[\[\]:*?/\\]")
_RESERVED_SHEET_NAMES = frozenset({"history"})
LEGACY_MAP_SHEET = "Data Loader Map"
LEGACY_MAP_HEADERS = ("Sheet Name", "Discriminator", "Parent Discriminator", "Business Object Name")
SET_COMMANDS_SHEET = "set commands"
ATTRIBUTE_DETAILS_HEADERS = (
    "Attribute Name", "Display Label", "Description", "Data Type", "Required",
    "Key Classification", "User-Key Alternatives", "Reference Type", "Reference Object",
    "Lookup Name", "Maximum Length", "Number Precision", "Hidden",
)

_MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
_XML_NS = "http://www.w3.org/XML/1998/namespace"
_CORE_PROPERTIES_NS = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
_EXTENDED_PROPERTIES_NS = "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
_DC_NS = "http://purl.org/dc/elements/1.1/"
_DCTERMS_NS = "http://purl.org/dc/terms/"
_XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
_VT_NS = "http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"
_NS = {"x": _MAIN_NS, "r": _REL_NS, "pr": _PKG_REL_NS}
_DATE_FORMAT_IDS = frozenset({14, 15, 16, 17, 18, 19, 20, 21, 22, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 45, 46, 47, 50, 51, 52, 53, 54, 55, 56, 57, 58})
_BUILTIN_DATE_FORMATS = {
    15: "d-mmm-yy", 16: "d-mmm", 17: "mmm-yy",
    18: "h:mm AM/PM", 19: "h:mm:ss AM/PM", 20: "h:mm",
    21: "h:mm:ss", 22: "m/d/yy h:mm",
}
_DISPLAY_DATE_TOKEN = re.compile(
    r'AM/PM|yyyy|mmmm|dddd|mmm|ddd|yy|mm|dd|hh|ss|y|m|d|h|s|"[^"]*"|\\.|[ /:.,-]+',
    re.IGNORECASE,
)
_CELL_REF = re.compile(r"^([A-Z]+)([1-9][0-9]*)$")
_ARTIFACT_WRITER = Path(__file__).with_name("artifact_xlsx_writer.cjs")

_STYLE_XML = base64.b64decode(
    "PHN0eWxlU2hlZXQgeG1sbnM9Imh0dHA6Ly9zY2hlbWFzLm9wZW54bWxmb3JtYXRzLm9yZy9zcHJlYWRzaGVldG1sLzIwMDYvbWFp"
    "biI+PG51bUZtdHMgY291bnQ9IjAiLz48Zm9udHMgY291bnQ9IjEiPjxmb250PjxuYW1lIHZhbD0iQ2FsaWJyaSIvPjxmYW1pbHkg"
    "dmFsPSIyIi8+PGNvbG9yIHRoZW1lPSIxIi8+PHN6IHZhbD0iMTEiLz48c2NoZW1lIHZhbD0ibWlub3IiLz48L2ZvbnQ+PC9mb250"
    "cz48ZmlsbHMgY291bnQ9IjIiPjxmaWxsPjxwYXR0ZXJuRmlsbC8+PC9maWxsPjxmaWxsPjxwYXR0ZXJuRmlsbCBwYXR0ZXJuVHlw"
    "ZT0iZ3JheTEyNSIvPjwvZmlsbD48L2ZpbGxzPjxib3JkZXJzIGNvdW50PSIxIj48Ym9yZGVyPjxsZWZ0Lz48cmlnaHQvPjx0b3Av"
    "Pjxib3R0b20vPjxkaWFnb25hbC8+PC9ib3JkZXI+PC9ib3JkZXJzPjxjZWxsU3R5bGVYZnMgY291bnQ9IjEiPjx4ZiBudW1GbXRJ"
    "ZD0iMCIgZm9udElkPSIwIiBmaWxsSWQ9IjAiIGJvcmRlcklkPSIwIi8+PC9jZWxsU3R5bGVYZnM+PGNlbGxYZnMgY291bnQ9IjEi"
    "Pjx4ZiBudW1GbXRJZD0iMCIgZm9udElkPSIwIiBmaWxsSWQ9IjAiIGJvcmRlcklkPSIwIiBwaXZvdEJ1dHRvbj0iMCIgcXVvdGVQ"
    "cmVmaXg9IjAiIHhmSWQ9IjAiLz48L2NlbGxYZnM+PGNlbGxTdHlsZXMgY291bnQ9IjEiPjxjZWxsU3R5bGUgbmFtZT0iTm9ybWFs"
    "IiB4ZklkPSIwIiBidWlsdGluSWQ9IjAiIGhpZGRlbj0iMCIvPjwvY2VsbFN0eWxlcz48dGFibGVTdHlsZXMgY291bnQ9IjAiIGRl"
    "ZmF1bHRUYWJsZVN0eWxlPSJUYWJsZVN0eWxlTWVkaXVtOSIgZGVmYXVsdFBpdm90U3R5bGU9IlBpdm90U3R5bGVMaWdodDE2Ii8+"
    "PGNvbG9ycz48aW5kZXhlZENvbG9ycz48cmdiQ29sb3IgcmdiPSIwMDAwMDAwMCIvPjxyZ2JDb2xvciByZ2I9IjAwRkZGRkZGIi8+"
    "PHJnYkNvbG9yIHJnYj0iMDBGRjAwMDAiLz48cmdiQ29sb3IgcmdiPSIwMDAwRkYwMCIvPjxyZ2JDb2xvciByZ2I9IjAwMDAwMEZG"
    "Ii8+PHJnYkNvbG9yIHJnYj0iMDBGRkZGMDAiLz48cmdiQ29sb3IgcmdiPSIwMEZGMDBGRiIvPjxyZ2JDb2xvciByZ2I9IjAwMDBG"
    "RkZGIi8+PHJnYkNvbG9yIHJnYj0iMDAwMDAwMDAiLz48cmdiQ29sb3IgcmdiPSIwMEZGRkZGRiIvPjxyZ2JDb2xvciByZ2I9IjAw"
    "RkYwMDAwIi8+PHJnYkNvbG9yIHJnYj0iMDAwMEZGMDAiLz48cmdiQ29sb3IgcmdiPSIwMDAwMDBGRiIvPjxyZ2JDb2xvciByZ2I9"
    "IjAwRkZGRjAwIi8+PHJnYkNvbG9yIHJnYj0iMDBGRjAwRkYiLz48cmdiQ29sb3IgcmdiPSIwMDAwRkZGRiIvPjxyZ2JDb2xvciBy"
    "Z2I9IjAwODAwMDAwIi8+PHJnYkNvbG9yIHJnYj0iMDAwMDgwMDAiLz48cmdiQ29sb3IgcmdiPSIwMDAwMDA4MCIvPjxyZ2JDb2xv"
    "ciByZ2I9IjAwODA4MDAwIi8+PHJnYkNvbG9yIHJnYj0iMDA4MDAwODAiLz48cmdiQ29sb3IgcmdiPSIwMDAwODA4MCIvPjxyZ2JD"
    "b2xvciByZ2I9IjAwQzBDMEMwIi8+PHJnYkNvbG9yIHJnYj0iMDA4MDgwODAiLz48cmdiQ29sb3IgcmdiPSIwMDk5OTlGRiIvPjxy"
    "Z2JDb2xvciByZ2I9IjAwOTkzMzY2Ii8+PHJnYkNvbG9yIHJnYj0iMDBGRkZGQ0MiLz48cmdiQ29sb3IgcmdiPSIwMENDRkZGRiIv"
    "PjxyZ2JDb2xvciByZ2I9IjAwNjYwMDY2Ii8+PHJnYkNvbG9yIHJnYj0iMDBGRjgwODAiLz48cmdiQ29sb3IgcmdiPSIwMDAwNjZD"
    "QyIvPjxyZ2JDb2xvciByZ2I9IjAwQ0NDQ0ZGIi8+PHJnYkNvbG9yIHJnYj0iMDAwMDAwODAiLz48cmdiQ29sb3IgcmdiPSIwMEZG"
    "MDBGRiIvPjxyZ2JDb2xvciByZ2I9IjAwRkZGRjAwIi8+PHJnYkNvbG9yIHJnYj0iMDAwMEZGRkYiLz48cmdiQ29sb3IgcmdiPSIw"
    "MDgwMDA4MCIvPjxyZ2JDb2xvciByZ2I9IjAwODAwMDAwIi8+PHJnYkNvbG9yIHJnYj0iMDAwMDgwODAiLz48cmdiQ29sb3Igcmdi"
    "PSIwMDAwMDBGRiIvPjxyZ2JDb2xvciByZ2I9IjAwMDBDQ0ZGIi8+PHJnYkNvbG9yIHJnYj0iMDBDQ0ZGRkYiLz48cmdiQ29sb3Ig"
    "cmdiPSIwMENDRkZDQyIvPjxyZ2JDb2xvciByZ2I9IjAwRkZGRjk5Ii8+PHJnYkNvbG9yIHJnYj0iMDA5OUNDRkYiLz48cmdiQ29s"
    "b3IgcmdiPSIwMEZGOTlDQyIvPjxyZ2JDb2xvciByZ2I9IjAwQ0M5OUZGIi8+PHJnYkNvbG9yIHJnYj0iMDBGRkNDOTkiLz48cmdi"
    "Q29sb3IgcmdiPSIwMDMzNjZGRiIvPjxyZ2JDb2xvciByZ2I9IjAwMzNDQ0NDIi8+PHJnYkNvbG9yIHJnYj0iMDA5OUNDMDAiLz48"
    "cmdiQ29sb3IgcmdiPSIwMEZGQ0MwMCIvPjxyZ2JDb2xvciByZ2I9IjAwRkY5OTAwIi8+PHJnYkNvbG9yIHJnYj0iMDBGRjY2MDAi"
    "Lz48cmdiQ29sb3IgcmdiPSIwMDY2NjY5OSIvPjxyZ2JDb2xvciByZ2I9IjAwOTY5Njk2Ii8+PHJnYkNvbG9yIHJnYj0iMDAwMDMz"
    "NjYiLz48cmdiQ29sb3IgcmdiPSIwMDMzOTk2NiIvPjxyZ2JDb2xvciByZ2I9IjAwMDAzMzAwIi8+PHJnYkNvbG9yIHJnYj0iMDAz"
    "MzMzMDAiLz48cmdiQ29sb3IgcmdiPSIwMDk5MzMwMCIvPjxyZ2JDb2xvciByZ2I9IjAwOTkzMzY2Ii8+PHJnYkNvbG9yIHJnYj0i"
    "MDAzMzMzOTkiLz48cmdiQ29sb3IgcmdiPSIwMDMzMzMzMyIvPjwvaW5kZXhlZENvbG9ycz48L2NvbG9ycz48L3N0eWxlU2hlZXQ+"
)

_THEME_XML = base64.b64decode(
    "PD94bWwgdmVyc2lvbj0iMS4wIj8+CjxhOnRoZW1lIHhtbG5zOmE9Imh0dHA6Ly9zY2hlbWFzLm9wZW54bWxmb3JtYXRzLm9yZy9k"
    "cmF3aW5nbWwvMjAwNi9tYWluIiBuYW1lPSJPZmZpY2UgVGhlbWUiPgogIDxhOnRoZW1lRWxlbWVudHM+CiAgICA8YTpjbHJTY2hl"
    "bWUgbmFtZT0iT2ZmaWNlIj4KICAgICAgPGE6ZGsxPgogICAgICAgIDxhOnN5c0NsciB2YWw9IndpbmRvd1RleHQiIGxhc3RDbHI9"
    "IjAwMDAwMCIvPgogICAgICA8L2E6ZGsxPgogICAgICA8YTpsdDE+CiAgICAgICAgPGE6c3lzQ2xyIHZhbD0id2luZG93IiBsYXN0"
    "Q2xyPSJGRkZGRkYiLz4KICAgICAgPC9hOmx0MT4KICAgICAgPGE6ZGsyPgogICAgICAgIDxhOnNyZ2JDbHIgdmFsPSIxRjQ5N0Qi"
    "Lz4KICAgICAgPC9hOmRrMj4KICAgICAgPGE6bHQyPgogICAgICAgIDxhOnNyZ2JDbHIgdmFsPSJFRUVDRTEiLz4KICAgICAgPC9h"
    "Omx0Mj4KICAgICAgPGE6YWNjZW50MT4KICAgICAgICA8YTpzcmdiQ2xyIHZhbD0iNEY4MUJEIi8+CiAgICAgIDwvYTphY2NlbnQx"
    "PgogICAgICA8YTphY2NlbnQyPgogICAgICAgIDxhOnNyZ2JDbHIgdmFsPSJDMDUwNEQiLz4KICAgICAgPC9hOmFjY2VudDI+CiAg"
    "ICAgIDxhOmFjY2VudDM+CiAgICAgICAgPGE6c3JnYkNsciB2YWw9IjlCQkI1OSIvPgogICAgICA8L2E6YWNjZW50Mz4KICAgICAg"
    "PGE6YWNjZW50ND4KICAgICAgICA8YTpzcmdiQ2xyIHZhbD0iODA2NEEyIi8+CiAgICAgIDwvYTphY2NlbnQ0PgogICAgICA8YTph"
    "Y2NlbnQ1PgogICAgICAgIDxhOnNyZ2JDbHIgdmFsPSI0QkFDQzYiLz4KICAgICAgPC9hOmFjY2VudDU+CiAgICAgIDxhOmFjY2Vu"
    "dDY+CiAgICAgICAgPGE6c3JnYkNsciB2YWw9IkY3OTY0NiIvPgogICAgICA8L2E6YWNjZW50Nj4KICAgICAgPGE6aGxpbms+CiAg"
    "ICAgICAgPGE6c3JnYkNsciB2YWw9IjAwMDBGRiIvPgogICAgICA8L2E6aGxpbms+CiAgICAgIDxhOmZvbEhsaW5rPgogICAgICAg"
    "IDxhOnNyZ2JDbHIgdmFsPSI4MDAwODAiLz4KICAgICAgPC9hOmZvbEhsaW5rPgogICAgPC9hOmNsclNjaGVtZT4KICAgIDxhOmZv"
    "bnRTY2hlbWUgbmFtZT0iT2ZmaWNlIj4KICAgICAgPGE6bWFqb3JGb250PgogICAgICAgIDxhOmxhdGluIHR5cGVmYWNlPSJDYW1i"
    "cmlhIi8+CiAgICAgICAgPGE6ZWEgdHlwZWZhY2U9IiIvPgogICAgICAgIDxhOmNzIHR5cGVmYWNlPSIiLz4KICAgICAgICA8YTpm"
    "b250IHNjcmlwdD0iSnBhbiIgdHlwZWZhY2U9IiYjeEZGMkQ7JiN4RkYzMzsgJiN4RkYzMDsmI3gzMEI0OyYjeDMwQjc7JiN4MzBD"
    "MzsmI3gzMEFGOyIvPgogICAgICAgIDxhOmZvbnQgc2NyaXB0PSJIYW5nIiB0eXBlZmFjZT0iJiN4QjlEMTsmI3hDNzQwOyAmI3hB"
    "Q0UwOyYjeEI1MTU7Ii8+CiAgICAgICAgPGE6Zm9udCBzY3JpcHQ9IkhhbnMiIHR5cGVmYWNlPSImI3g1QjhCOyYjeDRGNTM7Ii8+"
    "CiAgICAgICAgPGE6Zm9udCBzY3JpcHQ9IkhhbnQiIHR5cGVmYWNlPSImI3g2NUIwOyYjeDdEMzA7JiN4NjYwRTsmI3g5QUQ0OyIv"
    "PgogICAgICAgIDxhOmZvbnQgc2NyaXB0PSJBcmFiIiB0eXBlZmFjZT0iVGltZXMgTmV3IFJvbWFuIi8+CiAgICAgICAgPGE6Zm9u"
    "dCBzY3JpcHQ9IkhlYnIiIHR5cGVmYWNlPSJUaW1lcyBOZXcgUm9tYW4iLz4KICAgICAgICA8YTpmb250IHNjcmlwdD0iVGhhaSIg"
    "dHlwZWZhY2U9IlRhaG9tYSIvPgogICAgICAgIDxhOmZvbnQgc2NyaXB0PSJFdGhpIiB0eXBlZmFjZT0iTnlhbGEiLz4KICAgICAg"
    "ICA8YTpmb250IHNjcmlwdD0iQmVuZyIgdHlwZWZhY2U9IlZyaW5kYSIvPgogICAgICAgIDxhOmZvbnQgc2NyaXB0PSJHdWpyIiB0"
    "eXBlZmFjZT0iU2hydXRpIi8+CiAgICAgICAgPGE6Zm9udCBzY3JpcHQ9IktobXIiIHR5cGVmYWNlPSJNb29sQm9yYW4iLz4KICAg"
    "ICAgICA8YTpmb250IHNjcmlwdD0iS25kYSIgdHlwZWZhY2U9IlR1bmdhIi8+CiAgICAgICAgPGE6Zm9udCBzY3JpcHQ9Ikd1cnUi"
    "IHR5cGVmYWNlPSJSYWF2aSIvPgogICAgICAgIDxhOmZvbnQgc2NyaXB0PSJDYW5zIiB0eXBlZmFjZT0iRXVwaGVtaWEiLz4KICAg"
    "ICAgICA8YTpmb250IHNjcmlwdD0iQ2hlciIgdHlwZWZhY2U9IlBsYW50YWdlbmV0IENoZXJva2VlIi8+CiAgICAgICAgPGE6Zm9u"
    "dCBzY3JpcHQ9IllpaWkiIHR5cGVmYWNlPSJNaWNyb3NvZnQgWWkgQmFpdGkiLz4KICAgICAgICA8YTpmb250IHNjcmlwdD0iVGli"
    "dCIgdHlwZWZhY2U9Ik1pY3Jvc29mdCBIaW1hbGF5YSIvPgogICAgICAgIDxhOmZvbnQgc2NyaXB0PSJUaGFhIiB0eXBlZmFjZT0i"
    "TVYgQm9saSIvPgogICAgICAgIDxhOmZvbnQgc2NyaXB0PSJEZXZhIiB0eXBlZmFjZT0iTWFuZ2FsIi8+CiAgICAgICAgPGE6Zm9u"
    "dCBzY3JpcHQ9IlRlbHUiIHR5cGVmYWNlPSJHYXV0YW1pIi8+CiAgICAgICAgPGE6Zm9udCBzY3JpcHQ9IlRhbWwiIHR5cGVmYWNl"
    "PSJMYXRoYSIvPgogICAgICAgIDxhOmZvbnQgc2NyaXB0PSJTeXJjIiB0eXBlZmFjZT0iRXN0cmFuZ2VsbyBFZGVzc2EiLz4KICAg"
    "ICAgICA8YTpmb250IHNjcmlwdD0iT3J5YSIgdHlwZWZhY2U9IkthbGluZ2EiLz4KICAgICAgICA8YTpmb250IHNjcmlwdD0iTWx5"
    "bSIgdHlwZWZhY2U9IkthcnRpa2EiLz4KICAgICAgICA8YTpmb250IHNjcmlwdD0iTGFvbyIgdHlwZWZhY2U9IkRva0NoYW1wYSIv"
    "PgogICAgICAgIDxhOmZvbnQgc2NyaXB0PSJTaW5oIiB0eXBlZmFjZT0iSXNrb29sYSBQb3RhIi8+CiAgICAgICAgPGE6Zm9udCBz"
    "Y3JpcHQ9Ik1vbmciIHR5cGVmYWNlPSJNb25nb2xpYW4gQmFpdGkiLz4KICAgICAgICA8YTpmb250IHNjcmlwdD0iVmlldCIgdHlw"
    "ZWZhY2U9IlRpbWVzIE5ldyBSb21hbiIvPgogICAgICAgIDxhOmZvbnQgc2NyaXB0PSJVaWdoIiB0eXBlZmFjZT0iTWljcm9zb2Z0"
    "IFVpZ2h1ciIvPgogICAgICA8L2E6bWFqb3JGb250PgogICAgICA8YTptaW5vckZvbnQ+CiAgICAgICAgPGE6bGF0aW4gdHlwZWZh"
    "Y2U9IkNhbGlicmkiLz4KICAgICAgICA8YTplYSB0eXBlZmFjZT0iIi8+CiAgICAgICAgPGE6Y3MgdHlwZWZhY2U9IiIvPgogICAg"
    "ICAgIDxhOmZvbnQgc2NyaXB0PSJKcGFuIiB0eXBlZmFjZT0iJiN4RkYyRDsmI3hGRjMzOyAmI3hGRjMwOyYjeDMwQjQ7JiN4MzBC"
    "NzsmI3gzMEMzOyYjeDMwQUY7Ii8+CiAgICAgICAgPGE6Zm9udCBzY3JpcHQ9IkhhbmciIHR5cGVmYWNlPSImI3hCOUQxOyYjeEM3"
    "NDA7ICYjeEFDRTA7JiN4QjUxNTsiLz4KICAgICAgICA8YTpmb250IHNjcmlwdD0iSGFucyIgdHlwZWZhY2U9IiYjeDVCOEI7JiN4"
    "NEY1MzsiLz4KICAgICAgICA8YTpmb250IHNjcmlwdD0iSGFudCIgdHlwZWZhY2U9IiYjeDY1QjA7JiN4N0QzMDsmI3g2NjBFOyYj"
    "eDlBRDQ7Ii8+CiAgICAgICAgPGE6Zm9udCBzY3JpcHQ9IkFyYWIiIHR5cGVmYWNlPSJBcmlhbCIvPgogICAgICAgIDxhOmZvbnQg"
    "c2NyaXB0PSJIZWJyIiB0eXBlZmFjZT0iQXJpYWwiLz4KICAgICAgICA8YTpmb250IHNjcmlwdD0iVGhhaSIgdHlwZWZhY2U9IlRh"
    "aG9tYSIvPgogICAgICAgIDxhOmZvbnQgc2NyaXB0PSJFdGhpIiB0eXBlZmFjZT0iTnlhbGEiLz4KICAgICAgICA8YTpmb250IHNj"
    "cmlwdD0iQmVuZyIgdHlwZWZhY2U9IlZyaW5kYSIvPgogICAgICAgIDxhOmZvbnQgc2NyaXB0PSJHdWpyIiB0eXBlZmFjZT0iU2hy"
    "dXRpIi8+CiAgICAgICAgPGE6Zm9udCBzY3JpcHQ9IktobXIiIHR5cGVmYWNlPSJEYXVuUGVuaCIvPgogICAgICAgIDxhOmZvbnQg"
    "c2NyaXB0PSJLbmRhIiB0eXBlZmFjZT0iVHVuZ2EiLz4KICAgICAgICA8YTpmb250IHNjcmlwdD0iR3VydSIgdHlwZWZhY2U9IlJh"
    "YXZpIi8+CiAgICAgICAgPGE6Zm9udCBzY3JpcHQ9IkNhbnMiIHR5cGVmYWNlPSJFdXBoZW1pYSIvPgogICAgICAgIDxhOmZvbnQg"
    "c2NyaXB0PSJDaGVyIiB0eXBlZmFjZT0iUGxhbnRhZ2VuZXQgQ2hlcm9rZWUiLz4KICAgICAgICA8YTpmb250IHNjcmlwdD0iWWlp"
    "aSIgdHlwZWZhY2U9Ik1pY3Jvc29mdCBZaSBCYWl0aSIvPgogICAgICAgIDxhOmZvbnQgc2NyaXB0PSJUaWJ0IiB0eXBlZmFjZT0i"
    "TWljcm9zb2Z0IEhpbWFsYXlhIi8+CiAgICAgICAgPGE6Zm9udCBzY3JpcHQ9IlRoYWEiIHR5cGVmYWNlPSJNViBCb2xpIi8+CiAg"
    "ICAgICAgPGE6Zm9udCBzY3JpcHQ9IkRldmEiIHR5cGVmYWNlPSJNYW5nYWwiLz4KICAgICAgICA8YTpmb250IHNjcmlwdD0iVGVs"
    "dSIgdHlwZWZhY2U9IkdhdXRhbWkiLz4KICAgICAgICA8YTpmb250IHNjcmlwdD0iVGFtbCIgdHlwZWZhY2U9IkxhdGhhIi8+CiAg"
    "ICAgICAgPGE6Zm9udCBzY3JpcHQ9IlN5cmMiIHR5cGVmYWNlPSJFc3RyYW5nZWxvIEVkZXNzYSIvPgogICAgICAgIDxhOmZvbnQg"
    "c2NyaXB0PSJPcnlhIiB0eXBlZmFjZT0iS2FsaW5nYSIvPgogICAgICAgIDxhOmZvbnQgc2NyaXB0PSJNbHltIiB0eXBlZmFjZT0i"
    "S2FydGlrYSIvPgogICAgICAgIDxhOmZvbnQgc2NyaXB0PSJMYW9vIiB0eXBlZmFjZT0iRG9rQ2hhbXBhIi8+CiAgICAgICAgPGE6"
    "Zm9udCBzY3JpcHQ9IlNpbmgiIHR5cGVmYWNlPSJJc2tvb2xhIFBvdGEiLz4KICAgICAgICA8YTpmb250IHNjcmlwdD0iTW9uZyIg"
    "dHlwZWZhY2U9Ik1vbmdvbGlhbiBCYWl0aSIvPgogICAgICAgIDxhOmZvbnQgc2NyaXB0PSJWaWV0IiB0eXBlZmFjZT0iQXJpYWwi"
    "Lz4KICAgICAgICA8YTpmb250IHNjcmlwdD0iVWlnaCIgdHlwZWZhY2U9Ik1pY3Jvc29mdCBVaWdodXIiLz4KICAgICAgPC9hOm1p"
    "bm9yRm9udD4KICAgIDwvYTpmb250U2NoZW1lPgogICAgPGE6Zm10U2NoZW1lIG5hbWU9Ik9mZmljZSI+CiAgICAgIDxhOmZpbGxT"
    "dHlsZUxzdD4KICAgICAgICA8YTpzb2xpZEZpbGw+CiAgICAgICAgICA8YTpzY2hlbWVDbHIgdmFsPSJwaENsciIvPgogICAgICAg"
    "IDwvYTpzb2xpZEZpbGw+CiAgICAgICAgPGE6Z3JhZEZpbGwgcm90V2l0aFNoYXBlPSIxIj4KICAgICAgICAgIDxhOmdzTHN0Pgog"
    "ICAgICAgICAgICA8YTpncyBwb3M9IjAiPgogICAgICAgICAgICAgIDxhOnNjaGVtZUNsciB2YWw9InBoQ2xyIj4KICAgICAgICAg"
    "ICAgICAgIDxhOnRpbnQgdmFsPSI1MDAwMCIvPgogICAgICAgICAgICAgICAgPGE6c2F0TW9kIHZhbD0iMzAwMDAwIi8+CiAgICAg"
    "ICAgICAgICAgPC9hOnNjaGVtZUNscj4KICAgICAgICAgICAgPC9hOmdzPgogICAgICAgICAgICA8YTpncyBwb3M9IjM1MDAwIj4K"
    "ICAgICAgICAgICAgICA8YTpzY2hlbWVDbHIgdmFsPSJwaENsciI+CiAgICAgICAgICAgICAgICA8YTp0aW50IHZhbD0iMzcwMDAi"
    "Lz4KICAgICAgICAgICAgICAgIDxhOnNhdE1vZCB2YWw9IjMwMDAwMCIvPgogICAgICAgICAgICAgIDwvYTpzY2hlbWVDbHI+CiAg"
    "ICAgICAgICAgIDwvYTpncz4KICAgICAgICAgICAgPGE6Z3MgcG9zPSIxMDAwMDAiPgogICAgICAgICAgICAgIDxhOnNjaGVtZUNs"
    "ciB2YWw9InBoQ2xyIj4KICAgICAgICAgICAgICAgIDxhOnRpbnQgdmFsPSIxNTAwMCIvPgogICAgICAgICAgICAgICAgPGE6c2F0"
    "TW9kIHZhbD0iMzUwMDAwIi8+CiAgICAgICAgICAgICAgPC9hOnNjaGVtZUNscj4KICAgICAgICAgICAgPC9hOmdzPgogICAgICAg"
    "ICAgPC9hOmdzTHN0PgogICAgICAgICAgPGE6bGluIGFuZz0iMTYyMDAwMDAiIHNjYWxlZD0iMSIvPgogICAgICAgIDwvYTpncmFk"
    "RmlsbD4KICAgICAgICA8YTpncmFkRmlsbCByb3RXaXRoU2hhcGU9IjEiPgogICAgICAgICAgPGE6Z3NMc3Q+CiAgICAgICAgICAg"
    "IDxhOmdzIHBvcz0iMCI+CiAgICAgICAgICAgICAgPGE6c2NoZW1lQ2xyIHZhbD0icGhDbHIiPgogICAgICAgICAgICAgICAgPGE6"
    "c2hhZGUgdmFsPSI1MTAwMCIvPgogICAgICAgICAgICAgICAgPGE6c2F0TW9kIHZhbD0iMTMwMDAwIi8+CiAgICAgICAgICAgICAg"
    "PC9hOnNjaGVtZUNscj4KICAgICAgICAgICAgPC9hOmdzPgogICAgICAgICAgICA8YTpncyBwb3M9IjgwMDAwIj4KICAgICAgICAg"
    "ICAgICA8YTpzY2hlbWVDbHIgdmFsPSJwaENsciI+CiAgICAgICAgICAgICAgICA8YTpzaGFkZSB2YWw9IjkzMDAwIi8+CiAgICAg"
    "ICAgICAgICAgICA8YTpzYXRNb2QgdmFsPSIxMzAwMDAiLz4KICAgICAgICAgICAgICA8L2E6c2NoZW1lQ2xyPgogICAgICAgICAg"
    "ICA8L2E6Z3M+CiAgICAgICAgICAgIDxhOmdzIHBvcz0iMTAwMDAwIj4KICAgICAgICAgICAgICA8YTpzY2hlbWVDbHIgdmFsPSJw"
    "aENsciI+CiAgICAgICAgICAgICAgICA8YTpzaGFkZSB2YWw9Ijk0MDAwIi8+CiAgICAgICAgICAgICAgICA8YTpzYXRNb2QgdmFs"
    "PSIxMzUwMDAiLz4KICAgICAgICAgICAgICA8L2E6c2NoZW1lQ2xyPgogICAgICAgICAgICA8L2E6Z3M+CiAgICAgICAgICA8L2E6"
    "Z3NMc3Q+CiAgICAgICAgICA8YTpsaW4gYW5nPSIxNjIwMDAwMCIgc2NhbGVkPSIwIi8+CiAgICAgICAgPC9hOmdyYWRGaWxsPgog"
    "ICAgICA8L2E6ZmlsbFN0eWxlTHN0PgogICAgICA8YTpsblN0eWxlTHN0PgogICAgICAgIDxhOmxuIHc9Ijk1MjUiIGNhcD0iZmxh"
    "dCIgY21wZD0ic25nIiBhbGduPSJjdHIiPgogICAgICAgICAgPGE6c29saWRGaWxsPgogICAgICAgICAgICA8YTpzY2hlbWVDbHIg"
    "dmFsPSJwaENsciI+CiAgICAgICAgICAgICAgPGE6c2hhZGUgdmFsPSI5NTAwMCIvPgogICAgICAgICAgICAgIDxhOnNhdE1vZCB2"
    "YWw9IjEwNTAwMCIvPgogICAgICAgICAgICA8L2E6c2NoZW1lQ2xyPgogICAgICAgICAgPC9hOnNvbGlkRmlsbD4KICAgICAgICAg"
    "IDxhOnByc3REYXNoIHZhbD0ic29saWQiLz4KICAgICAgICA8L2E6bG4+CiAgICAgICAgPGE6bG4gdz0iMjU0MDAiIGNhcD0iZmxh"
    "dCIgY21wZD0ic25nIiBhbGduPSJjdHIiPgogICAgICAgICAgPGE6c29saWRGaWxsPgogICAgICAgICAgICA8YTpzY2hlbWVDbHIg"
    "dmFsPSJwaENsciIvPgogICAgICAgICAgPC9hOnNvbGlkRmlsbD4KICAgICAgICAgIDxhOnByc3REYXNoIHZhbD0ic29saWQiLz4K"
    "ICAgICAgICA8L2E6bG4+CiAgICAgICAgPGE6bG4gdz0iMzgxMDAiIGNhcD0iZmxhdCIgY21wZD0ic25nIiBhbGduPSJjdHIiPgog"
    "ICAgICAgICAgPGE6c29saWRGaWxsPgogICAgICAgICAgICA8YTpzY2hlbWVDbHIgdmFsPSJwaENsciIvPgogICAgICAgICAgPC9h"
    "OnNvbGlkRmlsbD4KICAgICAgICAgIDxhOnByc3REYXNoIHZhbD0ic29saWQiLz4KICAgICAgICA8L2E6bG4+CiAgICAgIDwvYTps"
    "blN0eWxlTHN0PgogICAgICA8YTplZmZlY3RTdHlsZUxzdD4KICAgICAgICA8YTplZmZlY3RTdHlsZT4KICAgICAgICAgIDxhOmVm"
    "ZmVjdExzdD4KICAgICAgICAgICAgPGE6b3V0ZXJTaGR3IGJsdXJSYWQ9IjQwMDAwIiBkaXN0PSIyMDAwMCIgZGlyPSI1NDAwMDAw"
    "IiByb3RXaXRoU2hhcGU9IjAiPgogICAgICAgICAgICAgIDxhOnNyZ2JDbHIgdmFsPSIwMDAwMDAiPgogICAgICAgICAgICAgICAg"
    "PGE6YWxwaGEgdmFsPSIzODAwMCIvPgogICAgICAgICAgICAgIDwvYTpzcmdiQ2xyPgogICAgICAgICAgICA8L2E6b3V0ZXJTaGR3"
    "PgogICAgICAgICAgPC9hOmVmZmVjdExzdD4KICAgICAgICA8L2E6ZWZmZWN0U3R5bGU+CiAgICAgICAgPGE6ZWZmZWN0U3R5bGU+"
    "CiAgICAgICAgICA8YTplZmZlY3RMc3Q+CiAgICAgICAgICAgIDxhOm91dGVyU2hkdyBibHVyUmFkPSI0MDAwMCIgZGlzdD0iMjMw"
    "MDAiIGRpcj0iNTQwMDAwMCIgcm90V2l0aFNoYXBlPSIwIj4KICAgICAgICAgICAgICA8YTpzcmdiQ2xyIHZhbD0iMDAwMDAwIj4K"
    "ICAgICAgICAgICAgICAgIDxhOmFscGhhIHZhbD0iMzUwMDAiLz4KICAgICAgICAgICAgICA8L2E6c3JnYkNscj4KICAgICAgICAg"
    "ICAgPC9hOm91dGVyU2hkdz4KICAgICAgICAgIDwvYTplZmZlY3RMc3Q+CiAgICAgICAgPC9hOmVmZmVjdFN0eWxlPgogICAgICAg"
    "IDxhOmVmZmVjdFN0eWxlPgogICAgICAgICAgPGE6ZWZmZWN0THN0PgogICAgICAgICAgICA8YTpvdXRlclNoZHcgYmx1clJhZD0i"
    "NDAwMDAiIGRpc3Q9IjIzMDAwIiBkaXI9IjU0MDAwMDAiIHJvdFdpdGhTaGFwZT0iMCI+CiAgICAgICAgICAgICAgPGE6c3JnYkNs"
    "ciB2YWw9IjAwMDAwMCI+CiAgICAgICAgICAgICAgICA8YTphbHBoYSB2YWw9IjM1MDAwIi8+CiAgICAgICAgICAgICAgPC9hOnNy"
    "Z2JDbHI+CiAgICAgICAgICAgIDwvYTpvdXRlclNoZHc+CiAgICAgICAgICA8L2E6ZWZmZWN0THN0PgogICAgICAgICAgPGE6c2Nl"
    "bmUzZD4KICAgICAgICAgICAgPGE6Y2FtZXJhIHByc3Q9Im9ydGhvZ3JhcGhpY0Zyb250Ij4KICAgICAgICAgICAgICA8YTpyb3Qg"
    "bGF0PSIwIiBsb249IjAiIHJldj0iMCIvPgogICAgICAgICAgICA8L2E6Y2FtZXJhPgogICAgICAgICAgICA8YTpsaWdodFJpZyBy"
    "aWc9InRocmVlUHQiIGRpcj0idCI+CiAgICAgICAgICAgICAgPGE6cm90IGxhdD0iMCIgbG9uPSIwIiByZXY9IjEyMDAwMDAiLz4K"
    "ICAgICAgICAgICAgPC9hOmxpZ2h0UmlnPgogICAgICAgICAgPC9hOnNjZW5lM2Q+CiAgICAgICAgICA8YTpzcDNkPgogICAgICAg"
    "ICAgICA8YTpiZXZlbFQgdz0iNjM1MDAiIGg9IjI1NDAwIi8+CiAgICAgICAgICA8L2E6c3AzZD4KICAgICAgICA8L2E6ZWZmZWN0"
    "U3R5bGU+CiAgICAgIDwvYTplZmZlY3RTdHlsZUxzdD4KICAgICAgPGE6YmdGaWxsU3R5bGVMc3Q+CiAgICAgICAgPGE6c29saWRG"
    "aWxsPgogICAgICAgICAgPGE6c2NoZW1lQ2xyIHZhbD0icGhDbHIiLz4KICAgICAgICA8L2E6c29saWRGaWxsPgogICAgICAgIDxh"
    "OmdyYWRGaWxsIHJvdFdpdGhTaGFwZT0iMSI+CiAgICAgICAgICA8YTpnc0xzdD4KICAgICAgICAgICAgPGE6Z3MgcG9zPSIwIj4K"
    "ICAgICAgICAgICAgICA8YTpzY2hlbWVDbHIgdmFsPSJwaENsciI+CiAgICAgICAgICAgICAgICA8YTp0aW50IHZhbD0iNDAwMDAi"
    "Lz4KICAgICAgICAgICAgICAgIDxhOnNhdE1vZCB2YWw9IjM1MDAwMCIvPgogICAgICAgICAgICAgIDwvYTpzY2hlbWVDbHI+CiAg"
    "ICAgICAgICAgIDwvYTpncz4KICAgICAgICAgICAgPGE6Z3MgcG9zPSI0MDAwMCI+CiAgICAgICAgICAgICAgPGE6c2NoZW1lQ2xy"
    "IHZhbD0icGhDbHIiPgogICAgICAgICAgICAgICAgPGE6dGludCB2YWw9IjQ1MDAwIi8+CiAgICAgICAgICAgICAgICA8YTpzaGFk"
    "ZSB2YWw9Ijk5MDAwIi8+CiAgICAgICAgICAgICAgICA8YTpzYXRNb2QgdmFsPSIzNTAwMDAiLz4KICAgICAgICAgICAgICA8L2E6"
    "c2NoZW1lQ2xyPgogICAgICAgICAgICA8L2E6Z3M+CiAgICAgICAgICAgIDxhOmdzIHBvcz0iMTAwMDAwIj4KICAgICAgICAgICAg"
    "ICA8YTpzY2hlbWVDbHIgdmFsPSJwaENsciI+CiAgICAgICAgICAgICAgICA8YTpzaGFkZSB2YWw9IjIwMDAwIi8+CiAgICAgICAg"
    "ICAgICAgICA8YTpzYXRNb2QgdmFsPSIyNTUwMDAiLz4KICAgICAgICAgICAgICA8L2E6c2NoZW1lQ2xyPgogICAgICAgICAgICA8"
    "L2E6Z3M+CiAgICAgICAgICA8L2E6Z3NMc3Q+CiAgICAgICAgICA8YTpwYXRoIHBhdGg9ImNpcmNsZSI+CiAgICAgICAgICAgIDxh"
    "OmZpbGxUb1JlY3QgbD0iNTAwMDAiIHQ9Ii04MDAwMCIgcj0iNTAwMDAiIGI9IjE4MDAwMCIvPgogICAgICAgICAgPC9hOnBhdGg+"
    "CiAgICAgICAgPC9hOmdyYWRGaWxsPgogICAgICAgIDxhOmdyYWRGaWxsIHJvdFdpdGhTaGFwZT0iMSI+CiAgICAgICAgICA8YTpn"
    "c0xzdD4KICAgICAgICAgICAgPGE6Z3MgcG9zPSIwIj4KICAgICAgICAgICAgICA8YTpzY2hlbWVDbHIgdmFsPSJwaENsciI+CiAg"
    "ICAgICAgICAgICAgICA8YTp0aW50IHZhbD0iODAwMDAiLz4KICAgICAgICAgICAgICAgIDxhOnNhdE1vZCB2YWw9IjMwMDAwMCIv"
    "PgogICAgICAgICAgICAgIDwvYTpzY2hlbWVDbHI+CiAgICAgICAgICAgIDwvYTpncz4KICAgICAgICAgICAgPGE6Z3MgcG9zPSIx"
    "MDAwMDAiPgogICAgICAgICAgICAgIDxhOnNjaGVtZUNsciB2YWw9InBoQ2xyIj4KICAgICAgICAgICAgICAgIDxhOnNoYWRlIHZh"
    "bD0iMzAwMDAiLz4KICAgICAgICAgICAgICAgIDxhOnNhdE1vZCB2YWw9IjIwMDAwMCIvPgogICAgICAgICAgICAgIDwvYTpzY2hl"
    "bWVDbHI+CiAgICAgICAgICAgIDwvYTpncz4KICAgICAgICAgIDwvYTpnc0xzdD4KICAgICAgICAgIDxhOnBhdGggcGF0aD0iY2ly"
    "Y2xlIj4KICAgICAgICAgICAgPGE6ZmlsbFRvUmVjdCBsPSI1MDAwMCIgdD0iNTAwMDAiIHI9IjUwMDAwIiBiPSI1MDAwMCIvPgog"
    "ICAgICAgICAgPC9hOnBhdGg+CiAgICAgICAgPC9hOmdyYWRGaWxsPgogICAgICA8L2E6YmdGaWxsU3R5bGVMc3Q+CiAgICA8L2E6"
    "Zm10U2NoZW1lPgogIDwvYTp0aGVtZUVsZW1lbnRzPgogIDxhOm9iamVjdERlZmF1bHRzLz4KICA8YTpleHRyYUNsclNjaGVtZUxz"
    "dC8+CjwvYTp0aGVtZT4K"
)


@dataclass(frozen=True)
class _Sheet:
    title: str
    state: str
    rows: tuple[tuple[str, ...], ...]
    # Parsed sheets omit empty rows; generated sheets use contiguous numbering.
    source_row_numbers: tuple[int, ...] = ()


@dataclass(frozen=True)
class _Workbook:
    sheets: tuple[_Sheet, ...]

    @property
    def sheetnames(self) -> tuple[str, ...]:
        return tuple(sheet.title for sheet in self.sheets)

    def sheet(self, title: str) -> _Sheet:
        for sheet in self.sheets:
            if sheet.title == title:
                return sheet
        raise KeyError(title)


def _tag(name: str) -> str:
    return f"{{{_MAIN_NS}}}{name}"


def _sheet_name(discriminator: str, used: set[str]) -> str:
    if not discriminator or _ILLEGAL_SHEET_NAME_CHARACTERS.search(discriminator):
        raise metadata.DataLoadError(
            "sample-generation", f"Section discriminator cannot be used as an Excel worksheet name: {discriminator!r}."
        )
    candidate = discriminator[:MAX_SHEET_NAME_LENGTH]
    if candidate.casefold() in _RESERVED_SHEET_NAMES or candidate.casefold() == LEGACY_MAP_SHEET.casefold():
        raise metadata.DataLoadError(
            "sample-generation", f"Section discriminator resolves to reserved Excel worksheet name: {candidate!r}."
        )
    if candidate.casefold() in used:
        raise metadata.DataLoadError(
            "sample-generation", f"Section discriminator worksheet prefix is not unique: {candidate!r}."
        )
    return candidate


def _plan_sheet_names(schema: metadata.BusinessObjectSchema) -> tuple[dict[str, str], bool]:
    """Preserve ordinary names and disambiguate collisions in hierarchy order."""
    names: dict[str, str] = {}
    counts: dict[str, int] = {}
    for section in schema.sections:
        discriminator = section.discriminator
        if discriminator in names:
            raise metadata.DataLoadError("sample-generation", "Duplicate section discriminator: " + discriminator)
        candidate = _sheet_name(discriminator, set())
        names[discriminator] = candidate
        counts[candidate.casefold()] = counts.get(candidate.casefold(), 0) + 1
    colliding = [name for name, candidate in names.items() if counts[candidate.casefold()] > 1]
    used = {candidate.casefold() for candidate in names.values() if counts[candidate.casefold()] == 1}
    used.update(_RESERVED_SHEET_NAMES)
    used.add(LEGACY_MAP_SHEET.casefold())
    number = 1
    for discriminator in colliding:
        while True:
            suffix = f"_{number}"
            number += 1
            candidate = discriminator[:MAX_SHEET_NAME_LENGTH - len(suffix)] + suffix
            if candidate.casefold() not in used:
                break
        names[discriminator] = candidate
        used.add(candidate.casefold())
    return names, bool(colliding)


def _as_cell_value(value: Any) -> str | None:
    return None if value is None else str(value)


def _column_name(index: int) -> str:
    result = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result


def _xml_bytes(root: ET.Element) -> bytes:
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _shared_strings_xml(values: tuple[str, ...], count: int) -> bytes:
    root = ET.Element(_tag("sst"), {"count": str(count), "uniqueCount": str(len(values))})
    for value in values:
        item = ET.SubElement(root, _tag("si"))
        text = ET.SubElement(item, _tag("t"))
        if value[:1].isspace() or value[-1:].isspace():
            text.set(f"{{{_XML_NS}}}space", "preserve")
        text.text = value
    return _xml_bytes(root)


def _shared_string_cell(ref: str, index: int, style_index: int) -> ET.Element:
    cell = ET.Element(_tag("c"), {"r": ref, "t": "s", "s": str(style_index)})
    value = ET.SubElement(cell, _tag("v"))
    value.text = str(index)
    return cell


def _shared_string_table(sheets: tuple[_Sheet, ...]) -> tuple[tuple[str, ...], dict[str, int], int]:
    values: list[str] = []
    indexes: dict[str, int] = {}
    count = 0
    for sheet in sheets:
        for row in sheet.rows:
            for value in row:
                text = _as_cell_value(value)
                if text is None:
                    continue
                count += 1
                if text not in indexes:
                    indexes[text] = len(values)
                    values.append(text)
    return tuple(values), indexes, count


def _ensure_text_style(styles: ET.Element) -> int:
    """Use Excel's Text category without an apostrophe/quote-prefix marker."""
    number_formats = styles.find("x:numFmts", _NS)
    if number_formats is None:
        number_formats = ET.Element(_tag("numFmts"), {"count": "0"})
        styles.insert(0, number_formats)
    format_ids = {
        int(item.get("numFmtId", "0"))
        for item in number_formats.findall("x:numFmt", _NS)
        if item.get("numFmtId", "").isdigit()
    }
    format_ids.update(
        int(item.get("numFmtId", "0"))
        for item in styles.findall(".//x:xf", _NS)
        if item.get("numFmtId", "").isdigit()
    )
    text_format = next(
        (item for item in number_formats.findall("x:numFmt", _NS) if item.get("formatCode") == "@"),
        None,
    )
    if text_format is None:
        format_id = max(format_ids | {163}) + 1
        text_format = ET.SubElement(
            number_formats,
            _tag("numFmt"),
            {"numFmtId": str(format_id), "formatCode": "@"},
        )
        number_formats.set("count", str(len(number_formats.findall("x:numFmt", _NS))))
    else:
        format_id = int(text_format.get("numFmtId", "0"))

    cell_formats = styles.find("x:cellXfs", _NS)
    if cell_formats is None:
        raise OSError("Bundled XLSX serializer omitted cell styles.")
    for index, style in enumerate(cell_formats.findall("x:xf", _NS)):
        if (
            style.get("numFmtId") == str(format_id)
            and style.get("quotePrefix", "0") in {"0", "false", "False"}
            and style.get("applyNumberFormat") in {"1", "true", "True"}
        ):
            return index
    ET.SubElement(
        cell_formats,
        _tag("xf"),
        {
            "numFmtId": str(format_id),
            "fontId": "0",
            "fillId": "0",
            "borderId": "0",
            "xfId": "0",
            "applyNumberFormat": "1",
            "quotePrefix": "0",
        },
    )
    cell_formats.set("count", str(len(cell_formats.findall("x:xf", _NS))))
    return len(cell_formats.findall("x:xf", _NS)) - 1


def _worksheet_xml(rows: tuple[tuple[Any, ...], ...], shared_indexes: dict[str, int], style_index: int) -> bytes:
    root = ET.Element(_tag("worksheet"))
    sheet_properties = ET.SubElement(root, _tag("sheetPr"))
    ET.SubElement(sheet_properties, _tag("outlinePr"), {"summaryBelow": "1", "summaryRight": "1"})
    ET.SubElement(sheet_properties, _tag("pageSetUpPr"))
    max_columns = max((len(row) for row in rows), default=0)
    if rows and max_columns:
        ET.SubElement(
            root,
            _tag("dimension"),
            {"ref": f"A1:{_column_name(max_columns)}{len(rows)}"},
        )
    sheet_views = ET.SubElement(root, _tag("sheetViews"))
    sheet_view = ET.SubElement(sheet_views, _tag("sheetView"), {"workbookViewId": "0"})
    ET.SubElement(sheet_view, _tag("selection"), {"activeCell": "A1", "sqref": "A1"})
    ET.SubElement(root, _tag("sheetFormatPr"), {"baseColWidth": "8", "defaultRowHeight": "15"})
    data = ET.SubElement(root, _tag("sheetData"))
    for row_number, values in enumerate(rows, start=1):
        row = ET.SubElement(data, _tag("row"), {"r": str(row_number)})
        for column_number, value in enumerate(values, start=1):
            text = _as_cell_value(value)
            if text is not None:
                row.append(
                    _shared_string_cell(
                        f"{_column_name(column_number)}{row_number}",
                        shared_indexes[text],
                        style_index,
                    )
                )
    ET.SubElement(root, _tag("pageMargins"), {"left": "0.75", "right": "0.75", "top": "1", "bottom": "1", "header": "0.5", "footer": "0.5"})
    return _xml_bytes(root)


def _core_properties_xml() -> bytes:
    ET.register_namespace("cp", _CORE_PROPERTIES_NS)
    ET.register_namespace("dc", _DC_NS)
    ET.register_namespace("dcterms", _DCTERMS_NS)
    ET.register_namespace("xsi", _XSI_NS)
    root = ET.Element(f"{{{_CORE_PROPERTIES_NS}}}coreProperties")
    ET.SubElement(root, f"{{{_DC_NS}}}title").text = "Oracle Fusion Data Loader Sample"
    ET.SubElement(root, f"{{{_DC_NS}}}creator").text = "Oracle Fusion Data Loader"
    ET.SubElement(root, f"{{{_CORE_PROPERTIES_NS}}}lastModifiedBy").text = "Oracle Fusion Data Loader"
    return _xml_bytes(root)


def _app_properties_xml(sheet_list: tuple[_Sheet, ...]) -> bytes:
    ET.register_namespace("", _EXTENDED_PROPERTIES_NS)
    ET.register_namespace("vt", _VT_NS)
    root = ET.Element(f"{{{_EXTENDED_PROPERTIES_NS}}}Properties")
    ET.SubElement(root, f"{{{_EXTENDED_PROPERTIES_NS}}}Application").text = "Microsoft Excel"
    ET.SubElement(root, f"{{{_EXTENDED_PROPERTIES_NS}}}DocSecurity").text = "0"
    ET.SubElement(root, f"{{{_EXTENDED_PROPERTIES_NS}}}ScaleCrop").text = "false"
    heading_pairs = ET.SubElement(root, f"{{{_EXTENDED_PROPERTIES_NS}}}HeadingPairs")
    heading_vector = ET.SubElement(heading_pairs, f"{{{_VT_NS}}}vector", {"size": "2", "baseType": "variant"})
    heading_variant = ET.SubElement(heading_vector, f"{{{_VT_NS}}}variant")
    ET.SubElement(heading_variant, f"{{{_VT_NS}}}lpstr").text = "Worksheets"
    heading_variant = ET.SubElement(heading_vector, f"{{{_VT_NS}}}variant")
    ET.SubElement(heading_variant, f"{{{_VT_NS}}}i4").text = str(len(sheet_list))
    titles = ET.SubElement(root, f"{{{_EXTENDED_PROPERTIES_NS}}}TitlesOfParts")
    titles_vector = ET.SubElement(titles, f"{{{_VT_NS}}}vector", {"size": str(len(sheet_list)), "baseType": "lpstr"})
    for sheet in sheet_list:
        ET.SubElement(titles_vector, f"{{{_VT_NS}}}lpstr").text = sheet.title
    ET.SubElement(root, f"{{{_EXTENDED_PROPERTIES_NS}}}Company").text = "Oracle"
    ET.SubElement(root, f"{{{_EXTENDED_PROPERTIES_NS}}}AppVersion").text = "1.0"
    return _xml_bytes(root)


def _artifact_runtime_available(node: Path, node_modules: Path) -> bool:
    """Fall back only for missing dependencies; propagate broken-runtime errors."""
    try:
        if not stat.S_ISREG(node.stat().st_mode) or not stat.S_ISDIR(node_modules.stat().st_mode):
            return False
    except FileNotFoundError:
        return False
    environment = os.environ.copy()
    environment["NODE_PATH"] = str(node_modules)
    probe = subprocess.run(
        [str(node), "-e", """
try {
    require.resolve("@oai/artifact-tool");
} catch (error) {
    if (error.code === "MODULE_NOT_FOUND" &&
        error.message.startsWith("Cannot find module '@oai/artifact-tool'")) {
        process.exit(3);
    }
    throw error;
}
"""],
        cwd=str(_ARTIFACT_WRITER.parent),
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    if probe.returncode == 3:
        return False
    if probe.returncode:
        detail = (probe.stderr or probe.stdout).strip()
        raise OSError(f"Unable to check bundled XLSX runtime: {detail or 'unknown error'}")
    return True


def _write_generic_workbook(sheets: tuple[_Sheet, ...], output_path: Path) -> None:
    """Write a complete, literal-text XLSX package using only the standard library."""
    content_ns = "http://schemas.openxmlformats.org/package/2006/content-types"
    spreadsheet_type = "application/vnd.openxmlformats-officedocument.spreadsheetml."
    # Package readers used by the preview require unprefixed package metadata.
    content_types = ET.Element("Types", {"xmlns": content_ns})
    for extension, content_type in (
        ("rels", "application/vnd.openxmlformats-package.relationships+xml"),
        ("xml", "application/xml"),
    ):
        ET.SubElement(content_types, "Default", {
            "Extension": extension, "ContentType": content_type,
        })

    root_relationships = ET.Element("Relationships", {"xmlns": _PKG_REL_NS})
    for index, (target, relationship_type) in enumerate((
        ("xl/workbook.xml", _REL_NS + "/officeDocument"),
        ("docProps/core.xml", _PKG_REL_NS + "/metadata/core-properties"),
        ("docProps/app.xml", _REL_NS + "/extended-properties"),
    ), start=1):
        ET.SubElement(root_relationships, "Relationship", {
            "Id": f"rId{index}", "Type": relationship_type, "Target": "/" + target,
        })

    workbook = ET.Element(_tag("workbook"))
    views = ET.SubElement(workbook, _tag("bookViews"))
    first_visible = next((index for index, sheet in enumerate(sheets) if sheet.state == "visible"), 0)
    ET.SubElement(views, _tag("workbookView"), {"activeTab": str(first_visible)})
    workbook_sheets = ET.SubElement(workbook, _tag("sheets"))
    relationships = ET.Element("Relationships", {"xmlns": _PKG_REL_NS})
    styles = ET.fromstring(_STYLE_XML)
    text_style = _ensure_text_style(styles)
    shared_values, shared_indexes, shared_count = _shared_string_table(sheets)
    parts = {
        "docProps/core.xml": (_core_properties_xml(), "application/vnd.openxmlformats-package.core-properties+xml"),
        "docProps/app.xml": (_app_properties_xml(sheets), "application/vnd.openxmlformats-officedocument.extended-properties+xml"),
    }
    for index, sheet in enumerate(sheets, start=1):
        attributes = {"name": sheet.title, "sheetId": str(index), f"{{{_REL_NS}}}id": f"rId{index}"}
        if sheet.state != "visible":
            attributes["state"] = sheet.state
        ET.SubElement(workbook_sheets, _tag("sheet"), attributes)
        target = f"xl/worksheets/sheet{index}.xml"
        ET.SubElement(relationships, "Relationship", {
            "Id": f"rId{index}", "Type": _REL_NS + "/worksheet", "Target": "/" + target,
        })
        parts[target] = (_worksheet_xml(sheet.rows, shared_indexes, text_style), spreadsheet_type + "worksheet+xml")

    for index, (target, kind, content, content_type) in enumerate((
        ("xl/styles.xml", "styles", _xml_bytes(styles), spreadsheet_type + "styles+xml"),
        ("xl/sharedStrings.xml", "sharedStrings", _shared_strings_xml(shared_values, shared_count), spreadsheet_type + "sharedStrings+xml"),
        ("xl/theme/theme1.xml", "theme", _THEME_XML, "application/vnd.openxmlformats-officedocument.theme+xml"),
    ), start=len(sheets) + 1):
        ET.SubElement(relationships, "Relationship", {
            "Id": f"rId{index}", "Type": _REL_NS + "/" + kind, "Target": "/" + target,
        })
        parts[target] = (content, content_type)
    parts["xl/workbook.xml"] = (_xml_bytes(workbook), spreadsheet_type + "sheet.main+xml")
    for target, (_, content_type) in parts.items():
        ET.SubElement(content_types, "Override", {
            "PartName": "/" + target, "ContentType": content_type,
        })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".xlsx", dir=output_path.parent, delete=False) as handle:
        temporary_path = Path(handle.name)
    try:
        with zipfile.ZipFile(temporary_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("[Content_Types].xml", _xml_bytes(content_types))
            archive.writestr("_rels/.rels", _xml_bytes(root_relationships))
            archive.writestr("xl/_rels/workbook.xml.rels", _xml_bytes(relationships))
            for target, (content, _) in parts.items():
                archive.writestr(target, content)
        temporary_path.replace(output_path)
    finally:
        temporary_path.unlink(missing_ok=True)


def _write_workbook(sheets: Iterable[_Sheet], output_path: Path) -> None:
    sheet_list = tuple(sheets)
    node_path = Path.home() / ".cache" / "codex-runtimes" / "codex-primary-runtime" / "dependencies" / "node"
    node = Path(os.environ.get("DATA_LOADER_ARTIFACT_NODE", node_path / "bin" / "node"))
    node_modules = Path(os.environ.get("DATA_LOADER_ARTIFACT_NODE_MODULES", node_path / "node_modules"))
    if not _artifact_runtime_available(node, node_modules):
        _write_generic_workbook(sheet_list, output_path)
        return
    if not _ARTIFACT_WRITER.is_file():
        raise OSError(f"Missing XLSX serializer: {_ARTIFACT_WRITER}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "outputPath": str(output_path.resolve()),
        "sheets": [
            {"title": sheet.title, "rows": [list(row) for row in sheet.rows]}
            for sheet in sheet_list
        ],
    }
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as handle:
        json.dump(payload, handle, ensure_ascii=False)
        input_path = Path(handle.name)
    try:
        environment = os.environ.copy()
        environment["NODE_PATH"] = str(node_modules)
        completed = subprocess.run(
            [str(node), str(_ARTIFACT_WRITER), str(input_path)],
            cwd=str(_ARTIFACT_WRITER.parent),
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode:
            detail = (completed.stderr or completed.stdout).strip()
            raise OSError(f"Bundled XLSX serializer failed: {detail or 'unknown error'}")
    finally:
        input_path.unlink(missing_ok=True)
    output_path.with_suffix(output_path.suffix + ".inspect.ndjson").unlink(missing_ok=True)
    _restore_literal_text_cells(output_path, sheet_list)
    _preserve_sheet_states(output_path, sheet_list)


def _restore_literal_text_cells(output_path: Path, sheets: tuple[_Sheet, ...]) -> None:
    """Replace inferred values with exact shared-string Data Loader literals."""
    with tempfile.NamedTemporaryFile(suffix=".xlsx", dir=output_path.parent, delete=False) as handle:
        replacement_path = Path(handle.name)
    try:
        with zipfile.ZipFile(output_path) as source:
            workbook = _xml(source, "xl/workbook.xml")
            relationships = _relationships(source, "xl/_rels/workbook.xml.rels")
            styles = _xml(source, "xl/styles.xml")
            shared_values, shared_indexes, shared_count = _shared_string_table(sheets)
            text_style_index = _ensure_text_style(styles)
            workbook_sheets = workbook.findall("x:sheets/x:sheet", _NS)
            if len(workbook_sheets) != len(sheets):
                raise OSError("Bundled XLSX serializer returned an unexpected worksheet count.")
            replacements = {
                "xl/sharedStrings.xml": _shared_strings_xml(shared_values, shared_count),
                "xl/styles.xml": _xml_bytes(styles),
            }
            for element, sheet in zip(workbook_sheets, sheets):
                relationship_id = element.get(f"{{{_REL_NS}}}id", "")
                relationship = relationships.get(relationship_id)
                if relationship is None or not relationship[0].endswith("/worksheet"):
                    raise OSError("Bundled XLSX serializer returned an invalid worksheet relationship.")
                worksheet_path = relationship[1]
                if worksheet_path not in source.namelist():
                    raise OSError("Bundled XLSX serializer omitted a generated worksheet.")
                replacements[worksheet_path] = _worksheet_xml(
                    sheet.rows,
                    shared_indexes,
                    text_style_index,
                )
            with zipfile.ZipFile(replacement_path, "w", compression=zipfile.ZIP_DEFLATED) as replacement:
                for item in source.infolist():
                    replacement.writestr(item, replacements.get(item.filename, source.read(item.filename)))
        replacement_path.replace(output_path)
    finally:
        replacement_path.unlink(missing_ok=True)


def _preserve_sheet_states(output_path: Path, sheets: tuple[_Sheet, ...]) -> None:
    """Restore non-visible states that the artifact writer does not expose."""
    if all(sheet.state == "visible" for sheet in sheets):
        return
    with tempfile.NamedTemporaryFile(suffix=".xlsx", dir=output_path.parent, delete=False) as handle:
        replacement_path = Path(handle.name)
    try:
        with zipfile.ZipFile(output_path) as source:
            workbook = ET.fromstring(source.read("xl/workbook.xml"))
            for element, sheet in zip(workbook.findall("x:sheets/x:sheet", _NS), sheets):
                if sheet.state == "visible":
                    element.attrib.pop("state", None)
                else:
                    element.set("state", sheet.state)
            with zipfile.ZipFile(replacement_path, "w", compression=zipfile.ZIP_DEFLATED) as replacement:
                for item in source.infolist():
                    content = _xml_bytes(workbook) if item.filename == "xl/workbook.xml" else source.read(item.filename)
                    replacement.writestr(item, content)
        replacement_path.replace(output_path)
    finally:
        replacement_path.unlink(missing_ok=True)


def write_sample_workbook(schema: metadata.BusinessObjectSchema, rows: dict[str, tuple[tuple[str, ...], Any]], output_path: Path) -> None:
    names, needs_map = _plan_sheet_names(schema)
    sheets: list[_Sheet] = []
    for section in schema.sections:
        header, data = rows[section.discriminator]
        if data is None:
            sheet_rows = (header,)
        elif data and isinstance(data[0], tuple):
            sheet_rows = (header, *data)
        else:
            sheet_rows = (header, data)
        sheets.append(_Sheet(names[section.discriminator], "visible", sheet_rows))
    if needs_map:
        map_rows = [LEGACY_MAP_HEADERS]
        for section in schema.sections:
            discriminator = section.discriminator
            is_root = discriminator == schema.discriminator
            parent = str(schema.components.get(discriminator, {}).get("ParentBusObjFileDiscriminator") or "")
            if not is_root and parent not in names:
                raise metadata.DataLoadError("sample-generation", "Missing or unknown parent discriminator for " + discriminator)
            map_rows.append((names[discriminator], discriminator, "" if is_root else parent,
                             schema.discriminator if is_root else ""))
        sheets.append(_Sheet(LEGACY_MAP_SHEET, "visible", tuple(map_rows)))
    _write_workbook(sheets, output_path)


def _attribute_key_classification(attribute: dict[str, Any] | None) -> str:
    if not attribute:
        return ""
    classifications: list[str] = []
    if metadata.is_surrogate_id_attribute(attribute): classifications.append("Surrogate")
    if metadata.is_mandatory(attribute): classifications.append("Mandatory")
    attribute_type = str(attribute.get("AttributeType") or "").upper()
    is_user_key = bool(metadata.user_key_attribute_names(attribute)) or "USER_KEY" in attribute_type
    if is_user_key: classifications.append("User Key")
    if metadata.is_foreign_key_attribute(attribute): classifications.append("Foreign Key")
    if metadata.is_key_attribute(attribute) and not is_user_key: classifications.append("Key")
    return "; ".join(classifications)


def _required_status(attribute: dict[str, Any] | None) -> str:
    """Render the live mandatory status without losing create-only requiredness."""
    if metadata.is_mandatory(attribute or {}):
        return "Yes"
    if metadata.is_required_for_create(attribute or {}):
        return "For new records"
    return "No"


def _attribute_details_row(section: metadata.TemplateSection, name: str, detail: dict[str, Any] | None, product_detail: dict[str, str] | None) -> tuple[Any, ...]:
    detail, product_detail = detail or {}, product_detail or {}
    return (section.raw_name_for(name), product_detail.get("label") or name, product_detail.get("description") or "", detail.get("DataType") or detail.get("AttributeDatatype") or "", _required_status(detail), _attribute_key_classification(detail), "; ".join(metadata.user_key_attribute_names(detail)), detail.get("AttributeMapKeyReferenceType") or "", detail.get("ReferenceIntObjName") or "", detail.get("LookupName") or "", detail.get("DataLength") or "", detail.get("NumberPrecision") or "", detail.get("HiddenAttr") or "")


def write_attribute_details_workbook(schema: metadata.BusinessObjectSchema, output_path: Path, product_metadata: dict[str, dict[str, dict[str, str]]] | None = None) -> None:
    names, _needs_map = _plan_sheet_names(schema)
    product_metadata = product_metadata or {}
    sheets: list[_Sheet] = []
    for section in schema.sections:
        name = names[section.discriminator]
        details = {metadata.normalize_attribute_name(str(attribute.get("AttributeName") or "")): attribute for attribute in schema.attributes.get(section.discriminator, ()) if str(attribute.get("AttributeName") or "").strip()}
        rows = [ATTRIBUTE_DETAILS_HEADERS]
        rows.extend(
            tuple(
                str(value)
                for value in _attribute_details_row(
                    section,
                    attribute_name,
                    details.get(attribute_name),
                    product_metadata.get(section.discriminator, {}).get(attribute_name),
                )
            )
            for attribute_name in section.attribute_names
            if not metadata.is_source_reference_attribute(attribute_name)
            and not metadata.is_standard_who_column(attribute_name)
        )
        sheets.append(_Sheet(name, "visible", tuple(rows)))
    _write_workbook(sheets, output_path)


def _stringify(value: Any) -> str:
    if value is None: return ""
    if isinstance(value, bool): return "true" if value else "false"
    if isinstance(value, datetime): return value.strftime("%Y-%m-%dT%H:%M:%SZ")
    if isinstance(value, date): return value.strftime("%Y/%m/%d")
    return str(value)


def _safe_target(source: str, target: str) -> str:
    if ".." in target.split("/"):
        raise metadata.DataLoadError("file-validation", "XLSX workbook contains an unsafe relationship target.")
    if target.startswith("/"):
        resolved = posixpath.normpath(target.lstrip("/"))
    else:
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(source), target))
    if resolved in {"", ".", ".."} or resolved.startswith("../") or resolved.startswith("/"):
        raise metadata.DataLoadError("file-validation", "XLSX workbook contains an unsafe relationship target.")
    return resolved


def _relationship_source(name: str) -> str:
    """Return the package part whose relationships are held by *name*."""
    directory, filename = posixpath.split(name)
    if directory.endswith("/_rels") and filename.endswith(".rels"):
        return posixpath.join(posixpath.dirname(directory), filename[:-5])
    return name


def _xml(archive: zipfile.ZipFile, name: str) -> ET.Element:
    try:
        return ET.fromstring(archive.read(name))
    except KeyError as exc:
        raise metadata.DataLoadError("file-validation", f"XLSX workbook is missing required part: {name}") from exc
    except (ET.ParseError, OSError, RuntimeError, zipfile.BadZipFile) as exc:
        raise metadata.DataLoadError("file-validation", f"Unable to parse XLSX workbook part {name}: {exc}") from exc


def _relationships(archive: zipfile.ZipFile, name: str) -> dict[str, tuple[str, str]]:
    root = _xml(archive, name)
    source = _relationship_source(name)
    return {rel.get("Id", ""): (rel.get("Type", ""), _safe_target(source, rel.get("Target", ""))) for rel in root.findall("pr:Relationship", _NS) if rel.get("TargetMode") != "External"}


def _shared_strings(archive: zipfile.ZipFile) -> tuple[str, ...]:
    if "xl/sharedStrings.xml" not in archive.namelist(): return ()
    root = _xml(archive, "xl/sharedStrings.xml")
    return tuple("".join(node.text or "" for node in item.findall(".//x:t", _NS)) for item in root.findall("x:si", _NS))


def _date_style_indexes(archive: zipfile.ZipFile) -> frozenset[int]:
    if "xl/styles.xml" not in archive.namelist(): return frozenset()
    root = _xml(archive, "xl/styles.xml")
    formats = {int(item.get("numFmtId", "-1")): item.get("formatCode", "") for item in root.findall("x:numFmts/x:numFmt", _NS) if item.get("numFmtId", "").isdigit()}
    indexes: set[int] = set()
    for index, xf in enumerate(root.findall("x:cellXfs/x:xf", _NS)):
        num_fmt = int(xf.get("numFmtId", "0"))
        code = formats.get(num_fmt, "")
        normalized = re.sub(r'"[^"]*"|\\\\.|\[[^]]*\]', "", code.lower())
        if num_fmt in _DATE_FORMAT_IDS or bool(re.search(r"[ymdhss]", normalized)):
            indexes.add(index)
    return frozenset(indexes)


def _date_style_formats(archive: zipfile.ZipFile) -> dict[int, str]:
    if "xl/styles.xml" not in archive.namelist():
        return {}
    root = _xml(archive, "xl/styles.xml")
    custom = {
        int(item.get("numFmtId", "-1")): item.get("formatCode", "")
        for item in root.findall("x:numFmts/x:numFmt", _NS)
        if item.get("numFmtId", "").isdigit()
    }
    return {
        index: custom.get(int(xf.get("numFmtId", "0")),
                          _BUILTIN_DATE_FORMATS.get(int(xf.get("numFmtId", "0")), ""))
        for index, xf in enumerate(root.findall("x:cellXfs/x:xf", _NS))
    }


def _adf_rest_date_text(value: date | datetime, format_code: str) -> str:
    """Render common Excel date formats; use deterministic ISO text for others."""
    fallback = (
        value.strftime("%Y-%m-%dT%H:%M:%S") if isinstance(value, datetime)
        else value.strftime("%Y-%m-%d")
    )
    if not format_code:
        return fallback
    tokens = _DISPLAY_DATE_TOKEN.findall(format_code)
    if "".join(tokens) != format_code or not any(
        re.fullmatch(r"y+|m+|d+|h+|s+", token, re.IGNORECASE)
        for token in tokens
    ):
        return fallback
    stamp = value if isinstance(value, datetime) else datetime.combine(value, datetime.min.time())
    has_ampm = any(token.upper() == "AM/PM" for token in tokens)
    rendered: list[str] = []
    for index, token in enumerate(tokens):
        lower = token.lower()
        if token.startswith('"'):
            rendered.append(token[1:-1])
        elif token.startswith("\\"):
            rendered.append(token[1:])
        elif lower == "am/pm":
            rendered.append("AM" if stamp.hour < 12 else "PM")
        elif lower in {"y", "yy", "yyyy"}:
            rendered.append(f"{stamp.year % 100:02d}" if lower == "yy" else str(stamp.year).zfill(4 if lower == "yyyy" else 1))
        elif lower in {"d", "dd", "ddd", "dddd"}:
            rendered.append(
                stamp.strftime("%a" if lower == "ddd" else "%A") if len(lower) >= 3
                else f"{stamp.day:02d}" if len(lower) == 2 else str(stamp.day)
            )
        elif lower in {"m", "mm", "mmm", "mmmm"}:
            previous = "".join(tokens[:index]).rstrip(" :")
            following = "".join(tokens[index + 1:]).lstrip(" :")
            minute = len(lower) <= 2 and (
                previous.lower().endswith(("h", "hh")) or following.lower().startswith(("s", "ss"))
            ) and (":" in "".join(tokens[max(0, index - 1):index + 2]))
            if minute:
                rendered.append(f"{stamp.minute:02d}" if len(lower) == 2 else str(stamp.minute))
            elif lower == "mmm":
                rendered.append(stamp.strftime("%b"))
            elif lower == "mmmm":
                rendered.append(stamp.strftime("%B"))
            else:
                rendered.append(f"{stamp.month:02d}" if len(lower) == 2 else str(stamp.month))
        elif lower in {"h", "hh"}:
            hour = (stamp.hour % 12 or 12) if has_ampm else stamp.hour
            rendered.append(f"{hour:02d}" if len(lower) == 2 else str(hour))
        elif lower in {"s", "ss"}:
            rendered.append(f"{stamp.second:02d}" if len(lower) == 2 else str(stamp.second))
        else:
            rendered.append(token)
    return "".join(rendered)


def _cell_coordinates(reference: str) -> tuple[int, int]:
    match = _CELL_REF.fullmatch(reference) if len(reference) <= 10 else None
    if not match: raise metadata.DataLoadError("file-validation", f"XLSX workbook has an invalid cell reference: {reference}")
    column = 0
    for character in match.group(1): column = column * 26 + ord(character) - 64
    row = int(match.group(2))
    if row > _MAX_XLSX_ROW or column > _MAX_XLSX_COLUMN:
        raise metadata.DataLoadError("file-validation", f"XLSX workbook has an out-of-range cell reference: {reference}")
    return row, column


def _excel_date(value: str, date_1904: bool) -> date | datetime:
    try: serial = float(value)
    except ValueError as exc: raise metadata.DataLoadError("file-validation", f"XLSX workbook has an invalid date serial: {value}") from exc
    origin = datetime(1904, 1, 1) if date_1904 else datetime(1899, 12, 30)
    if not date_1904 and 0 < serial < 60:
        # Excel's 1900 date system includes a fictional 1900-02-29 at serial 60.
        # Compensate before that boundary while preserving serial 60+ behavior.
        serial += 1
    converted = origin + timedelta(days=serial)
    return converted.date() if serial.is_integer() else converted


def _cell_value(
    cell: ET.Element,
    shared: tuple[str, ...],
    date_styles: frozenset[int],
    date_1904: bool,
    *,
    adf_rest_dates: bool = False,
    date_formats: dict[int, str] | None = None,
) -> str:
    cell_type = cell.get("t", "n")
    formula = cell.find("x:f", _NS)
    if formula is not None:
        if not (formula.text or "").strip():
            raise metadata.DataLoadError("file-validation", "XLSX workbook contains a formula that cannot be represented as literal text.")
        return "=" + (formula.text or "")
    if cell_type == "inlineStr": return "".join(node.text or "" for node in cell.findall(".//x:t", _NS))
    value = cell.findtext("x:v", default="", namespaces=_NS)
    if cell_type == "s":
        try: return shared[int(value)]
        except (ValueError, IndexError) as exc: raise metadata.DataLoadError("file-validation", "XLSX workbook contains an invalid shared-string reference.") from exc
    if cell_type == "b":
        if value not in {"0", "1"}: raise metadata.DataLoadError("file-validation", "XLSX workbook contains an invalid boolean cell.")
        return "true" if value == "1" else "false"
    if cell_type == "d":
        style_index = int(cell.get("s", "0")) if cell.get("s", "0").isdigit() else 0
        format_code = (date_formats or {}).get(style_index, "")
        try:
            parsed = (
                date.fromisoformat(value)
                if adf_rest_dates and "T" not in value and " " not in value
                else datetime.fromisoformat(value.replace("Z", "+00:00"))
            )
            return _adf_rest_date_text(parsed, format_code) if adf_rest_dates else _stringify(parsed)
        except ValueError as exc:
            raise metadata.DataLoadError("file-validation", f"XLSX workbook contains an invalid ISO date: {value}") from exc
    if cell_type in {"n", "str"}:
        if cell_type == "n" and cell.get("s", "").isdigit() and int(cell.get("s", "0")) in date_styles and value:
            parsed = _excel_date(value, date_1904)
            return (
                _adf_rest_date_text(parsed, (date_formats or {}).get(int(cell.get("s", "0")), ""))
                if adf_rest_dates else _stringify(parsed)
            )
        return value
    if cell_type == "e": raise metadata.DataLoadError("file-validation", "XLSX workbook contains an error cell.")
    raise metadata.DataLoadError("file-validation", f"XLSX workbook contains unsupported cell type: {cell_type}")


def _read_sheet(
    archive: zipfile.ZipFile,
    name: str,
    shared: tuple[str, ...],
    date_styles: frozenset[int],
    date_1904: bool,
    *,
    adf_rest_dates: bool = False,
    date_formats: dict[int, str] | None = None,
    enforce_header_width: bool = True,
) -> tuple[tuple[tuple[str, ...], ...], tuple[int, ...]]:
    root = _xml(archive, name)
    rows: dict[int, dict[int, str]] = {}
    for row in root.findall("x:sheetData/x:row", _NS):
        for cell in row.findall("x:c", _NS):
            reference = cell.get("r")
            if not reference: raise metadata.DataLoadError("file-validation", "XLSX workbook contains a cell without a reference.")
            row_number, column_number = _cell_coordinates(reference)
            values = rows.setdefault(row_number, {})
            if column_number in values:
                raise metadata.DataLoadError("file-validation", f"Worksheet {name} contains duplicate cell {reference}.")
            values[column_number] = _cell_value(
                cell, shared, date_styles, date_1904,
                adf_rest_dates=adf_rest_dates, date_formats=date_formats,
            )
    # A styled/explicitly empty cell must not enlarge the output rectangle.
    populated = {
        number: {column: value for column, value in values.items() if value != ""}
        for number, values in rows.items()
    }
    populated = {number: values for number, values in populated.items() if values}
    if not populated:
        return (), ()
    header_width = max(populated.get(1, {}), default=0)
    result: list[tuple[str, ...]] = []
    source_rows: list[int] = []
    output_cells = 0
    # Keep a missing header at physical row 1; never promote the first data row.
    for number in sorted(populated.keys() | {1}):
        values = populated.get(number, {})
        last_column = max(values, default=0)
        if enforce_header_width and header_width and last_column > header_width:
            raise metadata.DataLoadError(
                "file-validation",
                f"Worksheet {name} cell {_column_name(last_column)}{number} contains data beyond the header columns.",
            )
        width = max(header_width, last_column)
        output_cells += width
        if output_cells > _MAX_SHEET_OUTPUT_CELLS:
            raise metadata.DataLoadError(
                "file-validation",
                f"Worksheet {name} exceeds the output cell limit ({_MAX_SHEET_OUTPUT_CELLS}).",
            )
        result.append(tuple(values.get(column, "") for column in range(1, width + 1)))
        source_rows.append(number)
    return tuple(result), tuple(source_rows)


def _is_set_commands_sheet(title: str) -> bool:
    """Match Set Commands with optional inter-word whitespace, ignoring case."""
    return " ".join(title.split()).casefold() in (SET_COMMANDS_SHEET, "setcommands")


def _read_workbook(path: Path, *, adf_rest_dates: bool = False) -> _Workbook:
    try:
        with zipfile.ZipFile(path) as archive:
            if any(info.flag_bits & 0x1 for info in archive.infolist()): raise metadata.DataLoadError("file-validation", "Encrypted XLSX workbooks are not supported.")
            workbook_rels = _relationships(archive, "xl/_rels/workbook.xml.rels")
            shared, date_styles = _shared_strings(archive), _date_style_indexes(archive)
            date_formats = _date_style_formats(archive) if adf_rest_dates else {}
            workbook = _xml(archive, "xl/workbook.xml")
            date_1904 = workbook.find("x:workbookPr", _NS) is not None and workbook.find("x:workbookPr", _NS).get("date1904") in {"1", "true", "True"}
            sheets: list[_Sheet] = []
            for item in workbook.findall("x:sheets/x:sheet", _NS):
                relationship_id = item.get(f"{{{_REL_NS}}}id", "")
                relationship = workbook_rels.get(relationship_id)
                if not relationship or not relationship[0].endswith("/worksheet"): raise metadata.DataLoadError("file-validation", "XLSX workbook has a worksheet without a valid relationship.")
                title = item.get("name", "")
                state = item.get("state", "visible")
                sheet_rows, source_rows = _read_sheet(
                    archive, relationship[1], shared, date_styles, date_1904,
                    adf_rest_dates=(
                        adf_rest_dates and state == "visible" and title != LEGACY_MAP_SHEET
                        and not _is_set_commands_sheet(title)
                    ),
                    date_formats=date_formats,
                    enforce_header_width=(state == "visible" or title == LEGACY_MAP_SHEET),
                )
                sheets.append(_Sheet(title, state, sheet_rows, source_rows))
            return _Workbook(tuple(sheets))
    except metadata.DataLoadError: raise
    except (OSError, zipfile.BadZipFile) as exc:
        raise metadata.DataLoadError("file-validation", f"Unable to open XLSX workbook: {path}: {exc}") from exc


HeaderMapper = Callable[[str, tuple[str, ...]], tuple[tuple[str, ...], tuple[int, ...], tuple[metadata.ColumnMapping, ...]]]


def dat_record_directive(header: tuple[str, ...], values: tuple[str, ...]) -> str:
    """Return the DAT directive for one row without changing its values."""
    for operation_column in ("RestAction", "$operation"):
        try:
            operation_index = header.index(operation_column)
        except ValueError:
            continue
        if values[operation_index] == "DELETE":
            return "DELETE"
    return "MERGE"


def escape_dat_value(value: str) -> str:
    """Escape a literal pipe for the default HDL DAT file delimiter."""
    return value.replace("|", r"\|")


def _resolve_sheet_discriminator(sheet_name: str, discriminators: Iterable[str]) -> str:
    """Resolve an exact or generated 30-character worksheet name without guessing."""
    candidates = tuple(dict.fromkeys(str(value) for value in discriminators if str(value)))
    exact = [value for value in candidates if value == sheet_name]
    matches = exact or [value for value in candidates if value.startswith(sheet_name)]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise metadata.DataLoadError(
            "file-validation", f"Worksheet {sheet_name!r} does not match a section of the resolved business object."
        )
    raise metadata.DataLoadError(
        "file-validation", f"Worksheet prefix {sheet_name!r} is ambiguous for the resolved business object."
    )


def _read_set_commands(workbook: _Workbook) -> tuple[tuple[str, str], ...]:
    """Collect complete pairs, keeping each parameter's last supplied value."""
    commands: dict[str, str] = {}
    header_aliases = {"parameter": "parameters", "values": "value"}
    for sheet in workbook.sheets:
        if sheet.state != "visible" or not _is_set_commands_sheet(sheet.title) or not sheet.rows:
            continue
        headers = tuple(value.strip().casefold() for value in sheet.rows[0])
        headers = tuple(header_aliases.get(header, header) for header in headers)
        if "parameters" not in headers or "value" not in headers:
            continue
        parameter_index, value_index = headers.index("parameters"), headers.index("value")
        for row in sheet.rows[1:]:
            if len(row) <= max(parameter_index, value_index):
                continue
            parameter, value = row[parameter_index].strip(), row[value_index].strip()
            if parameter and value:
                commands[parameter] = value
    return tuple(commands.items())


def read_xlsx_source(
    path: Path,
    *,
    header_mapper: HeaderMapper | None = None,
    mapping_audit: list[metadata.ColumnMapping] | None = None,
    root_discriminator: str | None = None,
    section_discriminators: Iterable[str] | None = None,
    object_type: str | None = None,
) -> tuple[str, tuple[metadata.SourceSection, ...], str | None]:
    workbook = _read_workbook(path, adf_rest_dates=object_type == "ADF_REST")
    visible_sheets = [
        sheet for sheet in workbook.sheets
        if sheet.state == "visible" and sheet.title != LEGACY_MAP_SHEET
        and not _is_set_commands_sheet(sheet.title)
    ]
    if not visible_sheets: raise metadata.DataLoadError("file-validation", "XLSX workbook must contain at least one visible data worksheet.")
    visible_names = {sheet.title for sheet in visible_sheets}
    business_object_name: str | None = None
    if LEGACY_MAP_SHEET in workbook.sheetnames:
        map_rows = workbook.sheet(LEGACY_MAP_SHEET).rows
        if not map_rows or tuple(map_rows[0]) != LEGACY_MAP_HEADERS:
            raise metadata.DataLoadError(
                "file-validation", f"{LEGACY_MAP_SHEET} must use columns: " + ", ".join(LEGACY_MAP_HEADERS)
            )
        mappings: list[tuple[str, str]] = []
        seen_sheets: set[str] = set()
        seen_discriminators: set[str] = set()
        root_names: list[str] = []
        for row in map_rows[1:]:
            sheet_name, discriminator, parent, mapped_root = (
                value.strip() for value in (list(row) + [""] * 4)[:4]
            )
            if not sheet_name and not discriminator:
                continue
            if not sheet_name or not discriminator:
                raise metadata.DataLoadError("file-validation", f"{LEGACY_MAP_SHEET} contains an invalid sheet mapping.")
            if sheet_name not in visible_names:
                raise metadata.DataLoadError("file-validation", f"{LEGACY_MAP_SHEET} contains a stale worksheet mapping: {sheet_name}.")
            if sheet_name in seen_sheets or discriminator in seen_discriminators:
                raise metadata.DataLoadError("file-validation", f"{LEGACY_MAP_SHEET} contains duplicate sheet or discriminator mappings.")
            seen_sheets.add(sheet_name)
            seen_discriminators.add(discriminator)
            mappings.append((sheet_name, discriminator))
            if mapped_root:
                if mapped_root != discriminator or parent:
                    raise metadata.DataLoadError(
                        "file-validation", f"{LEGACY_MAP_SHEET} Business Object Name must appear only on the root section row."
                    )
                root_names.append(mapped_root)
        if visible_names != seen_sheets:
            raise metadata.DataLoadError("file-validation", f"Visible XLSX worksheets must be listed exactly once in {LEGACY_MAP_SHEET}.")
        if len(root_names) != 1:
            raise metadata.DataLoadError(
                "file-validation", f"{LEGACY_MAP_SHEET} must contain exactly one Business Object Name on the root section row."
            )
        business_object_name = root_names[0]
    else:
        available = tuple(str(value) for value in (section_discriminators or ()) if str(value))
        if available:
            mappings = [
                (sheet.title, _resolve_sheet_discriminator(sheet.title, available))
                for sheet in visible_sheets
            ]
            if root_discriminator is not None and mappings[0][1] != root_discriminator:
                raise metadata.DataLoadError("file-validation", "The first visible XLSX worksheet must identify the top-level business object.")
        else:
            mappings = [(sheet.title, sheet.title) for sheet in visible_sheets]
    converted_sections: list[tuple[str, tuple[str, ...], list[str]]] = []
    sections: list[metadata.SourceSection] = []
    for sheet_name, discriminator in mappings:
        sheet = workbook.sheet(sheet_name)
        rows = sheet.rows
        header = tuple(value.strip() for value in (rows[0] if rows else ()))
        if not header:
            raise metadata.DataLoadError("file-validation", f"Sheet {sheet_name} has no header row.")
        action_columns = [index for index, name in enumerate(header)
                          if metadata.normalized_name(name) == "dataloaderaction"]
        if object_type is not None and action_columns:
            if object_type != "ADF_VO" or len(action_columns) != 1 or header[action_columns[0]] != "DataLoaderAction":
                raise metadata.DataLoadError(
                    "file-validation", f"Sheet {sheet_name} must use the exact DataLoaderAction header only for ADF_VO objects."
                )
        action_index = action_columns[0] if object_type == "ADF_VO" and action_columns else None
        data_indexes = tuple(index for index in range(len(header)) if index != action_index)
        data_header = tuple(header[index] for index in data_indexes)
        if header_mapper is not None:
            normalized, retained_indexes, audit = header_mapper(discriminator, data_header)
            if mapping_audit is not None:
                mapping_audit.extend(audit)
        else:
            if any(not value for value in data_header):
                raise metadata.DataLoadError("file-validation", f"Sheet {sheet_name} has an empty header column.")
            normalized = tuple(metadata.normalize_attribute_name(value) for value in data_header)
            retained_indexes = tuple(range(len(data_header)))
        if not normalized:
            # Preserve the schema mismatch for a source with no usable columns;
            # this remains fail-closed rather than producing an empty DAT row.
            normalized = tuple(metadata.normalize_attribute_name(value) for value in data_header)
            retained_indexes = tuple(range(len(data_header)))
        if len(set(normalized)) != len(normalized): raise metadata.DataLoadError("file-validation", f"Sheet {sheet_name} has duplicate attribute columns.")
        records: list[str] = []
        row_numbers = sheet.source_row_numbers or range(1, len(rows) + 1)
        for row_number, row in zip(row_numbers[1:], rows[1:]):
            source_values = tuple((list(row) + [""] * len(header))[:len(header)])
            action = source_values[action_index].strip() if action_index is not None else ""
            if action_index is not None and action not in {"", "MERGE", "DELETE"}:
                raise metadata.DataLoadError(
                    "file-validation", f"Sheet {sheet_name} row {row_number} has invalid DataLoaderAction: {action}."
                )
            data_values = tuple(source_values[index] for index in data_indexes)
            values = tuple(data_values[index] for index in retained_indexes)
            if not any(values): continue
            if any("\r" in value or "\n" in value for value in values):
                raise metadata.DataLoadError(
                    "file-validation", f"Sheet {sheet_name} contains a line break."
                )
            records.append(
                (("DELETE" if action == "DELETE" else "MERGE") if object_type == "ADF_VO"
                 else dat_record_directive(normalized, values))
                + "|"
                + discriminator
                + "|"
                + "|".join(escape_dat_value(value) for value in values)
            )
        converted_sections.append((discriminator, normalized, records))
        sections.append(metadata.SourceSection(discriminator, normalized))
    root = business_object_name or root_discriminator
    if not any(records for _discriminator, _header, records in converted_sections):
        raise metadata.DataLoadError("file-validation", "XLSX workbook must include at least one data row.")
    lines: list[str] = [f"SET {parameter} {value}" for parameter, value in _read_set_commands(workbook)]
    for discriminator, header, records in converted_sections:
        if discriminator == root and not records:
            continue
        lines.append("METADATA|" + discriminator + "|" + "|".join(header))
        lines.extend(records)
    return "\n".join(lines), tuple(sections), business_object_name


def xlsx_to_dat(
    path: Path,
    *,
    header_mapper: HeaderMapper | None = None,
    mapping_audit: list[metadata.ColumnMapping] | None = None,
    root_discriminator: str | None = None,
    section_discriminators: Iterable[str] | None = None,
    object_type: str | None = None,
) -> tuple[str, tuple[metadata.SourceSection, ...]]:
    content, sections, _business_object_name = read_xlsx_source(
        path, header_mapper=header_mapper, mapping_audit=mapping_audit,
        root_discriminator=root_discriminator, section_discriminators=section_discriminators,
        object_type=object_type,
    )
    return content, sections


def xlsx_business_object_name(path: Path) -> str | None:
    _content, _sections, business_object_name = read_xlsx_source(path)
    return business_object_name


def xlsx_sheet_discriminators(path: Path) -> tuple[str, ...]:
    _content, sections, _business_object_name = read_xlsx_source(path)
    return tuple(section.discriminator for section in sections)
