#!/usr/bin/env python

"""zclient.py: Zmq Generic Async Client module ..."""

from __future__ import print_function
import gevent
import zmq.green as zmq
from zgreenbase import zeroGreenBase

__author__ = "Minos Galanakis"
__license__ = "LGPL"
__version__ = "X.X.X"
__email__ = "minos197@gmail.com"
__project__ = "codename"
__date__ = "26-05-2017"


class zeroclient(zeroGreenBase):

    def __init__(self,
                 hostname,
                 port,
                 transport,
                 zmq_mode,
                 max_workers=None):
        """ Instantiate an client object that will accept """

        super(zeroclient, self).__init__(hostname,
                                         port,
                                         transport,
                                         zmq_mode)

    def connect(self):
        self.socket.connect(self.binding)

    def _send(self, **kwargs):
        self.socket.send(self._pack(kwargs["msg"]))

    def _recv(self):
        return self.socket.recv()

    def _main(self):
        """ Main server loop that blocks on receive and spawn a different thread
        to deal with it. """

        print("Sending to Server")
        self._send(msg="Hello")
        rep = self._recv()
        print("Response: %s" % rep)
        gevent.sleep(1)

if __name__ == "__main__":
    zC = zeroclient("localhost", 24124, "tcp", zmq.REQ)
    zC.connect()
    zC.start()
    try:
        while True:
            gevent.sleep(0.1)
    except KeyboardInterrupt:
        zC.stop()
        zC.join(timeout=5)
