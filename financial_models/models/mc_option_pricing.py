import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utils.msm_future_volatility import MSMModel
from utils.live_stock_data import getHistData

def calculate_dynamic_volatility(returns, levels=4):
    model = MSMModel(returns, levels=levels)
    start_params = np.array([-2.0, 2.0] + [0.5] * levels)
    result = model.fit(start_params=start_params, method="bfgs", maxiter=2000)
    fitted_params = result.params

    sigma = np.exp(fitted_params[0])
    m = fitted_params[1]
    lambdas = 1 / (1 + np.exp(-fitted_params[2:]))

    n = len(returns)
    states = np.ones((levels, n))
    for i in range(levels):
        for t in range(1, n):
            if np.random.rand() < lambdas[i]:
                states[i, t] = m if states[i, t-1] == 1 else 1
            else:
                states[i, t] = states[i, t-1]

    sigmas_t = sigma * np.sqrt(np.prod(states, axis=0))
    return sigmas_t

def dynamicPrice(s, K, T, σ, r, optionType, data):
    df, years = getHistData(data)
    returns = np.log(df.close / df.close.shift(1)).dropna()

    steps = int(np.ceil(T * 252))
    dt = T / steps
    S = np.zeros(steps)
    S[0] = s

    dynamic_vol = np.zeros(steps)
    initial_vol = calculate_dynamic_volatility(returns)
    dynamic_vol[0] = initial_vol[-1]

    normal = np.random.standard_normal(steps)

    for i in range(1, steps):
        if i == 1:
            ret = returns.iloc[-1]
        else:
            ret = np.log(S[i-1] / S[i-2])

        updated_returns = returns._append(pd.Series([ret]), ignore_index=True)
        vol_series = calculate_dynamic_volatility(updated_returns)
        dynamic_vol[i] = vol_series[-1]

        S[i] = S[i - 1] * np.exp((r - 0.5 * dynamic_vol[i]**2) * dt + dynamic_vol[i] * np.sqrt(dt) * normal[i])

    plt.plot(S)
    plt.title('Simulierter Verlauf des Preises mit dynamischer Volatilität')
    plt.xlabel('Tage')
    plt.ylabel('Preis')
    plt.show()

    return S
