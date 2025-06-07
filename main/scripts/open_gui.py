from imports import st, pd, np, plt, sns
from models.bsm import BSMModel
from gui.option_pricing_module import OptionPricingConfig
from gui.option_analysis_module import OptionAnalysisConfig
from gui.gbm_generator_module import GBMGeneratorConfig
from gui.main_config import main_config_page



def main():
    application = main_config_page()
    if application == "Option Pricing Module":
        module = OptionPricingConfig()
        model_type = module.option_pricing_default()
        if model_type == "Black-Scholes-Merton":
            module.bsm_config()
        elif model_type == "Markov-Switching Multifractal":
            module.msm_config()
    elif application == "Option Data Analysis":
        module = OptionAnalysisConfig()
        module.option_analysis_default()
    elif application == "GBM Generator":
        module = GBMGeneratorConfig()
        module.gbm_generator_default()

if __name__ == "__main__":
    main()