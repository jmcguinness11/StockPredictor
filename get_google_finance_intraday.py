#!/usr/bin/env python 
"""
Retrieve intraday stock data from Google Finance.
"""

import csv
import datetime
import re

import numpy as np
import pandas as pd
import requests

# This function comes from https://gist.github.com/lebedov/f09030b865c4cb142af1
def get_google_finance_intraday(ticker, period=60, days=1):
    """
    Retrieve intraday stock data from Google Finance.

    Parameters
    ----------
    ticker : str
        Company ticker symbol.
    period : int
        Interval between stock values in seconds.
    days : int
        Number of days of data to retrieve.

    Returns
    -------
    df : pandas.DataFrame
        DataFrame containing the opening price, high price, low price,
        closing price, and volume. The index contains the times associated with
        the retrieved price values.
    """

    uri = 'https://www.google.com/finance/getprices' \
          '?i={period}&p={days}d&f=d,c,h,l,o,v&df=cpct&q={ticker}'.format(ticker=ticker,
                                                                          period=period,
                                                                          days=days)
    page = requests.get(uri)
    reader = csv.reader(page.content.splitlines())
    columns = ['Close', 'High', 'Low', 'Open', 'Volume']
    rows = []
    times = []
    for row in reader:
        if re.match('^[a\d]', row[0]):
            if row[0].startswith('a'):
                start = datetime.datetime.fromtimestamp(int(row[0][1:]))
                times.append(start)
            else:
                times.append(start+datetime.timedelta(seconds=period*int(row[0])))
            rows.append(map(float, row[1:]))
    if len(rows):
        return pd.DataFrame(rows, index=pd.DatetimeIndex(times, name='Date'),
                            columns=columns)
    else:
        return pd.DataFrame(rows, index=pd.DatetimeIndex(times, name='Date'))

company_tickers = [
    'MMM',
    'AXP',
    'BA',
    'CAT',
    'CVX',
    'KO',
    'DIS',
    'DWDP',
    'XOM',
    'GE',
    'GS',
    'HD',
    'IBM',
    'INTC',
    'JNJ',
    'JPM',
    'MCD',
    'NKE',
    'PFE',
    'AAPL',
    'PG',
    'TRV',
    'UTX',
    'UNH',
    'VZ',
    'V',
    'WMT',
    'MSFT',
    'MRK',
    'CSCO',
]

if __name__ == '__main__':
    hourly_percent_changes = []
    dfs = []

    for item in company_tickers:
        dfs.append(get_google_finance_intraday(item, 3600, 60))

    for dataframe in dfs:
        for index, row in dataframe.iterrows():
            hourly_percent_changes.append((row['Close'] - row['Open']) / row['Open'] * 100)

    print (np.percentile(hourly_percent_changes, 33.33))
    print (np.percentile(hourly_percent_changes, 66.67))
    # print (np.percentile(hourly_percent_changes, 10))
    # print (np.percentile(hourly_percent_changes, 90))
