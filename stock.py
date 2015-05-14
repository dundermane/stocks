##TODO
#Record 100d avg
#Record 5d avg
#Record 10d avg
#Record first and second derivative of 5d avg
#Record first and second derivative of 10d avg
#Record first and second derivative of 30d avg

from yahoo_finance import Share
import datetime

import string
import os

class Stock(object):
    def __init__(self, symbol, verbose=True):
        self.history_file=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', symbol + '.history')
        self.share = Share(symbol)
        self.symbol = symbol

    def check(self, verbose=True):
        self.share.refresh()
        if verbose: print self.share.get_info()['symbol'] + \
                          "\tvol: " + self.share.get_volume() + \
                          "\t\tprice: " + self.share.get_price() + \
                          "\t\ttime: " + self.share.get_trade_datetime()
        return {'share':'symbol'}
    def start_tracking_daemon(self, verbose=True):
        if verbose: print self.share.get_info()['symbol'] + " tracking daemon started"
    def update_history(self):
        print "Opening history file:  " + self.history_file
        history = open(self.history_file, 'a+')
        now = datetime.datetime.now().strftime('%Y-%m-%d')
        
        try:
            last_line = history.readlines()[-1]
        except:
            last_line = ''
        try:
            just_updating = True
            last_updated = last_line.split('\t')[0]
            yahoo_history = self.share.get_historical(last_updated, now)[::-1]
            if yahoo_history[-1]['Date'] == last_updated:
                print 'Data is current. No update for ' + self.symbol
                return
            print 'Updating. The current data will be appended'
        except:
            just_updating = False
            last_year = datetime.datetime.now() + datetime.timedelta(weeks=-21)
            last_year = last_year.strftime('%Y-%m-%d')
            yahoo_history = self.share.get_historical(last_year, now)[::-1]
            if len(yahoo_history)<1:
                return False

        categories = []; first = True
        for idx, item in enumerate(yahoo_history):
            try:
                if first: categories.append('Date')
                history.write(item['Date'] + '\t')

                if first: categories.append('Volume')
                history.write(item['Volume'] + '\t')

                if first: categories.append('Open')
                history.write(item['Open'] + '\t')

                if first: categories.append('Close')
                history.write(item['Close'] + '\t')

                if first: categories.append('High')
                history.write(item['High'] + '\t')

                if first: categories.append('Low')
                history.write(item['Low'] + '\t')

                #5 day average
                if first: categories.append('5_Day')
                num_avr = 5
                days = yahoo_history[max(idx-num_avr+1,0):idx+1]
                days = [float(day['Open']) for day in days]
                history.write(str(sum(days)/min(idx+1,num_avr)) + '\t')

                #10 day average
                if first: categories.append('10_Day')
                num_avr = 10
                days = yahoo_history[max(idx-num_avr+1,0):idx+1]
                days = [float(day['Open']) for day in days]
                history.write(str(sum(days)/min(idx+1,num_avr)) + '\t')

                #30 day average
                if first: categories.append('30_Day')
                num_avr = 30
                days = yahoo_history[max(idx-num_avr+1,0):idx+1]
                days = [float(day['Open']) for day in days]
                history.write(str(sum(days)/min(idx+1,num_avr)) + '\t')

                #80 day average
                if first: categories.append('80_Day')
                num_avr = 80
                days = yahoo_history[max(idx-num_avr+1,0):idx+1]
                days = [float(day['Open']) for day in days]
                history.write(str(sum(days)/min(idx+1,num_avr)) + '\t')

                #10 day average Volume
                if first: categories.append('10_Day_Vol')
                num_avr = 10
                days = yahoo_history[max(idx-num_avr+1,0):idx+1]
                days = [float(day['Volume']) for day in days]
                history.write(str(sum(days)/min(idx+1,num_avr)) + '\t')

                history.write('\n')
                first = False
            except:
                history.write('00-00-0000\t0\t0\t0\t0\t0\t0\t0\t0\t0\n')
        history.close()
        
        if not just_updating:
            #add categories to the top of the file
            cat_string = ''
            for cat in categories:
                cat_string += (cat + '\t')
            cat_string += '\n'
            with file(self.history_file, 'r') as original: data = original.read()
            with file(self.history_file, 'w') as modified: modified.write(cat_string + data)
        return True   

        
    def analyze(self):
        self.history_data = {}
        ##GET ALL THE HISTORY FOR THE STOCK
        history_file = open(self.history_file, 'r')
        history = history_file.readlines()
        history_file.close()
        categories = string.split(string.strip(history[0], '\n\t'),'\t')
        for col, cat in enumerate(categories):
            self.history_data[cat] = []
        for line in history[1:]:
            for col, cat in enumerate(categories):
                line_data = string.split(string.strip(line, '\n\t'),'\t')
                self.history_data[cat].append(line_data[col])

class piggy(object):
    def __init__(self, holdings=0,sim=False):
        from etradeGateway import Broker
        self.sim = sim
        self.holdings = holdings
        self.gains = 0
        self.wins = 0
        self.losses = 0
        self.open_trades = []
        self.closed_trades = []
        self.current_stock = {}
        
        self.broker = Broker()
        print self.broker.name + ' is set up as the broker for this strategy.'

        print 'Piggy Initiated.'
    def announce(self):
        print 'PIGGY: \tholdings: ' + str(self.holdings) + '\tgains: ' + str(self.gains) + '\tw:' + str(self.wins) + ' l:' + str(self.losses)
        print 'PIGGY: \tstocks: ' + str(self.current_stock)
    def buy(self, stock, n, date=None):
        print '\n'
        if self.sim:
            sale = {}
            i = stock.history_data['Date'].index(date)
            for key in stock.history_data.keys():
                sale[key] = stock.history_data[key][i]
            sale['Market'] = float(sale['Close'])
        else:
            print 'fake sale... .no functionality...'
        if n == 0:
            print color('Buying Zero Shares of ' + stock.symbol + '...?',6)
            self.announce()
            return
        print color(date + ': Buying ' + str(n) + ' shares @ $' + str(sale['Market']) + ' = ' + str(n * sale['Market']),6)
        self.holdings -= sale['Market'] * n + self.broker.tradeFee
        self.gains -= self.broker.tradeFee

        for tr in range(n):
            self.open_trades.insert(0,{ 'symbol':stock.symbol,
                                 'buy_date':date,
                                 'buy_price':sale['Market'],
                                 'sell_date':None,
                                 'sell_price':None})
        name = str(stock.symbol)
        self.current_stock[name] = self.current_stock.get(name,0) + n
        self.announce()


    def sell(self, stock, n=-1, date=None):
        print '\n'
        ##in simulation mode, take data from history
        if self.sim:
            sale = {}
            i = stock.history_data['Date'].index(date)
            for key in stock.history_data.keys():
                sale[key] = stock.history_data[key][i]
            sale['Market'] = float(sale['Close'])

        ##in deployment take data from actual market data
        else:
            print 'fake sale... .no functionality...'
        ##find the earliest instances of that stock which isnt sold
        if n < 0:
            is_done = int(self.current_stock[stock.symbol])
        elif n == 0:
            print 'Selling Zero Shares of ' + stock.symbol + '...?'
            return
        else:
            is_done = n
        n = is_done
        print color( date + ': Selling ' + str(n) + ' shares @ $' + str(sale['Market']) + ' = ' + str(n * sale['Market']),4)
        sale_gains = 0
        deleting = []
        for itr, trade in enumerate(self.open_trades):
            if is_done < 1:
                break
            #calculate gains, put money back in piggy
            if (trade['symbol'] == stock.symbol) and (trade['sell_date'] == None):
                #print self.open_trades.remove(trade)
                deleting.append(itr)
                trade['sell_date'] = date
                trade['sell_price'] = sale['Market']
                self.wins += (1 if trade['sell_price'] - trade['buy_price'] - (2*self.broker.tradeFee / n) > 0 else 0)
                self.losses += (1 if trade['sell_price'] - trade['buy_price'] - (2*self.broker.tradeFee / n) <= 0 else 0)
                self.holdings += (trade['sell_price'] - (self.broker.tradeFee / n))
                self.gains += (trade['sell_price'] - trade['buy_price'] - (self.broker.tradeFee / n))
                self.current_stock[trade['symbol']] = self.current_stock[trade['symbol']] - 1
                self.closed_trades.append(trade)
                is_done -= 1
            else:
                print 'i didnt make it'
        
        for d in reversed(deleting):
            self.open_trades.pop(d)
        
        self.announce()
        print 'open trades = ' + str(len(self.open_trades)) + ' closed trades = ' + str(len(self.closed_trades))
        
def color(s, color):
    return '\x1b\x5b1;3' + str(color) + ';40m' + str(s) + '\x1b\x5b0;37;40m' 

if __name__ == "__main__":
    google = Stock('TSLA')
    google.update_history()
    google.analyze() 
