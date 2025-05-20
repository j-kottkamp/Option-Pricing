import pandas as pd
from yahooquery import Ticker
from datetime import datetime
import numpy as np

def get_option_matrix(symbol="NVDA", option_type="call"):
    t = Ticker(symbol)
    spot = t.price[symbol]['regularMarketPrice']
    chain = t.option_chain
    now = pd.Timestamp.now()

    calls = chain.xs("calls", level=2).reset_index()
    puts = chain.xs("puts", level=2).reset_index()
    
    calls["expirations"] = pd.to_datetime(calls["expiration"])
    
    calls["timeToMaturity"] = ((calls["expiration"] - now).dt.total_seconds() / (365 * 24 * 3600)).round(2)
    calls["moneyness"] = (calls["strike"] / spot).round(2)
    calls["strike"] = calls["strike"].round(2)
    
    optionMatrix = calls.pivot_table(
        index="timeToMaturity",
        columns="moneyness",
        values="lastPrice"
    )
    return optionMatrix
    

if __name__ == "__main__":
    optionMatrix = get_option_matrix(symbol="NVDA", option_type="call")
    print(optionMatrix)