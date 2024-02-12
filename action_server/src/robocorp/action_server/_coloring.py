from termcolor import colored


def bold_yellow(msg):
    return colored(msg, color="yellow", attrs=["bold"])


def bold_red(msg):
    return colored(msg, color="red", attrs=["bold"])
