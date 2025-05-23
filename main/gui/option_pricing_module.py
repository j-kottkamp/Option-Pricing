from imports import st, pd, plt, np, sns
from models.bsm import BSMModel
from utils.create_heatmap import create_heatmap_matrix

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
    def __init__(self, 
                 model_type="Black-Scholes-Merton", 
                 S=100, 
                 K=100, 
                 r=0.05, 
                 sigma=0.2, 
                 T=1):
        self.model_type = model_type
        self.S = S
        self.K = K
        self.r = r
        self.sigma = sigma
        self.T = T
        self.topCall = None
        self.topPut = None
        
    def option_pricing_default(self):
        self.model_type = st.sidebar.selectbox(
            "Select the type of pricing model you want to use",
            ("Black-Scholes-Merton", "Markov-Switching Multifractal")
        )
        sidebar_default = {"S": ("Current asset price", 0.0, 100.0),
                      "K": ("Strike price", 0.0, 100.0),
                      "T": ("Time to maturity in years", 0.0, 1.0),
                      "r": ("Risk-free interest rate", 0.0, 0.05),
                      "sigma": ("Volatility (σ)", 0.0, 0.2)}
        
        for key, (description, min_val, default_val) in sidebar_default.items():
            setattr(self, key, st.sidebar.number_input(
            description,
            min_value=min_val, value=default_val
        ))
        
        return self.model_type
         
    def bsm_config(self):
        if self.model_type == "Black-Scholes-Merton":
            st.title("Black-Scholes-Merton Model")
            df = pd.DataFrame({
                "Spot Price": [self.S],
                "Strike Price": [self.K],
                "Risk-free Interest Rate": [self.r],
                "Volatility": [self.sigma],
                "Time to Maturity": [self.T]
            })
            st.table(df)
            
            
            model = BSMModel(S=self.S, K=self.K, T=self.T, r=self.r, sigma=self.sigma)
            callPrice = model.price_option(optionType="call")
            putPrice = model.price_option(optionType="put")
            
            self.topCall = callPrice
            self.topPut = putPrice
            
            self.show_option_prices()
            
            self.heatmap_config()
               
    def show_option_prices(self):
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
                '>{self.topCall.round(3)}</h2>
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
                '>{self.topPut.round(3)}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    def heatmap_config(self):
        st.sidebar.markdown("## Interactive Heatmap")
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

                
            