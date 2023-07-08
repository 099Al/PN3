# -*- coding: utf-8 -*-

import requests
import json


def setCurrenTime():
    curentTime = ''

def history(X,Y):
    resource = requests.get("https://cex.io/api/trade_history/{0}/{1}".format(X,Y))
    data = json.loads(resource.text)
    return data

