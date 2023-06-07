# ruff: noqa: E501
from datetime import datetime, timezone

import pytest

VALID_EMAIL = {
    "email": {
        "to": [
            {
                "address": "process.marks.moon_mission.a1234@mail.ci.robocloud.dev",
                "name": "",
            }
        ],
        "from": {"address": "mark.the.monkey@robocorp.com", "name": "Mark the Monkey"},
        "cc": [],
        "bcc": [],
        "replyTo": {"address": "mark@robocorp.com", "name": "Mark the Monkey"},
        "date": "2022-02-22T06:00:00Z",
        "subject": "A small step for a monkey...",
        "text": "Some text goes here",
    }
}

INVALID_EMAIL = {
    "failedEmail": {
        "to": [
            {
                "address": "process.marks.moon_mission.a1234@mail.ci.robocloud.dev",
                "name": "",
            }
        ],
        "from": {"address": "mark.the.monkey@robocorp.com", "name": "Mark the Monkey"},
        "cc": [],
        "bcc": [],
        "replyTo": {"address": "mark@robocorp.com", "name": "Mark the Monkey"},
        "date": "2022-02-22T06:00:00Z",
        "subject": "A small step for a monkey...",
    },
    "errors": [
        {"message": "Something failed"},
        {"message": "Files too!", "files": [{"name": "A file", "size": 123}]},
    ],
}

HTML_FILENAME = "__mail.html"
HTML_CONTENT = (
    rb'<div dir=3D"ltr"><div class=3D"gmail_default" style=3D"font-family:monospac='
    rb'e,monospace">{</div><div class=3D"gmail_default" style=3D"font-family:monos='
    rb'pace,monospace">&quot;message&quot;: &quot;from email&quot;</div><div class='
    rb'=3D"gmail_default" style=3D"font-family:monospace,monospace">}</div></div>'
)


def test_no_email(inputs):
    with pytest.raises(ValueError):
        inputs.current.email()


def test_valid_email(inputs):
    inputs.current._payload = VALID_EMAIL

    email = inputs.current.email()
    assert email.from_.name == "Mark the Monkey"
    assert (
        email.to[0].address == "process.marks.moon_mission.a1234@mail.ci.robocloud.dev"
    )
    assert email.date == datetime(2022, 2, 22, 6, 0, tzinfo=timezone.utc)
    assert email.text == "Some text goes here"
    assert email.html is None


def test_failed_email_raises(inputs):
    inputs.current._payload = INVALID_EMAIL

    with pytest.raises(ValueError) as error:
        inputs.current.email()
        assert "Something failed!" in str(error)


def test_failed_email_parses(inputs):
    inputs.current._payload = INVALID_EMAIL

    email = inputs.current.email(ignore_errors=True)
    assert email.from_.name == "Mark the Monkey"
    assert (
        email.to[0].address == "process.marks.moon_mission.a1234@mail.ci.robocloud.dev"
    )
    assert email.date == datetime(2022, 2, 22, 6, 0, tzinfo=timezone.utc)
    assert email.text is None
    assert email.html is None


def test_html_attachment(inputs, adapter):
    inputs.current._payload = VALID_EMAIL

    adapter.FILES[inputs.current.id][HTML_FILENAME] = HTML_CONTENT
    inputs.current._files = [HTML_FILENAME]

    email = inputs.current.email()
    assert isinstance(email.html, str)
    assert "from email" in email.html


def test_html_attachment_skip(inputs, adapter):
    inputs.current._payload = VALID_EMAIL

    adapter.FILES[inputs.current.id][HTML_FILENAME] = HTML_CONTENT
    inputs.current._files = [HTML_FILENAME]

    email = inputs.current.email(html=False)
    assert email.html is None
