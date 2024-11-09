import yfinance as yf
import matplotlib.pyplot as plt

ticker = yf.Ticker('BABA')

print(ticker.options)

expriation = ticker.options[2]
print(expriation)

option_chain = ticker.option_chain(expriation)

puts = option_chain.puts
puts = puts[puts.openInterest >= 200]
print(puts)
plt.figure(figsize=(10,8))
plt.plot(puts['strike'], puts['impliedVolatility'])
plt.show()

