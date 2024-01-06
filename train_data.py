from sense.backtest import *
from ta.volatility import BollingerBands
import pandas as pd


SYMBOL = 'BTC-USDT-SWAP'
pos_cnt = 0
neg_cnt = 0
temp = []
data = []


def on_bar():
    global SYMBOL, pos_cnt, neg_cnt, temp, data

    bars = get_bars(symbols=[SYMBOL], time_frame='15m',
                    count=20, fields=['ts', 'o', 'c'])[SYMBOL]
    indicator_bb = BollingerBands(
        close=pd.Series(bars['c']), window=20, window_dev=2)
    ma = indicator_bb.bollinger_mavg()
    hb = indicator_bb.bollinger_hband()
    lb = indicator_bb.bollinger_lband()

    if bars['c'][-1] < ma.iloc[-1]:
        for bar in temp:
            if (bars['c'][-1] - bar['c']) / bars['c'][-1] > 0.01:
                # data.append(bar)
                pos_cnt += 1
                print('+ sample', ts2dt(bar['ts']))
            else:
                neg_cnt += 1
                print('- sample', ts2dt(bar['ts']))
        temp.clear()

    if bars['o'][-1] < bars['c'][-1] and bars['c'][-1] > hb.iloc[-1]:
        temp.append({'ts': bars['ts'][-1], 'c': bars['c'][-1]})


if __name__ == '__main__':
    add_symbols([SYMBOL])
    backtest(begin_dt='2023-1-1 00:00:00',
             end_dt='2023-12-31 23:59:59',
             time_frames=['15m'],
             exchange='okx',
             on_bar=on_bar)
    print('pos_cnt', pos_cnt)
    print('neg_cnt', neg_cnt)
