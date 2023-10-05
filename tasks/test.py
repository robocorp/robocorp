import random
import time
from robocorp.tasks import task, hooks

from pydantic import BaseModel


@hooks.setup
def start_my_slow_thing(tasks):
    time.sleep(2)



class Foo(BaseModel):
    name: str
    something: str = "Default value here"
    count: int


class Bar(BaseModel):
    names: list[str]


@task
def complex_payloads(foo: Foo) -> Bar:
    print(foo)
    return Bar(names=["one", "two", "three"])


@task
def random_failure(message: str = "Generic error"):
    """This is a task that fails... sometimes"""
    should_fail = random.choice([True, False])
    if should_fail:
        raise RuntimeError(message)


@task
def sleep_some(amount: int) -> str:
    """I'm feeling kinda lazy today"""
    time.sleep(amount)
    return f"Yawn, what a nice {amount} seconds of sleep"
