# Original work Copyright 2017 Palantir Technologies, Inc. (MIT)
# Original work Copyright 2020 Open Law Library. (Apache 2)
# See ThirdPartyNotices.txt in the project root for license information.
# All modifications Copyright (c) Robocorp Technologies Inc.
# All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http: // www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A collection of URI utilities with logic built on the VSCode URI library.

https://github.com/Microsoft/vscode-uri/blob/e59cab84f5df6265aed18ae5f43552d3eef13bb9/lib/index.ts
"""

import re
import sys
from functools import lru_cache

from urllib.parse import (
    urlparse as parse_urlparse,  # noqa
    urlunparse as parse_urlunparse,  # noqa
    quote as parse_quote,  # noqa
    unquote as parse_unquote,  # noqa
)

IS_WIN = sys.platform == "win32"

RE_DRIVE_LETTER_PATH = re.compile(r"^\/[a-zA-Z]:")


if sys.platform == "win32":

    def normalize_drive(filename):
        if len(filename) > 1 and filename[1] == ":" and not filename[0].islower():
            return filename[0].lower() + filename[1:]
        return filename


else:

    def normalize_drive(filename):
        return filename


def _normalize_win_path(path):
    netloc = ""

    # normalize to fwd-slashes on windows,
    # on other systems bwd-slashes are valid
    # filename character, eg /f\oo/ba\r.txt
    if IS_WIN:
        path = path.replace("\\", "/")

    # check for authority as used in UNC shares
    # or use the path as given
    if path[:2] == "//":
        idx = path.index("/", 2)
        if idx == -1:
            netloc = path[2:]
        else:
            netloc = path[2:idx]
            path = path[idx:]

    # Ensure that path starts with a slash
    # or that it is at least a slash
    if not path.startswith("/"):
        path = "/" + path

    # Normalize drive paths to lower case
    if RE_DRIVE_LETTER_PATH.match(path):
        path = path[0] + path[1].lower() + path[2:]

    return path, netloc


@lru_cache(500)
def from_fs_path(path: str) -> str:
    """Returns a URI for the given filesystem path."""
    scheme = "file"
    params, query, fragment = "", "", ""
    path, netloc = _normalize_win_path(path)
    return urlunparse((scheme, netloc, path, params, query, fragment))


@lru_cache(500)
def normalize_uri(uri: str) -> str:
    if uri_scheme(uri) == "file":
        return from_fs_path(to_fs_path(uri))
    return uri


@lru_cache(500)
def to_fs_path(uri: str) -> str:
    """Returns the filesystem path of the given URI.

    Will handle UNC paths and normalize windows drive letters to lower-case.
    Also uses the platform specific path separator. Will *not* validate the
    path for invalid characters and semantics.
    Will *not* look at the scheme of this URI.
    """
    # scheme://netloc/path;parameters?query#fragment
    scheme, netloc, path, _params, _query, _fragment = urlparse(uri)

    if netloc and path and scheme == "file":
        # unc path: file://shares/c$/far/boo
        value = "//{}{}".format(netloc, path)

    elif RE_DRIVE_LETTER_PATH.match(path):
        # windows drive letter: file:///C:/far/boo
        value = path[1].lower() + path[2:]

    else:
        # Other path
        value = path

    if IS_WIN:
        value = value.replace("/", "\\")
        value = normalize_drive(value)

    return value


def uri_scheme(uri):
    try:
        return urlparse(uri)[0]
    except (TypeError, IndexError):
        return None


def uri_with(
    uri, scheme=None, netloc=None, path=None, params=None, query=None, fragment=None
):
    """Return a URI with the given part(s) replaced.

    Parts are decoded / encoded.
    """
    old_scheme, old_netloc, old_path, old_params, old_query, old_fragment = urlparse(
        uri
    )

    path, _netloc = _normalize_win_path(path)
    return urlunparse(
        (
            scheme or old_scheme,
            netloc or old_netloc,
            path or old_path,
            params or old_params,
            query or old_query,
            fragment or old_fragment,
        )
    )


def urlparse(uri):
    """Parse and decode the parts of a URI."""
    scheme, netloc, path, params, query, fragment = parse_urlparse(uri)
    return (
        parse_unquote(scheme),
        parse_unquote(netloc),
        parse_unquote(path),
        parse_unquote(params),
        parse_unquote(query),
        parse_unquote(fragment),
    )


def urlunparse(parts):
    """Unparse and encode parts of a URI."""
    scheme, netloc, path, params, query, fragment = parts

    # Avoid encoding the windows drive letter colon
    if RE_DRIVE_LETTER_PATH.match(path):
        quoted_path = path[:3] + parse_quote(path[3:])
    else:
        quoted_path = parse_quote(path)

    return parse_urlunparse(
        (
            parse_quote(scheme),
            parse_quote(netloc),
            quoted_path,
            parse_quote(params),
            parse_quote(query),
            parse_quote(fragment),
        )
    )
