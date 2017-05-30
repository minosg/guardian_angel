#!/usr/bin/env python

"""zgreenbase.py: Core modude for ZMQ and Greenlet module deployment ..."""

from __future__ import print_function
import gevent
import zmq.green as zmq
from gevent import Greenlet
from abc import ABCMeta, abstractmethod

__author__ = "Minos Galanakis"
__license__ = "LGPL"
__version__ = "X.X.X"
__email__ = "minos197@gmail.com"
__project__ = "codename"
__date__ = "26-05-2017"


class zeroGreenBase(Greenlet):

    __metaclass__ = ABCMeta

    _transport_ptcl_ = {"inproc", "ipc", "tcp", "pgm", "epgm"}

    def __init__(self,
                 hostname,
                 port,
                 transport,
                 zmq_mode):
        """ Instantiate an client object that will accept """

        super(zeroGreenBase, self).__init__()
        if transport not in self._transport_ptcl_:
            raise ValueError("Invalid transport %s" % transport)
        self.port = port
        self.hostname = hostname
        self.transport = transport
        if transport == "ipc":
            self.binding = "ipc:///tmp/%s" % (hostname)
        else:
            self.binding = "%s://%s:%s" % (transport, hostname, port)
        self.zmq_mode = zmq_mode
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq_mode)
        self.running = False

    @abstractmethod
    def connect(self): pass

    @abstractmethod
    def _send(self, **kwargs): pass

    @abstractmethod
    def _recv(self): pass

    def _pack(self, msg):
        """ Method defines how the data are serialized before transmission.
        Should be overridden by user """

        return msg

    def _unpack(self, msg):
        """ Method defines how the data should be proccessed and
         return a response to caller. Should be overridden by user """

        return msg

    def _main(self):
        """ Main server loop that blocks on receive and spawn a different thread
        to deal with it. """

        print("Sending to Server")
        self._send("Hello")
        rep = self._recv()
        print("Server's response: %s" % rep)
        gevent.sleep(1)

    def _run(self):
        """ Main run loop """

        self.running = True
        while self.running:
            self._main()

    def stop(self):
        """ Main run loop """

        self.running = False

if __name__ == "__main__":
    pass
