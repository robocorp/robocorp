import sys
import typing


class Task:
    def __init__(self, package_name: str, method: typing.Callable):
        self.package_name = package_name
        self.method = method

    @property
    def name(self):
        return self.method.__code__.co_name

    def run(self):
        self.method()

    def __typecheckself__(self) -> None:
        from robo._protocols import ITask
        from robo._protocols import check_implements

        _: ITask = check_implements(self)


class Context:
    def show(self, msg: str):
        print(msg)

    def show_error(self, msg: str):
        print(msg, file=sys.stderr)
