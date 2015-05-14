from __future__ import print_function
from yahoo_finance import Share
from os.path import realpath, join, dirname, isfile
import Queue, threading
import sys, os, subprocess
import time
import urllib2
import string
import pprint
from datetime import datetime, timedelta



threads = []

symbols = {}
symbols['nyse'] = []
symbols['nasdaq'] = []
symbols['amex'] = []
symbols['removed'] = []

nyse_url = 'http://www.advfn.com/nyse/newyorkstockexchange.asp?companies='
nasdaq_url = 'http://www.advfn.com/nasdaq/nasdaq.asp?companies='
amex_url = 'http://www.advfn.com/amex/americanstockexchange.asp?companies='

today = datetime.strftime(datetime.now(), '%Y-%m-%d')
yesterday = datetime.strftime(datetime.today()-timedelta(days=1),'%Y-%m-%d')


def progress(st):
    sys.stderr.write(' PROGRESS: {0} imported\r'.format(st))
    sys.stderr.flush()

def error(*objs):
    print("ERROR: ", *objs, file=sys.stderr)

def warning(*objs):
    print("WARNING: ", *objs, file=sys.stderr)

def stupdate(str):
    sys.stderr.write("UPDATE: {0}\n".format(str))
    #print("UPDATE: ", *objs, file=sys.stderr)

def isdate(d):
    try:
        datetime.strptime(d, '%Y-%m-%d')
        return True
    except ValueError:
        return False
    except:
        error('unknown error: the bitch gave me ' + sys.exc_info()[0])

def get_symbols(url, alpha, exchange):
    req = urllib2.Request(url+alpha)
    res = urllib2.urlopen(req)

    for line in res.readlines():
        if 'class=\"ts0\"' in line or 'class=\"ts1\"' in line:
            first = 'stockprice='
            last = '\" title'
            start = line.index( first ) + len( first )
            end = line.index( last, start )
            symbols[exchange].append(line[start:end])

def get_history(symbol, exchange):
    ## Check if symbol is in our database
    path = join(dirname(realpath(__file__)),'data', exchange, symbol + '.history')
    subprocess.call("touch " + path , shell=True)
    last_line = subprocess.Popen("tail -n1 "+ path, shell=True, stdout=subprocess.PIPE).stdout.read()
    last_date = last_line.split('\t')[0] 

    if isdate(last_date):
        if yesterday == last_date:
            stupdate( symbol + ' already up to date.')
            del path
            del last_date
            return True
        stupdate( symbol + ' updating..')
        share = Share(symbol)
    else:
        
        subprocess.call("echo \"Date\\tVolume\\tOpen\\tClose\\tHigh\\tLow\" > " + path, shell=True)
        try:
            share = Share(symbol)
            last_date = share.get_info()['start']
        except:
            last_date = '2000-01-04'

    dates = [last_date, '2000-01-04', '2005-01-04', '2010-01-04']
    for i, date in enumerate(dates):
        try:
            yahoo_history = share.get_historical(date, today)
            break
        except:
            error(sys.exc_info()[0])
            error('Yahoo error, inputs => date: ' + date + ' symbol: ' + symbol)
        if i == 3: return False
    
    bad_line = 0
    for day in yahoo_history[-2::-1]:
        try:
            echo = (
            day['Date'] + '\\t' +
            day['Volume'] + '\\t' +
            day['Open'] + '\\t' +
            day['Close'] + '\\t' +
            day['High'] + '\\t' +
            day['Low'])
            subprocess.call( "echo \"{0}\" >> {1}".format(echo, path), shell=True)
            del echo
        except:
            error(sys.exc_info()[0])
            del day
            if bad_line > 4:
                error(" aborting... bad symbol data: "+ symbol)
                global bad_symbols
                bad_symbols.append(symbol)
                del share
                del dates
                del exchange
                del bad_line
                del path
                del yahoo_history
                error(locals())
                return False
            bad_line += 1
            continue
    del yahoo_history
    del share
    return True

def bee():
    while True:
        symbol, exchange = q.get()
        get_history(symbol, exchange)
        q.task_done()



####
#### Go through that site that has every stock listed, and get a huge list.

stupdate('Geting all of the stock symbols')

for alpha in string.ascii_uppercase:
    t = threading.Thread(target=get_symbols, args=(nyse_url,alpha,'nyse'))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

for alpha in string.ascii_uppercase:
    t = threading.Thread(target=get_symbols, args=(nasdaq_url,alpha,'nasdaq'))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

for alpha in string.ascii_uppercase:
    t = threading.Thread(target=get_symbols, args=(amex_url,alpha,'amex'))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

#### Get a huge list Ended.
#### 

stupdate('All symbols collected.')

####
#### Go through that list and pick out the duds and get ALL OF THE HISTORY


q = Queue.Queue()

bad_symbols = []

n_workers = 10
for i in range(n_workers):
    t = threading.Thread(target=bee)
    t.daemon = True
    t.start()

for exchange in symbols.keys():
    for symbol in symbols[exchange]:
        q.put((symbol,exchange))

while q.qsize() > 0:
    progress(str(q.qsize()))
    time.sleep(.5)
    

q.join()
            
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(symbols) 
pp.pprint(bad_symbols)
