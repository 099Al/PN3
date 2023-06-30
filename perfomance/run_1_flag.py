# -*- coding: utf-8 -*-

'''Все функции и расчеты !ВЫНОСИТЬ в другой модуль
Здесь идет основной расчет(эмуляция)
'''

import time
from datetime import datetime

from perfomance.data.dataTic import *
from perfomance.entityes.TikTail import TikTail

from perfomance.order.checkOrders import checkOrder

import perfomance.loging.logAction as log
#from perfomance.balance.balance import DepoBalance
from algorithms.initialisation.init import initBalance
from algorithms.orders import ActiveOrders,ProcessLine
from db.connection import DBConnect

import perfomance.perfomParamset as pset
from perfomance.order.setOrder import placeOrder
from perfomance.order.removeOrder import remove_order
from perfomance.order.executedOrder import executeOrders

from algorithms.alg1.calculation import calculation, reset
import algorithms.alg1.parameters.algParams as algPrm
import algorithms.alg1.stop.resetMark as stopM

from api.cexio import Api


from util.util_datetime import unix_to_date


# Константы

# from perfomance.order.setOrder import id, ord_time, order_place_time, check_order_time_start, place_order

DELTA_T = pset.DELTA_T  # Запрос каждые десять секунд
START_DATE = pset.START_DATE  # Стартовое время
market = pset.MARKET

M_D = algPrm.M_D  # размер массива Новых элементов

# Класс с доступом к API
import perfomance.keys as k

api = Api(k.username, k.api_key, k.api_secret)

dbconn = DBConnect()
conn = dbconn.getConnect()

n = 0  # Начало итераций. Для тестирования
startCalcPeriodTime = int(datetime.strptime(START_DATE, '%Y-%m-%d %H:%M:%S').timestamp())  # Для тестирования

clear_history(conn, 'cex_history_tik')  # Предварительная очистка таблицы. Для тестирования.
log.clear_log(conn)

#tikObj = TikQueue(M_D)  # Массив размером 50
tikObj = TikTail(M_D)

prev_tik = 0
#f_orderIsSet = 0  # флаг (установлен ли ордер)
order_place_time = 0  # время установки флага

t_calc_start = 0  # время до всех рассчета внутри интервала    реальное время time.time()
t_calc_order = 0  # время окончания рассчета установки ордера
t_calc_reset = 0  # время окончания расчета по сбросу ордера
t_calc_check = 0  # время окончания расчета по проверки ордера (не нужно учитывать, если в алгоритме эта проверка будет через API)

    #Перенесено внутрь функции проверки
    #check_order_time_start = 0 #начало перида, на котором проверяется ордер(время его установки)    тестовое время
    #check_order_time_end = 0 #конец перида, на котором проверяется ордер(конец интервала)



print('==========', time.time())

#changeConst = changeConstants()
actOrders = ActiveOrders()  # список теукущих ордеров
pLines = ProcessLine()   #линии ордеров # Необходимо при инициализации указать максимальное доступное кол-во
'''
#!!! СОЗДАТЬ МАКСИМАЛЬНОЕ КОЛ_ВО ЛИНИЙ.. СОЗДАТЬ ЛИНИЮ ПРИ НЕОБХОДИМОСТИ (ПРИИ ПОИСКЕ СВОБОДНЫХ)
# ЕСЛИ СВОБОДНЫХ НЕТ, то СОЗДАЕТСЯ НОВАЯ ЕСЛИ НЕ БОЛЬШЕ ЛИМИТА 
'''
#Инициализация
deposit = initBalance()  # Начальный Баланс на депозите. Задается перед началом рассчета.
#initLines()

print('---Начальное состояние--', unix_to_date(time.time()))
print('USD=', deposit.blnc_USD)
print('BTC=', deposit.blnc_BTC)
print('------------------------')


while 1 == 1:
    n = n + 1
    if (n > 60): break  # Завершение цикла. При тестировании

    print('n=', n)
    if (n == 7):
        print('n=', n)

    # time.sleep(DELTA_T)   #Задержка по времени (реализовать в реальном времни) DELTA_T можно менять в зависимости от времени расчета
    startCalcPeriodTime = startCalcPeriodTime + DELTA_T  # В тесте время запроса рассчитывается  !!!! Возможно надо перенести в конец цикла

    # DELTA_T должно быть больше dT1 и dT2, тогда переносить не надо. Но период для проверки флага надо изменить

    # Получение последних 1000 tik на данный момент
    # Данные должны получаться через api



    r = f_data_tic_imitation(conn, startCalcPeriodTime)  # Эмулированный результат получения 1000 тиков
    '''# Эмулированный результат - словарь вида: {tid:,type:,unixdate:,amount:,price:} '''

    t_calc_start = time.time()  # datetime.now()-  формате. Время начала рассчетов.  Текущее время. Время,когда начался процесс рассчета
    curr_tik = r[0]['tid']  # максимальный tik_id из полученного запроса

    # print(n,'tik',prev_tik==curr_tik)
    if ( curr_tik != prev_tik):  # Только если за промежуток были новые данные. Могут и не быть(если ничего не происходит)

        new_data = [x for x in r if x['tid'] > prev_tik]  # Новые данные из полученных 1000 значений
        tikObj.add_tail(new_data)
        #last_prices = tikObj.get_last_n_prices(5)  # цены   разделены на два list  для sell и buy
        last_prices = tikObj.last_prices()

        # От tikObj можно отказаться, сохранив новый результат в таблицу  save_tik(conn,new_data)
        # и делать рассчет на основе данных из таблицы
        save_history_tik(conn, new_data)

        # =====Алгоритм===========
        '''if (f_orderIsSet == 0):  # ордер не установлен  ->  заменен на выбор свободной линии
            Всегда должна быть одна(1-я главная) линия
            Вторая возникает, если сработал алгоритм расчета на создание второй линии.
            По необходимости надо указать максимальное кол-во линий
            Линия удаляется из общего потока, после того как будет создан сигнал на удаление.
            Сигнал создается в отдельном проверочном алгоритме (возможно эту проверку надо ставить в нескольких местах)
            
            Так же вторая линия может быть, если она было создана в начальных условиях(Инициализация перед началом рассчетов)
        '''
        #Поиск свободной линии



        free_lines = pLines.freeLines()
        print('line',free_lines)
        if (len(free_lines) > 0):  # ордер не установлен (есть свободные линии)

            # делаем рассчет по одной линии
            # при нескольких линиях надо сделать цикл
            free_line = free_lines[0]


            # Расчет. Анализ данных. Вывод: действие(брать/продать/оставить)
            # Действие рассчитывается только для баланса.
            # Для активных ордеров будет отдельная проверка
            '''
            Переделать в класс, в котром в зависимости от параметра выбирается алгоритм
            Результат должен быть один, т.к. выставляться будет по одному(один ордере в промежуток времени)
            '''



            calculated_order = calculation.calc(last_prices,free_line)  # тогда делаем расчет по полученным данным. Добавить входные переменные.

            '''
                Для тестирования если расчет больше DELTA_T, то расчет будет не корректым
                Т.к. DELTA_T фиксирована
                В рабочем режиме запросы будут поступать на сервер после завершения расчетов(работы функции)
                Потому DELTA_T будет меняться  (Но расчет должен быть ограничен по времени, чтобы данные  были актуальны)
             '''
            r_act = calculated_order['type']  # результат. какое действие делать

            if (r_act == 'stop'):  # остановка
                exit()

            if (r_act == 'buy' or r_act == 'sell'):

                # УСТАНОВКА ОРДЕРА
                # api set order   # установка ордера через API
                # PRIVATE API place_order = api.buy_limit_order(amount,price,market)  # На выходе получается словарь с данными ордера
                # В этом случае логирование нужно вынести
                # place_order_for_log = place_order.update(add_subtype=0)
                # log.log_action(conn,free_line, place_order,r_act, market)
                # Попытка
                # time.sleep(1)
                # Для тестирования генерация id
                t_calc_order = time.time()        #обновление параметра
                '''
                    dCalctime = t_calc_order - t_calc_start  # Время работы  расчета
                 
                     # Проверка не превышен ли временной интервал рассчета !!!
                     if dCalctime > DELTA_T:  # расчет был слишком долгий  dCalctime > timedelta(seconds=DELTA_T) - в формате
                        print('Too long calc at tik=', curr_tik, ' startCalcPeriodTime=', datetime.fromtimestamp(startCalcPeriodTime))
                        continue
                
                   
                    Если рассчитывается несколько линий,
                    то все рассчеты должны влезть в интервал DELTA_T
                    если на каком-то шаге будет выход за интервал, то на этом шаге ордер не ставится. Идет переход на след. интервал.
                '''
                ord_time = int(startCalcPeriodTime) + int(t_calc_order - t_calc_start) # Время (по тестовым данным) установки
                # время установки флага

                #check_order_time_start = ord_time  #Время начала провеверки !Для конкретного ордера (check)


                place_order = placeOrder(free_line, calculated_order,0, ord_time)['place_order']    # 0 - это обычный ордер
                id_order = place_order['id']
                print('calc_order:',calculated_order)
                print('set order:',place_order)
                # резервировние на депозите внутри placeOrder

                log.log_action(conn, free_line, place_order, place_order['type'], market)  #Логирование ордера вынесено из placeOrder

                # -----тестирование----------

                #f_orderIsSet = 1
                pLines.placingLine(free_line,id_order)  #!!!!!!!!!!!!!!!!!===========$$$$$$$$$$$$$$$$$$$$$$$$$$$

                prev_tik = curr_tik
                continue




        #else:  # ордер установлен, тогда проверка сработал ли он. надо ли сбросить
        #Условие else заменяем на проверку по занятым линиям

        l_active_orders = actOrders.active_orders_list
        if(len(l_active_orders)>0):     #если есть активные ордера, то их надо проверить, сработали ли они

            '''
                 [check_order_time_start, check_order_time_end]-период времени, на котором идет проверка
                 
                 chech_order_time_start = ord_time  
                 check_order_time_end = startCalcPeriodTime
                 
                 chech_order_time_start   определен при установке флага. в предыдущем шаге
                 если ордер не сработал при первой проверке, то устанавливается равным
                 startCalcPeriodTime(предыдущая точка расчетов)
    
                 Время начала провеверки (check)  ord_time - время, когда был выставлен флаг
                
                 Проверка только на следующем шаге, после установки флага, т.к. иначе данные еще не были получены
            '''


            #цикл по ордерам перенесен во внутрь, чтобы было меньше подключений к базе

            #НЕОБХОДИМО заменить на проверку через API
            '''
                Проверка флага на предыдущем промежутке (от момента установки флага, до момента начала нового промежутка)   
                Длительность проверки не учитывается!
                Т.к. это происходит на сервере. Нужен сам сезультат.
                check_order_time_start для каждого определяется внутри процедуры
            '''
            start_prev_period = int(startCalcPeriodTime) - DELTA_T
            start_curr_period = int(startCalcPeriodTime)
            executed_orders = checkOrder(conn,start_prev_period ,start_curr_period,l_active_orders)

            if (len(executed_orders) > 0):  # Сработал

                #Делается пометка в активных ордерах и линиях
                #!!! Изменения в депозите можно вынести из этой функции, чтобы  это можно было отключить
                #!!!И изменения записывать на основе данных полученных из API
                executeOrders(executed_orders, market)
                #executeOneOrder(executed_orders, market)

                # get balace with API  and refresh
                # Test calc balance

                #f_orderIsSet = 0

                prev_tik = curr_tik
                continue

            '''
            # RESET
            # Проверка надо ли сбросить ордер:
            #   1.Просто сбрасываем, чтобы пересчитать новый флаг
            #   2.Сбрасываем, чтобы быстро продать BTC.
            '''

            '''
             Этот расчет заложен в алгоритме,
             поэтому надо учесть его длительность
            '''
            #time_s = time.time()  # начало расчетов

            '''
            Переделать в класс stop-loss
            В функцию передавать активные ордера
            '''
            #-----RESET-------------------
            # список ордеров на снятие
            reset_list = reset.calc_active_orders_reset(last_prices)  # RESET   РАСЧЕТ СБРОСА  Причина сброса


            '''
            цикл по всем снятым линиям
            '''
            for reset_flag in reset_list:


                f_act = reset_flag['action']  # результат. какое действие делать
                f_subt = reset_flag['reset_type']  # причина снятия

                # ----reset-------------------

                # время завершения расчета по снятию ордера
                t_calc_reset = time.time()
                reset_time = startCalcPeriodTime + int((t_calc_reset - t_calc_start))

                '''если ордер сняляся, то ниже идет обработка случаев из-за которых снялся ордер
                    т.е. может быть 1.продать по рынку
                                    2.продать по лимитной цене, но другие условия
                                    3.ничего не делать
                '''
                if (f_act == 'cancel'):

                    # API  запрос на снятие флага return true/false
                    # Если false => сработал либо связь           это проверяется в тесте через  r_ord = checkOrder(startCalcPeriodTime, reset_time)
                    # Если сработал => Проверка баланса через API

                    # Проверка ТОЛЬКО ДЛЯ ТЕСТА   сработал ли флаг при расчете
                    start_prev_period = int(startCalcPeriodTime) - DELTA_T
                    r_ord = checkOrder(conn, start_prev_period, reset_time, actOrders.active_orders_list) #НАДО СДЕЛАТЬ ПРОВЕРКУ ДЛЯ ОДНОГО ID

                    # В тесте необходимо проверить вручную на промежутке (time_order_place;tcalc2) либо (startCalcPeriodTime,tcalc2)


                    id = reset_flag['id']
                    removed_order = remove_order(id,f_subt,reset_time)   #линия освобождается



                    set_stop_time = startCalcPeriodTime + int((time.time() - t_calc_start))
                    '''
                        Сделать проверку, что set_stop_time < startCalcPeriodTime + DELTA_T
                    '''

                    stop_order = removed_order['removed_order']
                    # {'type': 'sell', 'mtype':'limit','crypt':'BTC', 'amount':amount, 'price':curr_price, 'x':x}
            #     if (f_subt == stopM.STOP_1):
            #         # type = 'sell'     остался тем же
            #         # mtype = 'limit'   остался тем же
            #         # amount = остается тем же
            #         # price - выставляем по значениям
            #         limit_price = calculated_reset_flag['limit_price']
            #         stop_order.update({'price':limit_price})
            #         #Расчитать время в этой точке
            #         place_order = placeOrder(free_line, stop_order, 1,set_stop_time)   #ВЫСТАВИТЬ ЛИМИТНЫЙ ПО ПАРАМЕТРАМ
            #         f_orderIsSet = 1
            #         #Запомнить старый ордер. В ACTIVE ORDERS Сделать список. По ID  ID отнести к процессу. ID знаем
            #
                    if (f_subt == stopM.STOP_2):
                        # type = 'sell'     остался тем же
                        # mtype = 'market'   остался тем же
                        # amount = остается тем же
                        # price - по рынку
                        stop_order.update({'mtype': 'market'})
                        stop_order.update({'price': -1})

                        place_order = placeOrder(free_line, stop_order, 1, set_stop_time)['place_order']  # ВЫСТАВИТЬ ПО РЫНКУ
                        pLines.placingLine(reset_flag['line'],place_order['id'])


            #
            #     if (f_subt == stopM.R_3):
            #         # type = 'sell'     остался тем же
            #         # mtype = 'limit'   остался тем же
            #         # amount = остается тем же
            #         # price - берется в сохраненных по ID
            #         stop_order.update({'price': 0})
            #
            #     place_order = placeOrder(free_line, stop_order, 1, set_stop_time)
            #     f_orderIsSet = 1


                prev_tik = curr_tik
                continue

            # т.к. при проверке на временном промежутке ничего не произошло
            #  , то его не надо повторно проверять
            # -----S1----F----S2-------S3-----     F-S2  - не сработал => этот промежуток больше не проверяется

            # т.к. на прошлом промежутке ничего не произошло, то его не надо повторно проверять
            # уменьшение проверяемого интервала
            # check_order_time_start = startCalcPeriodTime  не нужно

            tcalc2 = time.time()
            dCalctime = tcalc2 - t_calc_start  # Время работы  !!! ПРОВЕРИТЬ МОЖНО ЛИ ТАК ВЫЧИТАТЬ ВРЕМЯ

            # if dCalctime > DELTA_T:  # расчет был слишком долгий
            #    print('Too long calc at tik=' + curr_tik + ' startCalcPeriodTime=' + startCalcPeriodTime)
            #    continue

        prev_tik = curr_tik
        # т.к. на прошлом промежутке ничего не произошло, то его не надо повторно проверять
        # уменьшение проверяемого интервала
        # check_order_time_start = startCalcPeriodTime не нужно

dbconn.closeConnect(conn)

print('====Результат==============', unix_to_date(time.time()))
print('USD=', deposit.blnc_USD)
print('BTC=', deposit.blnc_BTC)
print('=================')