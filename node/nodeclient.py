#!/usr/bin/env python

""" nodeclient.py: Node client that communicates with remote server """

from __future__ import print_function
import projectpath
from zclient import ZClient
from ulinkmessenger import ULinkMessenger

__author__ = "Minos Galanakis"
__license__ = "LGPL"
__version__ = "0.0.1"
__email__ = "minos197@gmail.com"
__project__ = "ga"
__date__ = "16-06-2017"


class NodeClient(ZClient):
    """ NodeClient is just a zclient instance with a protocol buffer messenger
    built in """

    def __init__(self,
                 hostname,
                 port,
                 transport,
                 zmq_mode,
                 max_workers=None):
        """ Instantiate an client object that will accept """

        super(NodeClient, self).__init__(hostname,
                                         port,
                                         transport,
                                         zmq_mode)

        self.messenger = ULinkMessenger("Node")

    def _pack(self, msg):
        """ Set protobuf messenger as serialiser """
        return self.messenger.pack(msg)

    def _unpack(self, msg):
        """ Set protobuf messenger as de-serialiser """
        return self.messenger.unpack(msg)
