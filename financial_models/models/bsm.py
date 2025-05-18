import numpy as np
from utils.msm_future_volatility import get_future_volatility
from utils.std_normal_cdf import standard_normal_cdf

class BSMModel:
    def __init__(self, S=100, K=100, T=1, r=0.05, sigma=0.2, optionType="call"):
        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma
        self.optionType = optionType
        self.d1 = None
        self.d2 = None
        
    
    def calcd(self):
        t = 0   # Pricing time (today t=0)
        d1 = (np.log(self.S / self.K) + (self.r + 0.5 * self.sigma**2) * (self.T - t)) / self.sigma * np.sqrt(self.T - t)
        d2 = d1 - self.sigma * np.sqrt(self.T - t)
        self.d1 = d1
        self.d2 = d2

    def priceOption(self, optionType):
        self.calcd()
        if optionType == 'call':
            return self.S * standard_normal_cdf(self.d1) - self.K * np.exp(-self.r * self.T) * standard_normal_cdf(self.d2)
        elif optionType == 'put':
            return self.K * np.exp(-self.r * self.T) * standard_normal_cdf(-self.d2) - self.S * standard_normal_cdf(-self.d1)
        
        
        # elif optionType == "msm_call":
        #     d1, d2, effective_vol = get_future_volatility(S, K, T, σ, r, optionType, data)
        #     return (S * standard_normal_cdf(d1) - K * np.exp(-r * T) * standard_normal_cdf(d2)), effective_vol