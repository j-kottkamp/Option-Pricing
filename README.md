# Option Pricing Framework

## Overview
This project is a modular framework for option pricing and simulation, allowing the flexible application of various valuation models including:

Black-Scholes-Merton (BSM) model

Markov-Switching Multifractal (MSM) model

Hybrid approaches, e.g. BSM with MSM-based volatility

The system is built to analyze and simulate option prices under both constant and time-varying volatility regimes, supporting both academic exploration and real-world prototyping.

## Supported Models
Black-Scholes-Merton (BSM)
Standard European option pricing with constant volatility.

MSM (Markov-Switching Multifractal)
Volatility evolves via discrete regimes, switching over time. Simulates heteroskedastic returns and long-memory volatility.

Hybrid: BSM + MSM Volatility
Applies MSM-generated volatility to the BSM pricing framework.

## Planned Extensions
GUI for parameter tuning and visualization
Calibration comparison between models
American option support
Local & stochastic volatility models
Greek calculations (Delta, Gamma, Vega...)

## Academic Foundations
Black, F., & Scholes, M. (1973). The Pricing of Options and Corporate Liabilities.
Calvet, L. E., & Fisher, A. J. (2004). Forecasting Volatility using MSM models.
Hull, J. C. (2017). Options, Futures, and Other Derivatives.
