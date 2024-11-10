from asyncio.log import logger

import sqlalchemy
import yfinance as yf
import numpy as np
import pandas_ta as pandas_ta
import pandas as pd


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
    df["% Change"] = round(df["Adj Close"] / df["Adj Close"].shift(1) - 1, 4)
    logger.info("Process completed for function: get_return..")
    return df


def get_garman_klass_vol(df):
    """
    :param data_frame: Pandas DataFrame as Input

    :returns:
    data_frame: Transformed Pandas DataFrame as Output
    """
    check_pandas(df)
    df["garman_klass_vol"] = ((np.log(df["high"]) - np.log(df["low"])) ** 2) / 2 - (
        2 * np.log(2) - 1
    ) * ((np.log(df["adj close"]) - np.log(df["open"])) ** 2)
    logger.info("Process completed for function: get_garman_klass_vol..")
    return df


def get_rsi(df):
    """
    :param data_frame: Pandas DataFrame as Input

    :returns:
    data_frame: Transformed Pandas DataFrame as Output
    """
    check_pandas(df)
    df["rsi"] = df.groupby(level=1)["adj close"].transform(
        lambda x: pandas_ta.rsi(close=x, length=20)
    )
    logger.info("Process completed for function: get_rsi..")
    return df


def get_adj_close(df):
    """
    :param data_frame: Pandas DataFrame as Input

    :returns:
    data_frame: Transformed Pandas DataFrame as Output
    """
    check_pandas(df)
    df["bb_low"] = df.groupby(level=1)["adj close"].transform(
        lambda x: pandas_ta.bbands(close=np.log1p(x), length=20).iloc[:, 0]
    )
    return df


def get_bb_mid(df):
    """
    :param data_frame: Pandas DataFrame as Input

    :returns:
    data_frame: Transformed Pandas DataFrame as Output
    """
    check_pandas(df)
    df["bb_mid"] = df.groupby(level=1)["adj close"].transform(
        lambda x: pandas_ta.bbands(close=np.log1p(x), length=20).iloc[:, 1]
    )
    return df


def get_bb_high(df):
    """
    :param data_frame: Pandas DataFrame as Input

    :returns:
    data_frame: Transformed Pandas DataFrame as Output
    """
    check_pandas(df)
    df["bb_high"] = df.groupby(level=1)["adj close"].transform(
        lambda x: pandas_ta.bbands(close=np.log1p(x), length=20).iloc[:, 2]
    )
    return df


def compute_atr(stock_data):
    atr = pandas_ta.atr(
        high=stock_data["high"],
        low=stock_data["low"],
        close=stock_data["close"],
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
    df["atr"] = df.groupby(level=1, group_keys=False).apply(compute_atr)
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
    df["macd"] = df.groupby(level=1, group_keys=False)["adj close"].apply(compute_macd)
    return df


def get_dollar_volume(df):
    """
    :param data_frame: Pandas DataFrame as Input

    :returns:
    data_frame: Transformed Pandas DataFrame as Output
    """
    df["dollar_volume"] = (df["adj close"] * df["volume"]) / 1e6
    return df
