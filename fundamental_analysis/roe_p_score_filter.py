import time

import pandas as pd
from config.parser import logger

from fundamental_analysis.stock_info import Stock_Info
from utility import (
    vaid_hk_ticker_generator,
    vaid_shanghai_ticker_generator,
    vaid_shenzhen_ticker_generator,
    vaid_b_ticker_generator,
    vaid_techboard_ticker_generator,
)

stock_watch_list = []


def test_filter():
    for generator in [
        vaid_shenzhen_ticker_generator(),
        vaid_shanghai_ticker_generator(),
        vaid_hk_ticker_generator(),
        vaid_techboard_ticker_generator(),
        vaid_b_ticker_generator(),
    ]:
        for ticker in generator:
            try:
                stock = Stock_Info(ticker)
                roe = stock.roe_filter(0.2, 0.15)
                if roe[0]:
                    average_roe = roe[1]
                    stock_watch_list.append((ticker, average_roe))
                    logger.info(
                        f"ticker {ticker} with roe = {average_roe} has been appended to stock watch list"
                    )
                    pickle_file_path = "D:/alpha_forest/data"
                    yt = stock._ticker
                    for attr in dir(yt):
                        if isinstance(getattr(ticker, attr), pd.DataFrame):
                            yt.__getattribute__(attr).to_pickle(
                                f"{pickle_file_path}/{ticker}{attr}.pkl"
                            )
                time.sleep(1)
            except Exception as e:
                print(" ... failed", e)


# step 1:
test_filter()
stock_watch_list.sort(key=lambda a: a[1])
logger.info(f"raw stock watch list: {stock_watch_list}")

stock_watch_list_pscore = []

for ticker, _ in stock_watch_list:
    stock = Stock_Info(ticker)
    stock_watch_list_pscore.append((ticker, stock.piotroski_score()))
stock_watch_list_pscore.sort(key=lambda a: a[1])
print(stock_watch_list_pscore)

"""Rank from lowest score to highest score for further analysis: 
remove the ones less than score 5
[
('6113.HK', 5), ('1730.HK', 5), ('0669.HK', 5), ('002737.SZ', 5), ('0322.HK', 5), ('300770.SZ', 5), ('603606.SS', 5), 
('002475.SZ', 5), ('000333.SZ', 5), ('0300.HK', 5), ('0868.HK', 5), ('600563.SS', 5), ('1755.HK', 5), ('2020.HK', 5), 
('2155.HK', 5), ('002049.SZ', 5), ('000858.SZ', 5), ('600309.SS', 5), ('000661.SZ', 5), ('603091.SS', 5), 
('603082.SS', 5), ('601225.SS', 5), ('002027.SZ', 5), ('0151.HK', 5), ('300979.SZ', 5), ('0303.HK', 5), ('8512.HK', 
5), ('8371.HK', 5), ('002677.SZ', 5), ('603325.SS', 5), ('600803.SS', 5), ('1050.HK', 5), ('002555.SZ', 5), 
('1585.HK', 5), ('600519.SS', 5), ('2165.HK', 5), ('3658.HK', 5), ('6388.HK', 5), ('2439.HK', 5), ('1922.HK', 5), 
('600779.SS', 5), ('9633.HK', 5), ('1523.HK', 5), ('600961.SS', 5), ('2373.HK', 5), ('000707.SZ', 5), ('2367.HK', 5), 
('4332.HK', 5), ('002188.SZ', 5), ('0331.HK', 5), ('1579.HK', 6), ('1681.HK', 6), ('2276.HK', 6), ('6110.HK', 6), 
('002043.SZ', 6), ('601100.SS', 6), ('0990.HK', 6), ('001337.SZ', 6), ('002847.SZ', 6), ('2669.HK', 6), ('3306.HK', 
6), ('4336.HK', 6)]
 """
