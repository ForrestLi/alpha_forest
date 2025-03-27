import numpy as np
import pandas as pd

# Define parameters for both strategies
initial_portfolio_value = 100000
stock_price = 80
strike_price = 60
put_premium = 5
time_to_expiration = 30  # in days
cash_for_puts = 80000  # cash reserved to cover puts

# Define market environment
market_simulation_days = 250
np.random.seed(0)
returns = np.random.normal(loc=0.0001, scale=0.05, size=market_simulation_days)
stock_prices = stock_price * (1 + returns).cumprod()

# For both strategies
portfolio_values_puts = np.zeros(market_simulation_days)
portfolio_values_no_puts = np.zeros(market_simulation_days)

# Initial cash
cash_puts = initial_portfolio_value
cash_no_puts = initial_portfolio_value

# Stock ownership
owned_shares_puts = 0
owned_shares_no_puts = cash_no_puts // stock_price

for day in range(market_simulation_days):
    # Strategy with put options
    if stock_prices[day] < strike_price and cash_puts >= cash_for_puts:
        # Buy stock at strike price if put options are exercised
        owned_shares_puts += cash_for_puts // strike_price
        cash_puts -= owned_shares_puts * strike_price

    # Update portfolio value for put strategy
    portfolio_values_puts[day] = cash_puts + owned_shares_puts * stock_prices[day]
    if day % time_to_expiration == 0:
        cash_puts += put_premium * (cash_for_puts // strike_price)

    # Update portfolio value for no-put strategy
    portfolio_values_no_puts[day] = (
        cash_no_puts + owned_shares_no_puts * stock_prices[day]
    )


# Calculate total return and volatility
def calculate_metrics(portfolio_values):
    total_return = (portfolio_values[-1] / portfolio_values[0]) - 1
    volatility = np.std(np.diff(np.log(portfolio_values)))
    return total_return, volatility


return_puts, vol_puts = calculate_metrics(portfolio_values_puts)
return_no_puts, vol_no_puts = calculate_metrics(portfolio_values_no_puts)

print(f"Strategy with Puts: Return = {return_puts:.2%}, Volatility = {vol_puts:.2%}")
print(
    f"Strategy without Puts: Return = {return_no_puts:.2%}, Volatility = {vol_no_puts:.2%}"
)


# Compute maximum drawdown
def maximum_drawdown(portfolio_values):
    peak = np.maximum.accumulate(portfolio_values)
    drawdown = (portfolio_values - peak) / peak
    return drawdown.min()


dd_puts = maximum_drawdown(portfolio_values_puts)
dd_no_puts = maximum_drawdown(portfolio_values_no_puts)

print(f"Strategy with Puts: Max Drawdown = {dd_puts:.2%}")
print(f"Strategy without Puts: Max Drawdown = {dd_no_puts:.2%}")
