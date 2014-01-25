from functools import lru_cache
from itertools import *

import numpy as np


TEST_IN = list(repeat(800, times=30))


class Position(object):
    WAIT = 0
    LONG = 1
    SHORT = -1


def _raw_ema_weights(alpha):
    i = 1
    while True:
        yield i
        i *= alpha


@lru_cache()
def _ema_weights(num, alpha):
    """
    >>> _ema_weights(5,0.7)
    [0.086581803757527651, 0.12368829108218236, 0.17669755868883197, 0.25242508384118856, 0.36060726263026938]
    """

    weights = list(islice(_raw_ema_weights(alpha), num))
    weights = weights / np.sum(weights)
    return list(reversed(weights))


def ema(l, alpha):
    """
    >>> ema([1,1,2], alpha=0.5)
    1.5714285714285714
    >>> ema([1,2,2], alpha=0.5)
    1.857142857142857
    >>> ema([2,2,2], alpha=0.5)
    2.0
    """
    return np.dot(l, _ema_weights(len(l), alpha))


def sma(l):
    return np.mean(l)


def sma_gen(length):
    def f(last_closes):
        return sma(last_closes[-length:])

    return f


def ema_gen(alpha, length=20):
    def f(last_closes):
        return ema(last_closes[-length:], alpha)

    return f


def preferred_position(last_closes, current_position, quick_ma=sma_gen(5), slow_ma=sma_gen(20), open_threshold_ratio=0.01, close_threshold_ratio=0.008):
    """
    >>> preferred_position(TEST_IN + [650], current_position=Position.WAIT)
    -1
    >>> preferred_position(TEST_IN + [950], current_position=Position.WAIT)
    1
    >>> preferred_position(TEST_IN + [750], current_position=Position.WAIT)
    0
    >>> preferred_position(TEST_IN + [750], current_position=Position.SHORT)
    -1
    >>> list(range(20))[-5:]
    [15, 16, 17, 18, 19]
    """
    quick = quick_ma(last_closes)
    slow = slow_ma(last_closes)
    diff_ratio = (quick - slow) / quick
    return (
        Position.SHORT if diff_ratio < -open_threshold_ratio else
        Position.SHORT if diff_ratio < -close_threshold_ratio and current_position == Position.SHORT else
        Position.LONG if diff_ratio > open_threshold_ratio else
        Position.LONG if diff_ratio > close_threshold_ratio and current_position == Position.LONG else
        Position.WAIT
    )
