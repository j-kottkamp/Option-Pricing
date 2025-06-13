from imports import st, np, pd, plt, datetime, px, go
from utils.live_stock_data import get_stock_data

class StockDataConfig:
    def __init__(self):
        self.symbol = None
        self.tf = None
        self.tf_count = None
        self.start = None
        self.end = None
        self.live = None
        self.df = None
        
    def default_sidebar(self):
        self.live = st.sidebar.selectbox(
            "Live or Historical Data",
            ("Live", "Historical")
        )
        
        self.symbol = st.sidebar.text_input(
            "Enter stock symbol (e.g. AAPL, GOOG, MSFT)",
            value="AAPL",
        )
        
        if self.live == "Historical":
            self.start = st.sidebar.date_input(
                "Start Date",
                value=datetime.date.today() - datetime.timedelta(days=30 * 6),
            )
            
            self.end = st.sidebar.date_input(
                "End Date",
                value=datetime.date.today() - datetime.timedelta(days=30),
                max_value=datetime.date.today() - datetime.timedelta(days=1),
                help="Leave empty for data until now"
            )
            self.live = None
            
        elif self.live == "Live":
            use_start_date = st.sidebar.checkbox("Use Start Date?")
            if use_start_date:
                self.start = st.sidebar.date_input(
                    "Start Date",
                    value=datetime.date.today() - datetime.timedelta(days=5)
                )
            else:
                self.start = None
        
        self.tf = st.sidebar.selectbox(
            "Select Timeframe",
            ("Min", "Hour", "Day", "Week", "Month")
        )
        
        if self.tf == "Min":
            self.tf_count = st.sidebar.number_input(
                "Timeframe amount (e.g. 5Min, 30Min)",
                value=15, min_value=1, max_value=59
            )
        elif self.tf == "Hour":
            self.tf_count = st.sidebar.number_input(
                "Timeframe amount (Only 1 available)",
                value=1, min_value=1, max_value=1
            )
        if self.tf == "Day":
            self.tf_count = st.sidebar.number_input(
                "Timeframe amount (Only 1 available)",
                value=1, min_value=1, max_value=1
            )
        if self.tf == "Week":
            self.tf_count = st.sidebar.number_input(
                "Timeframe amount (Only 1 available)",
                value=1, min_value=1, max_value=1
            )
        if self.tf == "Month":
            self.tf_count = st.sidebar.selectbox(
                "Timeframe amount",
                ("1", "2", "3", "4", "6", "12")
            )
        
        timeframe_str = f"{self.tf_count}{self.tf}"
        return timeframe_str

    def stock_data_default(self):
        tf = self.default_sidebar()
        data = {"ticker": self.symbol,
                "tf": tf,
                "limit": "5000",
                "adj": "raw",
                "feed": "sip",
                "sort": "asc",
                "start": self.start,
                "end": self.end, 
                "live": self.live}
        
        try:
            self.df, years = get_stock_data(data)
            st.dataframe(self.df)
            self.plot_stock_data()
        except:
            st.error(f"Error fetching data. Try different ticker. Current: {self.symbol}")
        
        
    def price_to_color(self, val):
        start_value = self.df["close"].iloc[0]
        
        if val >= start_value:
            ratio = min((val - start_value) / start_value, 1)
            # Green to neutral
            return f"rgba({int(255 * (1 - ratio))}, 255, {int(255 * (1 - ratio))}, 1)"
        else:
            ratio = min((start_value - val) / start_value, 1)
            # Neutral to red
            return f"rgba(255, {int(255 * (1 - ratio))}, {int(255 * (1 - ratio))}, 1)"
    
    def plot_stock_data(self):
        colors = [self.price_to_color(p) for p in self.df["close"]]
        fig = go.Figure()

        for i in range(1, len(self.df["close"])):
            fig.add_trace(go.Scatter(
                x=self.df["timestamps"].iloc[i-1:i+1],
                y=self.df["close"].iloc[i-1:i+1],
                mode="lines",
                line=dict(color=colors[i], width=2),
                showlegend=False,
                hoverinfo="none"
            ))

        fig.add_trace(go.Scatter(
            x=self.df["timestamps"],
            y=self.df["close"],
            mode="lines",
            line=dict(color="rgba(0,0,0,0)", width=0),
            hoverinfo="x+y",
            name="Close"
        ))

        n = max(1, len(self.df) // 10)
        fig.update_layout(
            title=f"Price history of {self.symbol}",
            xaxis=dict(
                type='category',
                tickmode='array',
                tickvals=self.df["timestamps"][::n],
                ticktext=[ts.strftime('%Y-%m-%d %H:%M') for ts in self.df["timestamps"]][::n],
                tickangle=45,
                title='Date'
            ),
            yaxis_title="Price",
            template="plotly_white",
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)