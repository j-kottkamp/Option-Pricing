from models.bsm import BSMModel
from models.msm import MSMModel
from utils.calc_time_delta import calc_time_delta

def main():
    '''
    Parameters for option pricing:
    Required for all:
    - strike (dd.mm.yyyy): Date of maturity
    - S (int): Current stock price
    - K (int): Strike price
    - sigma (float): Base volatility
    - r (float): Risk-free interest rate
    - optionType (str): Type of option (e.g. "call" or "put")
    - pricingMethod (str): {"bsm": simple Black-Scholes-Merton modell
                            "mc_msm": Monte Carlo option pricing under the Markov-Switching Multifractal model
                            }
    
    Required for mc_msm:
    - k (int): Number of volatility components
    - m0 (float): Low volatility state value
    - m1 (float): High volatility state value
    - dt: Time steps
    - n: Number of simulations (for optimal performance 10k)
    '''
    strike = "23.06.2025" # %d.%m.%Y
    delta = calc_time_delta(strike)
    S =  100
    K = 100
    T = delta/252 # Use "delta/252" for Dates else (float) 
    sigma = 0.0729
    r = 0.05
    optionType = "put" # str, "call" or "put"
    pricingMethod = "msm" # "bsm" or "msm"
    k = 8
    m0 = 0.8
    m1 = 1.2
    dt = 1/252
    n = 100000
    data = {"ticker": "AAPL",
            "tf": "15Min",
            "limit": "10000",
            "adj": "raw",
            "feed": "sip",
            "sort": "asc",
            "start": "2024-04-09",
            "end": "2024-04-26",
            "live": False}

    if optionType == "call" or "put":
        
        if pricingMethod == "bsm":
            model = BSMModel(S=S, 
                             K=K, 
                             T=T, 
                             r=r, 
                             sigma=sigma)
            fairValue = model.price_option(optionType=optionType)
            print("--- Black-Scholes-Merton ---")
            print(f"The fair value of the {optionType} option is: {fairValue:.4f}")
        
        elif pricingMethod == "msm":
            model = MSMModel(
            k=k,
            m0=m0,
            m1=m1,
            sigma_base=sigma,
            S0=S,
            r=r,
            T=T,
            dt=dt
        )
            fairValue, _ = model.price_option(option_type=optionType, n_sims=n)
            print("--- Markov-Switching Multifractal ---")
            print(f"The fair value of the {optionType} option is: {fairValue:.4f}")
            
        else:
            raise ValueError(f"pricingMethod must be 'bsm' or 'msm'. Currently {pricingMethod}")
    else:
        raise ValueError(f"optionType must be 'call' or 'put'. Currently {optionType}")

if __name__ == "__main__":
    main()