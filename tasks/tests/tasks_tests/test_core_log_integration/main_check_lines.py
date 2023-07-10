from robocorp.tasks import task
from robocorp import log


def another_method_at_line_5(a):
    pass


@task
def entry_at_line_10():
    log.debug("debug at line 11")
    a = "at line 12"
    log.info("info at line 13")
    another_method_at_line_5(a)

    v = "at_16"
    if v > "at_17":
        pass

    for c in "at_line20":
        pass
