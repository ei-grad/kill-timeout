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

        @wraps(func)
        def wrapper(*args, **kwargs):
            parent_conn, child_conn = multiprocessing.Pipe()

            def target():
                child_conn.send(return_error(func)(*args, **kwargs))
                child_conn.close()

            process = multiprocessing.Process(target=target)
            process.start()
            process.join(seconds)
            if process.is_alive():
                process.kill()
                process.join()
                parent_conn.close()
                raise TimeoutError(
                    f"function {func.__name__} didn't complete in {seconds} seconds"
                )
            if parent_conn.poll():
                result = parent_conn.recv()
                parent_conn.close()
                if isinstance(result, Error):
                    result.reraise()
                return result
            parent_conn.close()
            raise TimeoutError(
                f"function {func.__name__} didn't complete in {seconds} seconds"
            )

        return wrapper

    return decorator
