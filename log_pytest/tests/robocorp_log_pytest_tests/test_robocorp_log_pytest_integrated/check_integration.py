def test_ok():
    a = 1  # noqa
    print("worked")
    for i in range(50):
        j = "************" * i
        print(j)


def test_fail():
    assert False, "Something failed..."
