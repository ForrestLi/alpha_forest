This is just for education purpose.

Please do not trade until you fully understand the risk
Only make educated bets when trading.

Simple Quantmental Trading Pipeline:

i) Select stocks based on Warren's favorite ROE indicator. 

ii) Use the Piotroski score to rank the stocks that pass the filter in step 1. Only select the top 20% for further analysis.

iii) Utilize human discretion to conduct additional research.

Just run alpha_pipeline.py first to store the target stocks' open high low volume related info into local database.

iv) Apply machine learning techniques (e.g. random forest, finrl) to train pricing features such as Bollinger Bands, 
moving average, mean-reversion related indicators (bias), other technical indicators (KDJ, RSI), and Markov-related patterns 
(e.g. several consecutive up/downs) to identify optimal buying/selling points (quantity and timing).

Just run run_forest to identify the most important features to be used to specific stocks.

vi) Besides that, there are some option trading strategies that can be utilized to minimize investing/trading cost
e.g. the cash secured put (but you may want to sell put only when premium is large enough, here need to use option
pricing tool to make wise decision)

Use the scripts under option_pricing folder

Next step, I will add support to apply ML by using intraday data & other info like M&A, company actions, retail
investor sentiment index in real time.

For video description, please view 
https://youtu.be/85erteJv8qI?si=X5SaU60WmMkh98H2