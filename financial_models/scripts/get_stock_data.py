from utils.live_stock_data import getHistData

def main():
    # Returns dataframe and count of years for plotting and metrics calculation, respectively.
    data = {"ticker": "AAPL",
            "tf": "15Min", # Timeframe (1-59Min, 1-23Hour, 1Day, 1Week, 1/2/3/4/6/12Month)
            "limit": "10000", # Max 10k
            "adj": "raw",
            "feed": "sip",
            "sort": "asc",
            "start": "2024-04-09", # %Y-%m-%d 
            "end": "2024-04-26", 
            "live": False}
    
    df, years = getHistData(data)

if __name__ == "__main__":
    main()