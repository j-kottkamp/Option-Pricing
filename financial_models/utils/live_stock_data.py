import requests, json
import pandas as pd
import datetime

def getHistData(data):
    symbol=data["ticker"]
    tf=data["tf"]
    limit=data["limit"]
    adj=data["adj"]
    feed=data["feed"]
    sort=data["sort"]
    start=data["start"]
    end=data["end"]
    live=data["live"]
    
    url1 = f"https://data.alpaca.markets/v2/stocks/bars?symbols={symbol}&timeframe={tf}&start={start}&end={end}&limit={limit}&adjustment={adj}&feed={feed}&sort={sort}"
    url2 = f"https://data.alpaca.markets/v2/stocks/bars?symbols={symbol}&timeframe={tf}&limit={limit}&adjustment={adj}&feed={feed}&sort={sort}"

    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": "PKNUIYFSASOKVHTZD66W",
        "APCA-API-SECRET-KEY": "lkO3kIHVpSgqyh39c2VL47HguKI1BwzkRgt88AXw"
    }

    search = url1 if not live else url2
    response = requests.get(search, headers=headers)
    data = json.loads(response.text)
    
    return formatData(data, symbol)

def formatData(data, symbol):
    df = pd.DataFrame()
    df["close"] = [bar["c"] for bar in data["bars"][symbol]]
    df["high"] = [bar["h"] for bar in data["bars"][symbol]]
    df["low"] = [bar["l"] for bar in data["bars"][symbol]]
    df["open"] = [bar["o"] for bar in data["bars"][symbol]]
    df["volume"] = [bar["v"] for bar in data["bars"][symbol]]
    
    timestamps = [bar["t"] for bar in data["bars"][symbol]]
    df["timestamps"] = [datetime.datetime.fromisoformat(t[:-1]) for t in timestamps]
    df["returns"] = df.close.pct_change().dropna()
    
    start_date = df.timestamps.min()
    end_date = df.timestamps.max()
    time_diff = (end_date - start_date).days
    years = time_diff / 365
    
    return df, years