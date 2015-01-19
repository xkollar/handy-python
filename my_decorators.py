import traceback
import sys
import os
from functools import wraps


def greenstack():
    print '\x1b[32mCalled from'
    for line in traceback.format_list(traceback.extract_stack()[:-1]):
        print line,
    print '\x1b[m'


def debug_decorator(fun_in):
    filename = traceback.extract_stack()[-2][0]

    @wraps(fun_in)
    def debug_decorator(*args, **kwargs):
        print "\n\x1b[31;1m%s: %s(%s)\x1b[m" % (
            filename,
            fun_in.__name__,
            ", ".join(
                [repr(val) for val in args] +
                [str(key) + "=" + repr(val) for key, val in kwargs.iteritems()]))
        if os.environ.get('DEBUG') == 'stack':
            greenstack()
        ret = fun_in(*args, **kwargs)
        print "\x1b[33;1m>>> %s returned %s\x1b[m" % (fun_in.__name__, repr(ret))
        return ret

    return debug_decorator


if __name__ == '__main__':
    @debug_decorator
    def kwak1(x, y, a=None):
        "Documentation for kwak1"
        return 1

    print kwak1(1, 2, 3)
    print kwak1.__doc__

    @debug_decorator
    def kwak2():
        print "before kwak1"
        kwak1(1, 2, 3)
        print "after kwak1"

    kwak2()
