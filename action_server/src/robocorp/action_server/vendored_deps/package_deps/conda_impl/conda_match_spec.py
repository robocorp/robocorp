# Based on: https://github.com/conda/conda/blob/main/conda/models/match_spec.py
"""
Original license:
BSD 3-Clause License

Copyright (c) 2012, Anaconda, Inc.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the copyright holder nor the names of its
      contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import os
import re
from logging import getLogger

from . import conda_url

log = getLogger(__name__)


class InvalidMatchSpec(RuntimeError):
    pass


def _parse_version_plus_build(v_plus_b):
    """This should reliably pull the build string out of a version + build string combo.
    Examples:
        >>> _parse_version_plus_build("=1.2.3 0")
        ('=1.2.3', '0')
        >>> _parse_version_plus_build("1.2.3=0")
        ('1.2.3', '0')
        >>> _parse_version_plus_build(">=1.0 , < 2.0 py34_0")
        ('>=1.0,<2.0', 'py34_0')
        >>> _parse_version_plus_build(">=1.0 , < 2.0 =py34_0")
        ('>=1.0,<2.0', 'py34_0')
        >>> _parse_version_plus_build("=1.2.3 ")
        ('=1.2.3', None)
        >>> _parse_version_plus_build(">1.8,<2|==1.7")
        ('>1.8,<2|==1.7', None)
        >>> _parse_version_plus_build("* openblas_0")
        ('*', 'openblas_0')
        >>> _parse_version_plus_build("* *")
        ('*', '*')
    """
    parts = re.search(
        r"((?:.+?)[^><!,|]?)(?:(?<![=!|,<>~])(?:[ =])([^-=,|<>~]+?))?$", v_plus_b
    )
    if parts:
        version, build = parts.groups()
        build = build and build.strip()
    else:
        version, build = v_plus_b, None
    return version and version.replace(" ", ""), build


def _parse_legacy_dist(dist_str):
    """
    Examples:
        >>> _parse_legacy_dist("_license-1.1-py27_1.tar.bz2")
        ('_license', '1.1', 'py27_1')
        >>> _parse_legacy_dist("_license-1.1-py27_1")
        ('_license', '1.1', 'py27_1')
    """
    from .conda_path import strip_pkg_extension

    dist_str, _ = strip_pkg_extension(dist_str)
    name, version, build = dist_str.rsplit("-", 2)
    return name, version, build


def _parse_channel(channel_val):
    from .conda_channel import Channel

    if not channel_val:
        return None, None
    chn = Channel(channel_val)
    channel_name = chn.name or chn.base_url
    return channel_name, chn.subdir


_PARSE_CACHE: dict = {}


def parse_spec_str(spec_str):
    cached_result = _PARSE_CACHE.get(spec_str)
    if cached_result:
        return cached_result

    import warnings

    from .conda_channel import Channel
    from .conda_path import expand, is_package_file, url_to_path
    from .conda_url import is_url

    original_spec_str = spec_str

    # pre-step for ugly backward compat
    if spec_str.endswith("@"):
        feature_name = spec_str[:-1]
        return {
            "name": "*",
            "track_features": (feature_name,),
        }

    # Step 1. strip '#' comment
    if "#" in spec_str:
        ndx = spec_str.index("#")
        spec_str, _ = spec_str[:ndx], spec_str[ndx:]
        spec_str.strip()

    # Step 1.b strip ' if ' anticipating future compatibility issues
    spec_split = spec_str.split(" if ", 1)
    if len(spec_split) > 1:
        log.debug("Ignoring conditional in spec %s", spec_str)
    spec_str = spec_split[0]

    # Step 2. done if spec_str is a tarball
    if is_package_file(spec_str):
        # treat as a normal url
        if not is_url(spec_str):
            spec_str = conda_url.unquote(conda_url.path_to_url(expand(spec_str)))

        channel = Channel(spec_str)
        if channel.subdir:
            name, version, build = _parse_legacy_dist(channel.package_filename)
            result = {
                "channel": channel.canonical_name,
                "subdir": channel.subdir,
                "name": name,
                "version": version,
                "build": build,
                "fn": channel.package_filename,
                "url": spec_str,
            }
        else:
            # url is not a channel
            if spec_str.startswith("file://"):
                # We must undo percent-encoding when generating fn.
                path_or_url = url_to_path(spec_str)
            else:
                path_or_url = spec_str

            return {
                "name": "*",
                "fn": os.path.basename(path_or_url),
                "url": spec_str,
            }
        return result

    # Step 3. strip off brackets portion
    brackets = {}
    m3 = re.match(r".*(?:(\[.*\]))", spec_str)
    if m3:
        brackets_str = m3.groups()[0]
        spec_str = spec_str.replace(brackets_str, "")
        brackets_str = brackets_str[1:-1]
        m3b = re.finditer(
            r'([a-zA-Z0-9_-]+?)=(["\']?)([^\'"]*?)(\2)(?:[, ]|$)', brackets_str
        )
        for match in m3b:
            key, _, value, _ = match.groups()
            if not key or not value:
                raise InvalidMatchSpec(
                    original_spec_str, "key-value mismatch in brackets"
                )
            brackets[key] = value

    # Step 4. strip off parens portion
    m4 = re.match(r".*(?:(\(.*\)))", spec_str)
    parens = {}
    if m4:
        parens_str = m4.groups()[0]
        spec_str = spec_str.replace(parens_str, "")
        parens_str = parens_str[1:-1]
        m4b = re.finditer(
            r'([a-zA-Z0-9_-]+?)=(["\']?)([^\'"]*?)(\2)(?:[, ]|$)', parens_str
        )
        for match in m4b:
            key, _, value, _ = match.groups()
            parens[key] = value
        if "optional" in parens_str:
            parens["optional"] = True

    # Step 5. strip off '::' channel and namespace
    m5 = spec_str.rsplit(":", 2)
    m5_len = len(m5)
    if m5_len == 3:
        channel_str, namespace, spec_str = m5
    elif m5_len == 2:
        namespace, spec_str = m5
        channel_str = None
    elif m5_len:
        spec_str = m5[0]
        channel_str, namespace = None, None
    else:
        raise NotImplementedError()
    channel, subdir = _parse_channel(channel_str)
    if "channel" in brackets:
        b_channel, b_subdir = _parse_channel(brackets.pop("channel"))
        if b_channel:
            channel = b_channel
        if b_subdir:
            subdir = b_subdir
    if "subdir" in brackets:
        subdir = brackets.pop("subdir")

    # Step 6. strip off package name from remaining version + build
    m3 = re.match(r"([^ =<>!~]+)?([><!=~ ].+)?", spec_str)
    if m3:
        name, spec_str = m3.groups()
        if name is None:
            raise InvalidMatchSpec(
                original_spec_str, "no package name found in '%s'" % spec_str
            )
    else:
        raise InvalidMatchSpec(original_spec_str, "no package name found")

    # Step 7. otherwise sort out version + build
    spec_str = spec_str and spec_str.strip()
    # This was an attempt to make MatchSpec('numpy-1.11.0-py27_0') work like we'd want. It's
    # not possible though because plenty of packages have names with more than one '-'.
    # if spec_str is None and name.count('-') >= 2:
    #     name, version, build = _parse_legacy_dist(name)
    if spec_str:
        if "[" in spec_str:
            raise InvalidMatchSpec(
                original_spec_str, "multiple brackets sections not allowed"
            )

        version, build = _parse_version_plus_build(spec_str)

        # Catch cases where version ends up as "==" and pass it through so existing error
        # handling code can treat it like cases where version ends up being "<=" or ">=".
        # This is necessary because the "Translation" code below mangles "==" into a empty
        # string, which results in an empty version field on "components." The set of fields
        # on components drives future logic which breaks on an empty string but will deal with
        # missing versions like "==", "<=", and ">=" "correctly."
        #
        # All of these "missing version" cases result from match specs like "numpy==",
        # "numpy<=", "numpy>=", "numpy= " (with trailing space). Existing code indicates
        # these should be treated as an error and an exception raised.
        # IMPORTANT: "numpy=" (no trailing space) is treated as valid.
        if version == "==" or version == "=":
            pass
        # Otherwise,
        # translate version '=1.2.3' to '1.2.3*'
        # is it a simple version starting with '='? i.e. '=1.2.3'
        elif version[0] == "=":
            test_str = version[1:]
            if version[:2] == "==" and build is None:
                version = version[2:]
            elif not any(c in test_str for c in "=,|"):
                if build is None and test_str[-1] != "*":
                    version = test_str + "*"
                else:
                    version = test_str
    else:
        version, build = None, None

    # Step 8. now compile components together
    components = {}
    components["name"] = name or "*"

    if channel is not None:
        components["channel"] = channel
    if subdir is not None:
        components["subdir"] = subdir
    if namespace is not None:
        # components['namespace'] = namespace
        pass
    if version is not None:
        components["version"] = version
    if build is not None:
        components["build"] = build

    # anything in brackets will now strictly override key as set in other area of spec str
    # EXCEPT FOR: name
    # If we let name in brackets override a name outside of brackets it is possible to write
    # MatchSpecs that appear to install one package but actually install a completely different one
    # e.g. tensorflow[name=* version=* md5=<hash of pytorch package> ] will APPEAR to install
    # tensorflow but actually install pytorch.
    if "name" in components and "name" in brackets:
        warnings.warn(
            f"'name' specified both inside ({brackets['name']}) and outside ({components['name']})"
            " of brackets. the value outside of brackets ({components['name']}) will be used."
        )
        del brackets["name"]
    components.update(brackets)
    components["_original_spec_str"] = original_spec_str
    _PARSE_CACHE[original_spec_str] = components
    return components
