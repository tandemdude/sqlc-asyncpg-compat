# Copyright (c) 2024-present tandemdude
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""SQLC compat layer for asyncpg to avoid using sqlalchemy."""

from __future__ import annotations

__all__ = ["text"]

import re
import typing as t

__version__ = "0.0.1"

_PARAM_RE: t.Final[re.Pattern[str]] = re.compile(r":p(\d+)")
_ESCAPED_COLON_RE: t.Final[re.Pattern[str]] = re.compile(r"\\\\:")

_CONVERTED_QUERIES: t.Final[dict[str, str]] = {}


def text(txt: str) -> str:
    """
    Converts a sqlalchemy-style query into an asyncpg compatible equivalent. This uses regex
    to replace parameters (e.g. ":p1") with the appropriate syntax (e.g. "$1"). Converted
    queries are cached for a slight performance boost.

    Args:
        txt: The query to fix.

    Returns:
        The fixed query.
    """
    if txt in _CONVERTED_QUERIES:
        return _CONVERTED_QUERIES[txt]

    query = _PARAM_RE.sub(lambda match: f"${match.group(1)}", txt)
    _CONVERTED_QUERIES[txt] = (query := _ESCAPED_COLON_RE.sub(":", query))
    return query
