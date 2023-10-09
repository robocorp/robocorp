class ActionNotPossible(ValueError):
    """Action is not possible for the given Control."""


class ElementNotFound(ValueError):
    """No matching elements were found."""


class ElementDisposed(ValueError):
    """The existing element was disposed and is no longer available."""
