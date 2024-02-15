import numpy as np  # For numerical operations
import pandas as pd  # For handling data in tables (dataframes)
import yfinance as yf  # For downloading financial data from Yahoo Finance
import mplfinance as mpf  # For creating financial charts, like candlestick charts
import matplotlib.pyplot as plt  # For creating plots and charts
from matplotlib.ticker import FuncFormatter  # For formatting chart labels
from concurrent.futures import ThreadPoolExecutor  # For parallel execution of code
from value_investing import portfolio_input  # Custom function to input portfolio data

# Obtain stock tickers from a predefined function that prompts user input or reads a file
ticks = portfolio_input()

# Define time windows for calculating moving averages, a common technique in momentum trading
# Short window for short-term trends, long window for long-term trends
short_window = 40  # Short moving average window (e.g., 40 days)
long_window = 100  # Long moving average window (e.g., 100 days)

# Define the start and end dates for the data to be analyzed
start_date = "2023-01-01"
end_date = "2024-01-01"

# Function to fetch and calculate momentum data for a given stock symbol
def fetch_momentum_data(symbol):
    """
    This function fetches historical stock price data and calculates two moving averages (short and long).
    It then determines the trading signal (buy, sell, hold) based on the crossover of these averages:
    - A 'buy' signal when the short-term average crosses above the long-term average, indicating upward momentum.
    - A 'sell' signal when the short-term average crosses below the long-term average, indicating downward momentum.
    """
    try:
        # Download historical stock data for the specified period
        data = yf.download(symbol, start=start_date, end=end_date)
        
        # Calculate moving averages
        data['SMA'] = data['Close'].rolling(window=short_window, min_periods=1).mean()  # Short-term moving average
        data['LMA'] = data['Close'].rolling(window=long_window, min_periods=1).mean()  # Long-term moving average
        
        # Generate trading signals based on the crossover strategy
        data['Signal'] = 0  # Default to hold
        data['Signal'][short_window:] = np.where(data['SMA'][short_window:] > data['LMA'][short_window:], 1, -1)
        
        # Return the latest data including the signal
        return {
            'Ticker': symbol,
            'Latest Close': data['Close'].iloc[-1],
            'SMA': data['SMA'].iloc[-1],
            'LMA': data['LMA'].iloc[-1],
            'Signal': data['Signal'].iloc[-1]  # 1 for Buy, -1 for Sell, 0 for Hold
        }
    except Exception as e:
        print(f"Error fetching momentum data for {symbol}: {e}")
        return None

# Use parallel processing to fetch momentum data for all symbols in the 'ticks' dataframe
with ThreadPoolExecutor() as executor:
    symbols = ticks['Ticker'].tolist()
    results = list(executor.map(fetch_momentum_data, symbols))

# Filter out any failed data fetches
results = [result for result in results if result]

# Create a DataFrame to neatly organize the fetched data
momentum_dataframe = pd.DataFrame(results)
print(momentum_dataframe)  # Display the resulting dataframe

# Function to visualize stock data using candlestick charts, highlighting the short and long moving averages
def visualize_stock(symbol):
    """
    This function downloads historical stock data for a given symbol and visualizes it using a candlestick chart.
    It overlays the short-term and long-term moving averages on the chart to help identify trends and potential
    buy/sell signals visually.
    """
    data = yf.download(symbol, start=start_date, end=end_date)
    data['SMA'] = data['Close'].rolling(window=short_window, min_periods=1).mean()
    data['LMA'] = data['Close'].rolling(window=long_window, min_periods=1).mean()
    
    # Configure the additional plots for SMA and LMA to overlay on the candlestick chart
    ap = [
        mpf.make_addplot(data['SMA'], color='blue', width=0.7),
        mpf.make_addplot(data['LMA'], color='red', width=0.7)
    ]
    # Create and show the candlestick chart with SMA and LMA
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