#!/usr/bin/env python

"""nodeserver.py: Remote backend server that talks protobuf ..."""

from __future__ import print_function
import gevent
import zmq.green as zmq
from zserver import ZServer
from nodemessenger import NodeMessenger

__author__ = "Minos Galanakis"
__license__ = "LGPL"
__version__ = "0.0.1"
__email__ = "minos197@gmail.com"
__project__ = "ga"
__date__ = "16-06-2017"


class NodeServer(ZServer):
    """ NodeServer is just a zclient instance with a protocol buffer messenger
    built in """

    def __init__(self,
                 hostname,
                 port,
                 transport,
                 zmq_mode,
                 max_workers=None):

        super(NodeServer, self).__init__(hostname,
                                         port,
                                         transport,
                                         zmq_mode)
        self.worker_pool = gevent.pool.Pool(size=max_workers)
        self.messenger = NodeMessenger("NodeServer")

    def _respond(self, req):
        """ Method defines how the data should be proccessed and
         return a response to caller. Should be overridden by user """

        print("Server Received msg")
        print(req)

        msg = req.payload[0].msg
        req.payload[0].msg = "%s to you too" % msg
        return req

    def _pack(self, msg):
        """ Set protobuf messenger as serialiser """
        return self.messenger.pack(msg)

    def _unpack(self, msg):
        """ Set protobuf messenger as de-serialiser """
        return self.messenger.unpack(msg)

if __name__ == "__main__":
    Zs = NodeServer("*", 24124, "tcp", zmq.ROUTER)
    Zs.connect()
    Zs.start()
    try:
        while True:
            gevent.sleep(0.1)
    except KeyboardInterrupt:
        Zs.stop()
        Zs.join(timeout=5)
