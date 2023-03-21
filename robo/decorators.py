def task(func):
    def wrapper(*args, **kwargs):
        print("decorated")
        return func(*args, **kwargs)

    return wrapper
