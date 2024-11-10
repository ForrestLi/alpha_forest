from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score
import sqlite3
import pandas as pd

from fundamental_analysis.config import raw_target_list
from fundamental_analysis.utility import create_engine

model = RandomForestClassifier(n_estimators=100, min_samples_split=100, random_state=1)

target_list = []

for ticker, score in raw_target_list:
    target_list.append(ticker)


def train_test_split(df: pd.DataFrame):
    train_length = int(len(df) * 0.7)
    return df[:train_length], df[train_length:]


ChinaEngine = create_engine("China")

# data = sqlite3.connect("/China.db")
# df = pd.DataFrame.from_records(data, index=None, exclude=None, columns=None, coerce_float=False, nrows=None)

for ticker in target_list:
    df = pd.read_sql(ticker, ChinaEngine.raw_connection())

    train, test = train_test_split(df)
    predictors = [
        "garman_klass_vol",
        "rsi",
        "bb_low",
        "bb_mid",
        "bb_high",
        "atr",
        "macd",
    ]
    target = ["state"]
    model.fit(train[predictors], train[target])
