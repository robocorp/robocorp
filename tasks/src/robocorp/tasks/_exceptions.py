class RobocorpTasksError(RuntimeError):
    pass


class RobocorpTasksCollectError(RobocorpTasksError):
    """
    Exception given if there was some issue collecting tasks.
    """


class InvalidArgumentsError(RobocorpTasksError):
    pass
