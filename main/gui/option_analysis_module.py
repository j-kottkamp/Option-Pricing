from imports import st, np, Ticker
from utils.live_option_data import OptionData
from models.msm import MSMModel
from utils.live_stock_data import get_stock_data

class OptionAnalysisConfig:
    def __init__(self):
        self.option_type = "call" # Default values
        self.ticker = "AAPL"
        self.model = "Black-Scholes-Merton"
        self.chain = None
        
    def option_analysis_default(self):
        self.option_type = st.sidebar.selectbox(
            "Select option type",
            ("call", "put")
        )
        self.ticker = st.sidebar.text_input(
            "Enter ticker symbol",
            value="AAPL"
        )
        all = st.sidebar.checkbox(
            "Show full data?"
        )
        
        try:
            self.chain = OptionData(ticker=self.ticker, option_type=self.option_type)
        except:
            st.error("Please enter a valid ticker symbol. E.g., AAPL")
        
        if all != True:
            data_type = st.sidebar.selectbox(
                "Select data",
                ('strike', 'expiration', 'currency', 'lastPrice', 'change',
                'percentChange', 'volume', 'openInterest', 'bid', 'ask', 'contractSize',
                'lastTradeDate', 'impliedVolatility', 'inTheMoney', 'timeToMaturity', 'moneyness')
            )

            option_data = self.chain.get_option_data(data=data_type)
            
        else:
            option_data = self.chain.return_full_data()
            
        compare = st.sidebar.checkbox(
            "Compare data with models?"
        )
        if compare:
            self.model = st.sidebar.selectbox(
                "Select model",
                ("Markov-Switching Multifractal")
            )
            
            self.option_model_comparison()
            
        st.write(
            "For better readability, hover over top bar and click the three dots next to the data column.\nThen select 'Autosize'"
        )
        
        if option_data is not None and not option_data.empty:
            st.dataframe(option_data, use_container_width=True)
        else:
            st.warning("No data available for the selected option.")
            
    
    def option_model_comparison(self):
        data = {"ticker": "AAPL",
                "tf": "1Day",
                "limit": "10000", # 10k max
                "adj": "raw",
                "feed": "sip",
                "sort": "asc",
                "start": "2023-05-30",
                "end": "2024-05-30", 
                "live": False}

        if self.model == "Markov-Switching Multifractal":
            prices, _ = get_stock_data(data)
            log_returns = np.log(prices["close"] / prices["close"].shift(1)).dropna()
            sigma_est = log_returns.std()
            spot_price = prices["close"].iloc[-1]
            
            option_chain_df = self.chain.return_full_data()
            modeled_prices = {}
            mispricings = {}
            
            strike_ttm_pairs = option_chain_df[["strike", "timeToMaturity"]].drop_duplicates().values


            for K, T in strike_ttm_pairs:
                model = MSMModel(dt=1/252, sigma=sigma_est, S=spot_price, r=0.0425, K=K, T=T)  # daily step
                model_price = model.price_option(option_type=self.option_type, n_sims=1000)
                modeled_prices[(K, T)] = model_price

                market_row = option_chain_df[
                    (option_chain_df["strike"] == K) & 
                    (option_chain_df["timeToMaturity"] == T)
                ]

                if not market_row.empty:
                    market_price = market_row["lastPrice"].values[0]
                else:
                    st.warning(f"Keine Marktdaten für Strike={K}, TTM={T}")
                    continue

                # Debug
                print(f"Strike: {K}, TTM: {T}")
                print(f"Market Price: {market_price}")
                print(f"Model Price:  {model_price}")
                print(f"Difference:   {market_price - model_price}\n")

                if abs(market_price - model_price) > 0.5:
                    mispricings[(K, T)] = market_price - model_price

            if mispricings:
                st.subheader("Significant Model-deviation (|Δ| > 0.5):")
                st.write(mispricings)
            else:
                st.success("No significant deviation between market and model found.")

                            
            