import numpy as np
import math
from utils.msm_future_volatility import get_future_volatility

def standard_normal_cdf(x):
    return 0.5 * (1 + math.erf(x / np.sqrt(2)))

def optionPricing(S, K, T, σ, r, optionType, data):
    t = 0   # Pricing time (today t=0)
    
    d1 = (np.log(S / K) + (r + 0.5 * σ**2) * (T - t)) / σ * np.sqrt(T - t)
    d2 = d1 - σ * np.sqrt(T - t)
    
    if optionType == "call":
        return S * standard_normal_cdf(d1) - K * np.exp(-r * T) * standard_normal_cdf(d2)
    
    elif optionType == "put":
        return K * np.exp(-r * T) * standard_normal_cdf(-d2) - S * standard_normal_cdf(-d1)
    
    elif optionType == "msm_call":
        d1, d2, effective_vol = get_future_volatility(S, K, T, σ, r, optionType, data)
        return (S * standard_normal_cdf(d1) - K * np.exp(-r * T) * standard_normal_cdf(d2)), effective_vol