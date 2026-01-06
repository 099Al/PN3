# -*- coding: utf-8 -*-


def info_USD_OUT(class_info_out):
    res = class_info_out.USD_OUT()

    print()
    print('USD на депозите:', res['x'])
    print('Довнесли с карты:', res['add_usd'], 'Ушло на депозит:',res['add_usd_dep'])
    print('USD на Карте:', res['usd_out'])
    print('После перевода в RUB:', res['rub'])
    print('После перевода в RUB(по старому курсу):', res['rub2'])
    print('------------------------------------------')
    return res

def info_RUB_OUT(class_info_out):
    res = class_info_out.RUB_OUT()
    #res = class_info_out.X_OUT('RUB') заменить на эту функцию

    print()
    print('USD на депозите:', res['x'])
    print('Довнесли с карты:', res['add_rub'], 'Ушло на депозит:',res['add_rub_x'])
    print('USD на Карте:', res['usd_out'])
    print('После перевода в RUB:', res['usd'])
    print('После перевода в RUB(по старому курсу):', res['usd2'])
    print('------------------------------------------')
    return res

def info_USD_to_BTC_sell_to_RUB_and_OUT(class_info_out):
    res = class_info_out.USD_btc_rub_OUT()

    print()
    print('USD на депозите:', res['usd'])
    print('BTC(с остатком):',res['btc_sum'],'BTC(куплено):',res['btc_max'],'mk_tk:максимальный')
    print('BTC продано:',res['btc_pre'],'BTC остаток',res['btc_sum']-res['btc_pre'],'mk_tk:',res['mk_tk_rub'])
    print('USD остаток:',res['dx'])
    print('RUB получено:',res['rub'],'Добавлено на деп',res['rub_add'],'Было на остатке:',res['rub_resed'])
    print('RUB выведено:',res['rub_out'])
    print('После перевода в USD:', res['usd_r'])
    print('После перевода в USD(по старому курсу):', res['usd_r_old'])
    print('------------------------------------------')


def info_RUB_to_BTC_sell_to_USD_and_OUT(class_info_out):
    res = class_info_out.RUB_btc_usd_OUT()

    print()
    print('RUB на депозите:', res['rub'])
    print('BTC(с остатком):',res['btc_sum'],'BTC(куплено):',res['btc_max'])
    print('BTC продано:',res['btc_pre'],'BTC остаток',res['btc_sum']-res['btc_pre'],'RUB остаток:',res['dx'])
    print('USD получено:',res['usd'],'Добавлено на деп',res['usd_add'],'Было на остатке:',res['usd_resed'])
    print('USD выведено:',res['usd_out'])
    print('После перевода в RUB:', res['rub_u'])
    print('После перевода в RUB(по старому курсу):', res['rub_u2'])
    print('------------------------------------------')



def info_BTC_to_USD_OUT(class_info_out):
    res = class_info_out.BTC_usd_OUT()

    print()
    print('BTC на Депозите:',res['btc'])
    print('BTC продано:',res['btcsell'],'mk_tk:',res['mk_tk'],'BTC остаток:',res['btc']-res['btcsell'])
    print('USD на Депозите(с учетом остатка):',res['usd_sum'],'USD получено при продаже:',res['usd'])
    print('USD выведено:',res['u_out'])
    print('После перевода в RUB:', res['rub_u'])
    print('После перевода в RUB(по старому курсу):', res['rub_u2'])
    print('------------------------------------------')


def info_BTC_to_RUB_OUT(class_info_out):
    res = class_info_out.BTC_rub_OUT()

    print()
    print('BTC на Депозите:',res['btc'])
    print('BTC продано:',res['btcsell'],'mk_tk:',res['mk_tk'],'BTC остаток:',res['btc']-res['btcsell'])
    print('RUB на Депозите(с учетом остатка):',res['rub_sum'],'USD получено при продаже:',res['rub'])
    print('RUB выведено:',res['rub_out'])
    print('После перевода в USD:', res['usd_r'])
    print('После перевода в USD(по старому курсу):', res['usd_r2'])
    print('------------------------------------------')


def info_IN_OUT(class_info_out,X,price_tobuy,price_tosell,type_x='RUB',type_y='RUB'):
    res = class_info_out.X_on_DEPOSIT_Y_out(X,price_tobuy,price_tosell,type_x,type_y)
    print()
    print('--IN_OUT----')
    print('Сумма ввода:',X,'type_x',' Будет на депозите',res['x_depo'])
    print('BTC:',res['btc'], 'По цене:',price_tobuy)
    print('После продажи BTC:',res['y_depo'],'По цене:',price_tosell)
    print('Выведено:',res['y_out'])
    if(type_x==type_y):
        print('Разница цен:',res['dp'],' ',res['dp']/price_tobuy,'%')


def info_Add_RUB_to_OUT(class_info_out):
    res = class_info_out.add_RUB_rub_out(depo_rub=-1)
    print('Необходимо довнести:',res)


def info_Need_X_on_DEPOSIT_to_GET_X0(class_info_out,x_out,type):

    x = class_info_out.X_on_DEPOSIT_to_OUT_X0(x_out, type)
    resB = class_info_out.BTC_on_DEPOSIT_to_GET_X0(x,type)

    print('Необходимо на Депозите:',x,type)
    print('или Для этого необходимо',resB['btc'],'BTC на Депозите. Продать по ',resB['price'])
    print()

    if(type=='RUB'):

        exch_price = class_info_out.usd_b
        def exch_curr(x, exch_price):
            import functions.exchange as exchf
            return exchf.sellUSD_revers(x, exch_price)

        xcur = exch_curr(x_out, exch_price) #надо продать xcur по цене usd_b, чтобы получить x_out
        xcurr_dep = class_info_out.X_on_DEPOSIT_to_OUT_X0(xcur, 'USD')
        resB2 = class_info_out.BTC_on_DEPOSIT_to_GET_X0(xcurr_dep, 'USD')

        print('Или необходимо на Депозите:', xcurr_dep , 'USD')
        print('Для этого необходимо:', resB2['btc'], 'BTC на Депозите. Продать по ', resB2['price'])
        print('Выведится:',xcur,'USD')
        print('Эту сумму надо обменятьпо курсу:',exch_price)

    if (type == 'USD'):
        exch_price = class_info_out.usd_s

        def exch_curr(x, exch_price):
            import functions.exchange as exchf
            return exchf.buyUSD_revers(x, exch_price)

        xcur = exch_curr(x_out, exch_price)  #надо купить x_out по цене usd_s
        xcurr_dep = class_info_out.X_on_DEPOSIT_to_OUT_X0(xcur, 'RUB')
        resB2 = class_info_out.BTC_on_DEPOSIT_to_GET_X0(xcurr_dep, 'RUB')

        print('Или необходимо на Депозите:', xcurr_dep, 'RUB')
        print('Для этого необходимо:', resB2['btc'], 'BTC на Депозите. Продать по ', resB2['price'])
        print('Выведится:', xcur, 'RUB')
        print('Эту сумму надо обменятьпо курсу:', exch_price)

if __name__ == '__main__':

    # Параметры
    from deposit.feeslimits.constant import taker, mk_tk
    from functions.info.infocalc.depositCalcOUT import InfoCalcFromDep
    from functions.price import last_prices, current_price


    # Комиссии при транзакции
    mk_tk_usd = mk_tk
    mk_tk_rub = mk_tk

    #Старый курс валют
    old_bank_sell_usd = 66.5
    old_bank_buy_usd = 66.5       #сделать обработку в случае 0


    # Курсы валют
    bank_sell_usd = 74.15
    bank_buy_usd = 73.4

    # Состояние депозита
    x_usd_depo = 100
    x_rub_depo = 0
    btc_depo = 0 #0.00416178

    # Довнести с карты
    x_usd = 0
    x_rub = 0

    # Цена
    p_u_l = last_prices('BTC', 'USD', delta_price=0)
    p_r_l = last_prices('BTC', 'RUB', delta_price=0)

    p_u_a = current_price('BTC', 'USD')['asks']  # При быстрой покупке, берем по цене, за которую  продают  комиссия taker
    p_r_a = current_price('BTC', 'RUB')['asks']  # При быстрой покупке, берем по цене, за которую  продают

    p_u_b = current_price('BTC', 'USD')['bids']  # При быстрой покупке, берем по цене, за которую  продают  комиссия taker
    p_r_b = current_price('BTC', 'RUB')['bids']  # При быстрой покупке, берем по цене, за которую  продают

    p_u=10000
    p_r=p_u*bank_sell_usd

    print('Цена для расчета:', p_u, 'usd', 'last:', p_u_l, 'asks', p_u_a, 'bids', p_u_b, 'delta:', p_u_a - p_u_b)
    print('Цена для расчета:', p_r, 'usd', 'last:', p_r_l, 'asks', p_r_a, 'bids', p_r_b, 'delta:', p_r_a - p_r_b)


    #Класс для подсчета информаци
    cl_fromDep = InfoCalcFromDep()
    cl_fromDep.setCurr(bank_buy_usd,bank_sell_usd)
    cl_fromDep.setOldCurr(old_bank_buy_usd,old_bank_sell_usd)
    cl_fromDep.setUsdPrmt(price_tosell_btcusd=p_u_a,price_tobuy_btcusd=p_u_b,maker_taker=mk_tk_usd,taker=taker)  #Необходимо менять цену в рассчетах
    cl_fromDep.setRubPrmt(price_tosell_btcrub=p_r_b, price_tobuy_btcrub=p_r_a,maker_taker=mk_tk_rub)                               #Необходимо менять цену в рассчетах
    cl_fromDep.setDepoBalance(x_usd=x_usd_depo,x_rub=x_rub_depo,btc=btc_depo)
    cl_fromDep.setAddX(add_usd=x_usd,add_rub=x_rub)



    #Вывод информации
    info_USD_OUT(cl_fromDep)
    #info_RUB_OUT(cl_fromDep)

    info_USD_to_BTC_sell_to_RUB_and_OUT(cl_fromDep)
    #info_RUB_to_BTC_sell_to_USD_and_OUT(cl_fromDep)

    #info_BTC_to_USD_OUT(cl_fromDep)
    #info_BTC_to_RUB_OUT(cl_fromDep)

    #info_Add_RUB_to_OUT(cl_fromDep)
    #info_Need_X_on_DEPOSIT_to_GET_X0(cl_fromDep, 5000, 'RUB')

    #info_IN_OUT(cl_fromDep, 5000/63.9, p_u_a, 8000*63.9, type_x='USD', type_y='RUB')

