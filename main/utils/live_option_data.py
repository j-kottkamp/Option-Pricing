from imports import pd, Ticker, np, st
class OptionData:
    def __init__(self, ticker="AAPL", option_type="call"):
        self.ticker = ticker.upper()
        self.option_type = option_type
        
    def format_df(self):
        try:
            self.chain = Ticker(self.ticker).option_chain
            dict = Ticker(self.ticker).price[self.ticker]
            # Should be spot = dict['regularMarketPrice'] but throws error: 
            # TypeError: string indices must be integers, not 'str'
            spot = dict['regularMarketPrice']

        except Exception as e:
            msg = f"Invalid response for ticker '{self.ticker}'. Using fallback 'AAPL'."
            try:
                st.error(msg)
            except: 
                raise ValueError(msg)
            
            try:
                # fallback default values
                self.chain = Ticker("AAPL").option_chain
                dict = Ticker("AAPL").price["AAPL"]
                spot = dict['regularMarketPrice']

            except:
                st.error("Cannot access Option Data in Cloud Version. Go to 'https://github.com/j-kottkamp/Quantitative-Research' to host App locally.")
                return
        
        if self.option_type == "call":
            self.chain = self.chain.xs("calls", level=2).reset_index()
        elif self.option_type == "put":
            self.chain = self.chain.xs("puts", level=2).reset_index()
        else:
            raise ValueError("Invalid option type. Please use 'call' or 'put'")

        now = pd.Timestamp.now()
        
        self.chain = self.chain.set_index("contractSymbol")
        self.chain["timeToMaturity"] = ((self.chain["expiration"] - now).dt.total_seconds() / (365 * 24 * 3600)).round(3)
        self.chain["moneyness"] = (self.chain["strike"] / spot).round(3)
        
        params = ["strike", "lastPrice", "change", "percentChange", "volume", "openInterest", "bid", "ask", "impliedVolatility"]
        for item in params:
            value = getattr(self.chain, item)
            rounded_val = value.round(3)
            setattr(self.chain, item, rounded_val)
            
        custom_order = [
            "symbol", "expiration", "timeToMaturity", "strike", "impliedVolatility", "lastPrice", "bid", "ask", "volume", 
            "percentChange", "change", "openInterest", "moneyness", "currency", "contractSize", "lastTradeDate", "inTheMoney"
        ]
        # Filter existing columns
        existing_columns = [col for col in custom_order if col in self.chain.columns]
        self.chain = self.chain[existing_columns]
        
    def create_option_matrix(self, matrix_params=["timeToMaturity", "moneyness", "impliedVolatility"], full=False):
        self.format_df()
            
        option_matrix = self.chain.pivot_table(
            index=matrix_params[0],
            columns=matrix_params[1],
            values=matrix_params[2],
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
        try:
            return self.chain[data]
        except:
            return
    
    def return_full_data(self):
        self.format_df()
        return self.chain