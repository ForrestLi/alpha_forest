from fundamental_analysis.config import raw_target_list
from fundamental_analysis.utility import get_data, TOSQL, create_engine

target_list = []

for ticker, score in raw_target_list:
    target_list.append(ticker)

China = get_data(target_list)

ChinaEngine = create_engine("China")

TOSQL(China, ChinaEngine)
