<!-- markdownlint-disable -->

# module `robocorp.http`

**Source:** [`__init__.py:0`](https://github.com/robocorp/robo/tree/master/http/src/robocorp/http/__init__.py#L0)

______________________________________________________________________

## function `download`

**Source:** [`_http.py:13`](https://github.com/robocorp/robo/tree/master/http/src/robocorp/http/_http.py#L13)

```python
download(
    url: str,
    path: Optional[str, Path] = None,
    overwrite: bool = False
) → Path
```

Download a file from the given URL.

If the `path` argument is not given, the file is downloaded to the current working directory. The filename is automatically selected based on either the response headers or the URL.

Params: url: URL to downloadpath: Path to destination fileoverwrite: Overwrite file if it already exists

**Returns:**
Path to created file
