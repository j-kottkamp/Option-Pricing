from imports import np, plt

def geometric_brownian_motion(S0=100, μ=0.07, σ=0.2, T=1, N=252, n_sims=1000000):
    dt = 1 / 252
    Z = np.random.standard_normal((N, n_sims))
    increments = ((μ - 0.5 * σ**2) * dt + σ * np.sqrt(dt) * Z)
    log_returns = np.vstack([np.zeros(n_sims), increments.cumsum(axis=0)])
    S = S0 * np.exp(log_returns)
    return S

if __name__ == "__main__":
    S = geometric_brownian_motion()
    print(S.shape, S[-1].mean(), S[-1].std())