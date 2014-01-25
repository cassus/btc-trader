from functools import reduce
import operator
import decisions
import price_history
from validation import historic_run

import matplotlib

import matplotlib.style
import matplotlib.pyplot as plt
import numpy as np


def simulate_money(price, **kwargs):
    t, money, position, close_t, close_pl_rate = historic_run.simulate(price, **kwargs)

    gains = (change for change in close_pl_rate if change > 0)
    losses = (change for change in close_pl_rate if change < 0)

    all_gains = reduce(operator.mul, gains, 1)
    all_losses = reduce(operator.mul, losses, 1)

    return all_gains, all_losses


def _tuple(*args):
    return args


def tune_run():
    length = 400
    y_range = x_range = np.linspace(0.01, 1.5, 10)

    prices = price_history.get_prices()[-length:]
    x, y, gains, losses = zip(*[
        _tuple(
            x,
            y,
            *simulate_money(prices, quick_ma=decisions.sma_gen(quick_sma), slow_ma=decisions.sma_gen(slow_sma), open_threshold_ratio=open_percent/100, close_threshold_ratio=close_percent/100)
        )
        for x in x_range
        for y in y_range
        for open_percent in [x]
        for close_percent in [y]
        for quick_sma in [9]
        for slow_sma in [24]
        if quick_sma < slow_sma
        if close_percent <= open_percent
    ])

    matplotlib.style.use('ggplot')
    fig, (p1) = plt.subplots(1, 1, sharex=True)

    for x_, y_, z_ in zip(x, y, gains):
        p1.scatter([x_], [y_], s=(z_ * 1000))
    for x_, y_, z_ in zip(x, y, losses):
        p1.scatter([x_], [y_], s=(z_ * 1000), c='r', alpha=0.5)
    for x_, y_, gain, loss in zip(x, y, gains, losses):
        p1.annotate(
            # '+{}%\n-{}%\n={}%'.format(int(gain * 100), int(loss * 100), int((gain - loss) * 100)),
            '*{}'.format(round(gain * loss, 1)),
            (x_, y_),
            color='w',
            horizontalalignment='center',
            verticalalignment='center',
            fontweight='bold'
        )

    plt.show()


if __name__ == '__main__':
    tune_run()
