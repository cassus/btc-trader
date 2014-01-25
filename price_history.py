from collections import namedtuple
from datetime import datetime, timedelta

import requests
import utils

BITCOIN_CHARTS_FIELDS = ['utc_timestamp', 'open', 'high', 'low', 'close', 'volume_btc', 'volume_currency', 'weighted_price']


class BitcoinChartsRow(namedtuple('BitcoinChartsRow', BITCOIN_CHARTS_FIELDS)):
    @property
    def dt(self):
        return datetime.utcfromtimestamp(int(self.utc_timestamp))


def parse(json):
    """
    >>> parse([[1385164800, 794.0, 802.0, 793.0, 802.0, 841.18390934, 672239.8531884623, 799.159191853667]])
    [BitcoinChartsRow(utc_timestamp=1385164800, open=794.0, high=802.0, low=793.0, close=802.0, volume_btc=841.18390934, volume_currency=672239.8531884623, weighted_price=799.159191853667)]
    """
    return [BitcoinChartsRow(*r) for r in json]


def assert_every_hour(parsed):
    for i, ii in zip(parsed[:-1], parsed[1:]):
        assert ii.dt - i.dt == timedelta(hours=1)


def correct_invalid_data_points(parsed, tolerate=2):
    last_good = parsed[0]
    for current in parsed:
        if last_good.close / tolerate < current.close < last_good.close * tolerate:
            last_good = current
        else:
            last_good = last_good._replace(utc_timestamp=current.utc_timestamp)
        yield last_good


def load_bitcoincharts_history(days):
    r"""
    >>> 24 < len(load_bitcoincharts_history(2)) < 48
    True
    """
    r = requests.get(
        url='http://bitcoincharts.com/charts/chart.json',
        params={
            'm': 'bitstampUSD',
            'r': days,
            'i': 'Hourly',
        },
        headers={
            'Referer': 'http://bitcoincharts.com/charts/bitstampUSD'
        })
    parsed = parse(r.json())
    assert_every_hour(parsed)
    parsed = list(correct_invalid_data_points(parsed))
    assert_every_hour(parsed)
    return parsed


def load_history():
    import utils.csv_utils

    mode = 'r'
    with utils.csv_utils.open_price_file(mode) as f:
        return utils.csv_utils.read_csv(f)


def get_prices():
    return [float(r.close) for r in load_history()]


def main():
    parsed = load_history()
    print("\n".join("{}\t{}".format(r.dt, r.close) for r in parsed))


if __name__ == '__main__':
    main()