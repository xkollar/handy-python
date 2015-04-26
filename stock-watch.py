#!/usr/bin/env python
# stock-watch - display simple info for given tickers
# Copyright (C) 2014 Matej Kollar
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

""" Example use:
# stock-watch.py RHT GOOG MSFT EURUSD=X
"""

__author__ = "Matej Kollar"
__contact__ = "208115@mail.muni.cz"

__version__ = "1.0"
__date__ = "2014. 05. 17."
__license__ = "GPLv3"

__credits__ = [__author__]
__maintainer__ = __author__
__status__ = "Working"

import csv
import sys
import urllib2


def term_color(c, s):
    if c is not None and sys.stdout.isatty():
        return "\033[38;5;%sm%s\033[m" % (c, s)
    else:
        return s


def float_(s):
    try:
        return float(s)
    except:
        return float('NaN')


def main(symbols):
    url = "https://download.finance.yahoo.com/d/quotes.csv?s=%s&f=sl1c1p2" % "+".join(symbols)
    reader = csv.reader(urllib2.urlopen(url))
    for line in reader:
        name = line[0]
        price = float_(line[1])
        change = float_(line[2])
        percent = float_(line[3][:-1])  # Remove percent sign
        color = None
        if change < 0:
            color = 196
        elif change > 0:
            color = 82
        print term_color(color, "{:<10} {:>6.2f} {:>+6.2f} ({:>+.2f}%)".format(name, price, change, percent))

if __name__ == "__main__":
    main(sys.argv[1:])
