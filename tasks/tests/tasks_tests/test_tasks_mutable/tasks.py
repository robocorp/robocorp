from robocorp.tasks import task, teardown


@teardown
def make_pass(task):
    task.status = "PASS"


@task
def raises_error():
    raise RuntimeError("Something went wrong")


@task
def division_error():
    _ = 1 / 0
