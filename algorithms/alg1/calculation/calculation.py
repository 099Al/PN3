# -*- coding: utf-8 -*-



import algorithms.alg1.parameters.orderParams as prmt
import deposit.feeslimits.constant as cons
from perfomance._balance.balance import DepoBalance
import function.transacFunction as trns
from algorithms.orders import ActiveOrders,ProcessLine
import numpy as np



'''
    В тестовом алгоритме берем по X продаем по k*X.  X-фиксированная величина
    резервирование идет пр установке ордера. Здесь толко расчет
'''
#В аргумент передать номер линии
#Выбрать ее параметры. Доступное кол-во.
def    calc(curr_prices,line):
     # curr_price - list []
    #changeConst = prmt.changeConstants()  #Убрать. Заменить на параметры из линии
    pLines = ProcessLine()

    bln = DepoBalance()

    buy_prices = curr_prices['buy']
    sell_prices = curr_prices['sell']

    bln_x = bln.blnc_USD
    bln_btc = bln.blnc_BTC
    avg_price = np.average(buy_prices)

    if(line>1):
        '''здесь должен быть алгоритм на обрабтку линии
            например, если цена сильно упала от цены покупки в первой линии
            и в первой линии ордер на продажу,
            то тогда идет расчет на покупку (докупить еще)
            Иначе сброс
        '''
        return {'type': None}



    #Покупка
     # Если на депозите больше X, то рассматриваем только покупку  x_bln ? p_last*btc_bln
    if(avg_price<5000):
        #ордер на покупку при цене чуть ниже последней
        #на сумму половина депозита
        # резервирование идет пр установке ордера. Здесь толко расчет

        #цена на покупку
        b_price = buy_prices[-1] - 0.02

        #будет потрачено x (какая часть от баланса)
        #как вычисляется x есть варианты
        x = bln_x  #в этом варианте все

        #на эту сумму возможно взять btc
        amount = trns.maxBTC(x,b_price)

        return {'type': 'buy', 'mtype':'limit','crypt':'BTC', 'amount':amount, 'price':b_price, 'x':x}

    #curr_prices[-1] нужен с определенным типом либо b либо s
    if (curr_prices[-1] >= 5090):
         # ордер на продажу при цене чуть ниже последней
         # на сумму половина депозита
         # резервирование идет пр установке ордера. Здесь толко расчет

         # цена на продажу
         b_price = curr_prices[-1] + 0.02

         # btc на продажу
         amount = pLines.lineAmountX()['amount'];

         #

         return {'type': 'buy', 'mtype': 'limit', 'crypt': 'BTC', 'amount': amount, 'price': b_price}


    #При первом запуске на линиию берем X% от баланса. Реализовать доп. условия.
    #% задать в параметрах

    #Добавление параметров

    #Проверка баланса

    #return {'action': 'sell', 'X': 'BTC','amount': 1000, 'price': 10000}
    #return {'action': 'reset','id':id_for_reset}
    #return {'action': 'N'}

    #Предрасчет




        #return {'type': 'sell', 'mtype':'limit','crypt':'BTC', 'amount':amount, 'price':curr_price, 'x':x}


        #return {'type': 'sell', 'crypt':'BTC', 'amount': amount, 'price': price, 'x': x}

if __name__ == '__main__':
    l = [1,2,3,4,5,6]
    print(l[-1])