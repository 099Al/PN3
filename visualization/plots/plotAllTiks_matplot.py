# -*- coding: utf-8 -*-

import visualization.dataPrepare as dp
import datetime
import matplotlib.pyplot as plt
import util.util_datetime as utl
from mpl_finance import candlestick_ohlc
import mplfinance as fplt



def plotTiksPeriod(dateFrom,dateTo):


    res = dp.dataTiks(date_time, date_time2)

    # x axis values
    x=[]
    x_s = []
    x_b = []
    sell = []
    buy = []
    print(res)
    #tid,type,amount,price,unixdate,date
    for i in res:
        tp = i[1]
        fmts = ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S']
        x_si = i[5]
        x_i = datetime.datetime.strptime(x_si, '%Y-%m-%d %H:%M:%S')

        x.append(x_i)
        if(tp=='sell'):
            x_s.append(x_i)
            sell.append(i[3])
        elif(tp=='buy'):
            x_b.append(x_i)
            buy.append(i[3])

    fig = plt.figure()
    ax = fig.add_subplot(111)  # We'll explain the "111" later. Basically, 1 row and 1 column.

    ax.scatter(x_s, sell, marker='h', s=20, color='red', label='sell')
    ax.scatter(x_b, buy, marker='o', s=20, color='green', label='buy')



    candlestick_ohlc(ax, ohlc.values, width=0.6, colorup='green', colordown='red', alpha=0.8)



    fig2 = plt.figure()

    ax_1 = fig2.add_subplot(2, 2, 1)
    ax_2 = fig2.add_subplot(2, 2, 2)
    ax_3 = fig2.add_subplot(2, 2, 3)
    ax_4 = fig2.add_subplot(2, 2, 4)

    ax_1.set(title='ax_1', xticks=[], yticks=[])
    ax_2.set(title='ax_2', xticks=[], yticks=[])
    ax_3.set(title='ax_3', xticks=[], yticks=[])
    ax_4.set(title='ax_4', xticks=[], yticks=[])

    #x.append('2019-02-03 11:33:39')
    x = list(set(x))


    #plt.xticks(x,rotation='vertical')

    plt.show()



'''
    x1=['1','2','6','5']
    y1=[100,120,130,100]
    x2=['3','5','7','8']
    y2=[125,105,135,140]
    x=x1+x2
    x.append('4')
    x.append('11')
    plt.scatter(x1,y1,color='red')
    plt.scatter(x2,y2,color='green')
    plt.xticks(x)
'''


def plotTiksSellBuy():
    pass



def plotTiksAndResults():
    pass



if __name__ == '__main__':
    date_time = datetime.datetime.fromtimestamp(1549181957)
    date_time2 = datetime.datetime.fromtimestamp(1549181957 + 1000)

    plotTiksPeriod(date_time,date_time2)
