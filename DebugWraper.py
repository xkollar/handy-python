#!/usr/bin/env python
# DebugWrapper - Wrapper for debugging calls + few handy functions
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

"""DebugWrapper: Wrapper for debugging calls + few handy functions

Example usage:

import xmlrpclib
from DebugWrapper import DebugWrapper, ppDebug, waitWithLine

client = DebugWrapper(xmlrpclib.Server(...), debug=1)

# ... code
client.api.call(param1, param2)
ppDebug(client.debug())
waitWithLine
# ... code
"""

__author__ = "Matej Kollar"
__contact__ = "xkolla06@stud.fit.vutbr.cz"

__version__ = "1.0"
__date__ = "2013. 09. 12."
__license__ = "GPLv3"

__credits__ = [__author__]
__maintainer__ = __author__
__status__ = "Working"

__all__ = ['DebugWrapper', 'getType', 'justTry', 'ppDebug', 'waitWithLine']

import inspect
import pprint
import sys


class DebugWrapper(object):
    """Wraps object intercepting calls to methods on object and subobjects,
    enabling user to see what was called and what was the result.
    Does not work for accessing attributes just for their value, you
    may need to keep unwrapped object for that."""
    def __init__(self, obj, debug=0, desc=sys.stderr):
        """debug -- debug level
             0 - no debugging information
             1 - method calls are printed to desc
             2 - method calls with types of arguments is printed to desc
             3 - method calls with arguments is printed to desc
        desc -- where to print debug information if any"""
        self.__wrap_obj = obj
        self.__wrap_debug = debug
        self.__wrap_desc = desc
        self.__wrap_attrs = []
        self.__wrap_state = obj
        self.__wrap_last_attr = None
        self.__wrap_last_result = None

    def __getattr__(self, attr):
        self.__wrap_attrs.append(attr)
        try:
            self.__wrap_state = getattr(self.__wrap_state, attr)
        except:
            print >> self.__wrap_desc, ("Accessing attributes without "
                                        "calling methods is forbidden.\n"
                                        "Resetting state, re-throwing. "
                                        "Occurred on %s") % ".".join(self.__wrap_attrs)
            self.__wrap_state = self.__wrap_obj
            self.__wrap_attrs = []
            raise
        return self

    def __call__(self, *args, **kwargs):
        attr = ".".join(self.__wrap_attrs)
        if self.__wrap_debug == 1:
            print >> self.__wrap_desc, "Calling %s(...)" % attr
        elif self.__wrap_debug == 2:
            print >> self.__wrap_desc, "Calling %s(%s)" % (attr, showArgs(args))
        elif self.__wrap_debug == 3:
            print >> self.__wrap_desc, "Calling %s%s" % (attr, tuple(args))
        ret = None
        try:
            ret = self.__wrap_state(*args, **kwargs)
        finally:
            self.__wrap_last_attr, self.__wrap_last_result = attr, ret
            self.__wrap_state = self.__wrap_obj
            self.__wrap_attrs = []
        return ret

    def debug(self):
        """Return tuple containg name of last method call and the result."""
        return (self.__wrap_last_attr, self.__wrap_last_result)


def getListType(l):
    assert type(l) is list
    a = set(getType(x) for x in l)
    return "List [ %s ]" % " + ".join(a)

# def getObjectType(o):
#     return "Object ..."


def getDictType(d):
    assert type(d) is dict
    a = list(d.iteritems())
    a.sort()
    a = (str(x) + ": " + getType(y) for (x, y) in a)
    return "Dict { %s }" % ", ".join(a)


def getTupleType(t):
    assert type(t) is tuple
    a = map(getType, t)
    return "%d-Tuple ( %s )" % (len(t), " , ".join(a))


def getSetType(s):
    assert type(s) is set
    a = set(getType(x) for x in s)
    return "Set of ( %s )" % " + ".join(a)


def getType(o):
    """Shows type of argument, not dissimilar from Haskell types.

    Examples:

    >>> getType([1, 'a'])
    List [ int + str ]

    >>> getType({'key': [1,set([1])]})
    'Dict { key: List [ int + Set of ( int ) ] }'

    First example tells us, that it is list that contains
    values of types 'int' and 'str', but nothing else.
    """
    t = type(o)
    if t is list:
        return getListType(o)
    elif t is dict:
        return getDictType(o)
    elif t is tuple:
        return getTupleType(o)
    elif t is set:
        return getSetType(o)
    else:
        return t.__name__


def showArgs(args):
    """Helper function to show types of arguments."""
    return ",".join(map(getType, args))


def ppDebug((d, o), PPrint=pprint.PrettyPrinter(indent=4).pprint):
    """Pretty printer for debugging informations provided by DebugWrapper."""
    print "%s: %s" % (d, getType(o))
    PPrint(o)
    print "--------"


def waitWithLine(text="Press Enter to continue..."):
    """Wait for Enter, providing information about line of code
    where it was called. Useful for debugging."""
    raw_input("line %s: %s" % (inspect.currentframe().f_back.f_lineno, text))


def justTry(fun, *args, **kwargs):
    """Call function with given arguments, suppressing any
    exception that might be thrown."""
    try:
        fun(*args, **kwargs)
    except:
        pass
        # print("Caught exception:", sys.exc_info()[0])

