from asyncio.log import logger

import sqlalchemy
import yfinance as yf
import numpy as np
import pandas_ta as pandas_ta


def get_data(tickers):
    data = []
    for ticker in tickers:
        data.append((ticker, yf.download(ticker).reset_index()))
    return data


def create_engine(name):
    engine = sqlalchemy.create_engine('sqlite:///' + name + '.db')
    return engine


def TOSQL(frames, engine):
    for symbol, frame in frames:
        frame.to_sql(symbol, engine.raw_connection(), index=False, if_exists="replace")
    logger.info('imported successfully')


def get_garman_klass_vol(df):
    df['garman_klass_vol'] = ((np.log(df['high']) - np.log(df['low'])) ** 2) / 2 - (2 * np.log(2) - 1) * (
            (np.log(df['adj close']) - np.log(df['open'])) ** 2)
    return df


def get_rsi(df):
    df['rsi'] = df.groupby(level=1)['adj close'].transform(lambda x: pandas_ta.rsi(close=x, length=20))
    return df


def get_adj_close(df):
    df['bb_low'] = df.groupby(level=1)['adj close'].transform(
        lambda x: pandas_ta.bbands(close=np.log1p(x), length=20).iloc[:, 0])
    return df


def get_bb_mid(df):
    df['bb_mid'] = df.groupby(level=1)['adj close'].transform(
        lambda x: pandas_ta.bbands(close=np.log1p(x), length=20).iloc[:, 1])
    return df


def get_bb_high(df):
    df['bb_high'] = df.groupby(level=1)['adj close'].transform(
        lambda x: pandas_ta.bbands(close=np.log1p(x), length=20).iloc[:, 2])
    return df
