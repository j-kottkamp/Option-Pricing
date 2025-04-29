from models.bsm_option_pricing import optionPricing
import datetime

def calcTime(strike):
    now = datetime.date.today()
    strikeDate = datetime.datetime.strptime(strike, "%d.%m.%Y").date()
    
    return (strikeDate - now).days

def main():
    strike = "23.05.2025"
    delta = calcTime(strike)
    S =  100 # Recent price
    K = 100 # Strike price
    T = delta/252 # Time to maturity (years)
    σ = 0.0729 # Volatility/ Std. deviation
    r = 0.05 # Risk free rate
    optionType = "call" # str, "call", "put" or "msm_call"
    data = {"ticker": "AAPL",
            "tf": "15Min",
            "limit": "10000",
            "adj": "raw",
            "feed": "sip",
            "sort": "asc",
            "start": "2024-04-09",
            "end": "2024-04-26",
            "live": False}

    
    
    if optionType == "msm_call":
        price, eff_vol = optionPricing(S, K, T, σ, r, optionType, data)
        print(f"Fair price for MSM-Call option is {price:.4f}")
        print(f"Effective integrated volatility: {eff_vol:.4f}")
    else:
        price = optionPricing(S, K, T, σ, r, optionType, data)
        print(f"Fair price for {optionType} option is {price:.4f}")
        
    return price
    
if __name__ == "__main__":
    main()