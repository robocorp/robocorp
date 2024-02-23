<!-- markdownlint-disable -->

# module `robocorp.action_server.vendored_deps.package_deps.conda_impl.conda_url`

**Source:** [`conda_url.py:0`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_url.py#L0)

Common URL utilities.

## Variables

- **file_scheme**
- **url_attrs**
- **on_win**

______________________________________________________________________

## function `hex_octal_to_int`

**Source:** [`conda_url.py:20`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_url.py#L20)

```python
hex_octal_to_int(ho)
```

______________________________________________________________________

## function `url_to_s3_info`

**Source:** [`conda_url.py:243`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_url.py#L243)

```python
url_to_s3_info(url)
```

Convert an s3 url to a tuple of bucket and key.

**Examples:**

` url_to_s3_info("s3://bucket-name.bucket/here/is/the/key")`
('bucket-name.bucket', '/here/is/the/key')

______________________________________________________________________

## function `is_url`

**Source:** [`conda_url.py:256`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_url.py#L256)

```python
is_url(url)
```

**Examples:**

` is_url(None)`
False
` is_url("s3://some/bucket")`True

______________________________________________________________________

## function `is_ipv4_address`

**Source:** [`conda_url.py:272`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_url.py#L272)

```python
is_ipv4_address(string_ip)
```

**Examples:**

` [is_ipv4_address(ip) for ip in ('8.8.8.8', '192.168.10.10', '255.255.255.255')]`
\[True, True, True\]
` [is_ipv4_address(ip) for ip in ('8.8.8', '192.168.10.10.20', '256.255.255.255', '::1')]`\[False, False, False, False\]

______________________________________________________________________

## function `is_ipv6_address`

**Source:** [`conda_url.py:287`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_url.py#L287)

```python
is_ipv6_address(string_ip)
```

**Examples:**

> > \[is_ipv6_address(ip) for ip in ('::1', '2001:db8:85a3::370:7334', '1234:'\*7+'1234')\]\[True, True, True\]>> \[is_ipv6_address(ip) for ip in ('192.168.10.10', '1234:'\*8+'1234')\]\[False, False\]

______________________________________________________________________

## function `is_ip_address`

**Source:** [`conda_url.py:302`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_url.py#L302)

```python
is_ip_address(string_ip)
```

**Examples:**

> > is_ip_address('192.168.10.10')True>> is_ip_address('::1')True>> is_ip_address('www.google.com')False

______________________________________________________________________

## function `join`

**Source:** [`conda_url.py:315`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_url.py#L315)

```python
join(*args)
```

______________________________________________________________________

## function `join`

**Source:** [`conda_url.py:315`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_url.py#L315)

```python
join(*args)
```

______________________________________________________________________

## function `has_scheme`

**Source:** [`conda_url.py:323`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_url.py#L323)

```python
has_scheme(value)
```

______________________________________________________________________

## function `strip_scheme`

**Source:** [`conda_url.py:327`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_url.py#L327)

```python
strip_scheme(url)
```

**Examples:**

` strip_scheme("https://www.conda.io")`
'www.conda.io'
` strip_scheme("s3://some.bucket/plus/a/path.ext")`'some.bucket/plus/a/path.ext'

______________________________________________________________________

## function `mask_anaconda_token`

**Source:** [`conda_url.py:338`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_url.py#L338)

```python
mask_anaconda_token(url)
```

______________________________________________________________________

## function `split_anaconda_token`

**Source:** [`conda_url.py:343`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_url.py#L343)

```python
split_anaconda_token(url)
```

**Examples:**

` split_anaconda_token("https://1.2.3.4/t/tk-123-456/path")`
(u'https://1.2.3.4/path', u'tk-123-456')
` split_anaconda_token("https://1.2.3.4/t//path")`(u'https://1.2.3.4/path', u'')
` split_anaconda_token("https://some.domain/api/t/tk-123-456/path")`
(u'https://some.domain/api/path', u'tk-123-456')
` split_anaconda_token("https://1.2.3.4/conda/t/tk-123-456/path")`(u'https://1.2.3.4/conda/path', u'tk-123-456')
` split_anaconda_token("https://1.2.3.4/path")`
(u'https://1.2.3.4/path', None)
` split_anaconda_token("https://10.2.3.4:8080/conda/t/tk-123-45")`(u'https://10.2.3.4:8080/conda', u'tk-123-45')

______________________________________________________________________

## function `split_platform`

**Source:** [`conda_url.py:365`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_url.py#L365)

```python
split_platform(known_subdirs, url)
```

**Examples:**

` from conda.base.constants import KNOWN_SUBDIRS`
` split_platform(KNOWN_SUBDIRS, "https://1.2.3.4/t/tk-123/linux-ppc64le/path")`(u'https://1.2.3.4/t/tk-123/path', u'linux-ppc64le')

______________________________________________________________________

## function `has_platform`

**Source:** [`conda_url.py:388`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_url.py#L388)

```python
has_platform(url, known_subdirs)
```

______________________________________________________________________

## function `split_scheme_auth_token`

**Source:** [`conda_url.py:398`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_url.py#L398)

```python
split_scheme_auth_token(url)
```

**Examples:**

` split_scheme_auth_token("https://u:p@conda.io/t/x1029384756/more/path")`
('conda.io/more/path', 'https', 'u:p', 'x1029384756')
` split_scheme_auth_token(None)`(None, None, None, None)

______________________________________________________________________

## function `split_conda_url_easy_parts`

**Source:** [`conda_url.py:420`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_url.py#L420)

```python
split_conda_url_easy_parts(known_subdirs, url)
```

______________________________________________________________________

## class `Url`

**Source:** [`conda_url.py:151`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_url.py#L151)

Object used to represent a Url. The string representation of this object is a url string.

This object was inspired by the urllib3 implementation as it gives you a way to construct URLs from various parts. The motivation behind this object was making something that is interoperable with built the `urllib.parse.urlparse` function and has more features than the built-in `ParseResult` object.

#### property `auth`

#### property `netloc`

______________________________________________________________________

### method `as_dict`

**Source:** [`conda_url.py:216`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_url.py#L216)

```python
as_dict() → dict
```

Provide a public interface for namedtuple's \_asdict

______________________________________________________________________

### classmethod `from_parse_result`

**Source:** [`conda_url.py:224`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_url.py#L224)

```python
from_parse_result(parse_result: ParseResult) → Url
```

______________________________________________________________________

### method `replace`

**Source:** [`conda_url.py:220`](https://github.com/robocorp/robocorp/tree/master/action_server/src/robocorp/action_server/vendored_deps/package_deps/conda_impl/conda_url.py#L220)

```python
replace(**kwargs) → Url
```

Provide a public interface for namedtuple's \_replace
