# -*- coding: utf-8 -*-



#Проверка ордера на заданном интервале
def checkOrder(connect,start_period,end_period,order_list):

    '''Если выставляется лимитный ордер на продажу(sell),
       то в истории он отобразится как buy. Т.е. его купили по рынку

       Передается список активных ордеров
       На выходе получаем список сработавших

       [start_period - end_period] - период времени, на котором идет проверка

       Должна идти на интервале [установка флага - начало нового периода(момент запроса на получение новых данных)]

        В реальной ситуации орден должен сработать до того как придут данные.

        В алгоритме в начале шага идет запрос к эмулированным данным,
        поэтому можно делать проверку на полученых данных.
        Проверку надо делать на cex_history_tik это не даст "заглянуть в будущее",
        и не надо делать лишний запрос, в слусае использовагния API.

        Эта функция используется только при тестировании.
        В рабочем состоянии проверка должна быть реализована через API.


    '''

    #На вход подается список ордеров в ожидании order_list
    # структура словаря order_list = {id: order}
    # структура ордера order = {'id': id, 'amount': amount, 'price': price, 'ord_time': ord_time, 'type': r_act, 'mtype':}

    #В результате получаем list словарей {'order_id':x,'tik_id':tik_id}
    # order_id - id ордера в списке
    # tik_id - id транзакции, на которой должен был сработать ордер

    # startPeriod - должен совпадать со временем установки флага

    orders_done = []
    curr = connect.cursor()
    sql_limit  = 'SELECT tid,unixdate,date,price \n' \
              'FROM cex_history_tik \n' \
              'WHERE tid = \n( ' \
              'SELECT  min(tid) /*самый 1-й id который удовлетворяет условию */ \n' \
              'FROM cex_history_tik \n' \
              'WHERE unixdate > \'{startPeriod}\' AND unixdate <= \'{endPeriod}\'\n' \
              '    and price {select_condition} {order_price}  \n' \
              '    and type = \'{type}\' \n' \
              ')';

    sql_market = 'SELECT tid,unixdate,date,price \n' \
                'FROM cex_history_tik \n' \
                'WHERE tid = \n( ' \
                'SELECT  min(tid) /*самый 1-й id  */ \n' \
                'FROM cex_history_tik \n' \
                'WHERE unixdate > \'{startPeriod}\' AND unixdate <= \'{endPeriod}\'\n' \
                '    and type = \'{type}\' \n' \
                ')';


    '''
        Проверка дделается только на предыдущем периоде.
        если ордер активный, значит на более старых периодах он не сработал.
        |-----Ord<---t1-->|<----t2--->|<----t3---->|  проверяются участки t1,t2,t3
    '''

    endPeriod = end_period

    for x in order_list:

        order_price = order_list[x]['price']
        type =  order_list[x]['type']
        mtype = order_list[x]['mtype']

        order_set_time = order_list[x]['ord_time']
        startPeriod = max(start_period,order_set_time)  #Время установки ордера берем из словаря


        sql_x = ''


        select_condition = ''
        if(mtype=='limit'):

            ord_type=''

            if (type == 'sell'):
                select_condition = '>='   # при продаже отбирается все price, которые больше ожидаемой в ордере, т.е. чтобы стработал ордер на продажу'
                ord_type = 'buy'  #сработавший ордер на продажу будет в истории отображаться как buy
            if (type == 'buy'):
                select_condition = '<='   # при покупке отбирается все price, которые меньше ожидаемого в ордере, т.е. чтобы стработал ордер на покупку'
                ord_type = 'sell'
            sql_x = sql_limit.format(startPeriod=startPeriod,endPeriod=endPeriod,order_price=order_price,type=ord_type,select_condition=select_condition)


        if(mtype=='market'):  #купить/продать по рынку

            if (type == 'sell'):   #продать по рынку
                #значить продать первому в стакане, из тех кто хочет купить.
                #т.к. история стакана не сохраняется,считаем по первому ордеру в диапазоне, который сработал по типу buy
                sql_x = sql_market.format(startPeriod=startPeriod,endPeriod=endPeriod,type='buy')
            if (type == 'buy'):   #купить по рынку
                # значить купить у первого в стакане, из тех кто хочет продать.
                # т.к. история стакана не сохраняется,считаем по первому ордеру в диапазоне, который сработал по типу sell
                sql_x = sql_market.format(startPeriod=startPeriod,endPeriod=endPeriod,type='sell')



        res = curr.execute(sql_x)

        try:
            list_res = res.fetchall()
            if(len(list_res)>0):
                tik_id = list_res[0][0]
                date_id = list_res[0][1]
                market_price = list_res[0][3]  # market_price необходима, чтобы узнать по какой цене по рынку был реализован ордер

                orders_done.append({'order_id':x,'tik_id':tik_id,'date_id':date_id,'price':market_price})
                #Для ордеров типа limit цена находится из ActiveOrders по id.

        except:
            print('Ошибка запроса к cex_history_tik. CheckOrders.')

    curr.close()

    return orders_done





if __name__ == '__main__':

    import db.connection as dbconn
    conn = dbconn.getConnect()

    order_list = {1:{'id': 1, 'amount': 0.03878, 'price': 100, 'time': '123546', 'type': 'buy'}
                  ,2:{'id': 2, 'amount': 0.03878, 'price': 35050, 'time': '123546', 'type': 'sell'}
                  }


    d = checkOrder(conn,  '2019-02-03 09:07:41','2019-02-04 12:14:56',order_list)

    print(d, len(d))
