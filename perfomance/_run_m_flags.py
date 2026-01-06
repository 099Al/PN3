# -*- coding: utf-8 -*-

'''Все функции и расчеты !ВЫНОСИТЬ в другой модуль
Здесь идет основной расчет(эмуляция)
Может быть одновременно только один флаг
'''

import time
from datetime import datetime

from emulatorApi.queriesIm import *
from perfomance._data.TikQueue import TikQueue

from perfomance._order.checkOrders import checkOrder

from algorithms.alg1 import calculation
import perfomance._loging.logAction as log
from algorithms.orders import ActiveOrders
from perfomance._balance.balance import DepoBalance

from api.cexioApi import Api

# Константы

DELTA_T = 60  # Запрос каждые десять секунд
LIMIT_ORDER = 5 #5 - лимит на количество установленныйх ордеров
START_DATE = '2019-02-03 11:05:17'  # Стартовое время

# Класс с доступом к API
#import perfomance.keys as k

api = Api(k.username, k.api_key, k.api_secret)

import db.connection as dbconn


conn = dbconn.getConnect()

n = 0  # Начало итераций. Для тестирования
startCalcPeriodTime = datetime.strptime(START_DATE, '%Y-%m-%d %H:%M:%S').timestamp()  # Для тестирования

clear_history(conn, 'cex_history_tik')  # Предварительная очистка таблицы. Для тестирования.
log.clear_log(conn)

tikObj = TikQueue(5)  # Массив размером 5
prev_tik = 0
orderCount = 0  # флаг (установлен ли ордер)
order_place_time = 0  # время установки флага
tcalc1 = 0  # время до рассчета
tcalc2 = 0  # время после рассчета

check_order_time_start = 0
check_order_time_end = 0

market = 'BTC/USD'

print('==========',time.time())

actOrders = ActiveOrders()  # список теукущих ордеров

deposit = DepoBalance()  # Баланс
deposit.setBTCblnc(0.00100008)
deposit.setRUBblnc(5)
deposit.setUSDblnc(27)


def setOrder(res):
    new_order = 0

    r_act = res['type']  # результат. какое действие делать

    if (r_act == 'stop'):  # остановка
        exit()

    if (r_act == 'buy' or r_act == 'sell'):
        amount = res['amount']  # количество
        price = res['price']  # по какой цене
        x_reserv = res['x']

        # api set _order   # установка ордера через API
        # PRIVATE API place_order = api.buy_limit_order(amount,price,market)  # На выходе получается словарь с данными ордера
        # Попытка
        # time.sleep(1)
        # Для тестирования генерация id
        id = int(time.time())
        ord_time = int(startCalcPeriodTime) + int(time.time() - tcalc1)  # Время (по тестовым данным) установки
        order_place_time = ord_time  # время установки флага

        chech_order_time_start = ord_time

        # реализовать Проверка в балансе

        place_order = {'id': id, 'amount': amount, 'price': price, 'ord_time': ord_time, 'type': r_act,
                       'x': x_reserv}

        # print('n=', n, 'place', place_order, datetime.fromtimestamp(id), id)
        # print('  startCalcPeriodTime=', datetime.fromtimestamp(startCalcPeriodTime), startCalcPeriodTime)
        # print('  ord_time           =', datetime.fromtimestamp(ord_time), ord_time)

        actOrders.addOrder(place_order['id'], place_order)
        deposit.changeBlnc(-x_reserv, 'USD')  # Проверка достаточности баланса проверяется в calculation
        log.log_action(conn, place_order, r_act, market)
        # -----тестирование----------

        new_order = 1

    return new_order





while 1 == 1:
    n = n + 1
    if (n > 60): break  # Завершение цикла при тестировании

    # time.sleep(DELTA_T)   #Задержка по времени (реализовать в реальном времни) DELTA_T можно менять в зависимости от времени расчета
    startCalcPeriodTime = startCalcPeriodTime + DELTA_T  # В тесте время запроса рассчитывается  !!!! Возможно надо перенести в конец цикла

    # DELTA_T должно быть больше dT1 и dT2, тогда переносить не надо. Но период для проверки флага надо изменить

    # Получение последних 1000 tik на данный момент
    # Данные должны получаться через api
    r = f_data_tic_imitation(conn, startCalcPeriodTime)  # Эмулированный результат

    tcalc1 = time.time()  # datetime.now()-  формате. Время начала рассчетов.  Текущее время. Время,когда начался процесс рассчета
    curr_tik = r[0]['tid']  # максимальный tik_id из полученного запроса

    # print(n,'tik',prev_tik==curr_tik)
    if (curr_tik != prev_tik):  # Только если за промежуток были новые данные. Могут и не быть(если ничего не происходит)

        new_data = [x for x in r if x['tid'] > prev_tik]  # Новые данные из полученных 1000 значений
        tikObj.add_tail(new_data)
        # От tikObj можно отказаться, сохранив новый результат в таблицу  save_tik(conn,new_data)
        # и делать рассчет на основе данных из таблицы
        # save_tik(conn,new_data) Сохраняем, чтобы можно было проверить сработал ли флаг не  через API

        # =====Алгоритм===========
        '''Алгоритм расчитывает несколько позиций'''

        #ПРОВЕРКА ОРДЕРА
        if (orderCount > 0):  # ордер установлен, тогда проверка сработал ли он

            # Доп проверка
            # например calculation2
            # либо в calculation(параметр calc2=true)

            # chech_order_time_start   определено при установке флага.
            # если ордер не сработал при первой проверке, то устанавливается равным
            # startCalcPeriodTime(предыдущая точка расчетов)
            check_order_time_end = startCalcPeriodTime

            # Проверка только на следующем шаге, посе устанолвки флага, т.к. иначе данные еще не были получены
            orders_done = checkOrder(conn, check_order_time_start, check_order_time_end,actOrders.active_orders_list)  # Проверка флага на промежутке

            for r_ord in orders_done:  # Цикл по сработавшим ордерам

                # Проверка всех ордеров по циклу
                # В данном случае один ордер

                id = r_ord['order_id']  # id сработавшего ордера
                tik_id = r_ord['tik_id']  # tik на котором сработал ордер
                date_id = r_ord['date_id']  # date когда сработал оредер

                doneOrd = actOrders.removeOrder(id)  # сработавший ордер
                xc = 0  # инициализация
                ord_type = doneOrd['type']

                if (ord_type == 'buy'):
                    xc = doneOrd['amount']
                    deposit.changeBlnc(xc, 'BTC')  # получили на депозит


                    doneOrd.update({'tik_id':tik_id})
                    doneOrd.update({'date_id':date_id})
                    log.log_action(conn, doneOrd, 'bought')
                if (ord_type == 'sell'):
                    xc = doneOrd['x']  # сумма, которую должны получить
                    deposit.changeBlnc(xc, 'USD')  # получили x на депозит


                    doneOrd.update({'tik_id': tik_id})
                    doneOrd.update({'date_id': date_id})
                    log.log_action(conn, doneOrd, 'sold',market)

                # get balace with API  and refresh
                # Test calc _balance

                orderCount = orderCount - 1

            prev_tik = curr_tik
            continue



        # Проверка надо ли сбросить

        time_s = time.time()
        res = calculation.calc_reset()  # проверка надо ли сбросить флаг
        r_act = res['type']  # результат. какое действие делать
        time_e = time.time()  # время завершения расчета
        reset_time = startCalcPeriodTime + int((time_e - time_s))


        if (r_act == 'cancel'):

            id = res['id']

            # API  запрос на снятие флага return true/false
            # Если false => сработал либо связь           это проверяется в тесте через  r_ord = checkOrder(startCalcPeriodTime, reset_time)
            # Если сработал => Проверка баланса через API

            # Проверка ТОЛЬКО ДЛЯ ТЕСТА   сработал ли флаг при расчете
            r_ord = checkOrder(conn, check_order_time_start, reset_time, actOrders.active_orders_list)

            # Далее обработка баланса и переъход на след шаг

            # Если true, то обработка баланса(возврат к предыдущему)

            # В тесте необходимо проверить вручную на промежутке (time_order_place;tcalc2) либо (startCalcPeriodTime,tcalc2)

            #order_reset = {'id': id, 'order_time': reset_time, 'status': 'ok'}  # сумма, которая возвращается не логируется
            removed = actOrders.removeOrder(id)  # ордер, который сняли
            removed.update({'reset_time':reset_time})
            xc = 0
            ord_type = removed['type']
            if (ord_type == 'buy'):
                xc = removed['x']  # зарезервированная сумма
                deposit.changeBlnc(xc, 'USD')  # возвратили x на депозит
            if (ord_type == 'sell'):
                xc = removed['amount']
                deposit.changeBlnc(xc, 'BTC')  # возвратили btc на депозит

            log.log_action(conn, removed, 'cancel',market)

            orderCount = orderCount - 1
            prev_tik = curr_tik
            continue

        if (r_act == 'cancelALL'):
            # res_api = ...
            # list_orders = reas_api['src_data']
            orderCount = 0
            # За время рассчетов мог сработать ордер
            # Проверять, если был установлен флаг
            check_order_time_start = startCalcPeriodTime  # т.к. на прошлом промежутке ничего не произошло, то его не надо повторно проверять
            tcalc2 = time.time()
            dCalctime = tcalc2 - tcalc1  # Время работы  !!! ПРОВЕРИТЬ МОЖНО ЛИ ТАК ВЫЧИТАТЬ ВРЕМЯ

            # if dCalctime > DELTA_T:  # расчет был слишком долгий
            #    print('Too long calc at tik=' + curr_tik + ' startCalcPeriodTime=' + startCalcPeriodTime)
            #    continue

        prev_tik = curr_tik


        #РАСЧЕТ НА УСТАНОВКУ ОРДЕРА
        if (orderCount <= LIMIT_ORDER):  # лимит на количество установленныйх ордеров

            # Расчет. Анализ данных. Вывод действия: брать/продать/оставить
            #======1 алгоритм на установку==========
            res = calculation.calc()  # тогда делаем расчет по полученным данным. Добавить входные переменные.
            tcalc2 = time.time()  # время окончания расчетов
            dCalctime = tcalc2 - tcalc1  # Время работы  расчета

            # if dCalctime > DELTA_T:  # расчет был слишком долгий  dCalctime > timedelta(seconds=DELTA_T) - в формате
            #    print('Too long calc at tik=', curr_tik, ' startCalcPeriodTime=', datetime.fromtimestamp(startCalcPeriodTime))
            #    continue
            n = setOrder(res)
            orderCount = orderCount+n
            #=======1==========

            #Повторить для другого расчета




            chech_order_time_start = int(startCalcPeriodTime) + int(time.time() - tcalc1)
            prev_tik = curr_tik
            continue



dbconn.closeConnect(conn)




