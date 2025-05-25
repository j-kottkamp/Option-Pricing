from utils.live_option_data import OptionData

def main():
    # Available data is:
    available = ['all', 'contractSymbol', 'strike', 'currency', 'lastPrice', 'change',
       'percentChange', 'volume', 'openInterest', 'bid', 'ask', 'contractSize',
       'lastTradeDate', 'impliedVolatility', 'inTheMoney', 'timeToMaturity', 'moneyness', 'expirations']
    
    ticker = "NVDA"
    option_type = "call"
    data = "all" # List above (str), "all" for full dataframe
    create_matrix = True # Requieres 3 Parameters
    matrix_params = ["timeToMaturity", "moneyness", "impliedVolatility"] # list (str), [index, columns, values]
    full = True # (bool), False returns densest submatrix
    
    option = OptionData(ticker, option_type)
    if data in available:
        if create_matrix:
            print(option.create_option_matrix(matrix_params, full))
        else:
            if data == "all":
                print(option.return_full_data())
            else:
                print(option.get_option_data(data))
    else:
        raise ValueError("Request valid data. Must be in list above")
    
if __name__ == "__main__":
    main()