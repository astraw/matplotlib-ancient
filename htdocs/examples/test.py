#!/usr/bin/env python
import datetime, time

class intdate(int):
     '''Subclasses int for use as dates.'''
     def __init__(self, ordinal):
         int.__init__(self, ordinal)
         self.__date = datetime.date.fromtimestamp(ordinal)

     day = property(fget=lambda self:self.__date.day)
     month = property(fget=lambda self:self.__date.month)
     year = property(fget=lambda self:self.__date.year)

     def isoformat(self): return self.__date.isoformat()

     def timetuple(self): return self.__date.timetuple()

     def date(self): return self.__date

def epoch(x):
     'convert userland datetime instance x to epoch'
     return time.mktime(x.timetuple())

def date(year, month, day):
     return intdate(epoch(datetime.date(year, month, day)))

def today():
     return intdate(epoch(datetime.date.today()))

from matplotlib.ticker import MinuteLocator, DateFormatter
from matplotlib.matlab import *

# simulate collecting data every minute starting at midnight
t0 = date(2004,04,27)
t = t0+arange(0, 2*3600, 60)  # 2 hours sampled every 2 minute
s = rand(len(t))

ax = subplot(111)
ax.xaxis.set_major_locator( MinuteLocator(20) )
ax.xaxis.set_major_formatter( DateFormatter('%H:%M') )
ax.bar(t, s, width=60)
#savefig('test')
show()



