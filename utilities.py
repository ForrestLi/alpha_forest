"""
Hong Kong, Shenzhen, Shanghai stocks used number + exch appendix (e.g. HK, SZ, SS)
so used a generator to generate the possible value within a pre-defined range.
"""


def vaid_shenzhen_ticker_generator():
    for i in range(1000001, 1011980):
        yield str(i)[1:] + '.SZ'


def vaid_techboard_ticker_generator():
    for i in range(1300001, 1301000):
        yield str(i)[1:] + '.SZ'


def vaid_b_ticker_generator():
    for i in range(1200002, 1201000):
        # for i in range(1201000,1202000):
        yield str(i)[1:]


def vaid_shanghai_ticker_generator():
    for i in range(1600001, 1603800):
        yield str(i)[1:] + '.SS'


def vaid_hk_ticker_generator():
    for i in range(10001, 19999):
        yield str(i)[1:] + '.HK'
