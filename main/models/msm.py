from imports import np, plt

class MSMModel:
    def __init__(self, k=8, m0=0.8, m1=1.2, gamma=None, sigma=0.2, S=100, K=100, r=0.05, T=1, dt=1/252):
        """
            k: Number of volatility components.
            m0: Low volatility state value.
            m1: High volatility state value.
            gamma: Transition probabilities for each component.
            sigma: Base volatility level.
            S: Initial asset price.
            r: Risk-free rate.
            T: Time to maturity (years).
            dt: Time step size (e.g., daily = 1/252).
        """
        self.k = k
        self.m0 = m0
        self.m1 = m1
        self.sigma = sigma
        self.S = S
        self.K = K
        self.r = r
        self.T = T
        self.dt = dt
        self.n_steps = int(T / dt)
        
        if gamma is None:
            self.gamma = np.array([0.5 * (4 ** (1 - i)) for i in range(1, k+1)]) # Simplified version to lower computational cost
        else:
            self.gamma = np.array(gamma)
        
        if len(self.gamma) != k:
            raise ValueError(f"gamma must have length {k}")

    def monte_carlo_simulate(self, n_sims=100000):
        # S_T (np.array): Terminal asset prices for all simulations.

        current_states = np.random.choice([self.m0, self.m1], size=(n_sims, self.k))
        logS = np.log(self.S) * np.ones(n_sims)
        
        
        for _ in range(self.n_steps):
            transitions = np.random.rand(n_sims, self.k) < self.gamma
            current_states = np.where(
                transitions,
                self.m1 - current_states + self.m0,  # Swaps m0 <-> m1
                current_states
            )
            product_components = np.prod(current_states, axis=1)
            sigma_t = self.sigma * np.sqrt(product_components)
            dW = np.random.standard_normal(n_sims)
            log_return = (self.r - 0.5 * sigma_t**2) * self.dt + sigma_t * np.sqrt(self.dt) * dW
            logS += log_return
            
        S_T = np.exp(logS)
        return S_T

    def price_option(self, option_type='call', n_sims=100000):
        """
            K (float): Strike price.
            option_type (str): 'call' or 'put'.
            n_sims: Number of simulations. Preferably 100000 for optimal performance results 
        """
        S_T = self.monte_carlo_simulate(n_sims)
        if option_type == 'call':
            payoffs = np.maximum(S_T - self.K, 0)
        elif option_type == 'put':
            payoffs = np.maximum(self.K - S_T, 0)
        else:
            raise ValueError("option_type must be 'call' or 'put'")
        discount_factor = np.exp(-self.r * self.T)
        price = discount_factor * np.mean(payoffs)
        
        if __name__ == "__main__":
            return price, S_T # return S_T only for histogram when running from this file (alone)
        return price
    
    def simulate_paths(self, n_paths=20):
        current_states = np.random.choice([self.m0, self.m1], size=(n_paths, self.k))
        logS_paths = np.log(self.S) * np.ones((self.n_steps + 1, n_paths))
        
        for t in range(1, self.n_steps + 1):
            transitions = np.random.rand(n_paths, self.k) < self.gamma
            current_states = np.where(
                transitions,
                self.m1 - current_states + self.m0,
                current_states
            )
            product_components = np.prod(current_states, axis=1)
            sigma_t = self.sigma * np.sqrt(product_components)
            dW = np.random.normal(0, 1, n_paths)
            log_return = (self.r - 0.5 * sigma_t**2) * self.dt + sigma_t * np.sqrt(self.dt) * dW
            logS_paths[t] = logS_paths[t - 1] + log_return
        
        S_paths = np.exp(logS_paths)
        return S_paths

if __name__ == "__main__":
    '''
    Initialize without modularity directly from this file 
    for visualization of generated movements
    '''
    model = MSMModel(
        k=8,
        m0=0.8,
        m1=1.2,
        sigma=0.25,
        S=100,
        K=100,
        r=0.05,
        T=252/252,
        dt=1/252
    )
    
    call_price, S_T = model.price_option(option_type='call', n_sims=100000)
    
    simulated_paths = model.simulate_paths(n_paths=1)
    time_grid = np.linspace(0, model.T, model.n_steps + 1)
    plt.figure(figsize=(12, 6))
    for i in range(simulated_paths.shape[1]):
        plt.plot(time_grid, simulated_paths[:, i], alpha=0.7)
    plt.title("Simulated Asset Price Paths under MSM Model")
    plt.xlabel("Time (Years)")
    plt.ylabel("Asset Price")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
    plt.hist(S_T, bins=100)
    plt.title("Histogramm der simulierten Endpreise S_T")
    plt.xlabel("S_T")
    plt.ylabel("Häufigkeit")
    plt.show()
    print(f"European Call Option Price: {call_price:.2f}")
