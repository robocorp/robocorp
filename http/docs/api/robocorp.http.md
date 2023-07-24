<!-- markdownlint-disable -->

<a href="https://github.com/robocorp/robo/tree/master/http/src/robocorp/http/__init__.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

# <kbd>module</kbd> `robocorp.http`





---

<a href="https://github.com/robocorp/robo/tree/master/http/src/robocorp/http/_http.py#L13"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `download`

```python
download(
    url: str,
    path: Optional[str, Path] = None,
    overwrite: bool = False
) → Path
```

Download a file from the given URL. 

If the `path` argument is not given, the file is downloaded to the current working directory. The filename is automatically selected based on either the response headers or the URL. 

Params: url: URL to download path: Path to destination file overwrite: Overwrite file if it already exists 



**Returns:**
 Path to created file 


