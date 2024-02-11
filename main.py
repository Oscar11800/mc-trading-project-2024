import numpy as np
import pandas as pd
import requests 
import math
from scipy import stats
import xlsxwriter
import yfinance as yf

stocks = pd.read_csv('tickers.csv', usecols=['Symbol'])

#print(pe_ratio)

def chunks(lst, n):
    '''divides stocks into chunks of 100 evenly'''
    for i in range(0, len(lst), n):
        yield lst[i:i + n]  

symbol_groups = list(chunks(stocks['Symbol'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(map(str, symbol_groups[i])))

tickers = []
prices = []
pe_ratios = []
num_shares = []

for symbol_string in symbol_strings:
    for symbol in symbol_string.split(','):
        ticker = yf.Ticker(symbol)
        ticker_data = ticker.history()
        if len(ticker_data["Close"]) > 1:
            last_quote = ticker_data['Close'].iloc[-1]
        else:
            continue
        if "forwardPE" in ticker.info.keys():
            pe_ratio = ticker.info['forwardPE']
        else:
            continue
        tickers.append(symbol)
        prices.append(last_quote)
        pe_ratios.append(pe_ratio)
        num_shares.append('N/A')

final_dataframe = pd.DataFrame({
    'Ticker': tickers,
    'Price': prices,
    'PE Ratio': pe_ratios,
    'Number of Shares to Buy': num_shares
})

final_dataframe['PE Ratio'] = pd.to_numeric(final_dataframe['PE Ratio'], errors='coerce')
final_dataframe.sort_values('PE Ratio', inplace = True)
final_dataframe = final_dataframe[final_dataframe['PE Ratio'] > 0]
final_dataframe = final_dataframe[:50]
final_dataframe.reset_index(inplace = True)
final_dataframe.drop('index', axis=1, inplace = True)

def portfolio_input():
    global portfolio_size
    portfolio_size = input("Enter the value of your portfolio:")

    try:
        val = float(portfolio_size)
    except ValueError:
        print("That's not a number! \n Try again:")
        portfolio_size = input("Enter the value of your portfolio:")

    position_size = float(portfolio_size) / len(final_dataframe.index)
    for i in range(0, len(final_dataframe['Ticker'])):
        final_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(position_size / final_dataframe['Price'][i])
    print(final_dataframe)

portfolio_input()