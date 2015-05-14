##### PENNIES STRATEGY ########

##Really just to fool around with penny stocks.  Here goes nothing...


import os
import random
from stock import Stock, piggy
from sys import argv
from sym2 import symbols

def update(symbol):

    stock = Stock(symbol)
    #update stock
    if stock.update_history() == False:
        print 'this one is a dud'
        return False
    print 'got history'
    #if no data, discard
    #if data, add to list
    #calculate 52 week high
    #calculate n week average volume
    



    #return stock
    return stock

if __name__ == '__main__':
    
    if len(argv) == 2:
        update(argv[1])

