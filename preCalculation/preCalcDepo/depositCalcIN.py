# -*- coding: utf-8 -*-


import PN3.deposit.depoMoneyInOut as depof
import PN3.function.exchangeFunction as exchf

import PN3.function.transacFunction as transf

#dtime = unix_to_date(p.get('timestamp'))

# GET PARAMETERS FEE DEPOSIT CURRENCY
# FOR USD RUB BTC

'''
r: rub
pr: price
'''

class InfoCalcToDep():



    def __init__(self):

        from PN3.configs.feeslimits.constant import com_in_pr_u ,com_in_f_u #Комиссия ввод USD
        from PN3.configs.feeslimits.constant import com_in_pr_r ,com_in_f_r #Комиссия ввод RUB

        # Комиссия на Ввод USD
        self.u_dep_prc = com_in_pr_u
        self.u_dep_fix = com_in_f_u

        # Комиссия на Ввод RUB
        self.r_dep_prc = com_in_pr_r
        self.r_dep_fix = com_in_f_r

    def setCurr(self,usd_b,usd_s):
        self.usd_b = usd_b
        self.usd_s= usd_s



    def setUsdPrmt(self,price_tobuy_btcusd,maker_taker,resedual_usd=0):
        self.price_tobuy_btcusd=price_tobuy_btcusd
        self.mk_tk_usd = maker_taker


    def setRubPrmt(self, price_tobuy_btcrub, maker_taker, resedual_rub=0):
        self.price_tobuy_btcrub = price_tobuy_btcrub
        self.mk_tk_rub = maker_taker


    def setDepoBalance(self,resedual_usd,resedual_rub,):
        self.resedual_usd = resedual_usd
        self.resedual_rub = resedual_rub


    def setX(self,x_usd=0,x_rub=0):  #Необходимо выбрать хотябы один из параметров
        self.x_usd = x_usd
        self.x_rub = x_rub





    def USD_DEPO_BTC(self):
        '''
        Перевод USD с карты
        и покупка BTC
        :return:
        '''

        if(self.x_usd==0):
            print("Для USD_DEPO_BTC не заданы параметры setUsdPrmt и setX")
            return

        # Покупка BTC за USD Первоначальная
        # на депозит
        x_depo = depof.X_to_DEPO(self.x_usd, self.u_dep_prc, self.u_dep_fix)  # перевод на депозит
        x_depo_sum = x_depo + self.resedual_usd
        btc_buy = transf.buyBTC(x_depo_sum, self.price_tobuy_btcusd, self.mk_tk_usd)  # покупка BTC максимальное кол-во
        btc = btc_buy['btc']
        x_resed = btc_buy['dx']  #остаток X

        return {'x':self.x_usd
                ,'x_depo':x_depo
                ,'x_depo_sum':x_depo_sum
                ,'btc':btc
                ,'x_resed':x_resed
                ,'price_u':self.price_tobuy_btcusd}


    # Второй вариант
    def USD_DEPO_BTC_v2(self):
        '''
        Перевод USD в RUB
        Перевод RUB на депозит
        Покупка BTC
        :return:
        '''

        if (self.x_usd == 0):
            print("Для USD_DEPO_BTC_v2 не заданы параметры setX")
            return

        if(self.price_tobuy_btcrub==0):
            print("Для USD_DEPO_BTC_v2 не заданы параметры setRubPrmt")

        rub = exchf.sellUSD(self.x_usd, self.usd_b)  # перевод USD в RUB до депозита

        x_depo = depof.X_to_DEPO(rub, self.r_dep_prc, self.r_dep_fix)  # перевод на депозит
        x_depo_sum = x_depo + self.resedual_rub
        btc_buy = transf.buyBTC(x_depo_sum, self.price_tobuy_btcrub, self.mk_tk_rub)  # покупка BTC
        btc = btc_buy['btc']
        x_resed = btc_buy['dx']  # остаток X

        return {'x': self.x_usd
                , 'x_exch':rub
                , 'x_depo': x_depo
                , 'x_depo_sum': x_depo_sum
                , 'btc': btc
                , 'x_resed': x_resed
                , 'price_r':self.price_tobuy_btcrub}




    # Функция Рубли на Депозит
    # rub - сумма, которая тратится
    def RUB_DEPO_BTC(self):
        '''
        Перевод RUB с карты
        и покупка BTC
        :return:
        '''

        # Покупка BTC за RUB Первый вариант
        x_depo = depof.X_to_DEPO(self.x_rub, self.r_dep_prc, self.r_dep_fix)  # RUB на депозите
        x_depo_sum = x_depo+self.resedual_rub
        btc_r = transf.buyBTC(x_depo_sum, self.price_tobuy_btcrub, self.mk_tk_rub)  # покупка BTC.
        btc = btc_r['btc']
        x_res = btc_r['dx']  # остаток X

        return {'x': self.x_rub
            , 'x_depo': x_depo
            , 'x_depo_sum': x_depo_sum
            , 'btc': btc
            , 'x_resed': x_res
            , 'price_r': self.price_tobuy_btcrub}





    # Второй вариант
    # Функция Рубли на Депозит
    # rub - сумма, которая тратится
    def RUB_DEPO_BTC_v2(self):
        '''
        Перевод RUB в USD
        Перевод USD на депозит
        Покупка BTC
        '''

        usd = exchf.buyUSD(self.x_rub, self.usd_s)  # покупка USD

        x_depo = depof.X_to_DEPO(usd, self.u_dep_prc, self.u_dep_fix)  # перевод на депозит
        x_depo_sum = x_depo+self.resedual_usd
        btc0_u = transf.buyBTC(x_depo_sum, self.price_tobuy_btcusd, self.mk_tk_usd)  # покупка BTC
        btc = btc0_u['btc']
        x_resed = btc0_u['dx']  # остаток X

        return {'x': self.x_rub
            , 'x_exch': usd
            , 'x_depo': x_depo
            , 'x_depo_sum': x_depo_sum
            , 'btc': btc
            , 'x_resed': x_resed
            , 'price_u':self.price_tobuy_btcusd}


#============XXXXX======================
    # Функция Деньги на Депозит
    def X_DEPO_BTC(self,type='USD'):
        '''
        Перевод USD с карты
        и покупка BTC
        :return:
        '''

        #init
        x = 1
        dep_prc = 1
        dep_fix = 0
        resedual_x = 0
        price_tobuy_btc = 1
        mk_tk = 0

        if(type=='USD'):
            x=self.x_usd
            dep_prc=self.u_dep_prc
            dep_fix=self.u_dep_fix
            resedual_x = self.resedual_usd
            price_tobuy_btc = self.price_tobuy_btcusd
            mk_tk = self.mk_tk_usd

            if (self.x_usd == 0):
                print("Для USD_DEPO_BTC не заданы параметры setUsdPrmt и setX")
                return

        if('type'=='RUB'):
            x = self.x_rub
            dep_prc = self.r_dep_prc
            dep_fix = self.r_dep_fix
            resedual_x = self.resedual_rub
            price_tobuy_btc = self.price_tobuy_btcrub
            mk_tk = self.mk_tk_rub

            if (self.x_rub == 0):
                print("Для RUB_DEPO_BTC не заданы параметры setRubPrmt и setX")
                return

        # Покупка BTC за USD Первоначальная
        # на депозит
        x_depo = depof.X_to_DEPO(x, dep_prc, dep_fix)  # перевод на депозит
        x_depo_sum = x_depo + resedual_x
        btc_buy = transf.buyBTC(x_depo_sum, price_tobuy_btc, mk_tk)  # покупка BTC максимальное кол-во
        btc = btc_buy['btc']
        x_resed = btc_buy['dx']  #остаток X

        return {'x':x
                ,'x_depo':x_depo
                ,'x_depo_sum':x_depo_sum
                ,'btc':btc
                ,'x_resed':x_resed
                ,'price':price_tobuy_btc}



    # Второй вариант
    def X_DEPO_BTC_v2(self,type='USD'):
        '''
        Перевод USD в RUB
        Перевод RUB на депозит
        Покупка BTC
        :return:
        '''

        #XB - валюта 1 базовая
        #XQ - валюта 2 (currency)


        # init
        x = 1
        dep_prc = 1
        dep_fix = 0
        resedual_x = 0
        price_tobuy_btc = 1
        mk_tk = 0

        if (type == 'USD'):
            x0 = self.x_usd
            dep_prc = self.u_dep_prc
            dep_fix = self.u_dep_fix
            resedual_x = self.resedual_usd
            price_tobuy_btc = self.price_tobuy_btcusd
            mk_tk = self.mk_tk_usd

            if (self.x_usd == 0):
                print("Для USD_DEPO_BTC_v2 не заданы параметры setX")
                return

            if (self.price_tobuy_btcrub == 0):
                print("Для USD_DEPO_BTC_v2 не заданы параметры setRubPrmt")

            x = exchf.sellUSD(x, self.usd_b)  # перевод USD в RUB до депозита

        if ('type' == 'RUB'):
            x0 = self.x_rub
            dep_prc = self.r_dep_prc
            dep_fix = self.r_dep_fix
            resedual_x = self.resedual_rub
            price_tobuy_btc = self.price_tobuy_btcrub
            mk_tk = self.mk_tk_rub

            if (self.x_rub == 0):
                print("Для RUB_DEPO_BTC_v2 не заданы параметры setX")
                return

            if (self.price_tobuy_btcusd == 0):
                print("Для RUB_DEPO_BTC_v2 не заданы параметры setUsdPrmt")

            x = exchf.buyUSD(x, self.usd_s)  # перевод RUB в USD до депозита




        x_depo = depof.X_to_DEPO(x, dep_prc, dep_fix)  # перевод на депозит
        x_depo_sum = x_depo + resedual_x
        btc_buy = transf.buyBTC(x_depo_sum, price_tobuy_btc, mk_tk)  # покупка BTC
        btc = btc_buy['btc']
        x_resed = btc_buy['dx']  # остаток X

        return {'x': self.x_usd
                , 'x_exch':x
                , 'x_depo': x_depo
                , 'x_depo_sum': x_depo_sum
                , 'btc': btc
                , 'x_resed': x_resed
                , 'price':price_tobuy_btc}





