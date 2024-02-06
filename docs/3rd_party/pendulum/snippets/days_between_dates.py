import pendulum


def days_between_dates(date1: str, date2: str) -> int:
    """
    Calculates the difference in days between two dates.

    Args:
        date1: first date in YYYY-MM-DD format
        date2: second date in YYYY-MM-DD format

    Returns:
        The difference in days between the two dates.
    """

    dt1 = pendulum.parse(date1)
    dt2 = pendulum.parse(date2)

    # Calculate the difference in days between the two dates
    difference = dt2.diff(dt1)

    return difference.in_days()
