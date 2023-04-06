from rich.console import Console as BaseConsole


class Console(BaseConsole):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_debug = False

    def debug(self, *args, **kwargs):
        if self.is_debug:
            self.log(*args, **kwargs)


console = Console(highlight=False)
