import io
import csv
import os

import config

import price_history


def _mock_write_csv(history):
    with io.StringIO() as o:
        write_csv(o, history)
        return o.getvalue()


def write_csv(file, history):
    r"""
    >>> _mock_write_csv([price_history.BitcoinChartsRow(utc_timestamp='1385164800', open='794.0', high='802.0', low='793.0', close='802.0', volume_btc='841.18390934', volume_currency='672239.8531884623', weighted_price='799.159191853667')])
    'utc_timestamp,open,high,low,close,volume_btc,volume_currency,weighted_price\r\n1385164800,794.0,802.0,793.0,802.0,841.18390934,672239.8531884623,799.159191853667\r\n'
    """
    writer = csv.writer(file)
    writer.writerow(price_history.BITCOIN_CHARTS_FIELDS)
    writer.writerows(history)


def read_csv(input):
    r"""
    >>> read_csv('utc_timestamp,open,high,low,close,volume_btc,volume_currency,weighted_price\r\n1385164800,794.0,802.0,793.0,802.0,841.18390934,672239.8531884623,799.159191853667\r\n'.splitlines(True))
    [BitcoinChartsRow(utc_timestamp='1385164800', open='794.0', high='802.0', low='793.0', close='802.0', volume_btc='841.18390934', volume_currency='672239.8531884623', weighted_price='799.159191853667')]
    """
    reader = csv.reader(input)
    return [price_history.BitcoinChartsRow(*row) for row in reader][1:]


def open_price_file(mode):
    return open(os.path.join(config.project_root(), 'prices.csv'), mode, newline='')