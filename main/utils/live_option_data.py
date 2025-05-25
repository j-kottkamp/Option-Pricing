from imports import pd, Ticker, np
class OptionData:
    def __init__(self, ticker="AAPL", option_type="call"):
        self.ticker = ticker
        self.chain = Ticker(self.ticker).option_chain
        self.option_type = option_type
        self.spot_price = None
        self.now = None
        
    def format_df(self):
        if self.option_type == "call":
            self.chain = self.chain.xs("calls", level=2).reset_index()
        elif self.option_type == "put":
            self.chain = self.chain.xs("puts", level=2).reset_index()
        else:
            raise ValueError("Invalid option type. Please use 'call' or 'put'")
        
        spot = Ticker(self.ticker).price[self.ticker]['regularMarketPrice']
        now = pd.Timestamp.now()
        
        self.chain["timeToMaturity"] = ((self.chain["expiration"] - now).dt.total_seconds() / (365 * 24 * 3600)).round(2)
        self.chain["moneyness"] = (self.chain["strike"] / spot).round(2)
        
        self.chain["expirations"] = pd.to_datetime(self.chain["expiration"])
        
        params = ["strike", "lastPrice", "change", "percentChange", "volume", "openInterest", "bid", "ask", "contractSize", "impliedVolatility"]
        for item in params:
            value = getattr(self.chain, item)
            rounded_val = value.round(2)
            setattr(self.chain, item, rounded_val)
        
        
    def create_option_matrix(self, matrix_params=["timeToMaturity", "moneyness", "impliedVolatility"], full=False):
        self.format_df()
            
        option_matrix = self.chain.pivot_table(
            index=matrix_params[0],
            columns=matrix_params[1],
            values=matrix_params[2]
        )
        
        rows, cols = option_matrix.shape
        window_size = rows
        
        min_nan_count = np.inf
        best_start_col = 0
        
        for start in range(cols - window_size + 1):
            
            submatrix = option_matrix.iloc[:, start : start + window_size]
            nan_count = submatrix.isna().sum().sum()
            
            if nan_count < min_nan_count:
                min_nan_count = nan_count
                best_start_col = start

        best_submatrix = option_matrix.iloc[:, best_start_col:best_start_col + window_size]

        print(f"Best window starts at column {best_start_col}, contains {min_nan_count} NaNs")
                
        return option_matrix if full else best_submatrix

    def get_option_data(self, data="impliedVolatility"):
        self.format_df()
        return self.chain[data]
    
    def return_full_data(self):
        self.format_df()
        return self.chain