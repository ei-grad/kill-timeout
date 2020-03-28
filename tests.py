from time import sleep

import pytest

from kill_timeout import kill_timeout, TimeoutError


@kill_timeout(0.1)
def f(s):
    sleep(s)
    return 1


def test_simple():
    assert f(0.01) == 1


def test_timeout():
    with pytest.raises(TimeoutError):
        f(0.2)
