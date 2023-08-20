# -*- coding: utf-8 -*-

class DepoBalance():

    blnc_USD = 0
    blnc_RUB = 0
    blnc_BTC = 0

    def setUSDblnc(self,x):
        DepoBalance.blnc_USD = x

    def setRUBblnc(self,x):
        DepoBalance.blnc_RUB = x

    def setBTCblnc(self,x):
        DepoBalance.blc_BTC = x

    def addUSDblnc(self, x):
        DepoBalance.blnc_USD = DepoBalance.blnc_USD + x

    def addRUBblnc(self, x):
        DepoBalance.blnc_RUB = DepoBalance.blnc_RUB + x

    def addBTCblnc(self, x):
        DepoBalance.blnc_BTC = DepoBalance.blnc_BTC + x

    def changeBlnc(self,x,type):
        if (type=='USD'):
            self.addUSDblnc(x)
        if (type == 'RUB'):
            self.addRUBblnc(x)
        if (type == 'BTC'):
            self.addBTCblnc(x)

    def totalBlnc(self,type):
        if (type=='USD'):
            return self.blnc_USD
        if (type == 'RUB'):
            return self.blnc_RUB
        if (type == 'BTC'):
            return self.blnc_BTC

    def sufficientUSDblnc(self,x):
        if (DepoBalance.blnc_USD >= x):
            return True
        else:
            return False

    def sufficientRUBblnc(self,x):
        if (DepoBalance.blnc_RUB >= x):
            return True
        else:
            return False

    def sufficientBTCblnc(self,x):
        if (DepoBalance.blnc_BTC >= x):
            return True
        else:
            return False
