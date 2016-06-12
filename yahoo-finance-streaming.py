#!/usr/bin/env python2

import Queue
import StringIO
import itertools
import json
import pycurl
import re
import threading


def iconcat(seq):
    for subseq in seq:
        for x in subseq:
            yield x


def deepDictUpdate(dst, src):
    assert(isinstance(dst, dict))
    assert(isinstance(src, dict))
    for (k,v) in src.iteritems():
        if (isinstance(v, dict) and isinstance(dst.get(k), dict)):
            deepDictUpdate(dst[k], v)
        else:
            dst[k] = v
    return dst


def brackets(o, c, seq):
    n = 0
    chunk = ""
    for x in seq:
        if x == o:
            n = n + 1
        if n > 0:
            chunk = chunk + x
        if x == c:
            n = n - 1
            if n == 0:
                yield chunk
                chunk = ""


def istream(url):
    END_OF_INPUT = object()

    def worker(url, queue):
        c = pycurl.Curl()
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.WRITEFUNCTION, queue.put)
        c.setopt(pycurl.FOLLOWLOCATION, 1)
        c.unsetopt(pycurl.CAPATH)
        c.setopt(pycurl.SSL_VERIFYPEER, 1)
        c.setopt(pycurl.SSL_VERIFYHOST, 2)
        c.setopt(c.HTTPHEADER, ["User-Agent: curl/7.26.0"])
        try:
            c.perform()
        except Exception, exn:
            queue.put(exn)
        queue.put(END_OF_INPUT)

    queue = Queue.Queue()
    thread = threading.Thread(target=worker, args=(url,queue,))
    thread.start()
    chunk = queue.get()
    while chunk is not END_OF_INPUT:
        if isinstance(chunk, Exception):
            raise chunk
        yield chunk
        chunk = queue.get()
    thread.join()


def translate(d):
    """
    http://www.underdog-projects.net/2008/12/use-yahoo-finance-streaming-api/
    parameter 's' -> symbol on the main site (what you currently looking at)
    parameter 'o' -> that is the ticker on the top
    parameter 'k' and 'j' -> that are the values that are transfered

    http://www.underdog-projects.net/2008/12/use-yahoo-finance-streaming-api/
    available symbols do , or may include any of the following:
    a00,a50,b00,b20,b30,b60,c10,c60,c63,c64,c81,c82,c85,c86,g00,h00,l10,l84,l86,l90,l91,o40,o50,p20,p40,p41,p43,p44,t10,t50,t51,t53,t54,v00,z02,z08,z09
    """
    property_dictionary = {
        "c10": "unknown c10 ? previous close %",
        "g00": "day low",
        "h00": "day high",
        "l10": "current price ? last trade",
        "p20": "unknown p20 ? time of last trade",
        "t10": "timstamp",
        "a00": "ask",
        "b00": "bid",
        "v00": "todays volume",
    }

    if "unixtime" in d:
        return d
    for (k,v) in d.iteritems():
        d[k] = dict((property_dictionary.get(a),b) for (a,b) in v.iteritems())
    return d


def istream_yf(tickers, props):
    def preproc_data(s):
        x = s[1:-3].partition('(')[2]
        return re.sub("[A-Za-z0-9]+:", lambda a: '"' + x.__getslice__(*a.span())[0:-1]+'":', x)

    url = "".join((
        "http://streamerapi.finance.yahoo.com/streamer/1.0?s=",
        ",".join(tickers),
        "&k=",
        ",".join(props),
        "&callback=parent.yfs_u1f&mktmcb=parent.yfs_mktmcb&gencallback=parent.yfs_gencb"))
    print url
    return itertools.imap(
        lambda x: json.loads(preproc_data(x)),
        itertools.ifilter(
            lambda x: x != '{}',
            brackets('{', '}', iconcat(istream(url)))))


def main(tickers):
    source = istream_yf(
        tickers,
        ["l10,a00,b00,t10,g00,h00,v00"])

    state = {}
    for chunk in source:
        deepDictUpdate(state, translate(chunk))
        print json.dumps(state, indent=2)

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
