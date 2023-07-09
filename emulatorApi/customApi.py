# -*- coding: utf-8 -*-

import requests
import json
import os


import emulatorApi.queriesIm as qr
from db.connection import DBConnect
'''
!!!Названия функция в этом модуле  должны совпадать с названиями в модуле api
   Некторые подзапросы вынесены в другой файл
'''


class CustomApi:
    """
    Emulation
    """
    def __init__(self):
        self._currentTime=None

    @property
    def currentTime(self):
        return self._currentTime

    @currentTime.setter
    def currentTime(self, value):
        self._currentTime = value

    def history(self,X,Y):
        #Эмуляция запроса к сайту. Время запроса current_time
        #resource = requests.get("https://cex.io/api/trade_history/{0}/{1}".format(X,Y))
        #data = json.loads(resource.text)

        #connect to DB with emulation data
        db=DBConnect()
        dbconn = db.getConnect()
        res = qr.f_history_tic_imitation(dbconn,self._currentTime)
        dbconn.close()


        return res



