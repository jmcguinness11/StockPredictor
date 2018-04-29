#!/usr/bin/env python

import csv
import datetime
import re

import numpy as np
import pandas as pd
import requests

dfs = {}
thresholds = []
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

def populateDataframes():
    for ticker in company_tickers:
        dfs[ticker] = get_google_finance_intraday(ticker, 3600, 60)

def calculateThresholds():
    if not dfs:
        populateDataframes()

    hourly_percent_changes = []
    for key in dfs:
        for index, row in dfs[key].iterrows():
            hourly_percent_changes.append((row['Close'] - row['Open']) / row['Open'] * 100)

    thresholds.append(np.percentile(hourly_percent_changes, 33))
    thresholds.append(np.percentile(hourly_percent_changes, 67))

def getLabel(ticker, month, day, hour):
    if not thresholds:
        calculateThresholds()

    time = datetime.datetime(2018, month, day, hour, 0, 0)
    open_price = dfs[ticker].loc[time, 'Open']
    close_price = dfs[ticker].loc[time, 'Close']
    print(open_price, close_price)

    percent_change = (close_price - open_price) / open_price * 100
    if percent_change > thresholds[1]:
        return 1
    elif percent_change > thresholds[0]:
        return 0
    else:
        return -1


if __name__ == '__main__':
    print (getLabel('AAPL', 4, 19, 12))
    print (getLabel('AAPL', 4, 19, 13))
    print (getLabel('AAPL', 4, 19, 14))
