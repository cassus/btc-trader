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
    length = 4200
    quick_sma_range = range(1, 10, 1)
    slow_sma_range = range(2, 30, 2)

    # quick_sma_range = range(2, 4)
    # slow_sma_range = range(5, 8, 2)

    prices = price_history.get_prices()[-length:]
    quick_sma, slow_sma, gains, losses = zip(*[
        _tuple(
            quick_sma,
            slow_sma,
            *simulate_money(prices, quick_ma=decisions.sma_gen(quick_sma), slow_ma=decisions.sma_gen(slow_sma))
        )
        for quick_sma in quick_sma_range
        for slow_sma in slow_sma_range
        if quick_sma < slow_sma
    ])

    matplotlib.style.use('ggplot')
    fig, (p1) = plt.subplots(1, 1, sharex=True)

    print([quick_sma, slow_sma, gains, losses])
    print(np.array([quick_sma, slow_sma, gains, losses]))
    for x, y, z in zip(quick_sma, slow_sma, gains):
        p1.scatter([x], [y], s=(z * 1000))
    for x, y, z in zip(quick_sma, slow_sma, losses):
        p1.scatter([x], [y], s=(z * 1000), c='r', alpha=0.5)
    for x, y, gain, loss in zip(quick_sma, slow_sma, gains, losses):
        p1.annotate(
            # '+{}%\n-{}%\n={}%'.format(int(gain * 100), int(loss * 100), int((gain - loss) * 100)),
            '*{}'.format(round(gain * loss, 1)),
            (x, y),
            color='w',
            horizontalalignment='center',
            verticalalignment='center',
            fontweight='bold'
        )

    plt.show()


if __name__ == '__main__':
    tune_run()