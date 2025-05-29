from imports import np
from utils.gbm_generator import geometric_brownian_motion
from models.msm import MSMModel

def profit_simulation(option_price=10, S=100, K=100, r=0.05, sigma=0.2, T=1, option_type="call", model="msm"):
    N = int(T * 252) # Number days to generate
    n=1000000
    
    if model == "bsm":
        price = geometric_brownian_motion(S0=S, μ=r, σ=sigma, T=T, N=N, n_sims=n)
        price_at_maturity = price[-1, :]
        
    elif model == "msm":
        model = MSMModel(S=S, K=K, T=T, r=r, sigma=sigma)
        price = model.monte_carlo_simulate()
        price_at_maturity = price
        
    if option_type == "call":
        payoff = np.maximum(price_at_maturity - K, 0)  
    elif option_type == "put":
        payoff = np.maximum(K - price_at_maturity, 0)
        
    discounted_payoff = payoff * np.exp(-r * T)
        
    profit = discounted_payoff - option_price
    avg_profit = np.mean(profit)
    roi = (avg_profit / option_price) * 100
        
    return avg_profit, roi
    
if __name__ == "__main__":
    avg_profit, roi = profit_simulation()
    print(f"Avg Profit: {avg_profit.round(4)}\nReturn on investment: {roi.round(2)}%")
    
