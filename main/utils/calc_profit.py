from imports import np
from utils.gbm_generator import geometric_brownian_motion

def profit_simulation(option_price=10, S=100, K=100, r=0.05, sigma=0.2, T=1, option_type="call"):
    market_price = option_price
    N = int(T * 252) # Number days to generate
    n=100000

    for i in range(n):
        net_profit = 0
        price = geometric_brownian_motion(S0=S, μ=r, σ=sigma, T=T, N=N)
        price_at_maturity = price[-1]
        if option_type == "call":
            profit = np.max(price_at_maturity - K, 0)  
        elif option_type == "put":
            profit = np.max(K - price_at_maturity, 0)
        profit = profit - market_price
        net_profit += profit
        
    avg_profit = net_profit / n
    roi = avg_profit / market_price
    roi = roi * 100 # turn to percentage
        
    return net_profit, avg_profit, roi

if __name__ == "__main__":
    net_profit, avg_profit, roi = profit_simulation()
    print(f"Net Profit: {net_profit:.2}\nProfit per Option: {avg_profit:.5}\nReturn on investment: {roi:.3}%")
    
