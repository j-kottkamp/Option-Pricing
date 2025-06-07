from imports import st, datetime, plt, np, scipy, pd, os
from utils.gbm_generator import geometric_brownian_motion
from utils.gbm_generator import gbm_memmap
from utils.calc_time_delta import calc_time_delta


class GBMGeneratorConfig:
    def __init__(self):
        self.S = None
        self.sigma = None
        self.T = None
        self.drift = None
        self.n_sims = None
    
    def gbm_generator_default(self):
        sidebar_default = {"S": ("Current asset price", 0.0, 100.0),
                            "sigma": ("Volatility (σ)", 0.0, 0.2), 
                            "drift": ("Drift (Avg. annual growth)", None, 0.1)}
        
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
                "Time to generate in years",
                min_value=0.0, value=1.0
            )
            
        else:
            strike = st.sidebar.date_input(
                "Generate till date",
                value=datetime.date.today() + datetime.timedelta(days=364)
            )
            strike = strike.strftime("%d.%m.%Y")

            delta = calc_time_delta(strike)
            self.T = delta/252
            
        bitcoin_mode = st.sidebar.checkbox(
            "Bitcoin Mode (Just for Fun)",
            help="Uses 95% Vol. and 125% Drift. Estimated by Bitcoins 2024 Performance"
        )
        
        if bitcoin_mode:
            self.S = 100000.0
            self.sigma = 0.95
            self.drift = 1.25
            
        n_sims_col, n_lines_col = st.columns(2)
        with n_sims_col:
            self.n_sims = st.number_input("Number of simulations", min_value=1, value=100000, max_value=1000000, help="Expected 10 sec. and 1Gb per 1Mio")
        with n_lines_col:
            self.n_lines = st.number_input("Number of lines to plot", min_value=1, value=20, help="Number of individual lines to show. Does not represent the full data")
            
        # Doesnt return anything. Creates gbm_paths.dat file in "data" folder to minimize RAM usage
        n_steps, file_path = gbm_memmap(S0=self.S, mu=self.drift, sigma=self.sigma, T=self.T, n_sims=self.n_sims)
        
        self.calc_metrics(file_path, n_steps)
        self.plot_gbm(file_path, n_steps)
        
        try:
            os.remove(file_path)  # file_path = path to your .dat file
        except FileNotFoundError:
            pass
        
        
    
    def plot_gbm(self, file_path, n_steps):         
        S = np.memmap(filename=file_path, dtype="float32", mode="r", shape=(self.n_sims, n_steps + 1))
        
        paths , conf_intervals = st.columns(2)
        with paths:
            n_lines = min(self.n_lines, S.shape[1])
            line_numbers = np.random.randint(0, self.n_sims, size=n_lines)
            lines = S[line_numbers, :]

            fig, ax = plt.subplots(figsize=(10, 6))
            if n_lines == 1:
                ax.set_title(f"{n_lines} Sampled Geometric Brownian Motion Path")
            else:
                ax.set_title(f"{n_lines} Sampled Geometric Brownian Motion Paths")
            ax.set_xlabel("Time Steps (Days)")
            ax.set_ylabel("Price")
            
            for number in line_numbers:
                ax.plot(S[number, :], lw=0.8, alpha=0.7)
                
            st.pyplot(fig)
            
        with conf_intervals:
            time_steps = np.arange(S.shape[1])
            p = np.percentile(S, [5,25,50,75,95], axis=0)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.set_title(f"Median, 5-95% and 25-75% Confidence Intervals")
            ax.set_xlabel("Time Steps (Days)")
            ax.set_ylabel("Price")
            
            ax.fill_between(time_steps, p[0], p[4], alpha=0.2, label="5-95%")
            ax.fill_between(time_steps, p[1], p[3], alpha=0.4, label="25-75%")
            ax.plot(time_steps, p[2], color='k', lw=1.5, label="Median")
            st.pyplot(fig)

        S.flush()
        del S
        
        
    def calc_metrics(self, file_path, n_steps):
        S = np.memmap(filename=file_path, dtype="float32", mode="r", shape=(self.n_sims, n_steps + 1))
        
        S_T = S[:, -1]  
        S0 = S[0, 0] 

        mean_terminal = np.mean(S_T)
        std_terminal = np.std(S_T)
        skew_terminal = scipy.stats.skew(S_T)
        kurt_terminal = scipy.stats.kurtosis(S_T)


        prob_up = np.mean(S_T > S0)
        prob_loss = np.mean(S_T < S0)
        prob_2x = np.mean(S_T > 2 * S0)

        VaR_95 = np.percentile(S_T, 5)
        ES_95 = np.mean(S_T[S_T <= VaR_95]) if np.any(S_T <= VaR_95) else np.nan

        metrics = {
            "Mean Terminal Value": mean_terminal,
            "Std Terminal Value": std_terminal,
            "Skewness": skew_terminal,
            "Kurtosis": kurt_terminal,
            "Value at Risk (95%)": VaR_95,
            "Expected Shortfall (95%)": ES_95,
            "Probability S_T > S0": prob_up,
            "Probability S_T < S0": prob_loss,
            "Probability S_T > 2x S0": prob_2x,
        }

        st.subheader("📊 Statistical metrics of GBM-Simulation")
        df_metrics = pd.DataFrame.from_dict(metrics, orient="index", columns=["Value"])
        df_metrics.index.name = "Metric"
        st.dataframe(df_metrics.style.format("{:.4f}"))
        
        S.flush()
        del S