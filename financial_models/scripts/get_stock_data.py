from utils.live_stock_data import get_stock_data
from utils.live_option_data import get_option_matrix

def main():
    # Returns dataframe and count of years for plotting and metrics calculation, respectively.
    data = {"ticker": "AAPL",
            "tf": "15Min", # Timeframe (1-59Min, 1-23Hour, 1Day, 1Week, 1/2/3/4/6/12Month)
            "limit": "10000", # Max 10k
            "adj": "raw",
            "feed": "sip",
            "sort": "asc",
            "start": "2024-04-09", # %Y-%m-%d, Default: the beginning of the current day.
            "end": "2024-04-26", 
            "live": True} # If live, neither start nor end parameters are required. Returns "limit" bars.
    
    df, years = get_stock_data(data)
    print(df.tail(20))
    

if __name__ == "__main__":
    main()