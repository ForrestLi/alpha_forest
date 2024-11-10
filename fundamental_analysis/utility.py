from asyncio.log import logger

import sqlalchemy
import yfinance as yf
import numpy as np
import pandas_ta as pandas_ta
import pandas as pd


"""
Hong Kong, Shenzhen, Shanghai stocks used number + exch appendix (e.g. HK, SZ, SS)
so used a generator to generate the possible value within a pre-defined range.
"""


def vaid_shenzhen_ticker_generator():
    for i in range(1000001, 1011980):
        yield str(i)[1:] + ".SZ"


def vaid_techboard_ticker_generator():
    for i in range(1300001, 1301000):
        yield str(i)[1:] + ".SZ"


def vaid_b_ticker_generator():
    for i in range(1200002, 1201000):
        # for i in range(1201000,1202000):
        yield str(i)[1:]


def vaid_shanghai_ticker_generator():
    for i in range(1600001, 1603800):
        yield str(i)[1:] + ".SS"


def vaid_hk_ticker_generator():
    for i in range(10001, 19999):
        yield str(i)[1:] + ".HK"


def get_data(tickers):
    data = []
    for ticker in tickers:
        data.append((ticker, yf.download(ticker).reset_index()))
    return data


def create_engine(name):
    engine = sqlalchemy.create_engine("sqlite:///" + name + ".db")
    return engine


def TOSQL(frames, engine):
    for symbol, frame in frames:
        frame.to_sql(symbol, engine.raw_connection(), index=False, if_exists="replace")
    logger.info("imported successfully")


def check_pandas(df: pd.DataFrame):
    logger.info("Process started for function: get_return..")
    if df.empty:
        logger.debug("The dataframe is empty. No transformations will be applied.")
        return df
    logger.info("Applying transformations to pd")


def get_return(df: pd.DataFrame):
    """
    :param data_frame: Pandas DataFrame as Input

    :returns:
    data_frame: Transformed Pandas DataFrame as Output
    """
    check_pandas(df)
    # also could just be df["Adj Close"].pct_change()
    df["Return"] = round(df["Adj Close"] / df["Adj Close"].shift(1) - 1, 4)
    logger.info("Process completed for function: get_return..")
    return df


def get_state(df: pd.DataFrame):
    """
    :param data_frame: Pandas DataFrame as Input

    :returns:
    data_frame: Transformed Pandas DataFrame as Output
    """
    check_pandas(df)
    df["state"] = np.where(df["Return"] > 0, "1", "0")
    return df


def get_garman_klass_vol(df):
    """
    :param data_frame: Pandas DataFrame as Input

    :returns:
    data_frame: Transformed Pandas DataFrame as Output
    """
    check_pandas(df)
    df["garman_klass_vol"] = ((np.log(df["High"]) - np.log(df["Low"])) ** 2) / 2 - (
        2 * np.log(2) - 1
    ) * ((np.log(df["Adj Close"]) - np.log(df["Open"])) ** 2)
    logger.info("Process completed for function: get_garman_klass_vol..")
    return df


def get_rsi(df):
    """
    :param data_frame: Pandas DataFrame as Input

    :returns:
    data_frame: Transformed Pandas DataFrame as Output
    """
    check_pandas(df)
    df["rsi"] = df["Adj Close"].transform(lambda x: pandas_ta.rsi(close=x, length=20))
    logger.info("Process completed for function: get_rsi..")
    return df


def get_bb_low(df):
    """
    :param data_frame: Pandas DataFrame as Input

    :returns:
    data_frame: Transformed Pandas DataFrame as Output
    """
    check_pandas(df)
    df["bb_low"] = df["Adj Close"].transform(
        lambda x: pandas_ta.bbands(close=np.log1p(x), length=20).iloc[:, 0]
    )
    # normalize the value by dividing it against adjust close price)
    df["bb_low"] = df["bb_low"] / df["Adj Close"]
    return df


def get_bb_mid(df):
    """
    :param data_frame: Pandas DataFrame as Input

    :returns:
    data_frame: Transformed Pandas DataFrame as Output
    """
    check_pandas(df)
    df["bb_mid"] = df["Adj Close"].transform(
        lambda x: pandas_ta.bbands(close=np.log1p(x), length=20).iloc[:, 1]
    )
    # normalize the value by dividing it against adjust close price)
    df["bb_mid"] = df["bb_mid"] / df["Adj Close"]
    return df


def get_bb_high(df):
    """
    :param data_frame: Pandas DataFrame as Input

    :returns:
    data_frame: Transformed Pandas DataFrame as Output
    """
    check_pandas(df)
    df["bb_high"] = df["Adj Close"].transform(
        lambda x: pandas_ta.bbands(close=np.log1p(x), length=20).iloc[:, 2]
    )
    # normalize the value by dividing it against adjust close price)
    df["bb_high"] = df["bb_high"] / df["Adj Close"]
    return df


def compute_atr(stock_data):
    atr = pandas_ta.atr(
        high=stock_data["High"],
        low=stock_data["Low"],
        close=stock_data["Close"],
        length=14,
    )
    return atr.sub(atr.mean()).div(atr.std())


def get_atr(df):
    """
    :param data_frame: Pandas DataFrame as Input

    :returns:
    data_frame: Transformed Pandas DataFrame as Output
    """
    check_pandas(df)
    df["atr"] = df.apply(compute_atr)
    return df


def compute_macd(close):
    """
    :param data_frame: Pandas DataFrame as Input

    :returns:
    data_frame: Transformed Pandas DataFrame as Output
    """
    macd = pandas_ta.macd(close=close, length=20).iloc[:, 0]
    return macd.sub(macd.mean()).div(macd.std())


def get_macd(df):
    """
    :param data_frame: Pandas DataFrame as Input

    :returns:
    data_frame: Transformed Pandas DataFrame as Output
    """
    df["macd"] = df["Adj Close"].apply(compute_macd)
    return df


def get_dollar_volume(df):
    """
    :param data_frame: Pandas DataFrame as Input

    :returns:
    data_frame: Transformed Pandas DataFrame as Output
    """
    df["dollar_volume"] = (df["Adj Close"] * df["Volume"]) / 1e6
    return df
