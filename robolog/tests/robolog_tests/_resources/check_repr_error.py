class ErrorInRepr:
    def __repr__(self):
        raise RuntimeError("Cannot do repr!")


def call_this(arg):
    pass


def main():
    call_this(ErrorInRepr())
