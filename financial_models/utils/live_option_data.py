import yfinance as yf

ticker = yf.Ticker("AAPL")
expDates = ticker.options
optionChain = ticker.option_chain(expDates[0])

print(expDates)