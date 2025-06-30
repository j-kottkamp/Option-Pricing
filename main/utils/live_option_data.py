from imports import pd, Ticker, np, st
class OptionData:
    def __init__(self, ticker="AAPL", option_type="call"):
        self.ticker = ticker.upper()
        self.option_type = option_type
        
    def format_df(self):
        try:
            print(f"\n[INFO] Requesting option chain and price for ticker: {self.ticker}")

            ticker_obj = Ticker(self.ticker)
            
            self.chain = ticker_obj.option_chain
            print(f"[DEBUG] type(self.chain): {type(self.chain)}")
            print(f"[DEBUG] self.chain keys (if dict-like): {getattr(self.chain, 'keys', lambda: 'N/A')()}")

            price_data = ticker_obj.price
            print(f"[DEBUG] type(price_data): {type(price_data)}")
            print(f"[DEBUG] price_data content: {price_data}")

            # Check if ticker key exists and is dict
            if self.ticker not in price_data:
                raise KeyError(f"Ticker '{self.ticker}' not found in price_data")

            ticker_price = price_data[self.ticker]
            print(f"[DEBUG] type(ticker_price): {type(ticker_price)}")
            print(f"[DEBUG] ticker_price content: {ticker_price}")

            if not isinstance(ticker_price, dict):
                raise TypeError("Expected dictionary for ticker_price, got something else.")

            spot = ticker_price['regularMarketPrice']
            print(f"[INFO] Spot price for {self.ticker}: {spot}")

        except Exception as e:
            msg = f"[ERROR] Invalid response for ticker '{self.ticker}': {e}. Using fallback 'AAPL'."
            print(msg)

            try:
                import streamlit as st
                st.error(msg)
            except Exception as streamlit_error:
                print(f"[WARNING] Streamlit not available or failed: {streamlit_error}")

            # fallback default values
            ticker_obj = Ticker("AAPL")
            self.chain = ticker_obj.option_chain
            print(f"[DEBUG] fallback self.chain type: {type(self.chain)}")

            price_data = ticker_obj.price
            print(f"[DEBUG] fallback price_data: {price_data}")

            ticker_price = price_data["AAPL"]
            print(f"[DEBUG] fallback ticker_price type: {type(ticker_price)}")
            print(f"[DEBUG] fallback ticker_price content: {ticker_price}")

            if not isinstance(ticker_price, dict):
                raise TypeError("Fallback ticker_price is not a dictionary!")

            spot = ticker_price['regularMarketPrice']
            print(f"[INFO] Fallback spot price: {spot}")

        # Check again: What is self.chain at this point?
        print(f"[DEBUG] Final type of self.chain: {type(self.chain)}")

        # Convert MultiIndex DataFrame into flat one
        try:
            if self.option_type == "call":
                print("[INFO] Extracting call options")
                self.chain = self.chain.xs("calls", level=2).reset_index()
            elif self.option_type == "put":
                print("[INFO] Extracting put options")
                self.chain = self.chain.xs("puts", level=2).reset_index()
            else:
                raise ValueError("Invalid option type. Please use 'call' or 'put'")
        except AttributeError as ae:
            print(f"[ERROR] self.chain does not support .xs(): {ae}")
            print(f"[DEBUG] self.chain content: {self.chain}")
            raise
        except Exception as e:
            print(f"[ERROR] Unexpected error while slicing option chain: {e}")
            raise
        

        now = pd.Timestamp.now()
        
        self.chain = self.chain.set_index("contractSymbol")
        self.chain["timeToMaturity"] = ((self.chain["expiration"] - now).dt.total_seconds() / (365 * 24 * 3600)).round(3)
        self.chain["moneyness"] = (self.chain["strike"] / spot).round(3)
                
        params = ["strike", "lastPrice", "change", "percentChange", "volume", "openInterest", "bid", "ask", "contractSize", "impliedVolatility"]
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
        return self.chain[data]
    
    def return_full_data(self):
        self.format_df()
        return self.chain