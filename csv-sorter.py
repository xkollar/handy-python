#!/usr/bin/env python
# csv-sorter - format content of headered CSV file
# Copyright (C) 2013 Matej Kollar
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
# cat companies.csv | python csv-sorter.py Sector Industry "P/E" Symbol
"""

__author__ = "Matej Kollar"
__contact__ = "xkolla06@stud.fit.vutbr.cz"

__version__ = "1.0"
__date__ = "2014. 05. 17."
__license__ = "GPLv3"

__credits__ = [__author__]
__maintainer__ = __author__
__status__ = "Working"

import csv
import errno
import sys

def csv_sort(in_file, out_file, fields):
    reader = csv.DictReader(in_file)
    writer = csv.DictWriter(out_file, reader.fieldnames)
    writer.writeheader()

    for line in sorted(reader, key=lambda x: [x[field] for field in fields]):
        writer.writerow(line)

if __name__ == "__main__":
    try:
        csv_sort(sys.stdin, sys.stdout, sys.argv[1:])
    except IOError, e:
        if e.errno != errno.EPIPE:
            raise
    except KeyboardInterrupt:
        pass
