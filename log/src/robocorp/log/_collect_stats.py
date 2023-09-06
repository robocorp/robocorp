"""
A helper module to collect statistics.
"""
import atexit

stats: dict = {}


def inc_stats(name):
    try:
        inc_stats.registered
    except AttributeError:
        inc_stats.registered = True
        atexit.register(print_stats)

    stats[name] = stats.get(name, 0) + 1


def print_stats():
    import json

    print(json.dumps(stats, indent=4))
