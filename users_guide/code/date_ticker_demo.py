import datetime
from matplotlib.matlab import *
from matplotlib.dates import MONDAY, SATURDAY
from matplotlib.finance import quotes_historical_yahoo
from matplotlib.dates import MonthLocator, WeekdayLocator, DateFormatter
from matplotlib.ticker import FormatStrFormatter

# the start and end date range for the financial plots
date1 = datetime.date( 2003, 1, 1 )
date2 = datetime.date( 2004, 4, 12 )

# the tick locators and formatters
mondays    = WeekdayLocator(MONDAY)       # every monday
months     = MonthLocator()               # every month
monthsFmt  = DateFormatter('%b %d')       # looks like May 01
dollarFmt  = FormatStrFormatter('$%0.2f') # dollars!

# get some financial data from the finance module
quotes = quotes_historical_yahoo(
    'INTC', date1, date2)
if not quotes:   raise SystemExit   # failsafe

# extract the date and opening prices from the quote tuples
dates = [q[0] for q in quotes]
opens = [q[1] for q in quotes]

# plot_date will choose a default date ticker and formatter
ax = subplot(111)
plot_date(dates, opens, markeredgecolor='k')

# but we'll override the default with our custom locators and
# formatters
ax.xaxis.set_major_locator(months)
ax.xaxis.set_major_formatter(monthsFmt)
ax.xaxis.set_minor_locator(mondays)

# format the y axis in dollars
ax.yaxis.set_major_formatter(dollarFmt)

# call autoscale to pick intelligent view limits based on our major
# tick locator
ax.autoscale_view()

# rotate the x labels for nicer viewing
labels = ax.get_xticklabels()
set(labels, 'rotation', 45, fontsize=10)

grid(True)

savefig('../figures/date_ticker_demo.eps')
savefig('../figures/date_ticker_demo.png')

show()
