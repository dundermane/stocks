#Stragegy File

###INTERSECTING WATERFALL STRATEGY
###When 5,10,30 day moving averages intersect and make a triangle
## with 30 day on top, 10 day in middle and 5 day on the bottom,
## Buy at when the percent increase from MARKET to 30_DAY reaches threshold  UNLESS the 5 day average exceeds the 10 day or 30 day.

## Sell when the 5 Day decreases

import os
import random
import datetime
from stock import Stock, piggy
from sys import argv
from sym2 import symbols

def strategy(symbol):
    stock = Stock(symbol)
    stock.update_history()
    stock.analyze()
    buy_dates = []
    buy_prices = []
    sell_dates = []
    sell_prices = []
    wiggly = piggy(sim=True,holdings=300)

    buy_flag = False
    staleness = 0
    sell_flag = False
    earn_flag = False
    last_bought = 0
    for itx, date in enumerate(stock.history_data['Date']):

        ptrn_lookahead = 5
        prox_thres = .02 * float(stock.history_data['Close'][itx])
        if float(stock.history_data['30_Day'][itx-ptrn_lookahead]) - prox_thres <= float(stock.history_data['10_Day'][itx-ptrn_lookahead]) <= float(stock.history_data['30_Day'][itx-ptrn_lookahead]) + prox_thres\
        and float(stock.history_data['30_Day'][itx-ptrn_lookahead]) - prox_thres <= float(stock.history_data['5_Day'][itx-ptrn_lookahead]) <= float(stock.history_data['30_Day'][itx-ptrn_lookahead]) + prox_thres\
        and float(stock.history_data['30_Day'][itx]) > float(stock.history_data['10_Day'][itx]) > float(stock.history_data['5_Day'][itx]):
            buy_flag = True
            staleness = 0
            
        gains_thres = 1.1
        buy_slop_err = 0.001
        if buy_flag \
        and float(stock.history_data['5_Day'][itx]) * gains_thres < float(stock.history_data['30_Day'][itx]) \
        and float(stock.history_data['5_Day'][itx]) > float(stock.history_data['5_Day'][itx-1]) * (1+buy_slop_err):  ##Once there is enough margin betweet the 5 day and 30 day, buy
            buy_dates.append(date)
            buy_prices.append(float(stock.history_data['Close'][itx]))
            buy_flag = False
            staleness = 0
            earn_flag = True
            num = int(wiggly.holdings * .5 / float(stock.history_data['Close'][itx]))
            wiggly.buy(stock,num,date=date)
            buy_dates.append(date)
            buy_prices.append(float(stock.history_data['Close'][itx]))
            last_bought = itx
 
        if (buy_flag
        and staleness > 20
        or (float(stock.history_data['5_Day'][itx]) > float(stock.history_data['10_Day'][itx]))):
            buy_flag = False
            staleness = 0

        earn_thres = 1.2
        if (earn_flag 
        and float(stock.history_data['10_Day'][itx]) > float(stock.history_data['10_Day'][itx-1]) * (1+buy_slop_err)
        and float(stock.history_data['Close'][itx]) > float(stock.history_data['5_Day'][last_bought]) * earn_thres): ## and the 5 Day is increasing, then throw the EARNING flag
            earn_flag = False
            sell_flag = True

        ceiling = .5
        if (sell_flag
        and float(stock.history_data['5_Day'][itx]) < float(stock.history_data['5_Day'][itx-1])) \
        or (sell_flag and float(stock.history_data['5_Day'][itx]) > float(stock.history_data['5_Day'][itx]) * (ceiling + 1)):
            sell_flag = False
            wiggly.sell(stock,-1,date=date)
            sell_dates.append(date)
            sell_prices.append(float(stock.history_data['Close'][itx]))

        staleness += 1


    if wiggly.current_stock[stock.symbol] > 0:
        print "\n\n#####Closing Out######"
        wiggly.sell(stock,-1,date=date)

    ##Make a plot
    import matplotlib.pyplot as plt
    import matplotlib.dates as plotdate
    import matplotlib.lines as line
    import numpy as np

    months    = plotdate.MonthLocator()   # every year
    days   = plotdate.DayLocator()  # every month
    monthsFmt = plotdate.DateFormatter('%m %d')

    fig, ax = plt.subplots()
    #ax2 = ax.twinx()
    t = [datetime.datetime.strptime(date,'%Y-%m-%d') for date in stock.history_data['Date']]
    ax.axis('auto')

    # format the ticks
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(monthsFmt)
    ax.xaxis.set_minor_locator(days)
    fig.autofmt_xdate()

    ax.plot(t, stock.history_data['5_Day'], '#0000FF')
    ax.plot(t, stock.history_data['10_Day'], '#5555FF')
    ax.plot(t, stock.history_data['30_Day'], '#9999FF')
    #ax.plot(t, stock.history_data['80_Day'], '#AAAAFF')
    #ax2.plot(t, stock.history_data['Volume'], '#CCFFCC')
    #ax2.plot(t, stock.history_data['10_Day_Vol'], '#88AA88')
    
    buy_dates = [datetime.datetime.strptime(date,'%Y-%m-%d') for date in buy_dates]
    ax.plot(buy_dates,buy_prices, 'g|',ms=100)

    sell_dates = [datetime.datetime.strptime(date,'%Y-%m-%d') for date in sell_dates]
    ax.plot(sell_dates,sell_prices, 'b|',ms=100)

    ax.plot(t, stock.history_data['Close'], 'r-')
    plt.title(stock.symbol)
    #ax.text(t[12], 250, 'hello')
    plt.show()
    return {'gains': wiggly.gains, 'symbol': stock.symbol, 'initial_value':stock.history_data['Open'][1]}


if __name__ == '__main__':

    if len(argv) > 1:
        
        for arg in argv[1:]:

            try:
                strategy(arg)
            except:
                exit()

    else:
        final_earnings = []
        rando = random.randint(0,len(symbols['nasdaq'])-20)
        for symbol in symbols['nasdaq'][rando:rando+20]:
            try:
                final_earnings.append(strategy(symbol))

            except:
                pass


        i = 0
        while os.path.exists("results/test%s.csv" % i):
            i += 1

        f = open('results/test%s.csv' % i,'w+')
        f.write('Test Results\n')
        f.write('Symbol\tInitial\tGains\n')
        for earnings in final_earnings:
            f.write(earnings['symbol'] + '\t')
            f.write(str(earnings['initial_value']) + '\t')
            f.write(str(earnings['gains']) + '\t\n')

        f.close()





