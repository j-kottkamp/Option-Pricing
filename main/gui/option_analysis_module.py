from imports import np, pd, st
from utils.live_option_data import OptionData

class OptionAnalysisConfig:
    def __init__(self):
        self.x = 1
        
    def option_analysis_default(self):
        option_type = st.sidebar.selectbox(
            "Select Option Type",
            ("call", "put")
        )
        ticker = st.sidebar.text_input(
            "Enter Ticker Symbol",
            value="AAPL"
        )
        all = st.sidebar.checkbox(
            "Show Full Data?"
        )
        
        model = OptionData(ticker=ticker, option_type=option_type)
        
        if all != True:
            data = st.sidebar.selectbox(
                "Select Data Type",
                ('contractSymbol', 'strike', 'currency', 'lastPrice', 'change',
                'percentChange', 'volume', 'openInterest', 'bid', 'ask', 'contractSize',
                'lastTradeDate', 'impliedVolatility', 'inTheMoney', 'timeToMaturity', 'moneyness', 'expirations')
            )

            
            
            df = model.get_option_data(data=data)
        else:
            df = model.return_full_data()
            
        if df is not None and not df.empty:
            st.dataframe(df)
        else:
            st.warning("No data available for the selected option.")

        
        
        
        