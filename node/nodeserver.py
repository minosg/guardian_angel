#!/usr/bin/env python

"""nodeserver.py: Remote backend server that talks protobuf ..."""

from __future__ import print_function
import sys
import projectpath
import gevent
import zmq.green as zmq
from zserver import ZServer
from ulinkmessenger import ULinkMessenger

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
        self.messenger = ULinkMessenger("NodeServer")

    def _pack(self, msg):
        """ Set protobuf messenger as serialiser """
        return self.messenger.pack(msg)

    def _unpack(self, msg):
        """ Set protobuf messenger as de-serialiser """
        return self.messenger.unpack(msg)

if __name__ == "__main__":
    print(sys.path)
    pass
