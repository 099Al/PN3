# -*- coding: utf-8 -*-

import numpy as np



#Изменение валюты  (USD в RUB)
#Продать свои USD (банк Покупает USD)
def sellUSD(u, bank_buy):
    r = u*bank_buy
    r= round(r,2)
    return r

#Изменение валюты (RUB в USD)
#Купить USD (банк продает)
def buyUSD(r, bank_sell):
    if(bank_sell==0):
        print('Курс не задан')
        return r
    u = r/bank_sell
    u= round(u,2)
    return u


#Обратные функции
def sellUSD_revers(r, bank_buy):
    u = r/bank_buy
    u= round(u,2)
    return u

def buyUSD_revers(u, bank_sell):
    if(bank_sell==0):
        print('Курс не задан')
        return r
    r = u*bank_sell
    r= round(r,2)
    return r