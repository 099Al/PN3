# -*- coding: utf-8 -*-

import requests
import json

'''CUSTOM PUBLIC API'''

#!!!!!!ПЕРЕДЕЛАТЬ в класс


class CustomApi:
    def loadonepair(self,X,Y):
        resource = requests.get("https://cex.io/api/ticker/{0}/{1}".format(X,Y))
        data = json.loads(resource.text)
        return data

    def lastprice(self,X,Y):
        resource = requests.get("https://cex.io/api/last_price/{0}/{1}".format(X,Y))
        data = json.loads(resource.text)
        return data

    def currlimits(self,X,Y):
        resource = requests.get("https://cex.io/api/currency_limits".format(X,Y))
        data = json.loads(resource.text)
        return data

    def ohlcv(self,DT,X,Y):
        resource = requests.get("https://cex.io/api/ohlcv/hd/{0}/{1}/{2}".format(DT,X,Y))
        data = json.loads(resource.text)
        return data

    def orderbook(self,X,Y):
        resource = requests.get("https://cex.io/api/order_book/{0}/{1}".format(X,Y))
        data = json.loads(resource.text)
        return data

    def history(self,X,Y):
        resource = requests.get("https://cex.io/api/trade_history/{0}/{1}".format(X,Y))
        data = json.loads(resource.text)
        return data


if __name__ == '__main__':

    api = CustomApi()
    print (api.lastprice('BTC','USD'))

