from robocorp.tasks import setup

print("In my_config 1")


@setup
def on_setup(task):
    print("Setup: my_config 1")


@setup(scope="session")
def on_setup_session(tasks):
    assert len(tasks) == 1
    print("Setup session: my_config 1")
