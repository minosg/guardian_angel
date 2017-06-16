#!/usr/bin/env python

"""node.py: Central Node. It acts as a inproc server for internal modules
and a client to a remote server ..."""

from __future__ import print_function
import zmq
import gevent
import time
from zserver import ZServer
from zclient import ZClient
from abc import ABCMeta, abstractmethod

__author__ = "Minos Galanakis"
__license__ = "LGPL"
__version__ = "0.0.1"
__email__ = "minos197@gmail.com"
__project__ = "ga"
__date__ = "30-05-2017"


class Node(ZServer):
    """ Object that will accept inproc comms and
    relay them to a remote machine """

    __metaclass__ = ABCMeta

    def __init__(self,
                 remote="localhost",
                 remote_port=24124,
                 remote_transport="tcp",
                 remote_zmq_mode=zmq.REQ,
                 node_ipcfname="zmqnode",
                 node_zmq_mode=zmq.ROUTER):

        super(Node, self).__init__(node_ipcfname,
                                   None,
                                   "ipc",
                                   node_zmq_mode)

        # Set up the remote server connection
        self.remote = ZClient(remote,
                              remote_port,
                              remote_transport,
                              remote_zmq_mode)

        # Nodes should autostart
        self.remote.start()
        self.connect()
        self.start()

        # Core logic of the node should run independantly of rx/tx
        self.core = gevent.spawn(self._node_loop)

    def _node_loop(self):
        """ Parallel greenlet for user code """

        self.node_init()
        while self.running:
            self.node_main()
            gevent.sleep(1)

    @abstractmethod
    def node_main(self):
        """ User implemented main loop for node """

        pass

    @abstractmethod
    def node_init(self):
        """ Initialisation of node """

        pass

    def _respond(self, req):
        """ The Node's primary role is to relay the message and return the
        reponse to the calling module """

        # store all incoming messages to the queue
        # in orde to proccess in the node_main
        self.rx_q.put(req, block=False, timeout=self._rx_timeout)

        # Note: In production code this needs to be Async since tx over
        # the wire round trip time >= over the ram rtt. Alternatively it
        # should aknowledge the  inproc message and then manage the remote
        # connection without time contrains
        return (self.upload("Nodemodule: %s" % req).replace("Nodemodule",
                                                            "Server"))

    def upload(self, msg, response=True, timeout=10):
        """ Upload a message to remote server and can return the response """

        # Connect and send the message
        self.remote.connect()
        self.remote.send_msg(msg)
        start_t = time.time()
        if response:
            while (start_t - time.time() < timeout):
                gevent.sleep(0.1)
                if self.remote.has_msg():
                    return self.remote.get_msg(blk=True)
            raise Exception("Timeout waiting for response")
        self.remote.disconnect()


class testNode(Node):

    def node_init(self):
        pass

    def node_main(self):
        """ User implemented main loop for node """

        if self.has_msg():
            m = self.get_msg()
            print("Node Relayed Message: %s" % m)
        gevent.sleep(0.1)

if __name__ == "__main__":
    ND = testNode()
    try:
        while True:
            gevent.sleep(0.1)
    except KeyboardInterrupt:
        ND.stop()
        ND.join(timeout=5)