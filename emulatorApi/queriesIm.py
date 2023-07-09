# -*- coding: utf-8 -*-

import configparser

conf_data = configparser.ConfigParser()
conf_data.read('../configs/config.ini')
cex_history_tbl = conf_data['SRC']['SRC_HISTORY']

# имитация получения данных с CEX
# Получение 1000 последних тиков на заданную дату
def f_history_tic_imitation(connect, curr_dttime):
    """
    Получение новых данных (эмуляция)

    :param connect:
    :param datetm:
    :return:

    """
    # WHERE unixdate - дата в формате unixdate
    curr = connect.cursor()

    # Получение 1000 последних тиков на заданную дату
    #Способ 1
    sql = "WITH t " \
          "as (" \
          "SELECT MAX(tid) m_tid " \
          "FROM "+cex_history_tbl+" " \
          "WHERE unixdate <= '{dt}'" \
          ") " \
          "SELECT tid,type,unixdate,amount,price " \
          "FROM "+cex_history_tbl+" " \
          "WHERE tid <= (select m_tid from t) " \
          "AND tid > (select m_tid from t)-1000 " \
          "ORDER BY tid desc "

    sql = sql.format(dt=curr_dttime)

    #Способ 2
    sql_2 = "SELECT tid,type,unixdate,amount,price " \
               "FROM "+cex_history_tbl+" " \
               "WHERE  unixdate < '{dt}' " \
               "ORDER BY tid desc limit 1000"
    sql_2 = sql_2.format(dt=curr_dttime)

    print(sql_2)

    r = curr.execute(sql_2)
    res = r.fetchall()

    #Преобразование результата. Чтобы данные выдавались как после запроса к CEX.
    res_dict = [dict(zip(('tid','type','date','amount','price'),x)) for x in res]

    return res_dict