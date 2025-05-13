from models.mc_option_pricing import dynamicPrice

data = {"ticker": "SPY",
            "tf": "15Min",
            "limit": "10000",
            "adj": "raw",
            "feed": "sip",
            "sort": "asc",
            "start": "2024-04-20",
            "end": "2024-04-26", 
            "live": False}
dynamicPrice(100, 100, 0.1, 0.2, 0.05, "call", data) 