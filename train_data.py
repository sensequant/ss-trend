from sense.backtest import *
from ta.volatility import BollingerBands
import pandas as pd
import numpy as np
import csv
import random


SYMBOL = 'BTC-USDT-SWAP'
pos_cnt = 0
neg_cnt = 0
win_cnt = 0
lose_cnt = 0
temp = []
xy = []
data = []
profit_ratio = 0.01


def on_bar():
    global SYMBOL, pos_cnt, neg_cnt, win_cnt, lose_cnt, temp, data, profit_ratio

    bars = get_bars(symbols=[SYMBOL], time_frame='15m',
                    count=40, fields=['ts', 'o', 'h', 'l', 'c'])[SYMBOL]
    indicator_bb = BollingerBands(
        close=pd.Series(bars['c']), window=20, window_dev=2)
    ma = indicator_bb.bollinger_mavg()
    hb = indicator_bb.bollinger_hband()
    lb = indicator_bb.bollinger_lband()
    ma5 = np.mean(bars['c'][-5:])
    ma8 = np.mean(bars['c'][-8:])
    ma12 = np.mean(bars['c'][-12:])
    max16 = np.max(bars['h'][-17:-2])
    max32 = np.max(bars['h'][-33:-2])

    if bars['c'][-1] < ma.iloc[-1]:
        for bar in temp:
            if bars['c'][-1] > bar['c']:
                if (bars['c'][-1] - bar['c']) / bars['c'][-1] > profit_ratio:
                    pos_cnt += 1
                    xy.append([1] + bar['feat'])
                win_cnt += 1
            else:
                neg_cnt += 1
                lose_cnt += 1
                xy.append([0] + bar['feat'])
        temp.clear()

    if bars['o'][-1] < bars['c'][-1] and bars['c'][-1] > hb.iloc[-1]:
        feat = []

        # ma5,8是否均线多头排列
        feat.append(1 if ma5 > ma8 else 0)

        # ma5,8 多头 ma8,12空头
        feat.append(1 if ma5 > ma8 and ma8 < ma12 else 0)

        # 当前K棒涨幅是否超过0.004
        feat.append(1 if (bars['c'][-1] - bars['o'][-1]
                          ) / bars['o'][-1] > 0.002 else 0)

        # 当前K棒涨幅是否超过0.01
        feat.append(1 if (bars['c'][-1] - bars['o'][-1]
                          ) / bars['o'][-1] > 0.005 else 0)

        # 当前K棒收盘价是否超过之前16根K棒最高价
        feat.append(1 if bars['c'][-1] > max16 else 0)

        # 当前K棒收盘价是否超过之前32根K棒最高价
        feat.append(1 if bars['c'][-1] > max32 else 0)

        # 当前BOLL开口是否小于价格的1%
        feat.append(1 if (hb.iloc[-1] - lb.iloc[-1]) /
                    bars['c'][-1] < 0.01 else 0)

        # 是否连续8个K棒的BOLL开口小于价格的1%
        f = 1
        for i in range(8):
            if (hb.iloc[-1-i] - lb.iloc[-1-i]) / bars['c'][-1-i] > 0.01:
                f = 0
                break
        feat.append(f)

        # 是否连续12个K棒的BOLL开口小于价格的1%
        f = 1
        for i in range(12):
            if (hb.iloc[-1-i] - lb.iloc[-1-i]) / bars['c'][-1-i] > 0.01:
                f = 0
                break
        feat.append(f)

        # 是否连续36个K棒的BOLL开口小于价格的1%
        f = 1
        for i in range(36):
            if (hb.iloc[-1-i] - lb.iloc[-1-i]) / bars['c'][-1-i] > 0.01:
                f = 0
                break
        feat.append(f)

        # 最近3根K棒最低价是否低于MA20
        feat.append(1 if np.min(bars['l'][-3:]) < ma.iloc[-1] else 0)

        # 上影线是否超过当前K棒的10%
        feat.append(1 if (bars['h'][-1] - bars['c'][-1]) /
                    (bars['c'][-1] - bars['o'][-1]) > 0.1 else 0)

        # BOLL当前K棒开口是否大于5根K棒前的开口
        feat.append(1 if (hb.iloc[-1] - lb.iloc[-1])
                    > (hb.iloc[-6] - lb.iloc[-6]) else 0)

        # 当前K棒的收盘价是否高于前一根K棒的最高价
        feat.append(1 if bars['c'][-1] > bars['h'][-2] else 0)

        # 最近8跟K棒的累计涨幅是否高于1%
        min = 1e9
        for i in range(8):
            if bars['l'][-1-i] < min:
                min = bars['l'][-1-i]
        feat.append(1 if (bars['c'][-1] - min) / min > 0.01 else 0)

        # 成交量是否是前一根K棒的两倍以内

        temp.append({'ts': bars['ts'][-1], 'c': bars['c'][-1], 'feat': feat})


if __name__ == '__main__':
    add_symbols([SYMBOL])
    pos_cnt = 0
    neg_cnt = 0
    backtest(begin_dt='2021-1-1 00:00:00',
             end_dt='2023-12-31 23:59:59',
             time_frames=['15m'],
             exchange='okx',
             on_bar=on_bar)
    pnr = pos_cnt / neg_cnt
    print(profit_ratio, pos_cnt, neg_cnt, pos_cnt / neg_cnt, win_cnt, lose_cnt)

    with open('data.csv', 'w') as f:
        writer = csv.writer(f)
        for line in xy:
            if line[0] == 1:
                writer.writerow(line)
            elif random.random() < pnr:
                writer.writerow(line)
