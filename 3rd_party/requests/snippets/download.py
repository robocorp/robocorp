import requests


def download_file(url, local_filename):
    response = requests.get(url)
    response.raise_for_status()  # this will raise an exception if the request fails
    with open(local_filename, 'wb') as stream:
        stream.write(response.content)  # write the content of the response to a file
    return local_filename
