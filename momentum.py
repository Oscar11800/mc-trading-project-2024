
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
symbol = 'RIVN'

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
    # Add plots for SMA and LMA
    ap = [
        mpf.make_addplot(data['SMA'], color='blue', width=0.7),
        mpf.make_addplot(data['LMA'], color='red', width=0.7),
    ]
    
    # Specify RSI plot in a separate panel below the main chart
    rsi_plot = mpf.make_addplot(data['RSI'], panel=1, color='purple', ylabel='RSI')
    
    # Add RSI plot to the list of additional plots
    ap.append(rsi_plot)

    # Make sure `panel_ratios` matches the number of panels you're creating
    # Here, it's 2: one for the price and SMA/LMA, another for RSI
    fig, axes = mpf.plot(data, type='candle', style='charles', addplot=ap,
                         title=f"{symbol} Stock Price, SMA, LMA, and RSI",
                         ylabel='Price ($)',
                         volume=True, ylabel_lower='Volume',
                         figratio=(12, 8), returnfig=True, panel_ratios=(6, 3))
    
    # Adding custom legend for SMA and LMA
    axes[0].legend(handles=[mlines.Line2D([], [], color='blue', label='SMA', linewidth=0.7),
                            mlines.Line2D([], [], color='red', label='LMA', linewidth=0.7)],
                   loc='upper left')


    
def RSI(data, window=14, adjust=False):
    delta = data['Close'].diff(1).dropna()
    loss = delta.copy()
    gains = delta.copy()
    gains[gains < 0] = 0
    loss[loss > 0] = 0

    gain_ewm = gains.ewm(com=window - 1, adjust=adjust).mean()
    loss_ewm = abs(loss.ewm(com=window - 1, adjust=adjust).mean())

    RS = gain_ewm / loss_ewm
    RSI = 100 - 100 / (1 + RS)

    return RSI



def generate_signals_with_risk_management(data):
    stop_loss_pct = 0.05  # 5% stop loss
    take_profit_pct = 0.10 # 10% take profit
    # Initialize additional columns for tracking
    data['Entry Price'] = np.nan
    data['Exit Signal'] = 0
    
    for i in range(1, len(data)):
        # Entry signal (for simplicity, assuming buy at close)
        if data.loc[data.index[i-1], 'Signal'] == 1:
            data.loc[data.index[i], 'Entry Price'] = data.loc[data.index[i], 'Close']
        
        if not np.isnan(data.loc[data.index[i-1], 'Entry Price']):
            entry_price = data.loc[data.index[i-1], 'Entry Price']
            current_price = data.loc[data.index[i], 'Close']
            
            # Calculate returns since entry
            returns_since_entry = (current_price - entry_price) / entry_price
            
            # Check for stop-loss or take-profit conditions
            if returns_since_entry <= -stop_loss_pct:
                data.loc[data.index[i], 'Exit Signal'] = -1  # Stop-loss triggered
            elif returns_since_entry >= take_profit_pct:
                data.loc[data.index[i], 'Exit Signal'] = 1  # Take-profit triggered



def calculate_momentum_returns(data):
    try:
        # Initialize the strategy return as the market return for now
        data['Market Returns'] = data['Close'].pct_change()
        data['Strategy Returns'] = data['Market Returns'] * data['Signal'].shift(1)

        # Now adjust the strategy return based on the exit signal
        for i in range(1, len(data)):
            if data.loc[data.index[i], 'Exit Signal'] == -1:
                # If there's an exit signal, we should not have any returns on the next day
                data.loc[data.index[i], 'Strategy Returns'] = 0
                
        # Calculate cumulative returns
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
data['RSI'] = RSI(data)
if data is not None:
    # Calculate indicators
    RSI(data)

    # Generate signals using SMA, LMA, and RSI
    generate_signals_with_risk_management(data)

    # Visualization and calculation of returns
    visualize_stock(data, symbol)
    plt.savefig('momentum_plot.png')

    momentum_returns = calculate_momentum_returns(data)
    print(pd.DataFrame([momentum_returns]))
else:
    print("Failed to fetch data for", symbol)

    
# Calculate and display the momentum returns for AAPL
momentum_returns = calculate_momentum_returns(data)