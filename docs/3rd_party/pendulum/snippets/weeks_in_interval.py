import pendulum


def weeks_in_interval(start_date: str, end_date: str) -> list[pendulum.DateTime]:
    """
    Generate a list of weeks within the interval between start_date and end_date

    Args:
        start_date: The start date of the interval.
        end_date: The end date of the interval.

    Returns:
        A list of weeks within the interval.
    """

    start_date = pendulum.parse(start_date)
    end_date = pendulum.parse(end_date)

    # Create an interval between the start and end dates
    interval = pendulum.interval(start_date, end_date)

    # Generate a list of weeks within the interval
    weeks_list = [week for week in interval.range("weeks")]

    return weeks_list
