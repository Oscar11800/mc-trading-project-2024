#this website for using yahoo finance https://pypi.org/project/yfinance/
import pandas as pd
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
def download_price_history(tickers):
    data_tickers = yf.download(tickers, period = "5y")
    data_tickers.to_csv("price_history_nyc_500_yahoo.csv")

#download income statements ONLY FREE CASH FLOW
#organized by Ticker and Date, multiple dates, most are NaN.
def download_free_cash_flow(tickers):
    df_free_cash_flow = pd.DataFrame()
    list_all_rows = []

    for ticker in tickers:
        company = yf.Ticker(ticker)
        company_df = company.cashflow.head(1)
        if company_df.empty:
            continue
        company_df.insert(loc=0, column="Ticker", value=ticker)
        list_all_rows.append(company_df)

    df_free_cash_flow = pd.concat(list_all_rows, ignore_index=True)

    date_time_cols = df_free_cash_flow.loc[:, df_free_cash_flow.columns != 'Ticker']
    ticker_col = df_free_cash_flow.Ticker

    date_time_cols.columns = pd.to_datetime(date_time_cols.columns).date
    date_time_cols = date_time_cols.sort_index(axis=1, ascending=False)

    final_df = pd.concat([ticker_col, date_time_cols], axis = 1)

    return final_df

download_free_cash_flow(sp500_nyc_yahoo_filtered).to_csv("free_cash_flow_nyc_500_yahoo.csv")
