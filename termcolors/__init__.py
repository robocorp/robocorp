try:
    from termcolor import colored
except ImportError:

    def _noop(msg):
        return msg

    bold_yellow = _noop
    bold_red = _noop
else:

    def bold_yellow(msg):
        return colored(msg, color="yellow", attrs=["bold"])

    def bold_red(msg):
        return colored(msg, color="red", attrs=["bold"])
