from ._rcc import get_rcc


TEMPLATE_URL = "github.com/robocorp/example-action-server-starter"


def create_new_project():
    directory = input("Enter path to create the project: ")

    rcc = get_rcc()

    rcc.pull(url=TEMPLATE_URL, directory=directory)

    print("✅ Project created")
