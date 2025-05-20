from utils.live_option_data import OptionData

def main():
    # Available data is:
    available = ['Full', 'contractSymbol', 'strike', 'currency', 'lastPrice', 'change',
       'percentChange', 'volume', 'openInterest', 'bid', 'ask', 'contractSize',
       'lastTradeDate', 'impliedVolatility', 'inTheMoney', 'timeToMaturity', 'moneyness', 'expirations']
    
    ticker = "NVDA"
    optionType = "call"
    data = "Full" # List above (str), "Full" for full dataframe
    createMatrix = True # Requieres 3 Parameters
    matrixParams = ["timeToMaturity", "moneyness", "impliedVolatility"] # list (str), [index, columns, values]
    
    option = OptionData(ticker, optionType, data)
    if data in available:
        if createMatrix:
            print(option.create_option_matrix(matrixParams))
        else:
            if data == "Full":
                print(option.return_full_data())
            else:
                print(option.get_option_data())
    else:
        raise ValueError("Request valid data. Must be in list above")
    
if __name__ == "__main__":
    main()