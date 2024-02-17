import numpy as np
import pandas as pd
import yfinance as yf
import mplfinance as mpf
import matplotlib.pyplot as plt
import warnings
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import mplfinance as mpf

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, module='mplfinance.*')

# Define time windows for calculating moving averages, a common technique in momentum trading
short_window = 40  # Short moving average window (e.g., 40 days)
long_window = 80  # Long moving average window (e.g., 100 days)



# Define the start and end dates for the data to be analyzed
start_date = "2023-01-01"
end_date = "2024-01-01"

# Directly use AAPL as the stock of interest
symbol = 'GOOG'

def fetch_momentum_data(symbol):
    try:
        data = yf.download(symbol, start=start_date, end=end_date)
        data['SMA'] = data['Close'].rolling(window=short_window, min_periods=1).mean()
        data['LMA'] = data['Close'].rolling(window=long_window, min_periods=1).mean()
        data['Signal'] = 0
        # Directly assign 'Signal' without using .loc for slicing
        signal_conditions = (data['SMA'] > data['LMA']).astype(int) - (data['SMA'] < data['LMA']).astype(int)
        data['Signal'] = signal_conditions
        return data
    except Exception as e:
        print(f"Error fetching momentum data for {symbol}: {e}")
        return None



# Visualize the AAPL stock data with SMA and LMA
def visualize_stock(data, symbol):
    ap = [
        mpf.make_addplot(data['SMA'], color='blue', width=0.7),
        mpf.make_addplot(data['LMA'], color='red', width=0.7)
    ]
    
    fig, axlist = mpf.plot(data, type='candle', style='charles', addplot=ap,
                           title=f"{symbol} Stock Price with Short and Long Moving Averages",
                           ylabel='Price ($)',
                           volume=True, ylabel_lower='Volume',
                           figratio=(12, 8), returnfig=True)
    
    # Create custom legend handles
    blue_line = mlines.Line2D([], [], color='blue', label='40-Day SMA', linewidth=0.7)
    red_line = mlines.Line2D([], [], color='red', label='100-Day LMA', linewidth=0.7)
    
    # Add the legend to the first (price) axis
    axlist[0].legend(handles=[blue_line, red_line], loc='upper left')
    
def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    data['RSI'] = rsi.fillna(0)  # Fill NA values with 0 for simplicity

def generate_signals(data):
    # Assuming 'Signal' column already exists and is initialized to 0
    # Buy signal: SMA > LMA and RSI < 30
    buy_signals = (data['SMA'] > data['LMA']) & (data['RSI'] < 30)
    data.loc[buy_signals, 'Signal'] = 1

    # Sell signal: SMA < LMA or RSI > 70
    sell_signals = (data['SMA'] < data['LMA']) | (data['RSI'] > 70)
    data.loc[sell_signals, 'Signal'] = -1


def calculate_momentum_returns(data):
    try:
        data['Market Returns'] = data['Close'].pct_change()
        data['Strategy Returns'] = data['Market Returns'] * data['Signal'].shift(1)
        data['Cumulative Market Returns'] = (1 + data['Market Returns']).cumprod() - 1
        data['Cumulative Strategy Returns'] = (1 + data['Strategy Returns']).cumprod() - 1
        return {
            'Ticker': symbol,
            'Cumulative Market Returns': data['Cumulative Market Returns'].iloc[-1],
            'Cumulative Strategy Returns': data['Cumulative Strategy Returns'].iloc[-1]
        }
    except Exception as e:
        print(f"Error calculating momentum returns: {e}")
        return None

data = fetch_momentum_data(symbol)

if data is not None:
    # Calculate indicators
    calculate_rsi(data)

    # Generate signals using SMA, LMA, and RSI
    generate_signals(data)

    # Visualization and calculation of returns
    visualize_stock(data, symbol)
    plt.savefig('momentum_plot.png')

    momentum_returns = calculate_momentum_returns(data)
    print(pd.DataFrame([momentum_returns]))
else:
    print("Failed to fetch data for", symbol)

    
# Calculate and display the momentum returns for AAPL
momentum_returns = calculate_momentum_returns(data)
