from asyncio.log import logger

from sklearn.metrics import precision_score
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import xgboost as xgb
from sklearn.metrics import mean_squared_error

color_pal = sns.color_palette()
plt.style.use("fivethirtyeight")

from config import raw_target_list
from utility import (
    create_engine,
    get_garman_klass_vol,
    get_rsi,
    get_bb_low,
    get_bb_mid,
    get_bb_high,
    get_atr,
    get_macd,
    get_state,
    get_return,
)

target_list = []

for ticker, score in raw_target_list:
    target_list.append(ticker)

model = xgb.XGBRegressor(
    n_estimators=1000, early_stopping_rounds=50, learning_rate=0.001
)


def train_test_split(df: pd.DataFrame):
    train_length = int(len(df) * 0.7)
    return df[:train_length], df[train_length:]


def predict(train, test, predicators, model):
    model.fit(
        train[predicators],
        train["state"],
        eval_set=[
            (train[predicators], train["state"]),
            (test[predicators], test["state"]),
        ],
        verbose=True,
    )
    preds = model.predict(test[predicators])
    logger.info(f"feature importance: {model.feature_importances_}")
    fi = pd.DataFrame(
        data=model.feature_importances_,
        index=model.feature_names_in_,
        columns=["importance"],
    )
    fi.sort_values("importance").plot(kind="barh", title="Feature Importance")
    plt.show()
    preds = pd.Series(preds, index=test.index, name="Predictions")
    combined = pd.concat([test["state"], preds], axis=1)
    return combined


ChinaEngine = create_engine("China")

# data = sqlite3.connect("/China.db")
# df = pd.DataFrame.from_records(data, index=None, exclude=None, columns=None, coerce_float=False, nrows=None)

for ticker in target_list:
    df = pd.read_sql(f"select * from '{ticker}'", ChinaEngine.raw_connection())
    df = get_garman_klass_vol(df)
    # df = get_rsi(df)
    df = get_bb_low(df)
    df = get_bb_mid(df)
    df = get_bb_high(df)
    df = get_return(df)
    df = get_state(df)
    # df = get_atr(df)
    # df = get_macd(df)

    train, test = train_test_split(df)
    predictors = [
        "garman_klass_vol",
        #   "rsi",
        "bb_low",
        "bb_mid",
        "bb_high",
        #   "atr",
        #   "macd",
    ]
    target = ["state"]
    combined = predict(train, test, predictors, model)
    combined.plot()
