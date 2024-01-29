def call_in_iterator(value):
    x = value  # noqa


def iterate_entries_in_project(steps: int):
    from robocorp_log_tests._resources.check_iterators_lib import iterator_in_library

    for step in range(steps):
        internal_value = step
        call_in_iterator(internal_value)
        for v in iterator_in_library(internal_value):
            yield v


def for_iter():
    for i in range(5):
        a = i  # noqa


def for_iter_multiple_targets():
    for i, j in enumerate(range(2)):
        a = i  # noqa
        b = j  # noqa


def while_loop_multiple_targets():
    i = 0
    j = 0
    while i < 10 and j < 10:
        i += 1
        j += 1
        a = i  # noqa
        b = j  # noqa


def for_iter_exc():
    for i in range(5):
        a = i  # noqa
        if i == 2:
            raise RuntimeError("some error")


def for_early_return():
    for i in range(5):
        a = i  # noqa
        if i == 2:
            return


def call_in_main(value):
    y = value  # noqa


def main():
    for entry in iterate_entries_in_project(5):
        call_in_main(entry)


def yield_from():
    from robocorp_log_tests._resources.check_iterators_lib import iterator_in_library

    yield from iterator_in_library(3)
    yield from iterator_in_library(2)


def main_yield_from():
    for v in yield_from():
        val = v  # noqa


def yield_augassign():
    v = 0
    v += yield "aug1"
    v += yield " aug2"
    v += yield " aug3"

    assert v == 3
    return " finish"


def main_yield_augassign():
    s = ""

    iter_in = yield_augassign()
    s += next(iter_in)
    s += iter_in.send(1)
    s += iter_in.send(1)
    try:
        s += iter_in.send(1)
    except StopIteration as e:
        s += e.value

    assert s == "aug1 aug2 aug3 finish"


def for_with_exception():
    try:
        for _a in range(2):
            raise RuntimeError()
    except RuntimeError:
        pass


def is_inside(i, exit_at):
    return i == exit_at


def yield_from_range():
    yield from range(3)


def for_and_yield(exit_at=0):
    for i in yield_from_range():
        if is_inside(i, exit_at):
            return i
    return None
