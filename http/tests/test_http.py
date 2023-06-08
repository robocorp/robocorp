from unittest import mock

from robocorp.http import download


def test_download():
    with mock.patch("robocorp.http.http.open"):
        with mock.patch("robocorp.http.http.requests") as mock_requests:
            path = download("https://example.com/file.txt")
            mock_requests.get.assert_called_once_with(
                "https://example.com/file.txt", stream=mock.ANY
            )
            assert path.name == "file.txt"
