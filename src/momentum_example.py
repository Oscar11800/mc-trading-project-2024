import numpy as np
import pandas as pd
from pandas.tseries.offsets import MonthEnd
import requests 
import math
import xlsxwriter
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor
from value_investing import portfolio_input

#TICKER CLEANING AND COLLECTION
test_data = 'https://www.youtube.com/redirect?event=video_description&redir_token=QUFFLUhqbF9WZk1XQ1hnRk9EVGJKTm9kcEpzOHV1RVpnZ3xBQ3Jtc0tuYm40cW56eFBYcUdoc0taeFUxbU9ibVZWeXhmVnRYdDJOUjN1WEJNWmhzQ0ZxX0FBaHVVTmpLblFfYTlNTVN4UFN6cm05cTR3NFc3Z1FxVTJVbW9hbXNFemNid3RXazFqbUt6anNiWVhFLXhnVm9nSQ&q=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FList_of_S%2526P_500_companies&v=L2nhNvIAyBI'

# top_50_tickers = portfolio_input()  #gets value investing filtered stocks
test_ticks = pd.read_html(test_data)[0].Symbol

df_ = pd.read_html(test_data)[1].Symbol

df_.Date = pd.to_datetime(df_.Date.Date)   #transforms date to day-time format

df_ = df_[df_.Date.Date >= '2020-01-01']    #filters from beginning of 2020

#remove added tickers
test_ticks = test_ticks[~(test_ticks.isin(df_.Added.Ticker))]

ticks_removed = df._Removed.Ticker  #select removed tickers
ticks_removed = ticks_removed[1:]   #removed Under Armor ticker bc of error

test_ticks = test_ticks.append(ticks_removed)
test_ticks.drop_duplicates(inplace=True)
test_ticks.dropna(inplace=True)

start ='2020-01-01'
prices,symbols = [], [] #for mapping mechanism

for symbol in test_ticks:
    df = yf.download(symbol, start=start) ['Adj Close'] #adjusted close price
    if not df.empty:    #avoid empty prices
        prices.append(df)
        symbols.append(symbol)
        
all_prices = pd.concat(prices, axis=1)
all_prices.columns = symbols    #daily prices for all tickers

(all_prices.pct_change() + 1).prod -1 #subtracts daily by daily for percentage change and accumulates that for entire time...  subtract 1 to get raw return

all_monthly_returns = all_prices.pct_change().resample('M').agg(lambda x: (x+1).prod() -1)     #gets df with all monthly returns

#df of all montly returns with raw prices
all_prices.resample('M').last()    #gets last price every month

all_monthly_returns_12 = all_monthly_returns.rolling(12).agg(lambda x: (x+1).prod()-1)

all_monthly_returns_12.dropna(inplace=True) #past year return for all assets
curr_ = all_monthly_returns_12.iloc[0]
win_ = curr_.nlargest(10)   #gets top 10 performers over last year

#get return of portfolio over next month
win_ret = all_monthly_returns.loc[win_.name + MonthEnd(1), win_.index]

#WAYS TO ANALYZE RETURNS
win_ret.mean()

def momentum(all_monthly_returns, lookback):
    all_monthly_returns_lb = all_monthly_returns(lookback).agg(lambda x: (x+1).prod()-1)
    all_monthly_returns_lb.dropna(inplace=True)
    
    rets = []
    
    for row in range(len(all_monthly_returns_lb) - 1):
        curr = all_monthly_returns_lb.iloc[row]
        win = curr.nlargest(50) #top 10%
        win_ret = all_monthly_returns.loc[win.name + MonthEnd(1), win.index]
        rets.append(win_ret.mean())
    return(pd.Series(rets) + 1).prod()-1

for lookback in range(1,13):
    print(momentum(all_monthly_returns, lookback))
    
s_p = yf.download('GSPC', start=start)
(s_p.Close.pct_change() + 1).prod() -1