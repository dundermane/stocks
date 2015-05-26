from os.path import realpath, join, dirname, isfile
import subprocess
from subprocess import Popen, PIPE
import sys, os
import time


def get_symbol_history(symbol, exchange):
    
    path = join(dirname(realpath(__file__)), 'data', exchange, symbol + '.history')
    apiURL = "http://ichart.finance.yahoo.com/table.csv?s={0}".format(symbol)

    p = Popen(["wget", '--timeout','30', apiURL, '-O', path], stderr=PIPE)
    return_code = p.wait()
    output = p.communicate()
    if return_code == 0:
        print '{0} saved'.format(symbol)
        return
    if return_code == 8:
        print '404 Not Found: Probably an invalid symbol'
    if return_code == 4:
        print 'Unable to connect to host.  Please try again later'
    else:
        print output
        print return_code

def get_all_exchange_symbols(exchange):
    
    path = join(dirname(realpath(__file__)), 'data', exchange + '.csv')
    excBaseURL = 'http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange={0}&render=download'.format(exchange)
        
    p = Popen(["wget", excBaseURL, '-O', path], stderr=PIPE)
    output = p.communicate()[0]

def get_symbol_list(exchange):
    fileInput = open( join(dirname(realpath(__file__)), 'data', exchange + '.csv') , 'r')
    syms = list()
    for line in fileInput:
        print line
        sym = line.split(',')[0].strip('\"')
        syms.append(sym)
    fileInput.close()
    return syms

def get_all_symbol_history(exchange):

    syms = get_symbol_list(exchange)

    for sym in syms:
        get_symbol_history(sym, exchange)
        time.sleep(10)


def get_nofly_txt(exchange):

    syms = get_symbol_list(exchange)
    excDir = join(dirname(realpath(__file__)),'data',exchange)
    for sym in syms:
        p = Popen(["tail","-n","1",join(excDir,sym+".history")], stdout=PIPE)
        print p.communicate()

if __name__ == '__main__':
    
    exchanges = ['amex','nyse','nasdaq']
    
    for exchange in exchanges:
#        get_all_symbol_history(exchange)
        get_nofly_txt(exchange)
