# -*- coding: utf-8 -*-

import requests
import json

'''CUSTOM PUBLIC API'''

def loadonepair(X,Y):
    resource = requests.get("https://cex.io/api/ticker/{0}/{1}".format(X,Y))
    data = json.loads(resource.text)
    return data

def lastprice(X,Y):
    resource = requests.get("https://cex.io/api/last_price/{0}/{1}".format(X,Y))
    data = json.loads(resource.text)
    return data

def currlimits(X,Y):
    resource = requests.get("https://cex.io/api/currency_limits".format(X,Y))
    data = json.loads(resource.text)
    return data

def ohlcv(DT,X,Y):
    resource = requests.get("https://cex.io/api/ohlcv/hd/{0}/{1}/{2}".format(DT,X,Y))
    data = json.loads(resource.text)
    return data

def orderbook(X,Y):
    resource = requests.get("https://cex.io/api/order_book/{0}/{1}".format(X,Y))
    data = json.loads(resource.text)
    return data

def history(X,Y):
    resource = requests.get("https://cex.io/api/trade_history/{0}/{1}".format(X,Y))
    data = json.loads(resource.text)
    return data


