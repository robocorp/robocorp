import functools
import inspect


def _cache(callback, func):
    """
    Helper function to create cache decorator for the result of calling
    some function and clearing the cache when the given callback is called.
    """
    cache = []

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        if cache:
            return cache[0]

        if inspect.isgeneratorfunction(func):
            iter_in = func(*args, **kwargs)
            cache.append(next(iter_in))

            def on_finish(*args, **kwargs):
                try:
                    next(iter_in)
                except StopIteration:
                    pass  # Expected
                finally:
                    cache.clear()
                    callback.unregister(on_finish)

            callback.register(on_finish)
        else:
            cache.append(func(*args, **kwargs))

            def on_finish(*args, **kwargs):
                cache.clear()
                callback.unregister(on_finish)

            callback.register(on_finish)

        return cache[0]

    # The cache can be manually cleaned if needed.
    # (for instance, if the given object becomes invalid
    # the cache should be cleaned -- i.e.: if a browser
    # page is closed the cache can be cleaned so that
    # a new one is created).
    new_func.clear_cache = cache.clear

    return new_func
