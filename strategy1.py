##Stragegy File
import datetime
from stock import Stock, piggy
from sys import argv


if __name__ == "__main__":
    if len(argv) > 1:
        if argv[1] == '--simulate':
            if len(argv) < 3:
                print 'Please specify symbol'
                exit()
            symbol = argv[2]
            stock = Stock(symbol)
            stock.update_history()
            stock.analyze()
            buy_dates = []
            buy_prices = []
            sell_dates = []
            sell_prices = []
            wiggly = piggy(sim=True,holdings=300)

            for itx, date in enumerate(stock.history_data['Date']):

                ## Sell if the 10_day drops
                trigger_drop = .02
                trigger_starved = 1.5
                if float(stock.history_data['10_Day'][itx]) <= float(stock.history_data['10_Day'][itx-5]) - trigger_drop*float(stock.history_data['10_Day'][itx]) \
                and bool(wiggly.current_stock.get(stock.symbol)) and wiggly.current_stock[stock.symbol] >= 1:
                    wiggly.sell(stock,-1,date=date)
                    sell_dates.append(date)
                    sell_prices.append(float(stock.history_data['Close'][itx]))

                ## Buy if the 10_day busts through the 30_day
                if (float(stock.history_data['10_Day'][itx]) > float(stock.history_data['30_Day'][itx])      ## If the 10 Day was below the 30 day
                and float(stock.history_data['10_Day'][itx-1]) < float(stock.history_data['30_Day'][itx-1])  ## and now the 10 day is above the 30
                and float(stock.history_data['Open'][itx-1]) > float(stock.history_data['10_Day'][itx-1])       ## and the current value is above the 10 day
                and float(stock.history_data['Close'][itx]) < (float(stock.history_data['30_Day'][itx]) * trigger_starved)
                and wiggly.holdings > float(stock.history_data['Close'][itx]) + wiggly.broker.tradeFee):     ## and I have enough money
                     num = int(wiggly.holdings * .5 / float(stock.history_data['Close'][itx]))
                     wiggly.buy(stock,num,date=date)
                     buy_dates.append(date)
                     buy_prices.append(float(stock.history_data['Close'][itx]))

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

            ax.plot(t, stock.history_data['Open'], 'r-')
            plt.title(stock.symbol)
            #ax.text(t[12], 250, 'hello')
            plt.show()

        elif argv[1] == '--deploy':
            print 'Sorry, Deploy function not ready yet.  Try some more simulations'
        elif argv[1] == '--help' or argv[1] == '-h':
            print 'Sorry, can\'t help you yet'
        else:
            print 'Sorry, ' + argv[1] + 'is not a valid argument.  Try \'-h\' for help'


    else:
        print 'Invalid Number of Arguments'
        print 'try \"--help\" for information on this module'
