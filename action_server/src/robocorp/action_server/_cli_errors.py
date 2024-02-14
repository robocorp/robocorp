class ActionPackageError(Exception):
    """
    Error raised which is handled in the cli to show just the error message
    and hide the traceback.
    """
