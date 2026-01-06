# -*- coding: utf-8 -*-
'''
Словарь выставленных ордеров
Последовательность купли/продажи

структура ордера _order ={'id':id
                            ,'amount':amount
                            ,'price':price
                            ,'time':ord_time
                            , 'type': r_act
                            , 'x':reserver_sum
                            }
структура словаря order_list  = {id: _order}

ActiveOrders - класс активных ордеров. Т.е. которые выставлены либо на покупку, либо на продажу

SavedOrders - класс со списком снятых ордеров. Запомнить параметры снятого, чтобы была возможность выставить повторно

ProcessLine  - класс линий, по которым идет купля/продажа.
Т.е. общая сумма на депозите разбивается на части. И покаждой части выставляется свой ордер.
Дальнейшие изменения высчитываются по каждой части.
'''

from  algorithms.alg1.parameters.algParams import MAX_LINES

class ActiveOrders():
    active_orders_list = {}  # активные ордера

    #Ключом key является id-ордера

    def addOrder(self,key,value):
        ActiveOrders.active_orders_list.update({key:value})

    # находим ордер из списка активных
    def findOrder(self,key):
        return ActiveOrders.active_orders_list[key]

        # удаляем ордер из списка активных
    def removeOrder(self,key):
        return ActiveOrders.active_orders_list.pop(key)




#Запомнить ордер, который сняли
class SavedOrders():

    saved_orders_list = {}  # сохраненные снятые ордера

    def saveOrderPrmt(self,id,order):
        SavedOrders.saved_orders_list.update({id:order})

    def removeSavedOrder(self,id):
        return SavedOrders.saved_orders_list.pop(id)


'''
Словарь процессов. В каждом процессе стоит Id-текущего ордера. И параметры сработавшего
в расчете одной линии(стратегии)
'''
class ProcessLine():
    '''Перед тем как расчитать ордер, необходимо найти линию, которая свободна.
    Для нее расситываются параметры ордера.
    Поэтому для конкретного Id-ордера номер линии известен.
    Поэтому его можно поместить в аргумент функции'

    threads = {
            line:{
                    line
                    ,order_id
                    ,prev_amount
                    ,prev_x
                    ,prev_price
                    ,result_amount
                    ,result_x
                }
        }

    '''




    threads = {} #если Id задан, то ордер установлен в текущем процессе(), если 0 - то линия свободна  {line-номер линии,id-ордера}
    #thread_prev = {} #параметры предыдущего сработавшего ордера в данном процессе(линии)
    #thread_result = {} # итог на данный момент по данному процессу

    #Инициализация линии
    def initLine(self,line,id,amount,x):
        '''Если ордер установлен, то надо указать id ордера, чтобы по нему найти линию.
        Если указаны, только доступные суммы, то id проставляется 0.
        '''

        d_line = {
                'line':line
                ,'id':id
                , 'prev_amount':None
                , 'prev_x': None
                , 'prev_price': None
                , 'prev_order_type':None
                , 'result_amount':amount
                , 'result_x':x
        }

        ProcessLine.threads.update({line:d_line}) #Новая активная линия
        #ProcessLine.thread_result.update({line:{'amount':amount,'x':x}})

    #общая сумма по всем линиям
    def sumTotalAmount(self):
        amount = 0
        x = 0
        for line,val in ProcessLine.threads:
            amount = amount+val['result_amount']
            x = x+val['result_x']
        return {'amount':amount,'x':x}


    #сумма по линии
    def lineAmountX(self,line):
        x = ProcessLine.threads[line]['result_x']
        amount = ProcessLine.threads[line]['result_amount']
        return {'amount':amount,'x':x}


    #Поиск свободной линии
    def firstFreeLine(self):
        if len(ProcessLine.threads) == 0:
            return 1
        free_line = min([line for line,val in ProcessLine.threads.items() if(val['id'] == 0)])
        return free_line

    #Поиск свободных линий
    def freeLines(self):

        work_lines = len(ProcessLine.threads)
        if (work_lines == 0):
            return [1] #номер свободной линии
        #освободившиеся линии
        free_lines = [line for line, val in ProcessLine.threads.items() if (val['id'] == 0)]
        #создание новой линии
        if(len(free_lines)==0):
            if(MAX_LINES-work_lines>0):
                return [work_lines+1]
            else:
                return []
        else:
            return sorted(free_lines)  #номера свободных линий

    #Поиск занятых линий
    def placedLines(self):
        placed_lines = [{'line':line,'id':val['id']} for line, val in ProcessLine.threads.items() if (val['id'] != 0)]
        return placed_lines.sort()

    #Удаление линии
    def removeLastLine(self):
        #1 - Главная линия. Не удаляется.
        max_line = max([line for line,val in ProcessLine.threads.items() if (val['id'] == 0 and line != 1)])
        del ProcessLine.threads[max_line]
        #del ProcessLine.thread_prev[max_line]
        #del ProcessLine.thread_result[max_line]

    #После установки ордера
    def placingLine(self,line,id):

        if line in  ProcessLine.threads:
            ProcessLine.threads[line].update({'id': id})
        else:

            d_line = {
                'line': line
                , 'id': id
                , 'prev_amount': None
                , 'prev_x': None
                , 'prev_price': None
                , 'prev_order_type':None
                , 'result_amount': 0
                , 'result_x': 0
            }
            ProcessLine.threads.update({line:d_line})


    #Снятие ордера
    def removeOrder(self,id):
        for line,v_id in  ProcessLine.threads.items():
            if (v_id==id):
                ProcessLine.threads[line].update({id:0})  #освобождаем линию
                return line


    #Ордер сработал
    def doneOrder(self,doneOrder):

        d_id = doneOrder['id']
        d_price = doneOrder['price']

        d_type = doneOrder['type']
        type2 = ''
        d_amount = doneOrder['amount']
        d_x = doneOrder['x']

        if d_type == 'buy':
            type2 = 'bought'
            d_amount = d_amount   #купили эту величину
            d_x = -d_x            #следовательно баланс уменьшился на эту

        if d_type == 'sell':
            type2 = 'sold'
            d_amount = -d_amount  #продали эту величину
            d_x = d_x             #следовательно баланс увеличился на эту


        for line, val in ProcessLine.threads.items():
            if (val['id'] == d_id):
                #освобождаем линию
                #сохраняем сработавший ордер как предыдущий
                ProcessLine.threads[line].update({'id': 0
                                                 ,'prev_price': d_price
                                                 ,'prev_amount':d_amount
                                                 ,'prev_x':d_x
                                                 ,'prev_order_type':d_type
                                                })

                #Баланс до изменения
                # !!!! try{}
                amount = ProcessLine.threads[line]['result_amount']
                x = ProcessLine.threads[line]['result_x']

                amount = amount + d_amount
                x = x + d_x

                #Баланс на данной линии после изменений
                ProcessLine.threads[line].update({'result_amount':amount,'result_x':x})

                return line


    #Поиск линии
    def findLinebyId(self,id):
        for line,v in  ProcessLine.threads.items():
            if (v['id']==id):
                return line




    #Поиск предыдущей цены
    def findPrevPrice(self,id):
        for line,v in  ProcessLine.threads.items():
            if (v['id']==id):
                return v['prev_price']

            else:
                return None

    #Поиск предыдущего ордера
    def findPrevOrder(self,id):
        for line,v in  ProcessLine.threads.items():
            if (v['id']==id):

                ord_prev = {
                  'price': v['prev_price']
                , 'amount': v['prev_amount']
                , 'x': ['prev_x']
                , 'order_type': ['prev_order_type']
                }

                return ord_prev
            else:
                return None

