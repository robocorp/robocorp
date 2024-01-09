# Requests

The `requests` library is one of the most known and used Python libraries for HTTP calls.

👉 Their slogan tells it all: `HTTP for Humans`

Whether you need to download a file, interact with an API or simply checking if a website is responding, for everything HTTP, you should just use `requests`.

## Usage

```python
import requests

def download_file(url, local_filename):
    response = requests.get(url)
    response.raise_for_status()  # This will raise an exception if the request fails
    with open(local_filename, 'wb') as f:
        f.write(response.content)  # Write the content of the response to a file
    return local_filename
```

Examples in Robocorp Portal:
* [Python PLaywright -template](https://robocorp.com/portal/robot/robocorp/template-python-browser)

## Links and references

* [PyPI](https://pypi.org/project/requests/)
* [Documentation](https://requests.readthedocs.io/en/latest/)
* [API reference](https://requests.readthedocs.io/en/latest/api/)
