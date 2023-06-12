def call_in_iterator(value):
    x = value


def iterate_entries_in_project(steps: int):
    from robocorp_log_tests._resources.check_iterators_lib import iterator_in_library

    for step in range(steps):
        internal_value = step
        call_in_iterator(internal_value)
        for v in iterator_in_library(internal_value):
            yield v


def for_iter():
    for i in range(5):
        a = i


def for_iter_multiple_targets():
    for i, j in enumerate(range(2)):
        a = i
        b = j


def for_iter_exc():
    for i in range(5):
        a = i
        if i == 2:
            raise RuntimeError("some error")


def call_in_main(value):
    y = value


def main():
    for entry in iterate_entries_in_project(5):
        call_in_main(entry)


def yield_from():
    from robocorp_log_tests._resources.check_iterators_lib import iterator_in_library

    yield from iterator_in_library(3)
    yield from iterator_in_library(2)


def main_yield_from():
    for v in yield_from():
        val = v


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
