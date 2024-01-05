import logging

from ._rcc import get_rcc

TEMPLATE_URL = "github.com/robocorp/template-action"

log = logging.getLogger(__name__)


def create_new_project(directory: str = ""):
    try:
        if not directory:
            directory = input("Name of the project: ")

        rcc = get_rcc()

        rcc.pull(url=TEMPLATE_URL, directory=directory)

        log.info("✅ Project created")
    except KeyboardInterrupt:
        log.debug("Operation cancelled")
