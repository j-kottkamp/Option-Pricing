from imports import st, np, plt, sns, pd
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
        
        self.prices = get_stock_data(data)
                       
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
            
        else:
            matrix = st.sidebar.checkbox(
                "Create custom Matrix?"
            )
            if matrix:
                self.create_matrix()
                
            else:      
                st.write(
                    "For better readability, hover over top bar and click the three dots next to the data column.\nThen select 'Autosize'"
                )
                
                if option_data is not None and not option_data.empty:
                    st.dataframe(option_data, use_container_width=True)
                else:
                    st.warning("No data available for the selected option.")
            
    def compare_sidebar(self):
        st.sidebar.markdown("## Option Parameter Selection")
        
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
            "MSM Market Differences": df["msm_market_diff"],
            "Fair MSM Market Differences": df["fair_msm_market_diff"],
            "BSM Market Differences": df["bsm_market_diff"],
            "Fair BSM Market Differences": df["fair_bsm_market_diff"],
        }

        other_diffs = {
            "Model Differences": df["model_diff"],
            "Fair Model Differences": df["fair_model_diff"],
            "MSM vs Fair MSM Differences": df["msm_fair_msm_diff"],
            "BSM vs Fair BSM Differences": df["bsm_fair_bsm_diff"],
            "Estimated vs Implied Volatility Differences": df["est_imp_vol_diff"],
        }
        
        market_plot, other_plot = st.columns(2)
        
        with market_plot:
            fig, ax = plt.subplots(figsize=(14, 6))
            for label, data in market_diffs.items():
                ax.plot(range(len(data)), data.values, label=label)
            
            ax.set_title("Line Plot of Model Differences")
            ax.set_xlabel("Index")
            ax.set_ylabel("Difference")
            ax.legend(loc='upper right', fontsize="small")
            ax.grid(True)
            
            st.pyplot(fig)
            
            print(f"Data ------->\n{data}")
        
        with other_plot:
            fig, ax = plt.subplots(figsize=(14, 6))
            for label, data in other_diffs.items():
                ax.plot(range(len(data)), data.values, label=label)
            
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
        
        print(f"TTMs: 0. {ttm[0]}, 1. {ttm[1]}")
        print(f"MinMax TTM {min_ttm}, {max_ttm}")
        print(f"Strikes: 0. {strike[0]}, 1. {strike[1]}")
        print(f"MinMax Strike {min_strike}, {max_strike}")
       
        filtered_df = option_chain_df[
            (option_chain_df["timeToMaturity"] > min_ttm) &
            (option_chain_df["timeToMaturity"] < max_ttm) &
            (option_chain_df["strike"] > min_strike) &
            (option_chain_df["strike"] < max_strike)
        ][["strike", "timeToMaturity", "impliedVolatility", "bid", "ask"]].drop_duplicates()

        option_pairs = filtered_df.values
        
        print(option_pairs)
        
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
            print(f"- - - Nr. {i} - - -")
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
        
        st.write(f"Average Model difference: {df['model_diff'].mean():.3f}")
        st.write(f"Average Fair Model difference: {df['fair_model_diff'].mean():.3f}")
        st.write(f"Average MSM-Market difference: {df['msm_market_diff'].mean():.3f}")
        st.write(f"Average Fair MSM-Market difference: {df['fair_msm_market_diff'].mean():.3f}")
        st.write(f"Average BSM-Market difference: {df['bsm_market_diff'].mean():.3f}")
        st.write(f"Average Fair BSM-Market difference: {df['fair_bsm_market_diff'].mean():.3f}")
        st.write(f"Average MSM-Fair MSM difference: {df['msm_fair_msm_diff'].mean():.3f}")
        st.write(f"Average BSM-Fair BSM difference: {df['bsm_fair_bsm_diff'].mean():.3f}")
        st.write(f"Average Est Imp Vol difference: {df['est_imp_vol_diff'].mean():.3f}")
        

        return df
    
    def create_matrix(self):
        params = ["expiration", "strike", "impliedVolatility", "timeToMaturity", "moneyness", "lastPrice", "bid", "ask", "volume", 
            "percentChange", "change", "openInterest", "currency", "contractSize", "lastTradeDate", "inTheMoney"]
        
        params_x = st.sidebar.selectbox(
            "Choose matrix parameter (index):",
            params,
            help="Choose parameters in order. X -> Y -> Val."
        )
        params_y = st.sidebar.selectbox(
            "Choose matrix parameter (columns):",
            [p for p in params if p != params_x],
        )
        params_val = st.sidebar.selectbox(
            "Choose value to display:",
            [p for p in params if p != params_x and p != params_y],
        )
        
        matrix_params = [params_x, params_y, params_val]
        
        matrix = self.chain.create_option_matrix(matrix_params=matrix_params)
        
        st.dataframe(matrix)