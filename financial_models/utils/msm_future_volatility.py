import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from scipy.stats import norm
import statsmodels.api as sm
from statsmodels.base.model import GenericLikelihoodModel
from utils.live_stock_data import getStockData



class MSMModel(GenericLikelihoodModel):
    def __init__(self, endog, levels=4, **kwargs):
        self.levels = levels
        super(MSMModel, self).__init__(endog, **kwargs)

    def loglike(self, params):
        sigma = np.exp(params[0])  # Basisvolatilität (immer positiv)
        m = params[1]              # Multiplikator >1
        lambdas = params[2:]       # Wechselwahrscheinlichkeiten pro Level
        
        lambdas = 1 / (1 + np.exp(-lambdas))  # logit -> (0,1)
        
        n = len(self.endog)
        states = np.ones((self.levels, n))
        
        for i in range(self.levels):
            for t in range(1, n):
                if np.random.rand() < lambdas[i]:
                    states[i, t] = m if states[i, t-1] == 1 else 1
                else:
                    states[i, t] = states[i, t-1]

        sigmas_t = sigma * np.sqrt(np.prod(states, axis=0))
        
        llf = np.sum(norm.logpdf(self.endog, scale=sigmas_t))
        return llf

def simulate_future_msm(params, levels, steps):
    sigma = np.exp(params[0])
    m = params[1]
    lambdas = 1 / (1 + np.exp(-params[2:]))

    states = np.ones(levels)
    future_vol = np.zeros(steps)

    for t in range(steps):
        for i in range(levels):
            if np.random.rand() < lambdas[i]:
                states[i] = m if states[i] == 1 else 1
        sigma_t = sigma * np.sqrt(np.prod(states))
        future_vol[t] = sigma_t

    return future_vol

def fitModel(T, data):
    df, years = getHistData(data)
    returns = np.log(df.close / df.close.shift(1)).dropna()
    steps = int(np.ceil(T * 252))
    
    levels = 4
    model = MSMModel(returns, levels=levels)

    start_params = np.array([-2.0, 2.0] + [0.5] * levels)

    result = model.fit(start_params=start_params, method="bfgs", maxiter=2000)

    fitted_params = result.params
    
    return fitted_params, levels, steps

def get_future_volatility(S, K, T, σ, r, optionType, data):
    
    df, years = getHistData(data)
    returns = np.log(df.close / df.close.shift(1)).dropna()
    steps = int(np.ceil(T * 252))

    levels = 4
    model = MSMModel(returns, levels=levels)

    start_params = np.array([-2.0, 2.0] + [0.5] * levels)

    result = model.fit(start_params=start_params, method="bfgs", maxiter=2000)

    fitted_params = result.params

    σ = simulate_future_msm(fitted_params, levels, steps)
    
    dt = T / 252
    integrated_variance = np.sum((σ**2) * dt)
    effective_vol = np.sqrt(integrated_variance / T)
        
    d1 = (np.log(S / K) + (r + 0.5 * effective_vol**2) * T) / (effective_vol * np.sqrt(T))
    d2 = d1 - effective_vol * np.sqrt(T)
    
    return d1, d2, effective_vol



