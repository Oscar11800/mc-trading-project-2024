import numpy as np
import pandas as pd
import requests 
import math
import xlsxwriter
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor

# Read stock symbols from CSV
stocks = pd.read_csv('tickers.csv', usecols=['Symbol'])

# Split symbols into chunks of 100
#symbol_groups = np.array_split(stocks['Symbol'].to_numpy(), math.ceil(len(stocks) / 100))

def fetch_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        pe_ratio = info.get('forwardPE', np.nan)

        ticker_data = ticker.history(period='1d')
        last_quote = ticker_data['Close'].iloc[-1] if not ticker_data.empty else np.nan

        return {
            'Ticker': symbol,
            'Price': last_quote,
            'PE Ratio': pe_ratio,
            'Number of Shares to Buy': 'N/A'
        }
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

# Use ThreadPoolExecutor for parallel processing
with ThreadPoolExecutor() as executor:
    # Fetch data for all symbols in parallel
    data_list = list(filter(None, executor.map(fetch_data, stocks['Symbol'])))

# Create the final DataFrame from the list of dictionaries
final_dataframe = pd.DataFrame(data_list)

# Drop rows with missing data
final_dataframe = final_dataframe.dropna(subset=['Price', 'PE Ratio'])

# Convert 'PE Ratio' to numeric
final_dataframe['PE Ratio'] = pd.to_numeric(final_dataframe['PE Ratio'], errors='coerce')

# Filter and sort the DataFrame
final_dataframe = final_dataframe[final_dataframe['PE Ratio'] > 0].sort_values('PE Ratio').head(50)

# Reset index
final_dataframe.reset_index(drop=True, inplace=True)

# Define the portfolio_input function
def portfolio_input():
    global portfolio_size
    portfolio_size = input("Enter the value of your portfolio:")

    try:
        val = float(portfolio_size)
    except ValueError:
        print("That's not a number! \n Try again:")
        portfolio_size = input("Enter the value of your portfolio:")

    position_size = float(portfolio_size) / len(final_dataframe.index)
    final_dataframe['Number of Shares to Buy'] = (position_size / final_dataframe['Price']).apply(np.floor)
    return (final_dataframe)

# Call the portfolio_input function
print(portfolio_input())
