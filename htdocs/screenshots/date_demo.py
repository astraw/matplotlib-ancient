"""
Show how to make date plots in matplotlib using date tick locators and
formatters.  See major_minor_demo1.py for more information on
controlling major and minor ticks

All matplotlib date plotting is done by converting date instances into
seconds since the epoch, gmtime.  The conversion, tick locating and
formatting is done behind the scenes so this is most transparent to
you.  The dates module provides several converter classes that you can
pass to the date plotting functions which will convert your dates as
necessary.  Currently epoch dates (already converted) are supported
with EpochCOnverter, python2.3 datetime instances are supported with
PyDatetimeConverter, and it won't be much work to add an mx.Datetime
converter.

If you want to define your own converter, the minimum you need to do
is derive a class from dates.DateConverter and implement the epoch and
from_epoch methods.

This example requires an active internet connection since it uses
yahoo finance to get the data for plotting
"""

import sys
try: import datetime
except ImportError:
    print >> sys.stderr, 'This example requires the python2.3 datetime module though you can use the matpltolib date support w/o it'
    sys.exit()

from matplotlib.matlab import *
from matplotlib.dates import PyDatetimeConverter, MONDAY
from matplotlib.finance import quotes_historical_yahoo, candlestick
from matplotlib.ticker import WeekdayLocator, DayLocator, DateFormatter

date1 = datetime.date( 2004, 1, 1 )
date2 = datetime.date( 2004, 4, 12 )

pydates = PyDatetimeConverter()

mondays    = WeekdayLocator(MONDAY)   # every week
days       = DayLocator()             # every day
fmt = DateFormatter('%b %d')


quotes = quotes_historical_yahoo(
    'INTC', date1, date2, converter=pydates)


ax = subplot(111)
candlestick(ax, quotes, width=0.6, converter=pydates)
title('INTC stock price')
ylabel('share price $')
ax.xaxis.set_major_locator(mondays)
ax.xaxis.set_major_formatter(fmt)
ax.xaxis.set_minor_locator(days)
ax.xaxis.autoscale_view()
labels = ax.get_xticklabels()
set(labels, 'rotation', 'vertical')
grid(True)
show()
