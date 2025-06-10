from imports import st, np, plt, pd
from utils.live_option_data import OptionData
from models.msm import MSMModel
from models.bsm import BSMModel
from utils.live_stock_data import get_stock_data

class OptionAnalysisConfig:
    def __init__(self):
        self.option_type = "call" # Default values
        self.ticker = "AAPL"
        self.model = "Black-Scholes-Merton"
        self.chain = OptionData(ticker=self.ticker, option_type=self.option_type)
        
    def option_model_comparison(self):
        data = {"ticker": "AAPL",
                "tf": "1Day", # Use Day so vol. etc. are calculated correctly
                "limit": "365", # 365 so the complete last year counts
                "adj": "raw",
                "feed": "sip",
                "sort": "asc",
                "start": "2024-05-30",
                "end": "2025-05-30", 
                "live": True}
        
        prices, _ = get_stock_data(data)
        log_returns = np.log(prices["close"] / prices["close"].shift(1)).dropna()
        sigma_est = log_returns.std() * np.sqrt(252) # annualize
        spot_price = prices["close"].iloc[-1]
        
        option_chain_df = self.chain.return_full_data()
        
        option_pairs = option_chain_df.loc[option_chain_df["timeToMaturity"] > 0.25, ["strike", "timeToMaturity", "impliedVolatility", "bid", "ask"]].drop_duplicates()
        option_pairs = option_pairs.loc[option_pairs["strike"] > (prices["close"].iloc[-1] * 1.1)].values # Search for deep out of the money options
        
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

        plt.figure(figsize=(14, 6))
        for label, data in market_diffs.items():
            plt.plot(data, label=label)

        plt.title("Line Plot of Model Differences")
        plt.xlabel("Index")
        plt.ylabel("Difference")
        plt.legend(loc='upper right', fontsize="small")
        plt.grid(True)
        plt.tight_layout()
        plt.show()


analysis = OptionAnalysisConfig()
analysis.option_model_comparison()