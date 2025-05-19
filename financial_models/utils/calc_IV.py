import math
from utils.std_normal_cdf import standard_normal_cdf
from models.bsm import BSMModel

def bs_vega(S, K, T, r, sigma):
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    return S * math.sqrt(T) * standard_normal_cdf(d1)

def implied_volatility(market_price, S, K, T, r, optionType='call', tol=1e-6, max_iter=100):
    sigma = 0.5
    model = BSMModel(S=S, K=K, T=T, r=r, sigma=sigma, optionType=optionType)

    for _ in range(max_iter):
        price = model.priceOption(S, K, T, r, sigma, optionType)
        vega = bs_vega(S, K, T, r, sigma)
        diff = market_price - price
        if abs(diff) < tol:
            return sigma
        sigma += diff / vega  # Newton-Raphson update
    return sigma  # Return best estimate if not converged