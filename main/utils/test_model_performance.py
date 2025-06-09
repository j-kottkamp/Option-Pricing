from imports import st, np, plt
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
        
        strike_ttm_pairs = option_chain_df.loc[option_chain_df["timeToMaturity"] > 0.25, ["strike", "timeToMaturity", "impliedVolatility"]].drop_duplicates()
        strike_ttm_pairs = strike_ttm_pairs.loc[strike_ttm_pairs["strike"] > (prices["close"].iloc[-1] * 1)].values # Search for deep out of the money options
        
        msm_prices = {}
        msm_fair_prices = {}
        bsm_prices = {}
        fair_prices = {}
        
        model_diffs = []
        msm_fair_diffs = []
        msm_market_diffs = []
        bsm_fair_diffs = []
        bsm_market_diffs = []
        fair_market_diffs = []
        imp_vol_est_vol_diffs = []
        msm_fair_msm_diffs = []
        msm_fair_bsm_diffs = []
        msm_fair_fair_diffs = []
        msm_fair_market_diffs = []
                    
        i = 0
        end = 100
        for K, T, imp_vol in strike_ttm_pairs:
            i += 1
            if i % end == 0:
                break
            model_msm = MSMModel(sigma=sigma_est, S=spot_price, r=0.0425, dt=1/252, K=K, T=T)  # daily step
            model_msm_fair = MSMModel(sigma=imp_vol, S=spot_price, r=0.0425, dt=1/252, K=K, T=T)
            model_bsm = BSMModel(sigma=sigma_est, S=spot_price, r=0.0425, K=K, T=T,)
            model_fair = BSMModel(sigma=imp_vol, S=spot_price, r=0.0425, K=K, T=T,)
            
            msm_price = model_msm.price_option(option_type=self.option_type, n_sims=50000)
            msm_fair_price = model_msm_fair.price_option(option_type=self.option_type, n_sims=50000)
            bsm_price = model_bsm.price_option(option_type=self.option_type)
            fair_price = model_fair.price_option(option_type=self.option_type)

            msm_prices[(K, T)] = msm_price
            msm_fair_prices[(K, T)] = msm_fair_price
            bsm_prices[(K, T)] = bsm_price
            fair_prices[(K, T)] = fair_price

            market_row = option_chain_df[
                (option_chain_df["strike"] == K) & 
                (option_chain_df["timeToMaturity"] == T)
            ]

            if not market_row.empty:
                market_price = market_row["lastPrice"].values[0]
            else:
                st.warning(f"No Market Data for Strike={K}, TTM={T}")
                continue

            model_diffs.append(bsm_price - msm_price)
            msm_fair_diffs.append(msm_price - fair_price)
            msm_market_diffs.append(msm_price - market_price)
            bsm_fair_diffs.append(bsm_price - fair_price)
            bsm_market_diffs.append(bsm_price - market_price)
            fair_market_diffs.append(fair_price - market_price)
            imp_vol_est_vol_diffs.append(imp_vol - sigma_est)
            msm_fair_msm_diffs.append(msm_fair_price - msm_price)
            msm_fair_bsm_diffs.append(msm_fair_price - bsm_price)
            msm_fair_fair_diffs.append(msm_fair_price - fair_price)
            msm_fair_market_diffs.append(msm_fair_price - market_price)
            
            # Debug
            print(f"- - - Nr. {i - 1} - - -")
            print(f"Strike: {K}, TTM: {T}, Imp Vol: {imp_vol}, Est Vol: {sigma_est:.3f}")
            print(f"Market Price: {market_price}")
            print(f"Fair Price:   {fair_price}")
            print(f"BSM Price:    {bsm_price}")
            print(f"MSM Price:    {msm_price}")
            print(f"MSM Fair Price: {msm_fair_price}")
            print(f"BSM-MSM Difference:   {bsm_price - msm_price}")
            print(f"Fair MSM-Market Difference: {msm_fair_price - market_price}")
            print(f"Fair MSM-Fair Difference: {msm_fair_price - fair_price}\n")

            
            model_diff = bsm_price - msm_price
            
        
        
        model_diffs = np.array(model_diffs)
        msm_fair_diffs = np.array(msm_fair_diffs)
        msm_market_diffs = np.array(msm_market_diffs)
        bsm_fair_diffs = np.array(bsm_fair_diffs)
        bsm_market_diffs = np.array(bsm_market_diffs)
        fair_market_diffs = np.array(fair_market_diffs)
        imp_vol_est_vol_diffs = np.array(imp_vol_est_vol_diffs)
        msm_fair_msm_diffs = np.array(msm_fair_msm_diffs)
        msm_fair_bsm_diffs = np.array(msm_fair_bsm_diffs)
        msm_fair_fair_diffs = np.array(msm_fair_fair_diffs)
        msm_fair_market_diffs = np.array(msm_fair_market_diffs)

        print(f"Avg Model diff: {model_diffs.mean()}")
        print(f"Avg MSM-Fair diff: {msm_fair_diffs.mean()}")
        print(f"Avg MSM-Market diff: {msm_market_diffs.mean()}")
        print(f"Avg BSM-Fair diff: {bsm_fair_diffs.mean()}")
        print(f"Avg BSM-Market diff: {bsm_market_diffs.mean()}")
        print(f"Avg Fair-Market diff: {fair_market_diffs.mean()}")
        print(f"Avg Imp Vol Est Vol diff: {imp_vol_est_vol_diffs.mean()}")
        print(f"Avg MSM-Fair-MSM diff: {msm_fair_msm_diffs.mean()}")
        print(f"Avg MSM-Fair-BSM diff: {msm_fair_bsm_diffs.mean()}")
        print(f"Avg MSM-Fair-Fair diff: {msm_fair_fair_diffs.mean()}")
        print(f"Avg MSM-Fair-Market diff: {msm_fair_market_diffs.mean()}")
        
        market_diffs = {
            "msm_market_diffs": msm_market_diffs,
            "bsm_market_diffs": bsm_market_diffs,
            "fair_market_diffs": fair_market_diffs,
            "msm_fair_market_diffs": msm_fair_market_diffs,
        }
        other_diffs = {
            "model_diffs": model_diffs,
            "msm_fair_diffs": msm_fair_diffs,
            "bsm_fair_diffs": bsm_fair_diffs,
            "imp_vol_est_vol_diffs": imp_vol_est_vol_diffs,
            "msm_fair_msm_diffs": msm_fair_msm_diffs,
            "msm_fair_bsm_diffs": msm_fair_bsm_diffs,
            "msm_fair_fair_diffs": msm_fair_fair_diffs,
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