from imports import np, pd, coint_johansen, adfuller, plt, datetime
from utils.live_stock_data import get_stock_data
from statsmodels.tsa.vector_ar.var_model import VAR
from statsmodels.api import OLS, add_constant



def build_data(tickers = ["PEP", "KO"]):
    data = {"ticker": None,
                "tf": "1Hour", # Timeframe (1-59Min, 1-23Hour, 1Day, 1Week, 1/2/3/4/6/12Month)
                "limit": "10000", # Max 10k
                "adj": "raw",
                "feed": "sip",
                "sort": "asc",
                "start": "2025-06-05", # %Y-%m-%d, Default: the beginning of the current day.
                "end": "2025-06-23", 
                "live": False} # If live, neither start nor end parameters are required. Returns "limit" bars.

    Y = pd.DataFrame()

    for ticker in tickers:
        data["ticker"] = ticker
        df = get_stock_data(data)
        
        Y[ticker] = df["close"]
        
    Y = Y.dropna()
    print(f"\n{df["timestamps"].iloc[0].date()} - {df["timestamps"].iloc[-1].date()}")
    
    return Y, tickers

def select_optimal_lag(Y, maxlags=10):
    model = VAR(Y)
    lag_selection = model.select_order(maxlags)
    selected_lag = lag_selection.selected_orders['bic']
    return selected_lag

def johansen_cointegration(Y, det_order=0, k_ar_diff=1):
    result = coint_johansen(Y, det_order=det_order, k_ar_diff=k_ar_diff)

    r = 0
    for i, trace_stat in enumerate(result.lr1):
        if trace_stat > result.cvt[i, 2]:  # 1=95% confidence level
            r += 1
    return result, r

def normalize_vector(v):
    return v / v[0]

def check_spread_stationarity(spread):
    adf_stat, pval, _, _, _, _ = adfuller(spread)
    return pval

def analyze_results(Y, result, r):
    vectors = result.evec[:, :r]
    first_vector = normalize_vector(vectors[:, 0])
    spread = Y.values @ vectors[:, 0]
    pval = check_spread_stationarity(spread)
    return first_vector, spread, pval

def estimate_half_life(spread):
    spread_lag = spread[:-1]
    delta_spread = np.diff(spread)
    model = OLS(delta_spread, add_constant(spread_lag)).fit()
    theta = model.params[1]
    return -np.log(2) / theta if theta != 0 else np.inf

def backtest_pair(Y, vector, spread, z_score, entry_z=1.5, exit_z=0.0, cost=0.00):
    # Hedge ratio
    beta = vector[1]

    trades = []
    position = None  # None, 'long', or 'short'
    entry_index = None

    for t in range(30, len(z_score)):
        z = z_score[t]

        if position is None:
            if z < -entry_z:
                position = 'long'
                entry_index = t
            elif z > entry_z:
                position = 'short'
                entry_index = t

        elif position == 'long' and z >= exit_z:
            # Long: buy stock1, sell beta * stock2
            exit_index = t
            pnl_stock1 = Y.iloc[exit_index, 0] - Y.iloc[entry_index, 0]
            pnl_stock2 = -(Y.iloc[exit_index, 1] - Y.iloc[entry_index, 1]) * beta
            gross_pnl = pnl_stock1 + pnl_stock2
            total_cost = cost * (abs(Y.iloc[entry_index, 0]) + abs(beta * Y.iloc[entry_index, 1])) * 2 # x% of both entry values. Times two if selling results in additional transaction fees
            trades.append({"type": "long", "entry": entry_index, "exit": exit_index, "pnl": gross_pnl - total_cost})
            position = None

        elif position == 'short' and z <= exit_z:
            # Short: sell stock1, buy beta * stock2
            exit_index = t
            pnl_stock1 = -(Y.iloc[exit_index, 0] - Y.iloc[entry_index, 0])
            pnl_stock2 = (Y.iloc[exit_index, 1] - Y.iloc[entry_index, 1]) * beta
            gross_pnl = pnl_stock1 + pnl_stock2
            total_cost = cost * (abs(Y.iloc[entry_index, 0]) + abs(beta * Y.iloc[entry_index, 1])) * 2 # x% of both entry values. Times two if selling results in additional transaction fees
            trades.append({"type": "short", "entry": entry_index, "exit": exit_index, "pnl": gross_pnl - total_cost})
            position = None

    return pd.DataFrame(trades)

def plot_metrics(Y, tickers, vector, spread, pval, z_score):
    fig, axs = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    fig.suptitle(f"Pair Analysis: {tickers[0]} & {tickers[1]} | ADF p-value: {pval:.4f}", fontsize=14)

    # Price series
    axs[0].plot(Y[tickers[0]], label=tickers[0])
    axs[0].plot(Y[tickers[1]] * abs(vector[1]), label=tickers[1])
    axs[0].set_ylabel("Price")
    axs[0].set_title(f"Price Series | 1 {tickers[0]} on {vector[1]} {tickers[1]}")
    axs[0].legend()

    # Spread
    axs[1].plot(spread, color='darkgreen')
    axs[1].set_ylabel("Spread")
    axs[1].set_title(f"Spread = {tickers[0]} - {vector[1]:.4f} * {tickers[1]}")

    # Z-score
    axs[2].plot(z_score, color='darkred')
    axs[2].axhline(1.5, color='gray', linestyle='--', lw=1)
    axs[2].axhline(-1.5, color='gray', linestyle='--', lw=1)
    axs[2].axhline(0, color='black', linestyle='--', lw=1)
    axs[2].set_ylabel("Z-score")
    axs[2].set_title("Z-score of Spread")
    axs[2].set_xlabel("Time")

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()


def find_pairs(backtest=True, plot=False):
    '''
    - pairs: 2d list with each item containing 2 correct ticker symbols in string
    format.
    - vector: 1d list with each item being a float representing the beta of the ticker.
    Normalized to ticker one so should be [1. , -x.x]
    - pval: result of the adf test, representing the stationarity of the spread. 
    The smaller the more stationary the spread is. Optimal < 0.001
    - strength: 1 represents a 99% confidence in cointegration
    '''
    results = []
    trade_dfs = {}
    
    pairs_2 = [
        ["AAPL", "MSFT"], ["GOOG", "META"], ["CSCO", "JNPR"], ["INTC", "AMD"],
        ["KO", "PEP"], ["PG", "CL"], ["PM", "MO"], ["XOM", "CVX"],
        ["SLB", "HAL"], ["COP", "OXY"], ["JPM", "BAC"], ["V", "MA"],
        ["T", "VZ"], ["WMT", "COST"], ["HD", "LOW"], ["GLD", "IAU"],
        ["QQQ", "VGT"], ["IWM", "VTWO"], ["LUV", "DAL"], ["UNP", "CSX"],
        ["NFLX", "DIS"], ["EBAY", "AMZN"], ["ORCL", "SAP"], ["ADBE", "CRM"],
        ["ABT", "MDT"], ["JNJ", "PFE"], ["CAT", "DE"], ["UPS", "FDX"],
        ["NVDA", "AVGO"], ["NKE", "UAA"], ["MCD", "SBUX"], ["GS", "MS"],
        ["WFC", "C"], ["TGT", "WMT"], ["UNH", "HUM"], ["MDT", "BSX"],
        ["NEE", "DUK"], ["BA", "LMT"], ["MMM", "HON"], ["CMCSA", "CHTR"],
        ["NOW", "WDAY"], ["SPGI", "MCO"], ["LRCX", "AMAT"]
    ]
    pairs = [["CSCO", "JNPR"], ["HD", "LOW"], ["GLD", "IAU"], ["NVDA", "AVGO"]]

    for pair in pairs_2:
        Y, tickers = build_data(tickers = pair)

        optimal_lag = select_optimal_lag(Y)
        result, coint_rank = johansen_cointegration(Y, det_order=0, k_ar_diff=optimal_lag)

        if coint_rank >= 1:
            vector, spread, pval = analyze_results(Y, result, coint_rank)
            half_life = estimate_half_life(spread)
            strength = result.lr1[0] / result.cvt[0, 1] # trace stat / 95% confidence value
            
            spread = pd.Series(spread)
            z_score = (spread - spread.rolling(30).mean()) / spread.rolling(30).std()
            
            trade_df = backtest_pair(Y, vector, spread, z_score)
            num_trades = len(trade_df["exit"])

            sharpe = trade_df["pnl"].sum() / trade_df["pnl"].std()
            pnl_per_trade = trade_df["pnl"].sum() / num_trades
            
            results.append({
                "pair": f"{tickers[0]} & {tickers[1]}",
                "pnl": trade_df['pnl'].sum(),
                "sharpe": sharpe,
                "p_value": pval,
                "half_life": half_life,
                "cointegration_strength": strength,
                "pnl_per_trade": pnl_per_trade,
                "num_trades": num_trades,
                "z_score_mean": np.mean(z_score),
            })
            
            trade_dfs[f"{tickers[0]} & {tickers[1]}"] = trade_df

            
            # --- plotting ---
            if plot:
                print(f"Spread is {pval:.4f} away from being stationary")
                print(f"Spread = {tickers[0]} + {vector[1]} {tickers[1]}")
                print(f"An increase of 1 in {tickers[1]} results in an expected increase of {abs(vector[1]):.4f} in {tickers[0]} (long-term equilibrium)\n")
                
                plot_metrics(Y, tickers, vector, spread, pval, z_score)
            # --- plotting ---
        
        else:
            pass
            
    results_df = pd.DataFrame(results)

    results_df_filtered = results_df[
        (results_df["p_value"] < 0.02) &
        (results_df["cointegration_strength"] > 1) &
        (results_df["half_life"] > 2) & (results_df["half_life"] < 10) &
        (results_df["pnl_per_trade"] > 0.5)
    ]
    
    results_df = results_df.sort_values(by="sharpe", ascending=False)
    results_df.reset_index(drop=True, inplace=True)
    results_df_filtered = results_df_filtered.sort_values(by="sharpe", ascending=False)
    results_df_filtered.reset_index(drop=True, inplace=True)

    print("Results data")
    print(results_df.head(20))
    print("\nFiltered Results data")
    print(results_df_filtered.head(20))
    
    for pair in results_df_filtered["pair"]:
        print(f"\n{pair}")
        print(trade_dfs[pair])
    
    
    
    
if __name__ == "__main__":
    find_pairs()