from imports import st
from utils.live_option_data import OptionData

class OptionAnalysisConfig:
    def __init__(self):
        self.x = 1
        
    def option_analysis_default(self):
        option_type = st.sidebar.selectbox(
            "Select option type",
            ("call", "put")
        )
        ticker = st.sidebar.text_input(
            "Enter ticker symbol",
            value="AAPL"
        )
        all = st.sidebar.checkbox(
            "Show full data?"
        )
        
        model = OptionData(ticker=ticker, option_type=option_type)
        
        if all != True:
            data = st.sidebar.selectbox(
                "Select data",
                ('strike', 'currency', 'lastPrice', 'change',
                'percentChange', 'volume', 'openInterest', 'bid', 'ask', 'contractSize',
                'lastTradeDate', 'impliedVolatility', 'inTheMoney', 'timeToMaturity', 'moneyness', 'expirations')
            )

            
            
            df = model.get_option_data(data=data)
        else:
            df = model.return_full_data()
            
        st.write(
            "For better readability, hover over top bar and click the three dots next to the data column.\nThen select 'Autosize'"
        )
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("No data available for the selected option.")

        
        
        
        