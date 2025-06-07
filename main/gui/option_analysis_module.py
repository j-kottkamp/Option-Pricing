from imports import st, np
from utils.live_option_data import OptionData
from models.msm import MSMModel
from models.bsm import BSMModel
from utils.live_stock_data import get_stock_data

class OptionAnalysisConfig:
    def __init__(self):
        self.option_type = "call" # Default values
        self.ticker = "AAPL"
        self.model = "Black-Scholes-Merton"
        self.chain = None
        
    def option_analysis_default(self):
        self.option_type = st.sidebar.selectbox(
            "Select option type",
            ("call", "put")
        )
        self.ticker = st.sidebar.text_input(
            "Enter ticker symbol",
            value="AAPL"
        )
        all = st.sidebar.checkbox(
            "Show full data?"
        )
        
        try:
            self.chain = OptionData(ticker=self.ticker, option_type=self.option_type)
        except:
            st.error("Please enter a valid ticker symbol. E.g., AAPL")
        
        if all != True:
            data_type = st.sidebar.selectbox(
                "Select data",
                ('strike', 'expiration', 'currency', 'lastPrice', 'change',
                'percentChange', 'volume', 'openInterest', 'bid', 'ask', 'contractSize',
                'lastTradeDate', 'impliedVolatility', 'inTheMoney', 'timeToMaturity', 'moneyness')
            )

            option_data = self.chain.get_option_data(data=data_type)
            
        else:
            option_data = self.chain.return_full_data()
            
        compare = st.sidebar.checkbox(
            "Compare data with models?"
        )
        if compare:
            self.model = st.sidebar.selectbox(
                "Select model",
                ("Markov-Switching Multifractal")
            )
            
            self.option_model_comparison()
            
        st.write(
            "For better readability, hover over top bar and click the three dots next to the data column.\nThen select 'Autosize'"
        )
        
        if option_data is not None and not option_data.empty:
            st.dataframe(option_data, use_container_width=True)
        else:
            st.warning("No data available for the selected option.")
            
    
    def option_model_comparison(self): # Working on implementing comparison between model and real price
        pass