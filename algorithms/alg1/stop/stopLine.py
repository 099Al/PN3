# -*- coding: utf-8 -*-


'''функции должны принимать только число и список'''
import algorithms.alg1.parameters.stopParameters as stopP
import algorithms.alg1.parameters.orderParams as prmt
from algorithms.alg1.parameters.stopParameters import STOP_LIMIT_1

STOP_TYPE = stopP.STOP_TYPE
K = stopP.STOP_K




#changeConst = prmt.changeConstants()

#ДЛЯ КАЖДОГО ID ДОЛЖНЫ БЫТЬ СВОИ СТОПЫ
#limit_price_1 = changeConst.get_stopLimit_1() #первый лимит. расчитывается от цены lastBuyPrice
#limit_price_2 = changeConst.get_stopLimit_2()




#Если хотя бы один из набора, ниже цены, то срабатывает
def stop_1_below(limit_price,last_prices):
    for x in last_prices:
        if x < limit_price:
            return 1
    return 0


#Если все ниже цены, то срабатывает
def stop_all_below(limit_price,last_prices):
    ln = len(last_prices)
    n = sum([x < limit_price for x in last_prices])

    if ln == n:
        return 1
    else:
        return 0


#Если k показателей ниже цены
def stop_any_k_below(limit_price,last_prices):
    n = sum([x < limit_price for x in last_prices])

    if K == n:
        return 1
    else:
        return 0

#Если k последних показателей ниже цены
def stop_last_k_below(limit_price,last_prices):
    stop_all_below(limit_price, last_prices[:K])


#Способ определения границы
def stop_below(limit_price,last_prices):
    if STOP_TYPE == 1:
        return stop_1_below(limit_price,last_prices)
    if STOP_TYPE == 2:
        return stop_all_below(limit_price,last_prices)
    if STOP_TYPE == 3:
        return stop_any_k_below(limit_price,last_prices)
    if STOP_TYPE == 4:
        return stop_last_k_below(limit_price,last_prices)

    return -1




def stop_line_mark(limit1,limit2,last_prices):
    # Добавить в функцию аргумент ID, т.к. стопя для каждого ID будут свои

    '''
    High
    --------limit 1
    Between
    --------limit 2
    Low
    '''


    if (STOP_LIMIT_1 == True):  # учытываем 1-й стоп
        stop_signal = stop_below(limit1, last_prices)
        if (stop_signal == 0):  # не вышли за предел
             return 'H'
        else:  # вышли за предел
            stop_signal2 = stop_below(limit2, last_prices)  # Тогда, сразу смотрим 2-й лимит
            if (stop_signal2 == 1):
                return 'L'
            else:  # оказались между лимитами
                return 'B'

    else:  # учитывать только 2-й лимит
        stop_signal2 = stop_below(limit2, last_prices)  # Тогда, сразу смотрим 2-й лимит
        if (stop_signal2 == 1):
            return 'L'
        else:
            return 'H'


if __name__ == '__main__':

    x = stop_all_below(11, [1,2,3,4,5,6,7,8,9])
    print(x)