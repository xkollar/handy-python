#!/usr/bin/env python
# extract-partial-zip - extract partially retrieved zip archives
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

"""Extract-partial-zip - experimental tool to extract partially retrieved
zip archives.

Heavily inspired by http://www.reddit.com/r/Python/comments/1dx9q0/

This simple tool is intended for cases when you download large zip
archive and want inspect content in already downloaded part. Already
extracted parts are skipped.

Archive is not held in whole in memory, archived files though are
(possible future enhancement).

In case you want to recover broken zip, you may prefer to
use "zip -FF" instead. However, this script is designed to
be easily modifiable, so you can turn off some checks
and try to use is for recovery too.
"""

__author__ = "Matej Kollar"
__contact__ = "xkolla06@stud.fit.vutbr.cz"

__version__ = "1.0"
__date__ = "2013. 11. 10."
__license__ = "GPLv3"

__credits__ = [__author__]
__maintainer__ = __author__
__status__ = "Prototype"

import errno
import os
import struct
import sys
import zlib

from collections import namedtuple

LOCAL_HEADER_FIELDS = [
    ('sig', 'I'),
    ('version', '2s'),
    ('flags', '2s'),
    ('method', 'H'),
    ('modtime', '2s'),
    ('moddate', '2s'),
    ('crc', '4s'),
    ('csize', 'L'),
    ('usize', 'L'),
    ('namelength', 'H'),
    ('extralength', 'H'),
]

LocalHeader = namedtuple('LocalHeader', [f[0] for f in LOCAL_HEADER_FIELDS])
HEADER_FORMAT = "<" + ''.join(f[1] for f in LOCAL_HEADER_FIELDS)
HEADER_SIZE = 30
HEADER_SIGNATURE = struct.pack('<L', 0x04034b50)


class FindFile(file):
    """Allows search for string in file"""
    def __init__(self, *args, **kwargs):
        super(FindFile, self).__init__(*args, **kwargs)
        self.buff = ""

    def read(self, n=-1):
        if n > len(self.buff) or n < 0:
            self.buff += super(FindFile, self).read(n - len(self.buff))
        if n < 0:
            n = len(self.buff)
        ret = self.buff[:n]
        self.buff = self.buff[n:]
        return ret

    def seek(self, offset, whence=0):
        assert offset >= 0
        if whence == 1:
            offset -= len(self.buff)
        self.buff = ""
        super(FindFile, self).seek(offset, whence)

    def find_seek(self, x):
        """Seeks to place where string occurs."""
        n = max(len(x), 2048)
        b = ['']
        while True:
            b.append(self.read(n))
            c = b[0] + b[1]
            if c == '':
                # EOF
                self.buff = ""
                return False
            m = c.find(x)
            if m >= 0:
                self.buff = c[m:]
                return True
            b.pop(0)


def main(archive, outdir):
    print "No CRC is done"
    f = FindFile(archive, 'rb')
    while f.find_seek(HEADER_SIGNATURE):
        hdr = LocalHeader(*struct.unpack(HEADER_FORMAT, f.read(HEADER_SIZE)))
        assert hdr.namelength < 1000, "Something wrong with headers probably?"
        name = os.path.normpath(os.sep.join([outdir, f.read(hdr.namelength)]))
        print "Processing %s..." % repr(name),
        _ = f.read(hdr.extralength)

        if os.path.exists(name):
            print "skipping (existing)"
            f.seek(hdr.csize, 1)
            continue

        cdata = f.read(hdr.csize)

        if len(cdata) != hdr.csize:
            print "skipping (incomplete data)"
            continue
        if hdr.method == 0:  # STORE
            data = cdata
        elif hdr.method == 8:  # DEFLATE
            data = zlib.decompress(cdata, -15)
        else:
            print "skipping (unsupported compression)"
            continue
        if len(data) != hdr.usize:
            print "skipping (incomplete decoded data)"
            continue
        if len(data) == 0:
            continue
        try:
            dirname = os.path.dirname(name)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            fd = open(name, 'wb')
            fd.write(data)
            fd.close()
        except IOError as e:
            pass
            # if e.errno in [errno.EISDIR, errno.ENOENT, errno.ENOTDIR]:
            #     os.makedirs(name)
            # else:
            #     print "Unexpected error %s" % e.errno
        print "done"
    print "End of archive"


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print 'usage: %s archive.zip output_dir/' % sys.argv[0]
    else:
        main(sys.argv[1], sys.argv[2])
