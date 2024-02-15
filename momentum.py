import numpy as np
import pandas as pd
import yfinance as yf
import mplfinance as mpf
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from concurrent.futures import ThreadPoolExecutor
from value_investing import portfolio_input

ticks = portfolio_input()

# Define the period for the moving averages and the visualization period
short_window = 40
long_window = 100
start_date = "2023-01-01"
end_date = "2024-01-01"


# Define the period for the moving averages
short_window = 40  # Short moving average window
long_window = 100  # Long moving average window

def fetch_momentum_data(symbol):
    """
    Fetch historical stock data and calculate short and long moving averages.
    Generate buy/sell signals based on the crossover strategy.
    
    Parameters:
    - symbol: The stock symbol for which to fetch data.
    
    Returns:
    A dictionary containing the ticker, SMA, LMA, and signal.
    """
    try:
        # Fetch historical data for the last 1 year
        data = yf.download(symbol, start="2023-01-01", end="2024-01-01")
        
        # Calculate moving averages
        data['SMA'] = data['Close'].rolling(window=short_window, min_periods=1).mean()
        data['LMA'] = data['Close'].rolling(window=long_window, min_periods=1).mean()
        
        # Identify signals (1 = Buy, -1 = Sell, 0 = Hold)
        data['Signal'] = 0  # Default to hold
        data['Signal'][short_window:] = np.where(data['SMA'][short_window:] > data['LMA'][short_window:], 1, -1)
        
        # Take the last signal for the most recent trading decision
        latest_signal = data['Signal'].iloc[-1]
        
        return {
            'Ticker': symbol,
            'Latest Close': data['Close'].iloc[-1],
            'SMA': data['SMA'].iloc[-1],
            'LMA': data['LMA'].iloc[-1],
            'Signal': latest_signal  # 1 for Buy, -1 for Sell, 0 for Hold
        }
    except Exception as e:
        print(f"Error fetching momentum data for {symbol}: {e}")
        return None

# Parallel fetching of momentum data
with ThreadPoolExecutor() as executor:
    # Extract the 'Ticker' column from the ticks DataFrame
    symbols = ticks['Ticker'].tolist()
    results = list(executor.map(fetch_momentum_data, symbols))

# Filter out None results
results = [result for result in results if result]

# Create a DataFrame from the results
momentum_dataframe = pd.DataFrame(results)

# Display the DataFrame
print(momentum_dataframe)

def visualize_stock(symbol):
    """
    Visualize the stock data with candlestick chart, including SMA and LMA.
    
    Parameters:
    - symbol: The stock symbol to visualize.
    """
    data = yf.download(symbol, start=start_date, end=end_date)
    data['SMA'] = data['Close'].rolling(window=short_window, min_periods=1).mean()
    data['LMA'] = data['Close'].rolling(window=long_window, min_periods=1).mean()
    
    # Create candlestick chart with moving averages
    ap = [
        mpf.make_addplot(data['SMA'], color='blue', width=0.7),
        mpf.make_addplot(data['LMA'], color='red', width=0.7)
    ]
    mpf.plot(data, type='candle', style='charles', addplot=ap, title=f"{symbol} - SMA and LMA", volume=True)

# Call visualize_stock for a specific stock
# visualize_stock('AAPL')  # Example symbol

def calculate_all_momentum_returns(ticks, start_date="2023-01-01", end_date="2024-01-01", short_window=40, long_window=100):
    """
    Calculate the cumulative returns for the momentum strategy and market for all stocks in `ticks`.
    
    Parameters:
    - ticks: DataFrame containing stock tickers.
    - start_date: The start date for fetching historical data.
    - end_date: The end date for fetching historical data.
    - short_window: The window size for the short moving average.
    - long_window: The window size for the long moving average.
    
    Returns:
    A DataFrame with tickers and their cumulative market and strategy returns.
    """
    def calculate_momentum_returns(symbol):
        try:
            data = yf.download(symbol, start=start_date, end=end_date)
            if data.empty:
                return None
            
            data['SMA'] = data['Close'].rolling(window=short_window, min_periods=1).mean()
            data['LMA'] = data['Close'].rolling(window=long_window, min_periods=1).mean()
            
            # Generate signals
            data['Signal'] = np.where(data['SMA'] > data['LMA'], 1, -1)
            
            # Calculate daily returns and strategy returns
            data['Market Returns'] = data['Close'].pct_change()
            data['Strategy Returns'] = data['Market Returns'] * data['Signal'].shift(1)
            
            # Calculate cumulative returns
            data['Cumulative Market Returns'] = (1 + data['Market Returns']).cumprod() - 1
            data['Cumulative Strategy Returns'] = (1 + data['Strategy Returns']).cumprod() - 1
            
            return {
                'Ticker': symbol,
                'Cumulative Market Returns': data['Cumulative Market Returns'].iloc[-1],
                'Cumulative Strategy Returns': data['Cumulative Strategy Returns'].iloc[-1]
            }
        except Exception as e:
            print(f"Error calculating momentum returns for {symbol}: {e}")
            return None

    # Execute the momentum returns calculation in parallel for all tickers
    with ThreadPoolExecutor() as executor:
        returns_results = list(executor.map(calculate_momentum_returns, ticks['Ticker']))

    # Filter out None results and assemble the DataFrame
    returns_results = [result for result in returns_results if result]
    returns_dataframe = pd.DataFrame(returns_results)

    return returns_dataframe

# Assuming the `ticks` DataFrame is already defined
# Call the function to calculate and get the returns DataFrame
returns_df = calculate_all_momentum_returns(ticks)
print(returns_df)