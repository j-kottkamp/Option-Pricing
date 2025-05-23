from imports import st, pd, np, plt, sns
from models.bsm import BSMModel
from gui.option_pricing_module import OptionPricingConfig
from gui.main_config import main_config_page



def main():
    application = main_config_page()
    if application == "Option Pricing Module":
        module = OptionPricingConfig()
        model_type = module.option_pricing_default()
        if model_type == "Black-Scholes-Merton":
            module.bsm_config()

if __name__ == "__main__":
    main()