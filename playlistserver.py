#!/usr/bin/env python

""" Simple server to serve music folders as playlists.

When run from directory, it will serve its content as
playlist, showing only files with appropriate extensions.

Most code "borrowed" from SimpleHTTPServer.
"""

__author__     = "Matej Kollar"
__contact__    = "xkolla06@stud.fit.vutbr.cz"

__version__    = "1.0"
__date__       = "2013. 10. 20."
__license__    = "GPLv3"

__credits__    = [__author__]
__maintainer__ = __author__
__status__     = "Working"

import SimpleHTTPServer
import BaseHTTPServer
import SocketServer
import os
import urllib
import sys
import errno

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


# class PlaylistHTTPServer(BaseHTTPServer.HTTPServer):
class PlaylistHTTPServer(
        SocketServer.ThreadingMixIn,
        BaseHTTPServer.HTTPServer):
    """Server to serve directory as a playlist"""

    ok_errnos = [
        errno.ECONNRESET,
        errno.EPIPE]

    def handle_error(self, request, client_address):
        """Handle an error gracefully.
        Ignore early connection close on client side,
        otherwise print traceback and continue.
        """
        err = sys.exc_info()[1]
        self.close_request(request)
        if isinstance(err, IOError) and err.errno in self.ok_errnos:
            return

        # New style `super` does not work here :-(
        return BaseHTTPServer.HTTPServer.handle_error(
            self, request, client_address)


class PlaylistHTTPHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    """Handler to serve directory as a playlist"""

    server_version = "PlaylistServer/" + __version__

    ALLOWED_EXTENSIONS = ["mp3", "flac"]

    def check_path(self, path):
        """Is path allowed?"""
        return path.rsplit('.', 1)[-1] in self.ALLOWED_EXTENSIONS

    def send_head(self):
        path = self.translate_path(self.path)
        if self.check_path(path) or os.path.isdir(path):
            return SimpleHTTPServer.SimpleHTTPRequestHandler.send_head(self)
        self.send_error(404, "Not found")
        return None

    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).

        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().

        """
        try:
            files = filter(self.check_path, os.listdir(path))
        except os.error:
            self.send_error(404, "Not found")
            return None
        files.sort(key=lambda a: a.lower())
        resp = StringIO()
        for name in files:
            fullname = os.path.join(path, name)
            if os.path.isdir(fullname):
                continue
            resp.write('%s\n' % urllib.quote(name))
        length = resp.tell()
        resp.seek(0)
        self.send_response(200)
        encoding = sys.getfilesystemencoding()
        self.send_header("Content-type", "text/plain; charset=%s" % encoding)
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return resp


def main():
    """Main. Takes one argument on command line: port to serve on."""
    if sys.argv[1:]:
        port = int(sys.argv[1])
    else:
        port = 8000
    server_address = ('', port)

    server = PlaylistHTTPServer(
        server_address, PlaylistHTTPHandler, "HTTP/1.1")

    print "Serving playlists on port", server_address[1], "..."

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print "Shutting down..."
        server.shutdown()


if __name__ == '__main__':
    main()
