# kill-timeout

Limit the function execution time.

This module provides a decorator which runs the function in a separate
`multiprocessing.Process` and sends `SIGKILL` after the specified timeout if
the function didn't complete.

**Note:** This uses `SIGKILL` and `multiprocessing.Process`, so it only works
on POSIX systems (Linux, macOS, etc.), not on Windows.

## Requirements

* Python 3.10+
* [tblib](https://pypi.org/project/tblib/) (to preserve tracebacks from the subprocess)

## Install

```bash
pip install kill-timeout
```

## Usage

```python
from kill_timeout import kill_timeout

limit_in_seconds = 5


@kill_timeout(limit_in_seconds)
def long_running_function(**parameters):
    """Function which makes some computations.

    It could take too long for some parameters.
    """
    ...

try:
    result = long_running_function(iterations=9001)
    print(f"Function returned: {result!r}")
except TimeoutError:
    print(f"Function didn't finish in {limit_in_seconds} seconds")
except Exception:
    print("Function failed with its internal error! Its original traceback:")
    raise
```

## How it works

Each call to a decorated function:

1. Spawns a new `multiprocessing.Process` to run the function.
2. Waits for the process to complete within the timeout using `process.join(seconds)`.
3. If the process is still alive after the timeout, sends `SIGKILL` and reaps it.
4. If the function raised an exception, re-raises it in the caller with the original traceback (via `tblib`).
