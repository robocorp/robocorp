import pendulum


def days_between_dates(date1, date2) -> int:
    """
    Calculates the difference in days between two dates.

    Args:
        date1 (str): first date in YYYY-MM-DD format
        date2 (str): second date in YYYY-MM-DD format

    Returns:
        int: difference in days between the two dates
    """

    dt1 = pendulum.parse(date1)
    dt2 = pendulum.parse(date2)

    # Calculate the difference in days between the two dates
    difference = dt2.diff(dt1)

    return difference.in_days()
