from robocorp.tasks import task

from . import module


@task
def something():
    print("worked")
