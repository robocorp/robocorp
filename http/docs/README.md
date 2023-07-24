# robocorp-http

This HTTP library is meant as a simple utility library for downloading
files over HTTP, and (later) making robust HTTP requests (GET/POST/etc.)

## Getting started

Currently the library exposes one method:

```python
from robocorp.http import download
from robocorp.tasks import task

def fetch_workbook():
	path = download("https://example.com/orders.xlsx")
	print(f"Downloaded file to: {path}")
```

## API Reference

Information on specific functions or classes: [robocorp.http](./api/robocorp.http.md)

## Changelog

A list of releases and corresponding changes can be found in the [changelog](./CHANGELOG.md).
