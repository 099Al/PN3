# -*- coding: utf-8 -*-

import visualization.dataPrepare as dp
import plotly as ply
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots

from datetime import datetime


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
        x_i = datetime.strptime(x_si, '%Y-%m-%d %H:%M:%S')

        x.append(x_i)
        if(tp=='sell'):
            x_s.append(x_i)
            sell.append(i[3])
        elif(tp=='buy'):
            x_b.append(x_i)
            buy.append(i[3])

    trace1 = go.Scatter(
        x=x_s,
        y=sell,
        mode='lines+markers',
        name='s'
    )

    trace2 = go.Scatter(
        x=x_b,
        y=buy,
        mode='lines+markers',
        name='b',
        color='green'
    )

    data = [trace1,trace2]

    ply.offline.plot(data, filename='line-mode')
    #fig = px.scatter(x=x_s, y=sell)
    #fig.show()

def plotTiksSellBuy():
    pass



def plotTiksAndResults():
    pass



def testPlot():
    x1=[1,2,3,4,11,13,15]
    y1 = [1, 2, 1, 2, 1, 2, 3]
    x2 = [3, 4, 5, 6, 9, 14, 21]
    y2 = [3, 4, 5, 4, 3, 4, 5]

    trace1 = go.Scatter(
        x=x1,
        y=y1,
        mode='lines+markers',
        name='s'
    )

    trace2 = go.Scatter(
        x=x2,
        y=y2,
        mode='lines+markers',
        name='s'
    )

    data = [trace1, trace2]

    ply.offline.plot(data, filename='line-mode')



if __name__ == '__main__':
    date_time = datetime.fromtimestamp(1549181957)
    date_time2 = datetime.fromtimestamp(1549181957 + 50000)

    #plotTiksPeriod(date_time,date_time2)

    testPlot()

    #print(date_time)