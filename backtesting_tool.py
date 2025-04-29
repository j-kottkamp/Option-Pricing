import yfinance as yf
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.style as style
import datetime
import talib as ta
import pandas as pd
import json
import requests


def getData(symbol, tf, limit, adj, feed, sort):
    url = f"https://data.alpaca.markets/v2/stocks/bars?symbols={symbol}&timeframe={tf}&limit={limit}&adjustment={adj}&feed={feed}&sort={sort}"

    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": "PKNUIYFSASOKVHTZD66W",
        "APCA-API-SECRET-KEY": "lkO3kIHVpSgqyh39c2VL47HguKI1BwzkRgt88AXw"
    }

    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    
    return data

def formatData(data, symbol):
    df = pd.DataFrame()
    df["close"] = [bar["c"] for bar in data["bars"][symbol]]
    df["high"] = [bar["h"] for bar in data["bars"][symbol]]
    df["low"] = [bar["l"] for bar in data["bars"][symbol]]
    df["open"] = [bar["o"] for bar in data["bars"][symbol]]
    df["volume"] = [bar["v"] for bar in data["bars"][symbol]]
    
    df['8_avg_volume'] = df.volume.rolling(window=8).mean()
    
    
    timestamps = [bar["t"] for bar in data["bars"][symbol]]
    df["timestamps"] = [datetime.datetime.fromisoformat(t[:-1]) for t in timestamps]
    df["returns"] = df.close.pct_change().dropna()
    
    
    start_date = df.timestamps.min()
    end_date = df.timestamps.max()
    time_diff = (end_date - start_date).days
    years = time_diff / 365
        
    
    return df, years



    
def CalculateIndicators(df, lb):
    df['rsi'] = ta.RSI(df.close.values.flatten(), timeperiod = 14)
    for lb in lb:
        df[f'ema_{lb}'] = ta.EMA(df.close.values.flatten(), timeperiod = lb)
    return df

def SetStrategy(df):
    df["Long"] = np.where((df.rsi < 70) & (df.rsi > 30), True, False)
    
def CalculateReturn(df, starting_balance, years):
    # Benchmark Performance
    df['Return'] = df.close / df.close.shift(1)
    df.Return.iat[0] = 1
    df['Bench_Bal'] = starting_balance * df.Return.cumprod()
    df['Bench_Peak'] = df.Bench_Bal.cummax()
    df['Bench_DD'] = df.Bench_Bal - df.Bench_Peak
    
    bench_dd = round(((df.Bench_DD / df.Bench_Peak).min() * 100), 2)
    bench_return = round(((df.Bench_Bal.iloc[-1]/df.Bench_Bal.iloc[0]) - 1) * 100, 2)
    
    # System Performance
    df["Sys_Return"] = np.where(df.Long.shift(1) == True, df.Return, 1)
    df['Sys_Bal'] = (starting_balance * df.Sys_Return.cumprod())
    df['Sys_Peak'] = df.Sys_Bal.cummax()
    df['Sys_DD'] = df.Sys_Bal - df.Sys_Peak
    
    sys_return = round(((df.Sys_Bal.iloc[-1]/df.Sys_Bal.iloc[0]) - 1) * 100, 2)
    sys_dd = round(((df.Sys_DD / df.Sys_Peak).min()) * 100, 2)
    sys_in_market = round((df.Long.value_counts().loc[True] / len(df)) * 100)
    sys_win = df.Sys_Return[df.Sys_Return > 1.0].count()
    sys_loss = df.Sys_Return[df.Sys_Return < 1.0].count()
    sys_winrate = round(sys_win / (sys_win + sys_loss) * 100, 2)
    
    # Sharpe Ratios
    daily_bench_ret = df['Return'].dropna() - 1
    bench_return_mean = daily_bench_ret.mean()
    bench_return_std = daily_bench_ret.std()
    sharpe_ratio_bench = (bench_return_mean / bench_return_std) * np.sqrt(252)
    
    daily_sys_ret = df['Sys_Return'].dropna() - 1
    sys_return_mean = daily_sys_ret.mean()
    sys_return_std = daily_sys_ret.std()
    sharpe_ratio_sys = (sys_return_mean / sys_return_std) * np.sqrt(252)


    
    print(f'Benchmark Total return: {bench_return}%')
    print(f'Benchmark DD: {bench_dd}%')
    print(f'Benchmark Sharpe Ratio: {sharpe_ratio_bench:.2f}')
    print('')
    print(f'System Total return: {sys_return}%')
    print(f'System DD: {sys_dd}%')
    print(f'System Sharpe Ratio: {sharpe_ratio_sys:.2f}')
    print(f'Time in Market: {sys_in_market}%')
    print(f'Trades Won: {sys_win}')
    print(f'Trades Loss: {sys_loss}')
    print(f'Winrate: {sys_winrate}%\n')
        
    
    
    
  
def PlotReturn(df):
    import matplotlib.pyplot as plt
    from matplotlib import style
    
    style.use('dark_background')
    
    # Figure mit zwei Subplots erstellen
    fig, axs = plt.subplots(2, 1, figsize=(12, 12))
    
    # Graph 1: Benchmark- und Portfolio-Bilanz
    axs[0].plot(df.Bench_Bal, label='Benchmark', color='blue', linewidth=1.5)
    axs[0].plot(df.Sys_Bal, label='System', color='green', linewidth=1.5)
    axs[0].set_title('Benchmark vs. Portfolio Balance', fontsize=14)
    axs[0].set_ylabel('Balance', fontsize=12)
    axs[0].legend()
    axs[0].grid(alpha=0.3)

    # Graph 2: Indikatoren und Schlusskurse
    axs[1].plot(df.close, label='Close Prices', color='cyan', linewidth=1.5)
    axs[1].plot(df.open, label='Open Prices', color='red', linewidth=0.5)
    axs[1].set_title('Indicators and Close Prices', fontsize=14)
    axs[1].set_ylabel('Price', fontsize=12)
    axs[1].legend()
    axs[1].grid(alpha=0.3)
    
    # X-Achse teilen und anpassen
    for ax in axs:
        ax.set_xlabel('Time', fontsize=12)
    
    # Layout-Anpassung
    plt.tight_layout()
    plt.show()

    
    
def main():
    symbol = "NVDA"
    tf = "1min"
    limit = "10000"
    adj = "raw"
    feed = "sip"
    sort = "asc"
    starting_balance = 10000
    lb = [9, 20, 50, 100]
    
    
    data = getData(symbol, tf, limit, adj, feed, sort)
    df, years = formatData(data ,symbol)
    
    CalculateIndicators(df, lb)
    
    SetStrategy(df)
    
    CalculateReturn(df, starting_balance, years)
    
    PlotReturn(df)
    


if __name__ == '__main__':
    main()