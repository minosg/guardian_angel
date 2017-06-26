#!/usr/bin/env python

"""zgreenbase.py: Core modude for ZMQ and Greenlet module deployment ..."""

from __future__ import print_function
import gevent
import zmq.green as zmq
from gevent import Greenlet, queue
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
    _rx_timeout = 3
    _tx_timeout = 3
    _rx_buff_size = 128
    _tx_buff_size = 128

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
        self.rx_q = gevent.queue.Queue(maxsize=self._rx_buff_size)
        self.tx_q = gevent.queue.Queue(maxsize=self._tx_buff_size)
        self.running = False

    @abstractmethod
    def connect(self):
        """ Socket connect implementation, zqm socket variant """
        pass

    @abstractmethod
    def disconnect(self):
        """ Socket disconnect implementation, zqm socket variant """

        pass

    @abstractmethod
    def _send(self, **kwargs):
        """ Socket send implementation, zqm socket variant """
        pass

    @abstractmethod
    def _recv(self):
        """ Socket receive implementation, zqm socket variant """
        pass

    def _pack(self, msg):
        """ Method defines how the data are serialized before transmission.
        Should be overridden by user """

        return msg

    def _unpack(self, msg):
        """ Method defines how the data should be proccessed and
         return a response to caller. Should be overridden by user """

        return msg

    @abstractmethod
    def _main(self):
        """ Main server loop that blocks on receive and spawn a different thread
        to deal with it. """

        pass

    def _run(self):
        """ Main run loop """

        self.running = True
        while self.running:
            self._main()

    def stop(self):
        """ Main run loop """

        self.running = False

    def send_msg(self, msg, blk=True, tmout=None):
        """ Place a message in the transmit queue """

        self.tx_q.put(msg, block=blk, timeout=tmout)

    def get_msg(self, blk=True, tmout=None):
        """ Get a message from the receive queue """

        return self.rx_q.get(block=blk, timeout=tmout)

    def has_msg(self):
        """ Indicate if incoming queue has any messages """
        return not self.rx_q.empty()

    def cleanup(self):
        try:
            self.disconnect()
        except zmq.ZMQError:
            pass
        self.socket.close()
        self.context.destroy()

if __name__ == "__main__":
    pass
