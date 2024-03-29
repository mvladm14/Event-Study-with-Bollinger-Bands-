import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep

def bollinger_events(ls_symbols, d_data, lookback):
    df_close = d_data['close']
    df_mean = pd.rolling_mean(df_close, lookback)
    df_std = pd.rolling_std(df_close, lookback)

    df_bands = (df_close - df_mean) / df_std

    # Creating an empty dataframe
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_close.index

    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            f_boll_today = df_bands[s_sym].ix[ldt_timestamps[i]]
            f_boll_yest = df_bands[s_sym].ix[ldt_timestamps[i - 1]]
            f_spy_today = df_bands['SPY'].ix[ldt_timestamps[i]]
            if f_boll_yest >= -2.00 and f_boll_today <= -2.00 and f_spy_today >= 1.3 :
                df_events[s_sym].ix[ldt_timestamps[i]] = 1

    return df_events


if __name__ == '__main__':
    dt_start = dt.datetime(2008, 1, 1)
    dt_end = dt.datetime(2009, 12, 31)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt.timedelta(hours=16))

    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list('sp5002012')
    ls_symbols.append('SPY')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)

    df_events = bollinger_events(ls_symbols, d_data, 20)

    ep.eventprofiler(df_events, d_data, i_lookback=20, i_lookforward=20,
                s_filename='sp5002012.pdf', b_market_neutral=True, b_errorbars=True,
                s_market_sym='SPY')

