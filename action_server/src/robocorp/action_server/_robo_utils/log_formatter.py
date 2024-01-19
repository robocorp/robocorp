import re
from datetime import datetime
from logging import Filter, Formatter

from termcolor import colored


class FormatterNoColor(Formatter):
    strip_colors_regex = re.compile(r"(\x1b\[|\x9b)[0-?]*[ -/]*[@-~]")

    def format(self, record):
        message = super().format(record)
        return self.strip_colors_regex.sub("", message)


class FormatterStdout(Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from uvicorn.logging import AccessFormatter

        self._access_formatter = AccessFormatter()

    def format(self, record):
        if record.name.startswith("uvicorn"):
            (
                client_addr,
                method,
                full_path,
                http_version,
                status_code,
            ) = record.args

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            status_code = self._access_formatter.get_status_code(int(status_code))
            return (
                colored(f"{timestamp}: ", attrs=["dark"])
                + colored(method, attrs=["bold"])
                + f" {full_path} {status_code}"
            )

        return super().format(record)


class UvicornLogFilter(Filter):
    def filter(self, record):
        # Log only Uvicorn Access messages
        return not (record.name.startswith("uvicorn") and len(record.args) != 5)
