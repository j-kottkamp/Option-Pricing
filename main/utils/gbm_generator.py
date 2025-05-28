import numpy as np
import matplotlib.pyplot as plt

def geometric_brownian_motion(S0=100, μ=0.07, σ=0.2, T=1, N=252):
    dt = 1/252  # Time step size
    S = np.zeros(N + 1)
    S[0] = S0
    normal = np.random.standard_normal(size=N)  # Gauss dist.
    
    for t in range(N):
        dW = normal[t] * np.sqrt(dt)  # ΔW_t = √dt * Z_t
        S[t + 1] = S[t] * np.exp((μ - 0.5 * σ**2) * dt + σ * dW)
    
    if __name__ == "__main__":
        plt.plot(S)
        plt.title('Simulated path')
        plt.xlabel('Days')
        plt.ylabel('Price')
        plt.show()
    
    return S