from robocorp.tasks import task
import difflib


@task
def check_difflib_log():
    diff = difflib.ndiff("aaaa bbb ccc ddd".split(), "aaaa bbb eee ddd".split())
    "".join(diff)
