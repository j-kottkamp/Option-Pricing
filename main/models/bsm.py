
from imports import np
from utils.std_normal_cdf import standard_normal_cdf

class BSMModel:
    def __init__(self, S=100, K=100, T=1, r=0.05, sigma=0.2):
        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma
        self.d1 = None
        self.d2 = None
        
    
    def calc_d(self):
        d1 = (np.log(self.S / self.K) + (self.r + 0.5 * self.sigma**2) * (self.T)) / (self.sigma * np.sqrt(self.T))
        d2 = d1 - self.sigma * np.sqrt(self.T)
        self.d1 = d1
        self.d2 = d2

    def price_option(self, optionType):
        if self.T <= 0:
            if optionType == 'call':
                return max(0, self.S - self.K)
            elif optionType == 'put':
                return max(0, self.K - self.S)
            
        self.calc_d()
        if optionType == 'call':
            return self.S * standard_normal_cdf(self.d1) - self.K * np.exp(-self.r * self.T) * standard_normal_cdf(self.d2)
        elif optionType == 'put':
            return self.K * np.exp(-self.r * self.T) * standard_normal_cdf(-self.d2) - self.S * standard_normal_cdf(-self.d1)
        