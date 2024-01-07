from sense.backtest import *
from ta.volatility import BollingerBands
import pandas as pd


def init():
    g.symbol = 'BTC-USDT-SWAP'
    g.last_h = 0
    set_balance(100000)
    add_symbols(symbols=[g.symbol])


def on_bar():
    bars = get_bars(symbols=[g.symbol], time_frame='15m',
                    count=20, fields=['ts', 'o', 'h', 'l', 'c', 'closed'])[g.symbol]
    long_pos = get_position(g.symbol, 'long')

    indicator_bb = BollingerBands(
        close=pd.Series(bars['c']), window=20, window_dev=2)
    ma = indicator_bb.bollinger_mavg()
    hb = indicator_bb.bollinger_hband()
    lb = indicator_bb.bollinger_lband()

    if long_pos.amount == 0:
        if g.last_h > 0 and bars['c'][-1] > g.last_h:
            order(symbol=g.symbol, side='open', position_side='long',
                  amount=1, price=bars['c'][-1])
            g.sl_price = g.last_hb
    else:
        if bars['c'][-1] < ma.iloc[-1]:
            order(symbol=g.symbol, side='close', position_side='long',
                  amount=1, price=bars['c'][-1])
        elif bars['c'][-1] < g.sl_price:
            order(symbol=g.symbol, side='close', position_side='long',
                  amount=1, price=bars['c'][-1])

    if bars['c'][-1] > hb.iloc[-1] and bars['closed'][-1]:
        g.last_h = bars['h'][-1]
        g.last_hb = hb.iloc[-1]
        print('time: ', ts2dt(bars['ts'][-1]))
        print('last_h: ', g.last_h)
        print(
            f"bars: o={bars['o'][-1]}, h={bars['h'][-1]}, l={bars['l'][-1]}, c={bars['c'][-1]}")


if __name__ == '__main__':
    init()
    backtest(
        begin_dt='2023-1-1 00:00:00',
        end_dt='2023-12-31 23:59:59',
        time_frames=['1m', '15m'],
        exchange='okx',
        on_bar=on_bar
    )
