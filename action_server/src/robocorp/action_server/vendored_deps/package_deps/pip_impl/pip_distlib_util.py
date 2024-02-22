import re
from types import SimpleNamespace as Container
from urllib.parse import urlparse

#
# Requirement parsing code as per PEP 508
#


IDENTIFIER = re.compile(r"^([\w\.-]+)\s*")
VERSION_IDENTIFIER = re.compile(r"^([\w\.*+-]+)\s*")
COMPARE_OP = re.compile(r"^(<=?|>=?|={2,3}|[~!]=)\s*")
MARKER_OP = re.compile(r"^((<=?)|(>=?)|={2,3}|[~!]=|in|not\s+in)\s*")
OR = re.compile(r"^or\b\s*")
AND = re.compile(r"^and\b\s*")
NON_SPACE = re.compile(r"(\S+)\s*")
STRING_CHUNK = re.compile(r"([\s\w\.{}()*+#:;,/?!~`@$%^&=|<>\[\]-]+)")


def parse_marker(marker_string):
    """
    Parse a marker string and return a dictionary containing a marker expression.

    The dictionary will contain keys "op", "lhs" and "rhs" for non-terminals in
    the expression grammar, or strings. A string contained in quotes is to be
    interpreted as a literal string, and a string not contained in quotes is a
    variable (such as os_name).
    """

    def marker_var(remaining):
        # either identifier, or literal string
        m = IDENTIFIER.match(remaining)
        if m:
            result = m.groups()[0]
            remaining = remaining[m.end() :]
        elif not remaining:
            raise SyntaxError("unexpected end of input")
        else:
            q = remaining[0]
            if q not in "'\"":
                raise SyntaxError("invalid expression: %s" % remaining)
            oq = "'\"".replace(q, "")
            remaining = remaining[1:]
            parts = [q]
            while remaining:
                # either a string chunk, or oq, or q to terminate
                if remaining[0] == q:
                    break
                elif remaining[0] == oq:
                    parts.append(oq)
                    remaining = remaining[1:]
                else:
                    m = STRING_CHUNK.match(remaining)
                    if not m:
                        raise SyntaxError("error in string literal: %s" % remaining)
                    parts.append(m.groups()[0])
                    remaining = remaining[m.end() :]
            else:
                s = "".join(parts)
                raise SyntaxError("unterminated string: %s" % s)
            parts.append(q)
            result = "".join(parts)
            remaining = remaining[1:].lstrip()  # skip past closing quote
        return result, remaining

    def marker_expr(remaining):
        if remaining and remaining[0] == "(":
            result, remaining = marker(remaining[1:].lstrip())
            if remaining[0] != ")":
                raise SyntaxError("unterminated parenthesis: %s" % remaining)
            remaining = remaining[1:].lstrip()
        else:
            lhs, remaining = marker_var(remaining)
            while remaining:
                m = MARKER_OP.match(remaining)
                if not m:
                    break
                op = m.groups()[0]
                remaining = remaining[m.end() :]
                rhs, remaining = marker_var(remaining)
                lhs = {"op": op, "lhs": lhs, "rhs": rhs}
            result = lhs
        return result, remaining

    def marker_and(remaining):
        lhs, remaining = marker_expr(remaining)
        while remaining:
            m = AND.match(remaining)
            if not m:
                break
            remaining = remaining[m.end() :]
            rhs, remaining = marker_expr(remaining)
            lhs = {"op": "and", "lhs": lhs, "rhs": rhs}
        return lhs, remaining

    def marker(remaining):
        lhs, remaining = marker_and(remaining)
        while remaining:
            m = OR.match(remaining)
            if not m:
                break
            remaining = remaining[m.end() :]
            rhs, remaining = marker_and(remaining)
            lhs = {"op": "or", "lhs": lhs, "rhs": rhs}
        return lhs, remaining

    return marker(marker_string)


def parse_requirement(req):
    """
    Parse a requirement passed in as a string. Return a Container
    whose attributes contain the various parts of the requirement.
    """
    remaining = req.strip()
    if not remaining or remaining.startswith("#"):
        return None
    m = IDENTIFIER.match(remaining)
    if not m:
        raise SyntaxError("name expected: %s" % remaining)
    distname = m.groups()[0]
    remaining = remaining[m.end() :]
    extras = mark_expr = versions = uri = None
    if remaining and remaining[0] == "[":
        i = remaining.find("]", 1)
        if i < 0:
            raise SyntaxError("unterminated extra: %s" % remaining)
        s = remaining[1:i]
        remaining = remaining[i + 1 :].lstrip()
        extras = []
        while s:
            m = IDENTIFIER.match(s)
            if not m:
                raise SyntaxError("malformed extra: %s" % s)
            extras.append(m.groups()[0])
            s = s[m.end() :]
            if not s:
                break
            if s[0] != ",":
                raise SyntaxError("comma expected in extras: %s" % s)
            s = s[1:].lstrip()
        if not extras:
            extras = None
    if remaining:
        if remaining[0] == "@":
            # it's a URI
            remaining = remaining[1:].lstrip()
            m = NON_SPACE.match(remaining)
            if not m:
                raise SyntaxError("invalid URI: %s" % remaining)
            uri = m.groups()[0]
            t = urlparse(uri)
            # there are issues with Python and URL parsing, so this test
            # is a bit crude. See bpo-20271, bpo-23505. Python doesn't
            # always parse invalid URLs correctly - it should raise
            # exceptions for malformed URLs
            if not (t.scheme and t.netloc):
                raise SyntaxError("Invalid URL: %s" % uri)
            remaining = remaining[m.end() :].lstrip()
        else:

            def get_versions(ver_remaining):
                """
                Return a list of operator, version tuples if any are
                specified, else None.
                """
                m = COMPARE_OP.match(ver_remaining)
                versions = None
                if m:
                    versions = []
                    while True:
                        op = m.groups()[0]
                        ver_remaining = ver_remaining[m.end() :]
                        m = VERSION_IDENTIFIER.match(ver_remaining)
                        if not m:
                            raise SyntaxError("invalid version: %s" % ver_remaining)
                        v = m.groups()[0]
                        versions.append((op, v))
                        ver_remaining = ver_remaining[m.end() :]
                        if not ver_remaining or ver_remaining[0] != ",":
                            break
                        ver_remaining = ver_remaining[1:].lstrip()
                        # Some packages have a trailing comma which would break things
                        # See issue #148
                        if not ver_remaining:
                            break
                        m = COMPARE_OP.match(ver_remaining)
                        if not m:
                            raise SyntaxError("invalid constraint: %s" % ver_remaining)
                    if not versions:
                        versions = None
                return versions, ver_remaining

            if remaining[0] != "(":
                versions, remaining = get_versions(remaining)
            else:
                i = remaining.find(")", 1)
                if i < 0:
                    raise SyntaxError("unterminated parenthesis: %s" % remaining)
                s = remaining[1:i]
                remaining = remaining[i + 1 :].lstrip()
                # As a special diversion from PEP 508, allow a version number
                # a.b.c in parentheses as a synonym for ~= a.b.c (because this
                # is allowed in earlier PEPs)
                if COMPARE_OP.match(s):
                    versions, _ = get_versions(s)
                else:
                    m = VERSION_IDENTIFIER.match(s)
                    if not m:
                        raise SyntaxError("invalid constraint: %s" % s)
                    v = m.groups()[0]
                    s = s[m.end() :].lstrip()
                    if s:
                        raise SyntaxError("invalid constraint: %s" % s)
                    versions = [("~=", v)]

    if remaining:
        if remaining[0] != ";":
            raise SyntaxError("invalid requirement: %s" % remaining)
        remaining = remaining[1:].lstrip()

        mark_expr, remaining = parse_marker(remaining)

    if remaining and remaining[0] != "#":
        raise SyntaxError("unexpected trailing data: %s" % remaining)

    if not versions:
        rs = distname
    else:
        rs = "%s %s" % (distname, ", ".join(["%s %s" % con for con in versions]))
    return Container(
        name=distname,
        extras=extras,
        constraints=versions,
        marker=mark_expr,
        url=uri,
        requirement=rs,
    )
