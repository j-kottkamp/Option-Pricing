from imports import pd, Ticker, np
class OptionData:
    def __init__(self, ticker="AAPL", optionType="call", data="impliedVolatility"):
        self.ticker = ticker
        self.chain = Ticker(self.ticker).option_chain
        self.optionType = optionType
        self.data = data
        self.spotPrice = None
        self.now = None
        
    def format_df(self):
        if self.optionType == "call":
            self.chain = self.chain.xs("calls", level=2).reset_index()
        elif self.optionType == "put":
            self.chain = self.chain.xs("puts", level=2).reset_index()
        else:
            raise ValueError("Invalid option type. Please use 'call' or 'put'")
        
        spot = Ticker(self.ticker).price[self.ticker]['regularMarketPrice']
        now = pd.Timestamp.now()
        
        self.chain["timeToMaturity"] = ((self.chain["expiration"] - now).dt.total_seconds() / (365 * 24 * 3600)).round(2)
        self.chain["moneyness"] = (self.chain["strike"] / spot).round(2)
        
        self.chain["expirations"] = pd.to_datetime(self.chain["expiration"])
        
        params = ["strike", "lastPrice", "change", "percentChange", "volume", "openInterest", "bid", "ask", "contractSize", "impliedVolatility"]
        if self.data in params:  
            self.chain[self.data] = self.chain[self.data].round(2)
        
        
    def create_option_matrix(self, matrixParams=["timeToMaturity", "moneyness", "impliedVolatility"], full=False):
        self.format_df()
            
        optionMatrix = self.chain.pivot_table(
            index=matrixParams[0],
            columns=matrixParams[1],
            values=matrixParams[2]
        )
        
        rows, cols = optionMatrix.shape
        window_size = rows
        
        min_nan_count = np.inf
        best_start_col = 0
        
        for start in range(cols - window_size + 1):
            
            submatrix = optionMatrix.iloc[:, start : start + window_size]
            nan_count = submatrix.isna().sum().sum()
            
            if nan_count < min_nan_count:
                min_nan_count = nan_count
                best_start_col = start

        best_submatrix = optionMatrix.iloc[:, best_start_col:best_start_col + window_size]

        print(f"Best window starts at column {best_start_col}, contains {min_nan_count} NaNs")
                
        return optionMatrix if full else best_submatrix

    def get_option_data(self):
        self.format_df()
        return self.chain[self.data]
    
    def return_full_data(self):
        self.format_df()
        return self.chain