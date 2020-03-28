Python library to limit the function execution time
===================================================

Install
-------

pip install kill-timeout

Usage
-----

```python
from kill_timeout import kill_timeout, TimeoutError


limit_in_seconds = 5


@kill_timeout(limit_in_seconds)
def long_running_function(**parameters):
    """Function which makes some computations

    It could take too long for some parameters.
    """
    ...

try:
    result = long_running_function(iterations=9001)
    print("Function returned: %r" % result)
except TimeoutError:
    print("Function didn't finished in %d seconds" % limit_in_seconds)
except Exception:
    print("Function failed with its internal error! Its original traceback:")
    raise
```
