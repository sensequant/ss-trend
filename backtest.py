from sense.backtest import *
import numpy as np


def init():
    g.symbol = 'BTC-USDT-SWAP'
    g.last_ts = 0
    g.last_h = 0
    g.last_cnt = 0
    set_trading_fee(0.0005)
    set_balance(100000)
    add_symbols(symbols=[g.symbol])


def on_bar():
    bars = get_bars(symbols=[g.symbol], time_frame='15m',
                    count=20, fields=['ts', 'o', 'h', 'l', 'c', 'closed'])[g.symbol]
    long_pos = get_position(g.symbol, 'long')

    ma5 = np.mean(bars['c'][-5:])
    ma20 = np.mean(bars['c'])
    std = np.std(bars['c'])
    hb = ma20 + 2 * std
    lb = ma20 - 2 * std

    if long_pos.amount == 0:
        if g.last_h > 0 and g.last_cnt > 32 and bars['c'][-1] > g.last_h:
            print('time: ', ts2dt(g.last_ts))
            order(symbol=g.symbol, side='open', position_side='long',
                  amount=1, price=bars['c'][-1])
            g.open_price = bars['c'][-1]
            g.sl_price = g.last_sl
    else:
        if bars['c'][-1] < ma20:
            order(symbol=g.symbol, side='close', position_side='long',
                  amount=1, price=bars['c'][-1])
        elif bars['c'][-1] < g.sl_price:
            order(symbol=g.symbol, side='close', position_side='long',
                  amount=1, price=bars['c'][-1])

    if bars['closed'][-1]:
        if bars['h'][-1] > hb and bars['h'][-1] > g.last_h:
            g.last_ts = bars['ts'][-1]
            g.last_h = bars['h'][-1]
            g.last_sl = lb
            g.last_cnt = 1
        else:
            g.last_cnt += 1
            if g.last_cnt > 96:
                g.last_h = 0


if __name__ == '__main__':
    init()
    backtest(
        begin_dt='2023-1-1 00:00:00',
        end_dt='2023-12-31 23:59:59',
        time_frames=['1m', '15m'],
        exchange='okx',
        on_bar=on_bar
    )
