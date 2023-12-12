import logging
from ._rcc import get_rcc


TEMPLATE_URL = "github.com/robocorp/example-action-server-starter"

log = logging.getLogger(__name__)


def create_new_project():
    try:
        directory = input("Name of the project: ")

        rcc = get_rcc()

        rcc.pull(url=TEMPLATE_URL, directory=directory)

        log.info("✅ Project created")
    except KeyboardInterrupt:
        log.debug("Operation cancelled")
