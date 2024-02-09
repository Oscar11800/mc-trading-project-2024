#this website for using yahoo finance https://pypi.org/project/yfinance/

import yfinance as yf
from pytickersymbols import PyTickerSymbols

#get all tickers
stock_data = PyTickerSymbols()

# getting yahoo tickers using the git instructions from pytickersymbols: 
# https://github.com/portfolioplus/pytickersymbols/tree/master

sp500_nyc_yahoo = stock_data.get_sp_500_nyc_yahoo_tickers()

ticker_error = ['SIVB', 'FRC', 'RE', 'BLL', 'PBSTV', 'NEEXU', 
                'ABC', 'PKI', 'KIM-PI', 'BOAPL', 'HBANN', 'CNP-PB', 
                'FISV', 'MNSLV', 'FBHS', 'WLTW', 'ATVI', 'UHID', 'HRS', 'XON']

#string of all tickers
sp500_nyc_yahoo_filtered = [ticker for ticker in sp500_nyc_yahoo if ticker not in ticker_error]
ticker_sp500_string = ' '.join(sp500_nyc_yahoo_filtered)

#initalizing multiple Ticker objects
all_tickers = yf.Tickers(ticker_sp500_string)

#download price history
data_tickers = yf.download(ticker_sp500_string, period = "5y")
data_tickers.to_csv("price_history_nyc_500_yahoo.csv")