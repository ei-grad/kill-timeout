from time import sleep
import sys

import pytest

from kill_timeout import kill_timeout, TimeoutError as KillTimeoutError


@kill_timeout(0.1)
def f(s):
    sleep(s)
    return 1


def test_simple():
    assert f(0.01) == 1


def test_timeout():
    with pytest.raises(KillTimeoutError):
        f(0.2)
    with pytest.raises(TimeoutError):
        f(0.2)


@kill_timeout(0.5)
def f2():
    1 / 0


def test_exception():
    with pytest.raises(ZeroDivisionError):
        f2()

    try:
        f2()
    except ZeroDivisionError:
        _, _, tb = sys.exc_info()
        while tb.tb_next is not None:
            tb = tb.tb_next
        assert tb.tb_frame.f_code.co_name == 'f2'
