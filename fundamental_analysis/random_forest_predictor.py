from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score
import sqlite3
import pandas as pd

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

model = RandomForestClassifier(n_estimators=100, min_samples_split=100, random_state=1)

target_list = []

for ticker, score in raw_target_list:
    target_list.append(ticker)


def train_test_split(df: pd.DataFrame):
    train_length = int(len(df) * 0.7)
    return df[:train_length], df[train_length:]


def predict(train, test, predicators, model):
    model.fit(train[predicators], train["state"])
    preds = model.predict(test[predicators])
    preds = pd.Series(preds, index=test.index, name="Predictions")
    precision_score(test["state"], preds)
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
    # model.fit(train[predictors], train[target])
    RandomForestClassifier(min_samples_split=100, random_state=1)
    # preds = model.predict(test[predictors])
    # preds = pd.Series(preds, index=test.index)
    # precision_score(test["state"], preds)

    # combined = pd.concat([test["state"], preds], axis=1)
    combined = predict(train, test, predictors, model)
    combined.plot()
