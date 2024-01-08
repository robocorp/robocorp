import requests

def download_file(url, local_filename):
    response = requests.get(url)
    response.raise_for_status()  # This will raise an exception if the request fails
    with open(local_filename, 'wb') as f:
        f.write(response.content)  # Write the content of the response to a file
    return local_filename