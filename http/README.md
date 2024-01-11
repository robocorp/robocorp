# robocorp-http

We are deprecating the `robocorp-http` -library and recommend using
[requests](https://pypi.org/project/requests/) -library directly.

`requests` is so widely used that just about any AI/LLM is able to provide you with the needed code so an extra wrapper
from us is not needed.

```python
import requests


def download_file(url, local_filename):
    response = requests.get(url)
    response.raise_for_status()  # this will raise an exception if the request fails
    with open(local_filename, 'wb') as stream:
        stream.write(response.content)  # write the content of the response to a file
    return local_filename
```

> Note: `requests` -library is already included in `robocorp` -package.
> 
> Check out more under our [**Requests**](https://github.com/robocorp/robocorp/blob/master/docs/3rd_party/requests/README.md)
> 3rd-party library documentation. 
