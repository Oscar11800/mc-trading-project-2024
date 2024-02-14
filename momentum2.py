import numpy as np
import pandas as pd
from pandas.tseries.offsets import MonthEnd
import requests 
import math
import xlsxwriter
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor
from value_investing import portfolio_input

ticks = portfolio_input()

print(ticks)