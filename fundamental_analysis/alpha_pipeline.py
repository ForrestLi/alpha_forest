from config import raw_china_target_list as raw_target_list
from utility import get_data, TOSQL, create_engine

target_list = []

for ticker, score in raw_target_list:
    target_list.append(ticker)

China = get_data(target_list)

ChinaEngine = create_engine("CHINA")

TOSQL(China, ChinaEngine)
