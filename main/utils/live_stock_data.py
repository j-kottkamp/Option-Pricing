from imports import requests, json, pd, datetime, os, load_dotenv


def get_stock_data(data):
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
    load_dotenv(dotenv_path=dotenv_path)
    api_key = os.getenv("API_KEY")
    secret_key = os.getenv("API_SECRET_KEY")
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
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": secret_key
    }

    search = url1 if not live else url2
    response = requests.get(search, headers=headers)
    data = json.loads(response.text)
    
    return format_data(data, symbol)

def format_data(data, symbol):
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