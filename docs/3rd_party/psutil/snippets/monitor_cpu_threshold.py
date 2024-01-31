import time

import psutil


def monitor_cpu_threshold(threshold_percent, interval_seconds) -> None:
    """
    Monitor CPU usage and print a message if it exceeds the threshold.

    :param threshold_percent: The CPU usage threshold percentage.
    :param interval_seconds: The interval to check CPU usage.
    """

    while True:
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > threshold_percent:
            print(
                f"CPU usage exceeds {threshold_percent}% ({cpu_percent}%). Consider taking action!"
            )

        time.sleep(interval_seconds)
