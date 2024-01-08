# robocorp-http

We are depricating the `robocorp-http` -library and recommend using [requests](https://pypi.org/project/requests/) -library directly.

`requests` is so widely used that just about any AI/LLM is able to provide you with the needed code so extra wrapper is not needed.

Note: `requests` -library is already included in `robocorp` -package.
[Requests documentation](https://requests.readthedocs.io/en/latest/)

```python
import requests

def download_file(url, local_filename):
    response = requests.get(url)
    response.raise_for_status()  # This will raise an exception if the request fails
    with open(local_filename, 'wb') as f:
        f.write(response.content)  # Write the content of the response to a file
    return local_filename
```
