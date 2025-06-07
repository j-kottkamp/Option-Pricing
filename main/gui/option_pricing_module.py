from imports import st, pd, plt, np, sns, datetime
from models.bsm import BSMModel
from models.msm import MSMModel
from utils.create_heatmap import create_heatmap_matrix
from utils.calc_time_delta import calc_time_delta
from utils.calc_profit import profit_simulation

def get_range_input(param_name: str):
        if param_name == "Volatility (σ)":
            min_val = st.sidebar.slider(f"{param_name} min", min_value=0.0, value=0.0)
            max_val = st.sidebar.slider(f"{param_name} max", min_value=0.0, value=1.0)
            return min_val, max_val
        else:
            min_val = st.sidebar.number_input(f"{param_name} min", min_value=0.0, value=50.0)
            max_val = st.sidebar.number_input(f"{param_name} max", min_value=0.0, value=150.0)
            return min_val, max_val

class OptionPricingConfig:
    def __init__(self, S=100, K=100, r=0.05, sigma=0.2, T=1):
        self.model = None
        self.S = S
        self.K = K
        self.r = r
        self.sigma = sigma
        self.T = T
        self.option_types = ["call", "put"]
        self.top_call = None
        self.top_put = None
        self.market_price= None
        self.n_options = None
        self.calc_profit = None
        self.option_type = None
        
    
    def option_pricing_default_sidebar(self):
        sidebar_default = {"S": ("Current asset price", 0.0, 100.0),
                            "K": ("Strike price", 0.0, 100.0),
                            "r": ("Risk-free interest rate", 0.0, 0.05),
                            "sigma": ("Volatility (σ)", 0.0, 0.2)}
        
        for key, (description, min_val, default_val) in sidebar_default.items():
            setattr(self, key, st.sidebar.number_input(
            description,
            min_value=min_val, value=default_val
        ))
            
        date = st.sidebar.checkbox(
            "Use (float) for T?"
        )
        
        if date:
            self.T = st.sidebar.number_input(
                "Time to maturity in years",
                min_value=0.0, value=1.0
            )
            
        else:
            strike = st.sidebar.date_input(
                "Select the date of expiration",
                value=datetime.date.today() + datetime.timedelta(days=30)
            )
            strike = strike.strftime("%d.%m.%Y")

            delta = calc_time_delta(strike)
            self.T = delta/252
            
        return self.S, self.K, self.r, self.sigma, self.T
        
        
    def option_pricing_default(self):
        model_type = st.sidebar.selectbox(
            "Select the type of pricing model you want to use",
            ("Black-Scholes-Merton", "Markov-Switching Multifractal")
        )
        
        self.option_pricing_default_sidebar()
            
        self.calc_profit, self.option_type = self.calc_profit_sidebar_config()
        
        return model_type
    
    def calc_profit_sidebar_config(self):
        option_type = "call" # Default
        calc_profit = st.sidebar.checkbox(
        "Calculate expected profit for market price?"
        )
        if calc_profit:
            option_type = st.sidebar.selectbox(
                "Select the option type",
                self.option_types
            )
            calc_profit_params = {
                "market_price": ("Real price of the Option", 0.0, 10.0),
                "n_options": ("Number of options to buy", 0.0, 1000.0)
            }
            
            for key, (description, min, default) in calc_profit_params.items():
                setattr(self, key, st.sidebar.number_input(
                    description, 
                    min_value=min, value=default
                ))
                
        return calc_profit, option_type
    
    def profit_calculations(self, type, model):
        profit = {}        
        profit[type] = profit_simulation(option_price=self.market_price, S=self.S, K=self.K, 
                                         r=self.r, sigma=self.sigma, T=self.T, option_type=type)
        
        avg_profit, roi = profit[type]
        net_profit = avg_profit * self.n_options
        
        profit_df = pd.DataFrame({
        "Net Profit": [net_profit.round(2)],
        "Profit per Option": [avg_profit.round(4)],
        "Return on investment": [roi.round(2)],
        })
        
        st.markdown(f"## Estimated profit data for {type} Option when buying {self.n_options} options at {self.market_price}\\$ for {self.n_options * self.market_price}\\$")
        st.table(profit_df)
        if model == "bsm":
            st.write("Calculated from the Black-Scholes-Merton formula using 1Mio paths of a Geometric Brownian motion")
            st.latex(r"""
            S_t^{(i)} = S_0 \cdot \exp\left( \sum_{k=1}^{t} \left[ \left( \mu - \frac{1}{2} \sigma^2 \right) \Delta t + \sigma \sqrt{\Delta t} \cdot Z_k^{(i)} \right] \right)
            """)
        elif model == "msm":
            st.write("Calculated using 100k paths from the Markov-Switching Multifractal model.")
            st.write("A model using stochastic volatility to model scale invariance, fat tails, and long-term persistence.")
            st.latex(r"""
            \begin{aligned}
                r_t &= \sigma_t \cdot \varepsilon_t,\quad \varepsilon_t \sim \mathcal{N}(0, 1) \\
                \sigma_t^2 &= \sigma^2 \cdot \prod_{k=1}^{K} M_{k,t} \\
                M_{k,t} &\in \{m_0, m_1\}, \quad \text{with } \mathbb{P}(M_{k,t} = m_1) = \gamma_k \\
                \gamma_k &= 1 - (1 - \gamma_1)^{b^{k - 1}}
            \end{aligned}
            """)
         
    def bsm_config(self):
        self.model = BSMModel(S=self.S, K=self.K, T=self.T, r=self.r, sigma=self.sigma)
        st.title("Black-Scholes-Merton Model")
        st.markdown("## Parameter")
        
        params_df = pd.DataFrame({
            "Spot Price": [self.S],
            "Strike Price": [self.K],
            "Risk-free Interest Rate": [self.r],
            "Volatility": [self.sigma],
            "Time to Maturity": [self.T]
        })
        st.table(params_df)
        
        
        
        if self.calc_profit:
            self.profit_calculations(type=self.option_type, model="bsm")
        
        self.show_option_prices()
        
        self.heatmap_config()
        
    def msm_config(self):
        self.model = MSMModel(S=self.S, K=self.K, T=self.T, r=self.r, sigma=self.sigma)
        st.title("Markov-Switching Multifractal Model")
        st.markdown("## Parameter")
        
        params_df = pd.DataFrame({
            "Spot Price": [self.S],
            "Strike Price": [self.K],
            "Risk-free Interest Rate": [self.r],
            "Volatility": [self.sigma],
            "Time to Maturity": [self.T]
        })
        st.table(params_df)
        
        self.show_option_prices()
        
        if self.calc_profit:
            self.profit_calculations(type=self.option_type, model="msm")
               
    def show_option_prices(self):
        price = {}
        for type in self.option_types:
            price[type] = self.model.price_option(option_type=type)
            setattr(self, f"top_{type}", price[type])
            
        callBox, putBox = st.columns(2)

        with callBox:
            st.markdown(
            f"""
            <div style='
                background: linear-gradient(135deg, #4CAF50, #66BB6A);
                padding: 30px;
                border-radius: 16px;
                text-align: center;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                margin: 20px auto;
                max-width: 600px;
                transition: 0.3s ease-in-out;
            '>
                <p style='
                    color: #f1f1f1;
                    font-size: 24px;
                    margin: 0;
                    letter-spacing: 1.5px;
                '>CALL Value</p>
                <h2 style='
                    color: white;
                    font-size: 40px;
                    margin-top: 10px;
                    font-weight: 600;
                '>{self.top_call.round(3)}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

        with putBox:
            st.markdown(
            f"""
            <div style='
                background: linear-gradient(135deg, #E53935, #EF5350);
                padding: 30px;
                border-radius: 16px;
                text-align: center;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                margin: 20px auto;
                max-width: 600px;
                transition: 0.3s ease-in-out;
            '>
                <p style='
                    color: #f1f1f1;
                    font-size: 24px;
                    margin: 0;
                    letter-spacing: 1.5px;
                '>PUT Value</p>
                <h2 style='
                    color: white;
                    font-size: 40px;
                    margin-top: 10px;
                    font-weight: 600;
                '>{self.top_put.round(3)}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    def heatmap_config(self):
        st.sidebar.markdown("## Interactive Heatmap")
        
        try: 
            params_x = st.sidebar.selectbox(
                "Choose heatmap parameter (index):",
                ["Spot Price", "Strike Price", "Volatility (σ)", "Time to Maturity", "Risk-Free Rate"],
            )
            params_y = st.sidebar.selectbox(
                "Choose heatmap parameter (columns):",
                ["Volatility (σ)", "Strike Price", "Spot Price", "Time to Maturity", "Risk-Free Rate"],
            )
            
            st.sidebar.markdown("### Heatmap Parameters")

            x_min, x_max = get_range_input(params_x)
            y_min, y_max = get_range_input(params_y)
            
            matrices, x, y = create_heatmap_matrix(self.S, self.K, self.T, self.r, self.sigma, params_x, params_y, x_min, x_max, y_min, y_max)

            heatmap_call, heatmap_put = st.columns(2)
            
            with heatmap_call:
                fig, ax = plt.subplots(figsize=(8, 6))
                sns.heatmap(matrices[0], 
                            xticklabels=np.round(x, 2), 
                            yticklabels=np.round(y, 2), 
                            cmap="YlOrRd", 
                            annot=True, 
                            ax=ax)
                ax.set_xlabel(params_x)
                ax.set_ylabel(params_y)
                ax.set_title("CALL Heatmap")
                st.pyplot(fig)
            
            with heatmap_put:
                fig, ax = plt.subplots(figsize=(8, 6))
                sns.heatmap(matrices[1], 
                            xticklabels=np.round(x, 2), 
                            yticklabels=np.round(y, 2), 
                            cmap="YlOrRd", 
                            annot=True, 
                            ax=ax)
                ax.set_xlabel(params_x)
                ax.set_ylabel(params_y)
                ax.set_title("PUT Heatmap")
                st.pyplot(fig)
        except:
            st.error("Please select two distinct parameters for the heatmap")
            
    
        


                
            