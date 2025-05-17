import numpy as np
import matplotlib.pyplot as plt

class MSMModel:
    def __init__(self, k=8, m0=0.8, m1=1.2, gamma=None, sigma_base=0.2, S0=100, r=0.05, T=1, dt=1/252):
        """
        Initialize the Markov Switching Multifractal (MSM) model.

        Parameters:
            k (int): Number of volatility components.
            m0 (float): Low volatility state value.
            m1 (float): High volatility state value.
            gamma (list): Transition probabilities for each component.
            sigma_base (float): Base volatility level.
            S0 (float): Initial asset price.
            r (float): Risk-free rate.
            T (float): Time to maturity (years).
            dt (float): Time step size (e.g., daily = 1/252).
        """
        self.k = k
        self.m0 = m0
        self.m1 = m1
        self.sigma_base = sigma_base
        self.S0 = S0
        self.r = r
        self.T = T
        self.dt = dt
        self.n_steps = int(T / dt)
        
        # Set default gamma if not provided (decaying transitions)
        if gamma is None:
            self.gamma = np.array([0.5 * (4 ** (1 - i)) for i in range(1, k+1)])
        else:
            self.gamma = np.array(gamma)
        
        if len(self.gamma) != k:
            raise ValueError(f"gamma must have length {k}")

    def monte_carlo_simulate(self, n_sims=10000):
        """
        Simulate asset price paths using the MSM model.

        Parameters:
            n_sims (int): Number of Monte Carlo simulations.
        Returns:
            S_T (np.array): Terminal asset prices for all simulations.
        """
        # Initialize states (each component randomly m0 or m1)
        current_states = np.random.choice([self.m0, self.m1], size=(n_sims, self.k))
        logS = np.log(self.S0) * np.ones(n_sims)
        
        
        for _ in range(self.n_steps):
            # Generate transitions for all components
            transitions = np.random.rand(n_sims, self.k) < self.gamma
            # Toggle states where transitions occur
            current_states = np.where(
                transitions,
                self.m1 - current_states + self.m0,  # Swaps m0 <-> m1
                current_states
            )
            # Compute instantaneous volatility
            product_components = np.prod(current_states, axis=1)
            sigma_t = self.sigma_base * np.sqrt(product_components)
            # Generate log returns
            dW = np.random.normal(0, 1, n_sims)
            log_return = (self.r - 0.5 * sigma_t**2) * self.dt + sigma_t * np.sqrt(self.dt) * dW
            logS += log_return
            
            
        
        # Convert to terminal prices
        S_T = np.exp(logS)
        return S_T

    def price_option(self, K, option_type='call', n_sims=10000):
        """
        Price a European option using Monte Carlo simulation.

        Parameters:
            K (float): Strike price.
            option_type (str): 'call' or 'put'.
            n_sims (int): Number of simulations.
        Returns:
            price (float): Option price.
        """
        S_T = self.monte_carlo_simulate(n_sims)
        if option_type == 'call':
            payoffs = np.maximum(S_T - K, 0)
        elif option_type == 'put':
            payoffs = np.maximum(K - S_T, 0)
        else:
            raise ValueError("option_type must be 'call' or 'put'")
        discount_factor = np.exp(-self.r * self.T)
        price = discount_factor * np.mean(payoffs)
        return price
    
    def simulate_paths(self, n_paths=20):
        current_states = np.random.choice([self.m0, self.m1], size=(n_paths, self.k))
        logS_paths = np.log(self.S0) * np.ones((self.n_steps + 1, n_paths))
        
        for t in range(1, self.n_steps + 1):
            transitions = np.random.rand(n_paths, self.k) < self.gamma
            current_states = np.where(
                transitions,
                self.m1 - current_states + self.m0,
                current_states
            )
            product_components = np.prod(current_states, axis=1)
            sigma_t = self.sigma_base * np.sqrt(product_components)
            dW = np.random.normal(0, 1, n_paths)
            log_return = (self.r - 0.5 * sigma_t**2) * self.dt + sigma_t * np.sqrt(self.dt) * dW
            logS_paths[t] = logS_paths[t - 1] + log_return
        
        S_paths = np.exp(logS_paths)
        return S_paths

# Example Usage
if __name__ == "__main__":
    # Initialize model with realistic parameters
    model = MSMModel(
        k=8,
        m0=0.8,
        m1=1.2,
        sigma_base=0.2,
        S0=100,
        r=0.05,
        T=1,
        dt=1/252
    )
    
    # Price a European call option
    call_price = model.price_option(K=100, option_type='call', n_sims=100000)
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
    print(f"European Call Option Price: {call_price:.2f}")
