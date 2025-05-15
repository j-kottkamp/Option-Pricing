from models.bsm_option_pricing import optionPricing
from utils.calc_time_delta import calcTimeDelta
from models.mc_option_pricing import dynamicPrice


def main():
    strike = "23.05.2025"
    delta = calcTimeDelta(strike)
    S =  100 # Recent price
    K = 100 # Strike price
    T = delta/252 # Time to maturity (years)
    σ = 0.0729 # Volatility/ Std. deviation
    r = 0.05 # Risk free rate
    optionType = "bsm_call" # str, "bsm_call", "bsm_put", "bsm_msm_call" or "mc_msm_call"
    data = {"ticker": "AAPL",
            "tf": "15Min",
            "limit": "10000",
            "adj": "raw",
            "feed": "sip",
            "sort": "asc",
            "start": "2024-04-09",
            "end": "2024-04-26",
            "live": False}

    
    
    if optionType == "bsm_msm_call": # BSM pricing with estimated effective vol.
        price, eff_vol = optionPricing(S, K, T, σ, r, optionType, data)
        print(f"Fair price for MSM-Call option is {price:.4f}")
        print(f"Effective integrated volatility: {eff_vol:.4f}")
    elif optionType == "bsm_call" or "bsm_put": # Standart BSM pricing
        price = optionPricing(S, K, T, σ, r, optionType, data)
        print(f"Fair price for {optionType} option is {price:.4f}")
    elif optionType == "mc_msm_call": # Monte Carlo simulation of Markov Switching Multifractal valuation
        price = dynamicPrice(S, K, T, σ, r, optionType, data)
        print(f"Fair price for {optionType} option is {price:.4f}")
    return price
    
if __name__ == "__main__":
    main()