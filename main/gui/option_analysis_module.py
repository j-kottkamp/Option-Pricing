from imports import st, np, plt, datetime, pd
from utils.live_option_data import OptionData
from models.msm import MSMModel
from models.bsm import BSMModel
from utils.live_stock_data import get_stock_data

class OptionAnalysisConfig:
    def __init__(self):
        self.option_type = "call" # Default values
        self.ticker = "AAPL"
        self.model = "Black-Scholes-Merton"
        self.chain = None
        
        data = {"ticker": "AAPL",
                "tf": "1Day", # Use Day so vol. etc. are calculated correctly
                "limit": "365", # 365 so the complete last year counts
                "adj": "raw",
                "feed": "sip",
                "sort": "asc",
                "start": None, # None for build in logic (gives "limit" data points of "tf"). Only with "live" on
                "end": "2030-05-30", # Is ignored with "live" on
                "live": True}
        
        self.prices, _ = get_stock_data(data)
                       
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
            self.compare_default()
                    
        st.write(
            "For better readability, hover over top bar and click the three dots next to the data column.\nThen select 'Autosize'"
        )
        
        if option_data is not None and not option_data.empty:
            st.dataframe(option_data, use_container_width=True)
        else:
            st.warning("No data available for the selected option.")
            
    def compare_sidebar(self):
        st.markdown("## Option Parameter Selection")
        
        last_price = self.prices["close"].iloc[-1]

        ttm = st.sidebar.slider(
            "Show options with time to maturity",
            min_value=0.0,
            max_value=2.0,
            value=(0.25, 1.0),
            help="Only show options between certain time to maturity values"
        )
        
        strike = st.sidebar.slider(
            "Show options with strike price",
            min_value=last_price * 0.5,
            max_value=last_price * 2,
            value=(last_price * 1.15, last_price * 1.5),
            help="Only show options with strike between certain values"
            )
        
        return ttm, strike
        
        
    def compare_default(self):
        ttm, strike = self.compare_sidebar()
        df = self.option_model_comparison(ttm, strike)
        
        market_diffs = {
        "msm_market_diffs": df["msm_market_diff"],
        "fair_msm_market_diffs": df["fair_msm_market_diff"],
        "bsm_market_diffs": df["bsm_market_diff"],
        "fair_bsm_market_diffs": df["fair_bsm_market_diff"],
        }

        other_diffs = {
            "model_diffs": df["model_diff"],
            "fair_model_diffs": df["fair_model_diff"],
            "msm_fair_msm_diffs": df["msm_fair_msm_diff"],
            "bsm_fair_bsm_diffs": df["bsm_fair_bsm_diff"],
            "est_imp_vol_diffs": df["est_imp_vol_diff"],
        }
        
        market_plot, other_plot = st.columns(2)
        
        with market_plot:
            fig, ax = plt.subplots(figsize=(14, 6))
            for label, data in market_diffs.items():
                ax.plot(data, label=label)
            
            ax.set_title("Line Plot of Model Differences")
            ax.set_xlabel("Index")
            ax.set_ylabel("Difference")
            ax.legend(loc='upper right', fontsize="small")
            ax.grid(True)
            
            st.pyplot(fig)
        
        with other_plot:
            fig, ax = plt.subplots(figsize=(14, 6))
            for label, data in other_diffs.items():
                ax.plot(data, label=label)
            
            ax.set_title("Line Plot of Model Differences")
            ax.set_xlabel("Index")
            ax.set_ylabel("Difference")
            ax.legend(loc='upper right', fontsize="small")
            ax.grid(True)
            
            st.pyplot(fig)
            
    
    def option_model_comparison(self, ttm, strike):
        log_returns = np.log(self.prices["close"] / self.prices["close"].shift(1)).dropna()
        sigma_est = log_returns.std() * np.sqrt(252) # annualize
        spot_price = self.prices["close"].iloc[-1]
        
        option_chain_df = self.chain.return_full_data()
        
        min_ttm , max_ttm = ttm[0], ttm[1]
        min_strike , max_strike = strike[0], strike[1]
        
        filtered_df = option_chain_df[
            (option_chain_df["timeToMaturity"] > min_ttm) &
            (option_chain_df["timeToMaturity"] < max_ttm) &
            (option_chain_df["strike"] > min_strike) &
            (option_chain_df["strike"] < max_strike)
        ][["strike", "timeToMaturity", "impliedVolatility", "bid", "ask"]].drop_duplicates()

        option_pairs = filtered_df.values
        
        df = pd.DataFrame(columns=["K", "T", "option_price", "msm_price", "fair_msm_price", "bsm_price", "fair_bsm_price", "model_diff", "fair_model_diff", 
                                   "msm_market_diff", "fair_msm_market_diff", "bsm_market_diff", "fair_bsm_market_diff", "msm_fair_msm_diff", 
                                   "bsm_fair_bsm_diff", "est_imp_vol_diff"])
                    
        i = 0
        end = 10
        for K, T, imp_vol, bid, ask in option_pairs:
            i += 1
            if i % end == 0:
                break
            
            model_msm = MSMModel(sigma=sigma_est, S=spot_price, r=0.0425, dt=1/252, K=K, T=T)  # daily step
            model_fair_msm = MSMModel(sigma=imp_vol, S=spot_price, r=0.0425, dt=1/252, K=K, T=T)
            model_bsm = BSMModel(sigma=sigma_est, S=spot_price, r=0.0425, K=K, T=T,)
            model_fair_bsm = BSMModel(sigma=imp_vol, S=spot_price, r=0.0425, K=K, T=T,)
            
            msm_price = model_msm.price_option(option_type=self.option_type, n_sims=50000)
            fair_msm_price = model_fair_msm.price_option(option_type=self.option_type, n_sims=50000)
            bsm_price = model_bsm.price_option(option_type=self.option_type)
            fair_bsm_price = model_fair_bsm.price_option(option_type=self.option_type)
            market_price = (bid + ask) / 2 # Mid price for simplicity

            new_row = {
                "K": K,                   
                "T": T,
                "option_price": market_price,            
                "msm_price": msm_price,        
                "fair_msm_price": fair_msm_price,    
                "bsm_price": bsm_price,        
                "fair_bsm_price": fair_bsm_price,    
                "model_diff": msm_price - bsm_price,        
                "fair_model_diff": fair_msm_price - fair_bsm_price,  
                "msm_market_diff": msm_price - market_price,    
                "fair_msm_market_diff": fair_msm_price - market_price,
                "bsm_market_diff": bsm_price - market_price,
                "fair_bsm_market_diff": fair_bsm_price - market_price,
                "msm_fair_msm_diff": msm_price - fair_msm_price,
                "bsm_fair_bsm_diff": bsm_price - fair_bsm_price,
                "est_imp_vol_diff": sigma_est - imp_vol
            }
            
            df = pd.concat([df, pd.DataFrame([new_row])])
            
            # Debug
            print(f"- - - Nr. {i - 1} - - -")
            print(f"Strike: {K}, TTM: {T}, Imp Vol: {imp_vol}, Est Vol: {sigma_est:.3f}")
            print(f"Market Price: {market_price}")
            print(f"Fair BSM Price:   {fair_bsm_price}")
            print(f"BSM Price:    {bsm_price}")
            print(f"MSM Fair Price: {fair_msm_price}")
            print(f"MSM Price:    {msm_price}")
            print(f"BSM-MSM Difference:   {bsm_price - msm_price}")
            print(f"Fair MSM-Market Difference: {fair_msm_price - market_price}")
            print(f"Fair MSM-Fair BSM Difference: {fair_msm_price - fair_bsm_price}\n")            

        print(f"Avg Model diff: {df["model_diff"].mean()}")
        print(f"Avg Fair Model diff: {df["fair_model_diff"].mean()}")
        print(f"Avg MSM-Market diff: {df["msm_market_diff"].mean()}")
        print(f"Avg Fair MSM-Market diff: {df["fair_msm_market_diff"].mean()}")
        print(f"Avg BSM-Market diff: {df["bsm_market_diff"].mean()}")
        print(f"Avg Fair BSM-Market diff: {df["fair_bsm_market_diff"].mean()}")
        print(f"Avg MSM-Fair MSM diff: {df["msm_fair_msm_diff"].mean()}")
        print(f"Avg BSM-Fair BSM diff: {df["bsm_fair_bsm_diff"].mean()}")
        print(f"Avg Est Imp Vol diff: {df["est_imp_vol_diff"].mean()}")
        
        st.write(
            f"Average Model difference: {df['model_diff'].mean():.3f}"
            f"Average Fair Model difference: {df['fair_model_diff'].mean():.3f}"
            f"Average MSM-Market difference: {df['msm_market_diff'].mean():.3f}"
            f"Average Fair MSM-Market difference: {df['fair_msm_market_diff'].mean():.3f}"
            f"Average BSM-Market difference: {df['bsm_market_diff'].mean():.3f}"
            f"Average Fair BSM-Market difference: {df['fair_bsm_market_diff'].mean():.3f}"
            f"Average MSM-Fair MSM difference: {df['msm_fair_msm_diff'].mean():.3f}"
            f"Average BSM-Fair BSM difference: {df['bsm_fair_bsm_diff'].mean():.3f}"
            f"Average Est Imp Vol difference: {df['est_imp_vol_diff'].mean():.3f}"                                                                      
        )

        return df