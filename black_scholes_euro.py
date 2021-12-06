# make sure you have downloaded these libraries, with the "pip install" command
from math import log, sqrt, exp
from scipy.stats import norm
from datetime import datetime, date
import numpy as np
import pandas as pd
import pandas_datareader.data as web


def d1(S, K, T, r, sigma):
    return (log(S / K) + (r + sigma ** 2 / 2.0) * T) / (sigma * sqrt(T))


def d2(S, K, T, r, sigma):
    return d1(S, K, T, r, sigma) - sigma * sqrt(T)


def bs_call(S, K, T, r, sigma):
    # Do not take into account this line break which is related to my auto-formatter
    return S * norm.cdf(d1(S, K, T, r, sigma)) - K * exp(-r * T) * norm.cdf(
        d2(S, K, T, r, sigma)
    )


def bs_put(S, K, T, r, sigma):
    return K * exp(-r * T) - S + bs_call(S, K, T, r, sigma)


stock = str(input("select the stock you want: "))

current_price = round(web.DataReader(stock, "yahoo")["Adj Close"].iloc[-1], 2)

print("The current price of", stock, " is: ", current_price)

choice = input("Wanna price a call or a put ? (c/p): ")


expiry = str(input("select the expiry date (format mm-dd-YYYY): "))
strike_price = int(input("select the strike price: "))

today = datetime.now()
one_year_ago = today.replace(year=today.year - 1)

df = web.DataReader(stock, "yahoo", one_year_ago, today)

df = df.sort_values(by="Date")
df = df.dropna()
df = df.assign(close_day_before=df.Close.shift(1))
df["returns"] = (df.Close - df.close_day_before) / df.close_day_before

# volatility
sigma = np.sqrt(252) * df["returns"].std()

# Treasury Yield 10 Years US as risk-free interest rate
ty10y = (web.DataReader("^TNX", "yahoo")["Close"].iloc[-1]) / 100
last_close = df["Close"].iloc[-1]
# time expiration in % of year
t = (datetime.strptime(expiry, "%m-%d-%Y") - datetime.utcnow()).days / 365

if choice == "c":
    print("The Call Price is: ", bs_call(last_close, strike_price, t, ty10y, sigma))


if choice == "p":
    print("The Put Price is: ", bs_put(last_close, strike_price, t, ty10y, sigma))
