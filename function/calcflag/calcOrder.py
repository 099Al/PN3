# -*- coding: utf-8 -*-

#ДАННЫЙ МОДУЛЬ НЕ ИСПОЛЬЗОВАТЬ
# Т.К. УСТАРЕЛ

# Идет только расчет
def calculationOrder(TikQueue, oldflag):
    # Передается ссылка на объект
    # С ним делается расчет
    # Использование check_flag_period

    # результат: тип:(купить/продать/сбросить/ничего) кол-во  цена

    f = {'type': 'b', 'curr': 'B', 'amount': 1000, 'price': 1000}

    return f


# Установка ордера
def setOrder(order):
    # request to server to SET ORDER  в реальных условиях

    import flag as f
    flag_dict.update(f)

    # режим эмуляции
    import function.calcflag.order as ord

    ord.order_price = order['price']
    ord.order_btc_value = order['value']
    ord.order_type = order['type']  # if order_prmt['type'] == 1 => sell  buy 0
    ord.order_status = 1  # Установлен ордер

    return 1


# Проверка флага (предполагаемая) на основе новых данных
def check_flag_period(TikQueue):
    # использовать таблицу  cex_history_tik(суда записываются предыдущие данные)
    # и новые данные
    pass


# Проверка флага при тестировании на основе данных в таблице
def check_flag_imulation(connect, from_Tf, to_Tf2):
    curr = connect.cursor()

    import function.calcflag.order as order
    sql = ''
    status = order.order_status
    type = order.order_type
    # sell BTC    buy BTC
    if (type == 'sell' and status == 1):
        sql = 'SELECT  min(price) price ' \
              'FROM im_cex_history_tik ' \
              'WHERE date > {dt_from} ' \
              'AND date <= {dt_to} ' \
              'AND price >= {prc}'

    if (type == 'buy' and status == 1):
        sql = 'SELECT  max(price) price ' \
              'FROM im_cex_history_tik ' \
              'WHERE date > {dt_from} ' \
              'AND date <= {dt_to} ' \
              'AND price <= {prc}'

    sql = sql.format(dt_from=from_Tf, dt_to=to_Tf2)

    r = curr.execute(sql)
    res = r.fetchall()

    # Залезть в таблицу и сравнить данные с глобальной переменной

    pass# -*- coding: utf-8 -*-


#Идет только расчет
def calculationOrder(TikQueue,oldflag): #Передаются данные в массиве TikQueque,которые анализируются и состояние ордера
    #Передается ссылка на объект
    #С ним делается расчет
    # Использование check_flag_period

    #результат: тип:(купить/продать/сбросить/ничего) кол-во  цена

    f={'type':'b','curr':'B','amount':1000,'price':1000}

    return f

#Установка ордера
def setOrder(order):
    #request to server to SET ORDER  в реальных условиях

    import flag as f
    flag_dict.update(f)

    #режим эмуляции
    import function.calcflag.order as ord

    ord.order_price = order['price']
    ord.order_btc_value = order['value']
    ord.order_type = order['type'] # if order_prmt['type'] == 1 => sell  buy 0
    ord.order_status = 1  # Установлен ордер

    return 1


#Проверка флага (предполагаемая) на основе новых данных
def check_flag_period(TikQueue):
          # использовать таблицу  cex_history_tik(суда записываются предыдущие данные)
          # и новые данные
    pass

#Проверка флага при тестировании на основе данных в таблице
def check_flag_imulation(connect,from_Tf, to_Tf2):
    curr = connect.cursor()

    import function.calcflag.order as order
    sql = ''
    status = order.order_status
    type =   order.order_type
    # sell BTC    buy BTC
    if (type=='sell' and status ==1):

        sql = 'SELECT  min(price) price ' \
              'FROM im_cex_history_tik ' \
              'WHERE date > {dt_from} ' \
              'AND date <= {dt_to} ' \
              'AND price >= {prc}'



    if (type == 'buy' and status == 1):

        sql = 'SELECT  max(price) price ' \
                  'FROM im_cex_history_tik ' \
                  'WHERE date > {dt_from} ' \
                  'AND date <= {dt_to} ' \
                  'AND price <= {prc}'


    sql = sql.format(dt_from=from_Tf,dt_to=to_Tf2)

    r = curr.execute(sql)
    res = r.fetchall()



    # Залезть в таблицу и сравнить данные с глобальной переменной

    pass