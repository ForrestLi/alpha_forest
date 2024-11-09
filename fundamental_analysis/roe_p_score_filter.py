import math
import time

import pandas as pd
import yfinance as yf
from config.parser import logger

from utilities import vaid_hk_ticker_generator, vaid_shanghai_ticker_generator, vaid_shenzhen_ticker_generator, \
    vaid_b_ticker_generator, vaid_techboard_ticker_generator

"""
 In a 1987 letter to shareholders, Buffett said that a good investment must meet the following two conditions: 
 one is that the average ROE for the past ten years is higher than 20%, and the other is that the ROE for no one year 
 in the past ten years is less than 15%. 
 Buffett attached great importance to the ROE indicator
"""


class Stock_Info:
    def __init__(self, ticker):
        self._ticker = yf.Ticker(ticker)
        self.ticker_name = ticker

    def piotroski_score(self):

        """
        The Piotroski score is broken down into the following categories:
        Profitability （4 points):

        Net Income (1 point)
        Positive return on assets in the current year (1 point)
        Positive operating cash flow in the current year (1 point)
        Cash flow from operations being greater than net Income (quality of earnings) (1 point)

        Leverage, liquidity, and source of funds (3 points)

        Lower ratio of long term debt in the current period, compared to the previous year (decreased leverage) (1 point)
        Higher current ratio this year compared to the previous year (more liquidity) (1 point)
        No new shares were issued in the last year (lack of dilution) (1 point).


        Operating efficiency (2 points)
        A higher gross margin compared to the previous year (1 point)
        A higher asset turnover ratio compared to the previous year (1 point)
        If a company has a score of 8 or 9, it is considered a good value.
        If the score adds up to between 0-2 points, the stock is considered weak
        """

        return self.get_p_profitability_score() + self.get_p_liquidity_score() + self.get_p_operating_efficiency()

    def yearly_dividend(self, year):
        dividends = self._ticker.dividends.resample('YE').sum()
        return dividends.loc[year].values[year]

    def latest_net_income(self):
        income_statement = self._ticker.income_stmt
        net_income = income_statement.iloc[:, 0]['Net Income']
        return net_income

    def latest_operating_cash_flow(self):
        cash_statement = self._ticker.cash_flow
        operating_cash_flow = cash_statement.iloc[:, 0]['Operating Cash Flow']
        return operating_cash_flow

    def latest_return_on_asset(self):
        balance_sheet = self._ticker.balance_sheet
        total_asset = balance_sheet.iloc[:, 0]['Total Assets']
        return self.latest_net_income() / total_asset

    def current_ratio_comparator(self):
        balance_sheet = self._ticker.balance_sheet
        latest_current_assets = balance_sheet.iloc[:, 0].get('Current Assets')
        latest_current_liabilities = balance_sheet.iloc[:, 0].get('Current Liabilities')
        prev_current_assets = balance_sheet.iloc[:, 1].get('Current Assets')
        prev_current_liabilities = balance_sheet.iloc[:, 1].get('Current Liabilities')
        if latest_current_assets and latest_current_liabilities and prev_current_assets and prev_current_liabilities:
            latest_one = latest_current_assets / latest_current_liabilities
            pre_one = prev_current_assets / prev_current_liabilities
            print({f'Ticker: {self.ticker_name} current ratio latest {latest_one} pre one {pre_one}'})
            return latest_one > pre_one
        else:
            return False

    def get_p_profitability_score(self):
        s = 0
        if self.latest_net_income() > 1:
            s += 1
        if self.latest_operating_cash_flow() > 1:
            s += 1
        if self.latest_return_on_asset() > 1:
            s += 1
        if self.latest_operating_cash_flow() > self.latest_net_income():
            s += 1
        return s

    def shares_diluted_or_not(self):
        current_shares = self._ticker.get_shares_full('2023-09-01')
        try:
            if current_shares:
                shares_one_year_ago = current_shares.iloc[0]
                latest_share_num = current_shares.iloc[-1]
                if shares_one_year_ago and latest_share_num:
                    return latest_share_num < shares_one_year_ago
            else:
                return False
        except:
            return False

    def higher_gross_margin_or_not(self):
        income_statement = self._ticker.income_stmt
        c_sales = income_statement.iloc[:, 0]['Total Revenue']
        c_cogs = income_statement.iloc[:, 0].get('Cost of Revenue')
        if c_cogs:
            c_gross_margin = (c_sales - c_cogs) / c_cogs
        else:
            return 0
        p_sales = income_statement.iloc[:, 1]['Total Revenue']
        p_cogs = income_statement.iloc[:, 1]['Cost of Revenue']
        p_gross_margin = (p_sales - p_cogs) / p_cogs
        print(f'current gross margin: {c_gross_margin} previous gross margin:{p_gross_margin}')
        return c_gross_margin > p_gross_margin

    def higher_asset_turnover_ratio_or_not(self):
        income_statement = self._ticker.income_stmt
        c_sales = income_statement.iloc[:, 0]['Total Revenue']
        p_sales = income_statement.iloc[:, 1]['Total Revenue']
        balance_sheet = self._ticker.balance_sheet
        c_total_asset = balance_sheet.iloc[:, 0]['Total Assets']
        p_total_asset = balance_sheet.iloc[:, 1]['Total Assets']
        pp_total_asset = balance_sheet.iloc[:, 2]['Total Assets']

        c_asset_turnover_ratio = 2 * c_sales / (c_total_asset + p_total_asset)
        p_asset_turnover_ratio = 2 * p_sales / (c_total_asset + p_total_asset)
        print(
            f'current asset_turnover_ratio: {c_asset_turnover_ratio} previous asset_turnover_ratio:{p_asset_turnover_ratio}')
        return c_asset_turnover_ratio > p_asset_turnover_ratio

    def get_p_liquidity_score(self):
        s = 0
        balance_sheet = self._ticker.balance_sheet
        current_long_deb = balance_sheet.iloc[:, 0].get('Long Term Debt')
        pre_long_deb = balance_sheet.iloc[:, 1].get('Long Term Debt')
        if not current_long_deb or pre_long_deb:
            current_long_deb = balance_sheet.iloc[:, 0].get('Long Term Debt And Capital Lease Obligation')
            pre_long_deb = balance_sheet.iloc[:, 1].get('Long Term Debt And Capital Lease Obligation')
        if current_long_deb and pre_long_deb:
            if current_long_deb < pre_long_deb:
                s += 1
        if self.current_ratio_comparator():
            s += 1
        if self.shares_diluted_or_not():
            s += 1

        return s

    def get_p_operating_efficiency(self):
        s = 0
        if self.higher_gross_margin_or_not():
            s += 1
        if self.higher_asset_turnover_ratio_or_not():
            s += 1
        return s

    def roe_filter(self, average_roe_requriement, min_roe_requirement):
        income_statement = self._ticker.income_stmt
        balance_sheet = self._ticker.balance_sheet
        row_num = income_statement.shape[1]
        roe_sum = 0
        n = 0
        for i in range(row_num):
            net_income = income_statement.iloc[:, i]['Net Income']
            if not math.isnan(net_income):
                common_stock_equity = balance_sheet.iloc[:, i]['Common Stock Equity']
                roe = net_income / common_stock_equity
                if roe < min_roe_requirement:
                    print(f'roe of {self.ticker_name} {roe} is less than {min_roe_requirement}')
                    return False, 0
                else:
                    roe_sum += roe
                    n += 1
        average_roe = roe_sum / n
        print(f'average roe of {self.ticker_name} is {average_roe}')
        #filter out companies with history less than 4 years
        if average_roe >= average_roe_requriement and n > 3:
            return True, average_roe
        else:
            return False, average_roe


stock_watch_list = []


def test_filter():
    for generator in [vaid_shenzhen_ticker_generator(), vaid_shanghai_ticker_generator(),vaid_hk_ticker_generator(),
                      vaid_techboard_ticker_generator(), vaid_b_ticker_generator()]:
        for ticker in generator:
            try:
                stock = Stock_Info(ticker)
                roe = stock.roe_filter(0.2, 0.15)
                if roe[0]:
                    average_roe = roe[1]
                    stock_watch_list.append((ticker, average_roe))
                    logger.info(f'ticker {ticker} with roe = {average_roe} has been appended to stock watch list')
                    pickle_file_path = 'D:/alpha_forest/data'
                    yt = stock._ticker
                    for attr in dir(yt):
                        if isinstance(getattr(ticker, attr), pd.DataFrame):
                            yt.__getattribute__(attr).to_pickle(f'{pickle_file_path}/{ticker}{attr}.pkl')
                time.sleep(1)
            except Exception as e:
                print(' ... failed', e)


# step 1:
test_filter()
stock_watch_list.sort(key=lambda a: a[1])
logger.info(f'raw stock watch list: {stock_watch_list}')

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

