# ruff: noqa: E501
import copy
from datetime import datetime, timezone

import pytest

EMAIL_VALID = {
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

EMAIL_FAILED = {
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

# Missing replyTo field
EMAIL_OPTIONAL_FIELD = {
    "email": {
        "from": {"name": "Snake", "address": "snake@python.com"},
        "to": [
            {
                "name": "Example",
                "address": "example@address.com",
            }
        ],
        "cc": [],
        "bcc": [],
        "subject": "attachemnts",
        "date": "2023-03-26T16:38:38.000Z",
        "text": "Lorem Impsum",
    }
}

# Missing bcc field
EMAIL_MISSING_FIELD = {
    "email": {
        "from": {"name": "Snake", "address": "snake@python.com"},
        "to": [
            {
                "name": "Example",
                "address": "example@address.com",
            }
        ],
        "cc": [],
        "subject": "attachemnts",
        "date": "2023-03-26T16:38:38.000Z",
        "text": "Lorem Impsum",
    }
}

# Field from is str instead of dict
EMAIL_MALFORMED = {
    "email": {
        "from": "invalid@address.com",
        "to": [
            {
                "name": "Example",
                "address": "example@address.com",
            }
        ],
        "cc": [],
        "bcc": [],
        "replyTo": {"name": "A Name", "address": "a@address.com"},
        "subject": "attachemnts",
        "date": "2023-03-26T16:38:38.000Z",
        "text": "Lorem Impsum",
    }
}

EMAIL_VALID_SNAKE_CASE = {
    "email": {
        "from": {"name": "Snake", "address": "snake@python.com"},
        "to": [
            {
                "name": "Example",
                "address": "example@address.com",
            }
        ],
        "cc": [],
        "bcc": [],
        "reply_to": {"name": "A Name", "address": "a@address.com"},
        "subject": "attachemnts",
        "date": "2023-03-26T16:38:38.000Z",
        "text": "Lorem Impsum",
    }
}

HTML_FILENAME = "__mail.html"
HTML_CONTENT = (
    rb'<div dir=3D"ltr"><div class=3D"gmail_default" style=3D"font-family:monospac='
    rb'e,monospace">{</div><div class=3D"gmail_default" style=3D"font-family:monos='
    rb'pace,monospace">&quot;message&quot;: &quot;from email&quot;</div><div class='
    rb'=3D"gmail_default" style=3D"font-family:monospace,monospace">}</div></div>'
)


def test_no_email(inputs):
    with pytest.raises(ValueError) as exc_info:
        inputs.current.email()

    assert str(exc_info.value) == "No email in work item"


def test_wrong_payload_type(inputs):
    inputs.current._payload = ["Some array of things"]

    with pytest.raises(ValueError) as exc_info:
        inputs.current.email()

    assert str(exc_info.value) == "Expected 'dict' payload, was 'list'"


def test_optional_field(inputs):
    inputs.current._payload = EMAIL_OPTIONAL_FIELD

    email = inputs.current.email()
    assert email.reply_to is None


def test_missing_field(inputs):
    inputs.current._payload = EMAIL_MISSING_FIELD

    with pytest.raises(ValueError) as exc_info:
        inputs.current.email()

    assert str(exc_info.value) == "Missing key in 'email' field: 'bcc'"


def test_malformed(inputs):
    inputs.current._payload = EMAIL_MALFORMED

    with pytest.raises(ValueError) as exc_info:
        inputs.current.email()

    assert "Malformed 'email' field" in str(exc_info.value)


def test_email_valid(inputs):
    inputs.current._payload = EMAIL_VALID

    email = inputs.current.email()
    assert email.from_.name == "Mark the Monkey"
    assert (
        email.to[0].address == "process.marks.moon_mission.a1234@mail.ci.robocloud.dev"
    )
    assert email.date == datetime(2022, 2, 22, 6, 0, tzinfo=timezone.utc)
    assert email.text == "Some text goes here"
    assert email.html is None


def test_email_valid_regression(inputs):
    inputs.current._payload = EMAIL_VALID_SNAKE_CASE
    email = inputs.current.email()
    assert email is not None
    assert email.reply_to.name == "A Name"


def test_email_failed_raises(inputs):
    inputs.current._payload = EMAIL_FAILED

    with pytest.raises(ValueError) as exc_info:
        inputs.current.email()

    assert "Something failed" in str(exc_info.value)


def test_email_failed_parses(inputs):
    inputs.current._payload = EMAIL_FAILED

    email = inputs.current.email(ignore_errors=True)
    assert email.from_.name == "Mark the Monkey"
    assert (
        email.to[0].address == "process.marks.moon_mission.a1234@mail.ci.robocloud.dev"
    )
    assert email.date == datetime(2022, 2, 22, 6, 0, tzinfo=timezone.utc)
    assert email.text is None
    assert email.html is None
    assert email.errors[0] == "Something failed"


def test_html_attachment(inputs, adapter):
    inputs.current._payload = EMAIL_VALID

    adapter.files[inputs.current.id][HTML_FILENAME] = HTML_CONTENT
    inputs.current._files = [HTML_FILENAME]

    email = inputs.current.email()
    assert isinstance(email.html, str)
    assert "from email" in email.html


def test_html_attachment_skip(inputs, adapter):
    inputs.current._payload = EMAIL_VALID

    adapter.files[inputs.current.id][HTML_FILENAME] = HTML_CONTENT
    inputs.current._files = [HTML_FILENAME]

    email = inputs.current.email(html=False)
    assert email.html is None


def test_email_extra_field(inputs):
    email_extra_field = copy.deepcopy(EMAIL_VALID)
    email_extra_field["email"]["unknown"] = "Some value"

    inputs.current._payload = email_extra_field

    email = inputs.current.email()
    assert email.from_.name == "Mark the Monkey"
