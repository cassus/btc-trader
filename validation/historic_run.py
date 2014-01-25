from itertools import repeat, accumulate
from math import ceil

import matplotlib

import matplotlib.style
import matplotlib.pyplot as plt
import matplotlib.collections as MpCollections
import numpy as np
import operator

import decisions
from decisions import Position
import price_history


KEEP = 30
EXCHANGE_RATE = 0.0015
DAILY_MARGIN_INTEREST_RATE = 0.003
np.seterr(all='raise')


def print_tsv(*args):
    print("\t".join(str(a) for a in args))


def run(prices, position=Position.WAIT, **kwargs):
    yield from repeat(position, KEEP)

    # noinspection PyArgumentList
    for i in range(KEEP, len(prices)):
        position = decisions.preferred_position(last_closes=(prices[:i]), current_position=position, **kwargs)
        yield position


def moving_average_values(prices, f):
    return [f(prices[:i + 1]) for i, _ in enumerate(prices)]


def gen_open_close_pairs(time, positions):
    open_t = 1
    for t in time[1:]:
        if positions[t] != positions[t - 1]:
            if positions[t - 1] != Position.WAIT:
                # Closing a position
                assert open_t
                yield (open_t, t)
                open_t = None

            if positions[t] != Position.WAIT:
                # Opening a new position
                open_t = t


def position_close_profit_rate(positions, open_t, close_t, prices):
    position_direction = positions[open_t]
    assert position_direction in [1, -1]

    close_price = prices[close_t]
    open_price = prices[open_t]
    price_difference = close_price - open_price
    gross_profit = position_direction * price_difference
    exchange_commission = EXCHANGE_RATE * (open_price + close_price)
    open_days = ceil((close_t - open_t) / 24)
    margin_interest = open_days * DAILY_MARGIN_INTEREST_RATE
    net_profit = gross_profit - exchange_commission - margin_interest
    return 1 + (net_profit / open_price)


def simulate(prices, **kwargs):
    t = range(0, len(prices))
    position = np.array(list(run(prices, **kwargs)))
    open_close_t = list(gen_open_close_pairs(t, position))
    close_t = [close_t for (open_t, close_t) in open_close_t]
    lose_profit_loss_rate = [position_close_profit_rate(position, open_t, close_t, prices) for open_t, close_t in open_close_t]
    money = list(accumulate(lose_profit_loss_rate, func=operator.mul))
    return t, money, position, close_t, lose_profit_loss_rate


def historic_run():
    length = 400
    price = price_history.get_prices()[-length:]
    quick_ma_f = decisions.sma_gen(9)
    slow_ma_f = decisions.sma_gen(24)
    open_percent = 0.8
    close_percent = 0.5
    t, money, position, close_t, close_profit_loss_rate = simulate(price, quick_ma=quick_ma_f, slow_ma=slow_ma_f, open_threshold_ratio=open_percent/100, close_threshold_ratio=close_percent/100)

    quick_ma = moving_average_values(price, quick_ma_f)
    slow_ma = moving_average_values(price, slow_ma_f)

    matplotlib.style.use('ggplot')
    fig, (p1, p2) = plt.subplots(2, 1, sharex=True)
    p1.plot(t, price, 'k-', linewidth=2)
    p1.plot(t, quick_ma, 'r-', linewidth=1)
    p1.plot(t, slow_ma, 'g-', linewidth=1)

    p1.add_collection(MpCollections.BrokenBarHCollection.span_where(t, ymin=0, ymax=10000, where=position > 0, facecolor='green', alpha=0.1))
    p1.add_collection(MpCollections.BrokenBarHCollection.span_where(t, ymin=0, ymax=10000, where=position < 0, facecolor='red', alpha=0.1))

    # p2_1 = p2.twinx()
    p2.plot(close_t, money, 'b-')
    money_prev = [1] + money[:-1]
    p2.bar(
        close_t,
        (np.array(close_profit_loss_rate) - 1) * money_prev,
        bottom=money_prev,
        width=10,
        color=['r' if pl < 1 else 'g' for pl in close_profit_loss_rate],
        alpha=1)

    plt.show()


# def diff_mul(a, b):
#     return ((1 + a) * (1 + b)) - 1


if __name__ == '__main__':
    historic_run()
