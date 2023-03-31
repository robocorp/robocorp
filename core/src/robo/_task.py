import sys
import typing
from types import ModuleType
from robo._protocols import Status


class Task:
    def __init__(self, module: ModuleType, method: typing.Callable):
        self.package_name = module.__name__
        self.filename = module.__file__ or "<filename unavailable>"
        self.method = method
        self.status = Status.NOT_RUN
        self.message = ""

    @property
    def name(self):
        return self.method.__code__.co_name

    @property
    def lineno(self):
        return self.method.__code__.co_firstlineno

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
