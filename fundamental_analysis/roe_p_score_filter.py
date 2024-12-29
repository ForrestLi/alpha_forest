import time
from asyncio.log import logger

import pandas as pd

from stock_info import Stock_Info
from utility import (
    vaid_hk_ticker_generator,
    vaid_shanghai_ticker_generator,
    vaid_shenzhen_ticker_generator,
    vaid_b_ticker_generator,
    vaid_techboard_ticker_generator, sp_500_generator,
)

stock_watch_list = []


def test_filter():
    for generator in [
        # vaid_shenzhen_ticker_generator(),
        # vaid_shanghai_ticker_generator(),
        # vaid_hk_ticker_generator(),
        # vaid_techboard_ticker_generator(),
        # vaid_b_ticker_generator(),
        sp_500_generator()
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

"""
US SP 500 ones

[('BALL', 5), ('RMD', 5), ('MPWR', 5), ('MNST', 5), ('SWKS', 5), ('WST', 5), ('KEYS', 5), ('JKHY', 5), ('GOOGL', 5), 
('GOOG', 5), ('META', 5), ('UNH', 5), ('DHI', 5), ('MKTX', 5), ('PHM', 5), ('URI', 5), ('NFLX', 5), ('REGN', 5), ('MMC', 5), 
('CDNS', 5), ('WM', 5), ('LYB', 5), ('ODFL', 5), ('CARR', 5), ('BR', 5), ('LULU', 5), ('CMG', 5), ('PG', 5), ('JNJ', 5),
 ('FDS', 5), ('TPR', 5), ('K', 5), ('CTAS', 5), ('EMR', 5), ('DG', 5), ('OMC', 5), ('NVDA', 5), ('CAT', 5), ('V', 5), 
 ('AMT', 5), ('NKE', 5), ('KO', 5), ('UNP', 5), ('ZTS', 5), ('ALLE', 5), ('TSCO', 5), ('PEP', 5), ('HSY', 5), ('GWW', 5), 
 ('ROK', 5), ('SPG', 5), ('SHW', 5), ('VRSK', 5), ('DVA', 5), ('AMGN', 5), ('AAPL', 5), ('CL', 5), ('KR', 6), ('CPRT', 6), 
 ('HII', 6), ('MOH', 6), ('CPAY', 6), ('FAST', 6), ('ADBE', 6), ('PAYX', 6), ('AMAT', 6), ('QCOM', 6), ('ADP', 6), ('IDXX', 6), 
 ('IT', 6), ('KMB', 6)]

"""