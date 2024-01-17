import re
from logging import Formatter


class FormatterNoColor(Formatter):
    strip_colors_regex = re.compile(r"(\x1b\[|\x9b)[0-?]*[ -/]*[@-~]")

    def format(self, record):
        message = super().format(record)
        return self.strip_colors_regex.sub("", message)
