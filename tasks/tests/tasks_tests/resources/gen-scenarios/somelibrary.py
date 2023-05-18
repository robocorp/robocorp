def call_generators_in_library():
    yield from range(2)

    for i in range(2):
        yield f"Generated: {i}"
