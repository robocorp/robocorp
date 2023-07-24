from tempfile import TemporaryDirectory
from unittest import mock

import pytest
import responses

from robocorp.http import download


@pytest.fixture
def mock_open():
    with mock.patch("robocorp.http._http.open") as mock_open:
        yield mock_open


@responses.activate
def test_download_with_header_path(mock_open):
    responses.add(
        responses.GET,
        "https://example.com/url_name.txt",
        body="some_content",
        headers={
            "Something-Else": "Not Relevant",
            "Content-Disposition": 'attachment; filename="header_name.txt"',
        },
    )

    path = download("https://example.com/url_name.txt")
    assert path.name == "header_name.txt"


@responses.activate
def test_download_with_url_path(mock_open):
    responses.add(
        responses.GET,
        "https://example.com/url_name.txt",
        body="some_content",
    )

    path = download("https://example.com/url_name.txt")
    assert path.name == "url_name.txt"


@responses.activate
def test_download_with_manual_path(mock_open):
    responses.add(
        responses.GET,
        "https://example.com/url_name.txt",
        body="some_content",
    )

    path = download("https://example.com/url_name.txt", "custom_name.txt")
    assert path.name == "custom_name.txt"


@responses.activate
def test_download_with_non_filename_path(mock_open):
    responses.add(
        responses.GET,
        "https://example.com/path_name/",
        body="some_content",
    )

    path = download("https://example.com/path_name/")
    assert path.name == "path_name"


@responses.activate
def test_download_with_url_params(mock_open):
    responses.add(
        responses.GET,
        "https://example.com/filename.pdf?first=1&second=2",
        body="some_content",
    )

    path = download("https://example.com/filename.pdf?first=1&second=2")
    assert path.name == "filename.pdf"


@responses.activate
def test_download_with_dir_path(mock_open):
    responses.add(
        responses.GET,
        "https://example.com/filename.txt",
        body="some_content",
    )

    with TemporaryDirectory() as dirname:
        path = download("https://example.com/filename.txt", dirname)
        assert path.name == "filename.txt"
        assert str(path.parent) == str(dirname)


@responses.activate
def test_download_with_url_path_nested(mock_open):
    responses.add(
        responses.GET,
        "https://example.com/dir/subdir/filename.txt",
        body="some_content",
    )

    path = download("https://example.com/dir/subdir/filename.txt")
    assert path.name == "filename.txt"
