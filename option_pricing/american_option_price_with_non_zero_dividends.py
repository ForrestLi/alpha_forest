import numpy as np


def calculate_option_price(S, K, r, T, N, sigma, div_dates, div_amounts):
    dt = T / N  # Time step
    u = np.exp(sigma * np.sqrt(dt))  # Up factor
    d = 1 / u  # Down factor
    p = (np.exp(r * dt) - d) / (u - d)  # Risk-neutral probability

    # Calculate the relevant stock prices at each node
    stock_prices = np.zeros((N + 1, N + 1))
    stock_prices[0, 0] = S
    for i in range(1, N + 1):
        stock_prices[i, 0] = stock_prices[i - 1, 0] * u
        for j in range(1, i + 1):
            stock_prices[i, j] = stock_prices[i - 1, j - 1] * d

    # Calculate the present value of dividends
    div_present_value = 0
    for div_date, div_amount in zip(div_dates, div_amounts):
        div_present_value += div_amount * np.exp(-r * div_date)

    # Calculate option prices at each node
    option_prices = np.zeros((N + 1, N + 1))
    early_exercise_indicator = np.zeros((N + 1, N + 1))
    for j in range(N + 1):
        option_prices[N, j] = max(
            0, stock_prices[N, j] - K - div_present_value
        )  # Option payoff at maturity

    for i in range(N - 1, -1, -1):
        for j in range(i + 1):
            option_prices[i, j] = np.exp(-r * dt) * (
                p * option_prices[i + 1, j + 1] + (1 - p) * option_prices[i + 1, j]
            )
            stock_price_ex_div = stock_prices[i, j] - div_present_value
            early_exercise = max(0, K - stock_price_ex_div)
            option_prices[i, j] = max(
                option_prices[i, j], early_exercise
            )  # Consider early exercise
            if early_exercise > 0:
                early_exercise_indicator[i, j] = 1  # Early exercise indicator

    return {
        "option_prices": option_prices,
        "early_exercise_indicator": early_exercise_indicator,
        # Other characteristics can also be calculated here
    }


# Example usage
S = 81.08  # Current BABA stock price  Sep 8th 2024
K = 72.5  # Strike price
r = 0.037  # Risk-free rate current United States 10-Year Bond Yield
T = 100  # Time to maturity
N = 100  # Number of time steps
sigma = 0.34  # Volatility
div_dates = [0]  # Dividend dates
div_amounts = [0]  # Dividend amounts

result = calculate_option_price(S, K, r, T, N, sigma, div_dates, div_amounts)
print(result["option_prices"])
print(result["early_exercise_indicator"])
