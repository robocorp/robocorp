import platform
import subprocess

from robo_cli.config import generate_yamls, delete_yamls

def rcc_command(command: str, cwd=None, stdout=None):
    system = platform.system()
    if system == "Windows":
        command.replace("rcc", "rcc.exe")

    command_and_args = command.split(" ")
    return subprocess.run(command_and_args, shell=False, cwd=cwd, check=True, stdout=stdout)


def run():
    try:
        generate_yamls()
        rcc_command("rcc run")
    finally:
        delete_yamls()

