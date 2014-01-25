from collections import namedtuple
import json
import base64
import hmac
import hashlib
import time

import requests

import secrets


BitfinexCredentials = namedtuple('BitfinexCredentials', ['key', 'secret'])

credentials = BitfinexCredentials(key=secrets.API_KEY, secret=secrets.API_SECRET)

BITFINEX = 'https://api.bitfinex.com'


def _headers(payload, credentials=None):
    j = json.dumps(payload)
    payload = base64.standard_b64encode(j.encode())

    if credentials:
        h = hmac.new(credentials.secret, payload, hashlib.sha384)
        signature = h.hexdigest()

        return {
            "X-BFX-APIKEY": credentials.key,
            "X-BFX-SIGNATURE": signature,
            "X-BFX-PAYLOAD": payload,
        }
    else:
        return {
            "X-BFX-PAYLOAD": payload,
        }


def get(url, credentials=None, payload=None):
    payload = payload or {}
    if credentials:
        payload.update({"request": url, "nonce": str(int(time.time() * 100000))})
    headers = _headers(payload, credentials=credentials)
    r = requests.request('get', BITFINEX + url, headers=headers)
    return r.json()


def ticker(symbol="btcusd"):
    """
    >>> ticker()
    """
    return get("/v1/ticker/" + symbol)


def today(symbol="btcusd"):
    """
    >>> today()
    """
    return get("/v1/today/" + symbol)


def orders():
    """
    >>> orders()
    """
    return get("/v1/orders", credentials=credentials)


def balances():
    """
    >>> balances()
    """
    return get("/v1/balances", credentials=credentials)


def trades(symbol="btcusd", **payload):
    """
    >>> trades(limit_trades=1)
    """
    return get("/v1/trades/" + symbol, payload=payload)


