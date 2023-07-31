# Email triggering

A process can be started in Control Room by sending an email, after which the
payload and files will contain the email metadata, text, and possible attached files.
This requires the `Parse email` configuration option to be enabled for the
process in Control Room.

An input work item in this library has a helper method called `email()`,
which can be used to parse an email into a typed container:

```python
from robocorp import workitems
from robocorp.tasks import task

@task
def read_email():
    item = workitems.inputs.current
    email = item.email()

    print("Email sent by:", email.from_.address)
    print("Email subject:", email.subject)

    payload = json.loads(email.text)
    print("Received JSON payload:", payload)
```

## Email structure

The email content in the payload is parsed into the following typed container:

```python
class Address:
    name: str
    address: str

class Email:
    from_: Address
    to: list[Address]
    cc: list[Address]
    bcc: list[Address]

    subject: str
    date: datetime

    reply_to: Optional[Address]
    message_id: Optional[str]

    text: Optional[str]
    html: Optional[str]

    errors: list[str]
```

## Error handling

When Control Room can not parse the email, for example when the content is too
large to handle, it will set specific error fields. These are parsed by the
work items library and raised as a corresponding exception. These errors
can also be ignored with the `ignore_errors` argument to the `email()` method.

## Using the raw payload

In some use-cases, it's necessary to access additional metadata such as custom
headers. Control Room attaches the raw unparsed email as a file attachment,
which can be parsed by the Robot code. One option for this is the Python built-in
`email` library:

```python
import email
from robocorp import workitems
from robocorp.tasks import task


@task
def parse_message_id():
    for item in workitems.inputs:
        path = item.get_file("__raw_mail")
        with open(path) as fd:
            message = email.message_from_file(fd)
            message_id = message["Message-ID"]
```

## Further documentation

To learn more about email triggering in Control Room, see
[the docs page](https://robocorp.com/docs/control-room/attended-or-unattended/email-trigger).