# -*- coding: utf-8 -*-

from perfomance._balance.balance import DepoBalance
import algorithms.alg1.parameters.balanceParams as algBlnc
from algorithms.orders import ActiveOrders,ProcessLine

# ! Скрипт нужно обновить
def initBalance():
    deposit = DepoBalance()  # Баланс
    deposit.setBTCblnc(algBlnc.balance_BTC)
    deposit.setRUBblnc(algBlnc.balance_RUB)
    deposit.setUSDblnc(algBlnc.balance_USD)

    return deposit



def initLines():
    pLines = ProcessLine()
    pLines.initLine(1, 0, 0.003, 0.65)
    pLines.initLine(2, 0, 0.0056, 120.90)

    checkLines()



def checkLines():
    deposit = DepoBalance()  # Баланс
    pLines = ProcessLine()

    sumAX = pLines.sumAmount()
    sumAmount = sumAX['amount']
    sumX = sumAX['x']

    if(sumAmount > deposit.blnc_BTC):
        print('Сумма линий по amount больше чем на депозите')
        exit()

    if (sumAmount > deposit.blnc_USD):
        print('Сумма линий по x больше чем на депозите')
        exit()

