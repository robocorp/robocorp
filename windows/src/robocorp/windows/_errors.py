class ActionNotPossible(ValueError):
    """Action is not possible for the given Control."""


class ElementNotFound(ValueError):
    """No matching elements were found."""


class ElementDisposed(ValueError):
    """The existing element was disposed and is no longer available."""


class InvalidLocatorError(Exception):
    """The locator specified is invalid."""


class InvalidStrategyDuplicated(InvalidLocatorError):
    """A given strategy is defined more than once in the same level."""


class ParseError(InvalidLocatorError):
    """
    The locator specified is invalid because it was not possible to parse it properly.
    """

    def __init__(self, msg, index):
        Exception.__init__(self, msg)
        self.index = index
