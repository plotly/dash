"""Basic http server for tests to simulate PyPI or custom indexes
"""

import time
import threading
from setuptools.compat import BaseHTTPRequestHandler
from setuptools.compat import HTTPServer, SimpleHTTPRequestHandler

class IndexServer(HTTPServer):
    """Basic single-threaded http server simulating a package index

    You can use this server in unittest like this::
        s = IndexServer()
        s.start()
        index_url = s.base_url() + 'mytestindex'
        # do some test requests to the index
        # The index files should be located in setuptools/tests/indexes
        s.stop()
    """
    def __init__(self, server_address=('', 0),
            RequestHandlerClass=SimpleHTTPRequestHandler):
        HTTPServer.__init__(self, server_address, RequestHandlerClass)
        self._run = True

    def start(self):
        self.thread = threading.Thread(target=self.serve_forever)
        self.thread.start()

    def stop(self):
        "Stop the server"

        # Let the server finish the last request and wait for a new one.
        time.sleep(0.1)

        self.shutdown()
        self.thread.join()
        self.socket.close()

    def base_url(self):
        port = self.server_port
        return 'http://127.0.0.1:%s/setuptools/tests/indexes/' % port

class RequestRecorder(BaseHTTPRequestHandler):
    def do_GET(self):
        requests = vars(self.server).setdefault('requests', [])
        requests.append(self)
        self.send_response(200, 'OK')

class MockServer(HTTPServer, threading.Thread):
    """
    A simple HTTP Server that records the requests made to it.
    """
    def __init__(self, server_address=('', 0),
            RequestHandlerClass=RequestRecorder):
        HTTPServer.__init__(self, server_address, RequestHandlerClass)
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.requests = []

    def run(self):
        self.serve_forever()

    @property
    def url(self):
        return 'http://localhost:%(server_port)s/' % vars(self)
