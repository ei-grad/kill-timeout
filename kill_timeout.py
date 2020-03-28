from functools import wraps
import multiprocessing

from tblib.decorators import return_error, Error


class TimeoutError(TimeoutError):
    """Custom TimeoutError

    To distinguish from TimeoutError's raised by functions wrapped in
    kill_timeout decorator.
    """
    pass


def kill_timeout(seconds):
    """Decorator to limit function execution time

    It runs the function in separate multiprocessing.Process and sends SIGKILL after
    the specified timeout if the function didn't complete.
    """

    def decorator(func):

        manager = multiprocessing.Manager()
        results = manager.dict()

        def target(key, *args, **kwargs):
            results[key] = return_error(func)(*args, **kwargs)

        @wraps(func)
        def wrapper(*args, **kwargs):
            # key object would be uniq in the parent process, but it can't be
            # used directly, because when it goes to manager the new object is
            # created, so the `id(key)` should be used as the real key
            key = object()
            process = multiprocessing.Process(
                target=target,
                args=(id(key),) + args,
                kwargs=kwargs,
            )
            process.start()
            process.join(seconds)
            if process.is_alive():
                # NOTE: killing the process without getting its return code via
                # .join() would cause the zombie process to stay until the next
                # multiprocessing.Process() run, it is acceptable, since it
                # shouldn't end up with many zombie processes, and the
                # alternatives like creating the daemon threads to catch the
                # zombies don't look like a good fit
                process.kill()
            if id(key) in results:
                result = results.pop(id(key))
                if isinstance(result, Error):
                    result.reraise()
                else:
                    return result
            else:
                raise TimeoutError("function %s didn't complete in %s seconds" % (
                    func.__name__, seconds
                ))

        return wrapper

    return decorator
