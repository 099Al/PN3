# -*- coding: utf-8 -*-



#Пока не используется
# Информация вычисляетсянапрямую

class InfoPreCalcTransac():

    def __init__(self):
        '''  #Эти параметры не нужны здесь

        from feeslimits.constant import com_out_pr_u,com_out_f_u #Комиссия ввод USD
        from feeslimits.constant import com_out_pr_r,com_out_f_r #Комиссия ввод RUB
        from feeslimits.constant import limit_usd,limit_rub


        self.u_dep_prc = com_out_pr_u
        self.u_dep_fix = com_out_f_u

        self.r_dep_prc = com_out_pr_r
        self.r_dep_fix = com_out_f_r


        self.limit_usd=limit_usd
        self.limit_rub=limit_rub

    def setCurr(self,usd_b,usd_s):
        self.usd_b = usd_b
        self.usd_s= usd_s

    def setOldCurr(self,usd_b,usd_s):
        self.old_usd_b = usd_b
        self.old_usd_s= usd_s
    '''


    def setUsdPrmt(self,price_btcusd,maker_taker):
        self.price_btcusd=price_btcusd
        self.mk_tk_usd = maker_taker

    def setRubPrmt(self, price_btcrub, maker_taker):
        self.price_btcrub = price_btcrub
        self.mk_tk_rub = maker_taker

    # Заполнение депозита
    def setDepoBalance(self, x_usd=0, x_rub=0, btc=0):
            self.x_usd = x_usd
            self.x_rub = x_rub
            self.btc = btc

