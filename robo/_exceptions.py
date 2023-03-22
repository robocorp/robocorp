class RoboError(RuntimeError):
    pass


class RoboCollectError(RoboError):
    """
    Exception given if there was some issue collecting robo tasks.
    """
