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

    def disconnect(self):
        """ Socket disconnect implementation, zqm socket variant """

        self.socket.unbind(self.binding)

    def _process(self, *args):
        """ Implement a request reply logic """

        id, empt, req = args
        rep = self._respond(req)

        # Only send it there is a response
        if rep:
            try:
                self._send(id_frame=id, empty_frame=empt, msg=rep)
            except zmq.ZMQError as e:
                print("Error %s" % e)

    def _respond(self, req):
        """ Method defines how the data should be proccessed and
         return a response to caller. Should be overridden by user """

        # Note: Returning None will cancell server response but can block
        # Socket based on zmq configuration
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

        # Server does not need Asynchronous buffered queues since it needs to
        # enforce the comms pattern of zmq req/rep. router/rep and will handle
        # Clients in isolated threads
        try:
            m = self._recv()
            print("Received " + m[2])
        except zmq.ZMQError as e:
            print("Error %s" % e)

        # Spawn a new thread to handle the response
        self.worker_pool.spawn(self._process, *m)

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
