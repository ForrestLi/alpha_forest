import math


def american_option_price(steps, S, K, r, sigma, T, q, option_type):
    dt = T / steps
    u = math.exp(sigma * math.sqrt(dt))
    d = 1 / u
    p = (math.exp((r - q) * dt) - d) / (u - d)

    payoff = [0] * (steps + 1)
    for i in range(steps + 1):
        ST = S * (u**i) * (d ** (steps - i))
        if option_type == "c":
            payoff[i] = max(ST - K, 0)
        elif option_type == "p":
            payoff[i] = max(K - ST, 0)

    for j in range(steps - 1, -1, -1):
        for i in range(j + 1):
            ST = S * (u**i) * (d ** (j - i))
            if option_type == "c":
                exercise_value = ST - K
            elif option_type == "p":
                exercise_value = K - ST
            payoff[i] = max(
                math.exp(-r * dt) * (p * payoff[i + 1] + (1 - p) * payoff[i]),
                exercise_value,
            )

    return payoff[0]


# Example usage
steps = 1000
S = 81.08  # Current BABA stock price  Sep 8th 2024
K = 72.5  # Strike price
r = 0.048  # Risk-free rate current United States 10-Year Bond Yield
sigma = 0.3453  # Volatility
T = 99  # Time to maturity
q = 0.02
option_type = "p"  # 'c' for call option, 'p' for put option

price = american_option_price(steps, S, K, r, sigma, T, q, option_type)
if option_type == "c":
    print(f"American Call Option Price: {price}")
elif option_type == "p":
    print(f"American Put Option Price: {price}")
