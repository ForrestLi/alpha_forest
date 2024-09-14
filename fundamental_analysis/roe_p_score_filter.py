import math
import time

from config.parser import logger

from utilities import vaid_hk_ticker_generator, vaid_shanghai_ticker_generator, vaid_shenzhen_ticker_generator
import yfinance as yf
import pandas as pd
import numpy as np

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
    for ticker in vaid_shenzhen_ticker_generator():
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
#test_filter()
#stock_watch_list.sort(key=lambda a: a[1])
#print(stock_watch_list)

"""
HK one by using vaid_hk_ticker_generator:
[('6113.HK', 0.20248745588109135), ('2147.HK', 0.2035715508469652), ('1730.HK', 0.203592899710689), ('1929.HK', 0.20361744275033525), ('0669.HK', 0.20366930718306323), ('0322.HK', 0.20435252276659838), ('1579.HK', 0.20467906429234145), ('1093.HK', 0.20633579088224474), ('0867.HK', 0.21100540096114473), ('0240.HK', 0.21311561791275815), ('1691.HK', 0.2151588886140266), ('6610.HK', 0.21616454365808768), ('2878.HK', 0.21666154728899462), ('0868.HK', 0.21869186781285932), ('2798.HK', 0.2202644423213487), ('1681.HK', 0.22089013461298979), ('2156.HK', 0.22239064577143158), ('1755.HK', 0.22494950430217625), ('2020.HK', 0.2253584518631166), ('2276.HK', 0.22545157217237105), ('2155.HK', 0.22761991227873274), ('0388.HK', 0.2303678172618944), ('6110.HK', 0.23201875745086514), ('1651.HK', 0.23251260573178756), ('8368.HK', 0.24717140727766448), ('1979.HK', 0.2473863603014601), ('2293.HK', 0.25072546969561094), ('0151.HK', 0.2514193548362013), ('0990.HK', 0.25259928819709976), ('1978.HK', 0.26531217531718143), ('0303.HK', 0.2658828067373678), ('1425.HK', 0.27152423212160065), ('8512.HK', 0.277090227045544), ('8371.HK', 0.27750936731650777), ('2535.HK', 0.2788127107143141), ('4333.HK', 0.2834217123876148), ('3660.HK', 0.28948927574814587), ('1428.HK', 0.2907412340414729), ('1050.HK', 0.2923051311941422), ('1585.HK', 0.30266429089357133), ('0992.HK', 0.30392037702276115), ('3798.HK', 0.3073516740100123), ('2165.HK', 0.3100226047400576), ('3306.HK', 0.31391040432714207), ('3316.HK', 0.31601844514905997), ('3658.HK', 0.3249203609413618), ('6388.HK', 0.3308035350503574), ('2669.HK', 0.33144113283175347), ('2439.HK', 0.331523160443621), ('1922.HK', 0.336428013421128), ('2477.HK', 0.33794117166370524), ('2660.HK', 0.346085251491757), ('1692.HK', 0.3490507799517873), ('9633.HK', 0.36536446854584803), ('1277.HK', 0.3844423348245405), ('4338.HK', 0.38686140022617527), ('2226.HK', 0.3950414289435453), ('8056.HK', 0.4088130093661255), ('1165.HK', 0.409162752808072), ('2498.HK', 0.4373473159491258), ('1497.HK', 0.44216011085080864), ('4336.HK', 0.4443370152994915), ('2442.HK', 0.4482454208836759), ('0901.HK', 0.4682137591193942), ('8316.HK', 0.4720572475921861), ('1523.HK', 0.5022129966647219), ('1830.HK', 0.5458668692504183), ('1239.HK', 0.5496289325357826), ('1308.HK', 0.5632107987407642), ('1947.HK', 0.5990856097657355), ('2405.HK', 0.6113032532554051), ('2373.HK', 0.6596427494579451), ('0724.HK', 0.663368144166677), ('2882.HK', 0.7201082367413418), ('0816.HK', 0.7373627652461117), ('3883.HK', 0.7732715191106456), ('2367.HK', 0.8263422808560122), ('0708.HK', 0.8436196621457458), ('0264.HK', 0.8919478800467084), ('8163.HK', 0.9933164538362322), ('6116.HK', 1.0638547337206372), ('4332.HK', 1.1297695268441958), ('8238.HK', 1.2239266296832583), ('8176.HK', 1.4324145329795588), ('0331.HK', 2.5278401840461417), ('0776.HK', 2.5927878871085377), ('8412.HK', 3.577813318621018), ('6959.HK', 4.309094845965417), ('0993.HK', 10.109170733178924)]
Shanghai one by using :
[('603219.SS', 0.20251835064055124), ('600845.SS', 0.20429373429157233), ('601012.SS', 0.20649021000808426), ('603606.SS', 0.20989297734898998), ('603369.SS', 0.2175015046673089), ('603307.SS', 0.21928553201056594), ('600570.SS', 0.22121369462713816), ('600925.SS', 0.22167570662287084), ('600436.SS', 0.222628257980088), ('600563.SS', 0.2246230121023151), ('603565.SS', 0.224913462625879), ('603605.SS', 0.22642304165210048), ('600702.SS', 0.233332000835402), ('603198.SS', 0.23398594107439505), ('603360.SS', 0.23478634866983708), ('601100.SS', 0.24005146593926374), ('600309.SS', 0.24165498467084115), ('603170.SS', 0.24398064116869614), ('603082.SS', 0.24429454015449711), ('603071.SS', 0.2464206720388512), ('601225.SS', 0.24837877672647984), ('603310.SS', 0.2516013303498317), ('603344.SS', 0.25885503991029735), ('603288.SS', 0.25902613424946674), ('603195.SS', 0.2591917681196744), ('603391.SS', 0.26229767263555276), ('603350.SS', 0.26731243764456675), ('603375.SS', 0.28292263608974194), ('603312.SS', 0.28436490579619605), ('603325.SS', 0.2883891408721299), ('603215.SS', 0.2902629218108201), ('600803.SS', 0.2921060675377192), ('603444.SS', 0.3037502764551028), ('600519.SS', 0.3075884252579019), ('601156.SS', 0.3096345228624696), ('600809.SS', 0.35467343703666654), ('600779.SS', 0.3595752471072648), ('603285.SS', 0.37979156907416617), ('603207.SS', 0.5286152329291797), ('600961.SS', 0.5670468804469195), ('600132.SS', 0.9359016014611057), ('600083.SS', 3.560264278509315)]
Shenzhen one by using vaid_shenzhen_ticker_generator
[('002737.SZ', 0.20373925960248793), ('002978.SZ', 0.20709778053085826), ('002216.SZ', 0.20851627031884873), ('002833.SZ', 0.2093268316907757), ('002475.SZ', 0.21351768585530423), ('000848.SZ', 0.21569199740410067), ('000333.SZ', 0.21856739907765932), ('002415.SZ', 0.2215111812384322), ('001323.SZ', 0.22204808616853333), ('000651.SZ', 0.22918651165565707), ('002049.SZ', 0.23015943051173504), ('000858.SZ', 0.23401109421813104), ('002690.SZ', 0.23510363516720156), ('001203.SZ', 0.23668751505239824), ('002043.SZ', 0.23884043856907247), ('000661.SZ', 0.2428165073303845), ('000895.SZ', 0.24405487603589465), ('002027.SZ', 0.250723251199283), ('002372.SZ', 0.25619504145366145), ('001308.SZ', 0.2564999351979211), ('001337.SZ', 0.2612514546488952), ('002847.SZ', 0.2673361100732311), ('001269.SZ', 0.276131012930511), ('002677.SZ', 0.2796671717657299), ('002032.SZ', 0.2872003483519895), ('000568.SZ', 0.2917574191375312), ('002555.SZ', 0.2940370098005248), ('000048.SZ', 0.30414234575095433), ('000792.SZ', 0.4603298240337589), ('000707.SZ', 0.8153137575823761), ('002188.SZ', 1.1832507703480186)]
"""

hk_raw_stock_watch_list = [('6113.HK', 0.20248745588109135), ('2147.HK', 0.2035715508469652),
                           ('1730.HK', 0.203592899710689), ('1929.HK', 0.20361744275033525),
                           ('0669.HK', 0.20366930718306323), ('0322.HK', 0.20435252276659838),
                           ('1579.HK', 0.20467906429234145), ('1093.HK', 0.20633579088224474),
                           ('0867.HK', 0.21100540096114473), ('0240.HK', 0.21311561791275815),
                           ('1691.HK', 0.2151588886140266), ('6610.HK', 0.21616454365808768),
                           ('2878.HK', 0.21666154728899462), ('0868.HK', 0.21869186781285932),
                           ('2798.HK', 0.2202644423213487), ('1681.HK', 0.22089013461298979),
                           ('2156.HK', 0.22239064577143158), ('1755.HK', 0.22494950430217625),
                           ('2020.HK', 0.2253584518631166), ('2276.HK', 0.22545157217237105),
                           ('2155.HK', 0.22761991227873274), ('0388.HK', 0.2303678172618944),
                           ('6110.HK', 0.23201875745086514), ('1651.HK', 0.23251260573178756),
                           ('8368.HK', 0.24717140727766448), ('1979.HK', 0.2473863603014601),
                           ('2293.HK', 0.25072546969561094), ('0151.HK', 0.2514193548362013),
                           ('0990.HK', 0.25259928819709976), ('1978.HK', 0.26531217531718143),
                           ('0303.HK', 0.2658828067373678), ('1425.HK', 0.27152423212160065),
                           ('8512.HK', 0.277090227045544), ('8371.HK', 0.27750936731650777),
                           ('2535.HK', 0.2788127107143141), ('4333.HK', 0.2834217123876148),
                           ('3660.HK', 0.28948927574814587), ('1428.HK', 0.2907412340414729),
                           ('1050.HK', 0.2923051311941422), ('1585.HK', 0.30266429089357133),
                           ('0992.HK', 0.30392037702276115), ('3798.HK', 0.3073516740100123),
                           ('2165.HK', 0.3100226047400576), ('3306.HK', 0.31391040432714207),
                           ('3316.HK', 0.31601844514905997), ('3658.HK', 0.3249203609413618),
                           ('6388.HK', 0.3308035350503574), ('2669.HK', 0.33144113283175347),
                           ('2439.HK', 0.331523160443621), ('1922.HK', 0.336428013421128),
                           ('2477.HK', 0.33794117166370524), ('2660.HK', 0.346085251491757),
                           ('1692.HK', 0.3490507799517873), ('9633.HK', 0.36536446854584803),
                           ('1277.HK', 0.3844423348245405), ('4338.HK', 0.38686140022617527),
                           ('2226.HK', 0.3950414289435453), ('8056.HK', 0.4088130093661255),
                           ('1165.HK', 0.409162752808072), ('2498.HK', 0.4373473159491258),
                           ('1497.HK', 0.44216011085080864), ('4336.HK', 0.4443370152994915),
                           ('2442.HK', 0.4482454208836759), ('0901.HK', 0.4682137591193942),
                           ('8316.HK', 0.4720572475921861), ('1523.HK', 0.5022129966647219),
                           ('1830.HK', 0.5458668692504183), ('1239.HK', 0.5496289325357826),
                           ('1308.HK', 0.5632107987407642), ('1947.HK', 0.5990856097657355),
                           ('2405.HK', 0.6113032532554051), ('2373.HK', 0.6596427494579451),
                           ('0724.HK', 0.663368144166677), ('2882.HK', 0.7201082367413418),
                           ('0816.HK', 0.7373627652461117), ('3883.HK', 0.7732715191106456),
                           ('2367.HK', 0.8263422808560122), ('0708.HK', 0.8436196621457458),
                           ('0264.HK', 0.8919478800467084), ('8163.HK', 0.9933164538362322),
                           ('6116.HK', 1.0638547337206372), ('4332.HK', 1.1297695268441958),
                           ('8238.HK', 1.2239266296832583), ('8176.HK', 1.4324145329795588),
                           ('0331.HK', 2.5278401840461417), ('0776.HK', 2.5927878871085377),
                           ('8412.HK', 3.577813318621018), ('6959.HK', 4.309094845965417),
                           ('0993.HK', 10.109170733178924)]

sh_raw_stock_watch_list = [('603219.SS', 0.20251835064055124), ('600845.SS', 0.20429373429157233),
                           ('601012.SS', 0.20649021000808426), ('603606.SS', 0.20989297734898998),
                           ('603369.SS', 0.2175015046673089), ('603307.SS', 0.21928553201056594),
                           ('600570.SS', 0.22121369462713816), ('600925.SS', 0.22167570662287084),
                           ('600436.SS', 0.222628257980088), ('600563.SS', 0.2246230121023151),
                           ('603565.SS', 0.224913462625879), ('603605.SS', 0.22642304165210048),
                           ('600702.SS', 0.233332000835402), ('603198.SS', 0.23398594107439505),
                           ('603360.SS', 0.23478634866983708), ('601100.SS', 0.24005146593926374),
                           ('600309.SS', 0.24165498467084115), ('603170.SS', 0.24398064116869614),
                           ('603082.SS', 0.24429454015449711), ('603071.SS', 0.2464206720388512),
                           ('601225.SS', 0.24837877672647984), ('603310.SS', 0.2516013303498317),
                           ('603344.SS', 0.25885503991029735), ('603288.SS', 0.25902613424946674),
                           ('603195.SS', 0.2591917681196744), ('603391.SS', 0.26229767263555276),
                           ('603350.SS', 0.26731243764456675), ('603375.SS', 0.28292263608974194),
                           ('603312.SS', 0.28436490579619605), ('603325.SS', 0.2883891408721299),
                           ('603215.SS', 0.2902629218108201), ('600803.SS', 0.2921060675377192),
                           ('603444.SS', 0.3037502764551028), ('600519.SS', 0.3075884252579019),
                           ('601156.SS', 0.3096345228624696), ('600809.SS', 0.35467343703666654),
                           ('600779.SS', 0.3595752471072648), ('603285.SS', 0.37979156907416617),
                           ('603207.SS', 0.5286152329291797), ('600961.SS', 0.5670468804469195),
                           ('600132.SS', 0.9359016014611057), ('600083.SS', 3.560264278509315)]
sz_raw_stock_watch_list = [('002737.SZ', 0.20373925960248793), ('002978.SZ', 0.20709778053085826),
                           ('002216.SZ', 0.20851627031884873), ('002833.SZ', 0.2093268316907757),
                           ('002475.SZ', 0.21351768585530423), ('000848.SZ', 0.21569199740410067),
                           ('000333.SZ', 0.21856739907765932), ('002415.SZ', 0.2215111812384322),
                           ('001323.SZ', 0.22204808616853333), ('000651.SZ', 0.22918651165565707),
                           ('002049.SZ', 0.23015943051173504), ('000858.SZ', 0.23401109421813104),
                           ('002690.SZ', 0.23510363516720156), ('001203.SZ', 0.23668751505239824),
                           ('002043.SZ', 0.23884043856907247), ('000661.SZ', 0.2428165073303845),
                           ('000895.SZ', 0.24405487603589465), ('002027.SZ', 0.250723251199283),
                           ('002372.SZ', 0.25619504145366145), ('001308.SZ', 0.2564999351979211),
                           ('001337.SZ', 0.2612514546488952), ('002847.SZ', 0.2673361100732311),
                           ('001269.SZ', 0.276131012930511), ('002677.SZ', 0.2796671717657299),
                           ('002032.SZ', 0.2872003483519895), ('000568.SZ', 0.2917574191375312),
                           ('002555.SZ', 0.2940370098005248), ('000048.SZ', 0.30414234575095433),
                           ('000792.SZ', 0.4603298240337589), ('000707.SZ', 0.8153137575823761),
                           ('002188.SZ', 1.1832507703480186)]

raw_stock_watch_list = hk_raw_stock_watch_list + sz_raw_stock_watch_list + sh_raw_stock_watch_list
stock_watch_list_pscore = []

for ticker, _ in raw_stock_watch_list:
    stock = Stock_Info(ticker)
    stock_watch_list_pscore.append((ticker, stock.piotroski_score()))
stock_watch_list_pscore.sort(key=lambda a: a[1])
print(stock_watch_list_pscore)

"""
Rank from lowest score to highest score for further analysis:

[('2226.HK', 1), ('8316.HK', 1), ('1239.HK', 1), ('0724.HK', 1), ('8238.HK', 1), ('0901.HK', 2), ('3883.HK', 2), 
('0264.HK', 2), ('0776.HK', 2), ('002216.SZ', 2), ('000895.SZ', 2), ('002372.SZ', 2), ('000048.SZ', 2), ('2798.HK', 
3), ('2293.HK', 3), ('2535.HK', 3), ('3660.HK', 3), ('1277.HK', 3), ('1165.HK', 3), ('2498.HK', 3), ('2442.HK', 3), 
('2405.HK', 3), ('2882.HK', 3), ('0708.HK', 3), ('8163.HK', 3), ('6116.HK', 3), ('8176.HK', 3), ('002978.SZ', 3), 
('001203.SZ', 3), ('001308.SZ', 3), ('002032.SZ', 3), ('601012.SS', 3), ('603369.SS', 3), ('600702.SS', 3), 
('603071.SS', 3), ('600083.SS', 3), ('2147.HK', 4), ('1929.HK', 4), ('1093.HK', 4), ('0867.HK', 4), ('0240.HK', 4), 
('1691.HK', 4), ('6610.HK', 4), ('2878.HK', 4), ('2156.HK', 4), ('0388.HK', 4), ('1651.HK', 4), ('8368.HK', 4), 
('1979.HK', 4), ('1978.HK', 4), ('1425.HK', 4), ('1428.HK', 4), ('0992.HK', 4), ('3798.HK', 4), ('3316.HK', 4), 
('2477.HK', 4), ('2660.HK', 4), ('1692.HK', 4), ('4338.HK', 4), ('8056.HK', 4), ('1497.HK', 4), ('1830.HK', 4), 
('1308.HK', 4), ('0816.HK', 4), ('6959.HK', 4), ('0993.HK', 4), ('002833.SZ', 4), ('000848.SZ', 4), ('002415.SZ', 4), 
('001323.SZ', 4), ('000651.SZ', 4), ('002690.SZ', 4), ('001269.SZ', 4), ('000568.SZ', 4), ('000792.SZ', 4), 
('603219.SS', 4), ('600845.SS', 4), ('603307.SS', 4), ('600570.SS', 4), ('600925.SS', 4), ('600436.SS', 4), 
('603565.SS', 4), ('603605.SS', 4), ('603198.SS', 4), ('603360.SS', 4), ('603170.SS', 4), ('603310.SS', 4), 
('603344.SS', 4), ('603288.SS', 4), ('603195.SS', 4), ('603391.SS', 4), ('603350.SS', 4), ('603375.SS', 4), 
('603312.SS', 4), ('603215.SS', 4), ('603444.SS', 4), ('601156.SS', 4), ('600809.SS', 4), ('603285.SS', 4), 
('603207.SS', 4), ('600132.SS', 4), ('6113.HK', 5), ('1730.HK', 5), ('0669.HK', 5), ('0322.HK', 5), ('0868.HK', 5), 
('1755.HK', 5), ('2020.HK', 5), ('2155.HK', 5), ('0151.HK', 5), ('0303.HK', 5), ('8512.HK', 5), ('8371.HK', 5), 
('4333.HK', 5), ('1050.HK', 5), ('1585.HK', 5), ('2165.HK', 5), ('3306.HK', 5), ('3658.HK', 5), ('6388.HK', 5), 
('2439.HK', 5), ('1922.HK', 5), ('9633.HK', 5), ('1523.HK', 5), ('2373.HK', 5), ('2367.HK', 5), ('4332.HK', 5), 
('0331.HK', 5), ('8412.HK', 5), ('002737.SZ', 5), ('002475.SZ', 5), ('000333.SZ', 5), ('002049.SZ', 5), ('000858.SZ', 
5), ('000661.SZ', 5), ('002027.SZ', 5), ('002677.SZ', 5), ('002555.SZ', 5), ('000707.SZ', 5), ('002188.SZ', 5), 
('603606.SS', 5), ('600563.SS', 5), ('600309.SS', 5), ('603082.SS', 5), ('601225.SS', 5), ('603325.SS', 5), 
('600803.SS', 5), ('600519.SS', 5), ('600779.SS', 5), ('600961.SS', 5), ('1579.HK', 6), ('1681.HK', 6), ('2276.HK', 
6), ('6110.HK', 6), ('0990.HK', 6), ('2669.HK', 6), ('4336.HK', 6), ('1947.HK', 6), ('002043.SZ', 6), ('001337.SZ', 
6), ('002847.SZ', 6), ('601100.SS', 6)]
"""
