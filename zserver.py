#!/usr/bin/env python

"""zserver.py: Zmq Generic Async Server module ..."""

from __future__ import print_function
import gevent
import gevent.pool
import zmq.green as zmq
from zgreenbase import zeroGreenBase

__author__ = "Minos Galanakis"
__license__ = "LGPL"
__version__ = "X.X.X"
__email__ = "minos197@gmail.com"
__project__ = "codename"
__date__ = "26-05-2017"


class ZServer(zeroGreenBase):

    def __init__(self,
                 hostname,
                 port,
                 transport,
                 zmq_mode,
                 max_workers=None):
        """ Instantiate an client object that will accept """

        super(ZServer, self).__init__(hostname,
                                      port,
                                      transport,
                                      zmq_mode)
        self.worker_pool = gevent.pool.Pool(size=max_workers)

    def connect(self):
        self.socket.bind(self.binding)

    def _process(self, id, empt, req):
        """ Implement a request reply logic """

        rep = self._respond(req)
        self._send(id_frame=id, empty_frame=empt, msg=rep)

    def _respond(self, req):
        """ Method defines how the data should be proccessed and
         return a response to caller. Should be overridden by user """

        return req + " to you too"

    def _send(self, **kwargs):
        """ Expose the send method. This should be overridden if different
        functionality is implemented """

        self.socket.send_multipart([kwargs["id_frame"],
                                    kwargs["empty_frame"],
                                    self._pack(kwargs["msg"])])

    def _recv(self):
        id_frame, empty_frame, data_frame = self.socket.recv_multipart()
        return [id_frame, empty_frame, self._unpack(data_frame)]

    def _main(self):
        """ Main server loop that blocks on receive and spawn a different thread
        to deal with it. """

        id_frame, empty_frame, req = self._recv()
        print("Received " + req)
        self.worker_pool.spawn(self._process, id_frame, empty_frame, req)


if __name__ == "__main__":
    Zs = ZServer("*", 24124, "tcp", zmq.ROUTER)
    Zs.connect()
    Zs.start()
    try:
        while True:
            gevent.sleep(0.1)
    except KeyboardInterrupt:
        Zs.stop()
        Zs.join(timeout=5)
