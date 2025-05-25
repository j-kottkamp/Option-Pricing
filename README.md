# Option Pricing Framework

## Overview
This project is a modular framework for option pricing and simulation, allowing the flexible application of various valuation models including:

Black-Scholes-Merton (BSM) model

Markov-Switching Multifractal (MSM) model

The system is built to analyze and simulate option prices under both constant and time-varying volatility regimes, supporting both academic exploration and real-world prototyping.

## Supported Models
### Black-Scholes-Merton (BSM)
Standard European option pricing with constant volatility.

### [Markov-Switching Multifractal (MSM)](docs/msm.md)
Volatility evolves via discrete regimes, switching over time. Simulates heteroskedastic returns and long-memory volatility.

## Graphical User Interface - WiP!
Direct usage of most of the repositorys features via a functual user Interface.

## Planned Extensions
Calibration comparison between models

American option support

Greek calculations (Delta, Gamma, Vega...)

## Academic Foundations
Black, F., & Scholes, M. (1973). The Pricing of Options and Corporate Liabilities.

Calvet, L. E., & Fisher, A. J. (2004). Forecasting Volatility using MSM models.

Hull, J. C. (2017). Options, Futures, and Other Derivatives.
