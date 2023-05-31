import email
from email.header import decode_header
from email.message import Message
from typing import Optional, Tuple


def parse_email_body(content: str, html_first: bool = False) -> Tuple[str, list[str]]:
    """Decodes email body and extracts its text/html content.

    Automatically detects character set if the header is not set.

    Args:
        message:    Raw 7-bit message body input e.g. from `imaplib`.
                    Double encoded in quoted-printable and latin-1
        html_first: Prioritize html extraction over text

    Returns:
        Message body and a list of attachment names
    """
    message = email.message_from_string(content)

    if not message.is_multipart():
        content_charset = message.get_content_charset()
        body = str(
            message.get_payload(decode=True),
            content_charset or "utf-8",
            "ignore",
        )
        return body.strip(), []

    text = None
    html = None
    attachments: list[str] = []

    for part in message.walk():
        if not part:
            continue

        if filename := _get_part_filename(part):
            attachments.append(filename)
            continue

        content_charset = part.get_content_charset()

        content_type = "text/plain"
        if content_charset:
            content_type = part.get_content_type()

        content = ""
        if payload := part.get_payload(decode=True):
            content = str(payload, str(content_charset), "ignore")

        if content_type == "text/plain":
            text = content
        elif content_type == "text/html":
            html = content

    if html_first:
        body = html or text or ""
    else:
        body = text or html or ""

    body = body.strip()
    return body, attachments


def _get_part_filename(msg: Message) -> Optional[str]:
    filename = msg.get_filename()
    if not filename:
        return None

    parts = decode_header(filename)
    value, charset = parts[0]

    if charset is not None:
        filename = value.decode(charset)

    return str(filename).replace("\r", "").replace("\n", "")
