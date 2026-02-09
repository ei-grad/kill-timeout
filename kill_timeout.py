from functools import wraps
import multiprocessing

from tblib.decorators import return_error, Error

_fork_ctx = multiprocessing.get_context("fork")


class TimeoutError(TimeoutError):
    """Custom TimeoutError

    To distinguish from TimeoutError's raised by functions wrapped in
    kill_timeout decorator.
    """
    pass


def _target(func, child_conn, args, kwargs):
    """Top-level target function for the subprocess (must be picklable)."""
    try:
        child_conn.send(return_error(func)(*args, **kwargs))
    finally:
        child_conn.close()


def kill_timeout(seconds):
    """Decorator to limit function execution time

    It runs the function in separate multiprocessing.Process and sends SIGKILL after
    the specified timeout if the function didn't complete.

    Note: return values larger than the OS pipe buffer (~64KB on Linux) may cause
    a false timeout because the child blocks on send() while the parent waits on
    join(). Keep return values small or return None and communicate large results
    through files or shared memory.
    """

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            parent_conn, child_conn = _fork_ctx.Pipe()
            process = _fork_ctx.Process(
                target=_target,
                args=(func, child_conn, args, kwargs),
            )
            process.start()
            child_conn.close()
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
            if process.exitcode and process.exitcode < 0:
                raise ChildProcessError(
                    f"function {func.__name__} was killed by signal "
                    f"{-process.exitcode}"
                )
            raise ChildProcessError(
                f"function {func.__name__} exited unexpectedly "
                f"(exit code {process.exitcode})"
            )

        return wrapper

    return decorator
