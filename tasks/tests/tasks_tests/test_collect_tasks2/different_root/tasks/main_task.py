from robocorp.tasks import task

from . import module  # noqa


@task
def something():
    print("worked")
