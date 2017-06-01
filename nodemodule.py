#!/usr/bin/env python

"""nodemodule.py: Module Description ..."""

from __future__ import print_function
import zmq.green as zmq
import zmq.error
import gevent
from zclient import ZClient
from abc import ABCMeta, abstractmethod

__author__ = "Minos Galanakis"
__license__ = "LGPL"
__version__ = "0.0.1"
__email__ = "minos197@gmail.com"
__project__ = "ga"
__date__ = "30-05-2017"


class NodeModule(ZClient):
    """ Communications module that implemts a request/response logic """

    __metaclass__ = ABCMeta

    def __init__(self,
                 ipcfname="zmqnode"):
        """ Instantiate an client object that will accept """

        super(NodeModule, self).__init__(ipcfname,
                                         None,
                                         "ipc",
                                         zmq.REQ)
        # Node Modules should automatically start/connect
        self.connect()
        self.start()

        # Core logic of the node should run independantly of rx/tx
        self.node_core = gevent.spawn(self._node_loop)

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


class testNodeModule(NodeModule):

    def node_init(self):
        """ Initialisation of node """

        self.message_base = "Hello %d"
        self.counter = 0

    def node_main(self):
        """ User implemented main loop for node """

        test_msg = self.message_base % self.counter
        self.send_msg(test_msg)
        print("Nodemodule: Sending %s" % test_msg)
        gevent.sleep(0.3)
        if self.has_msg():
            rep = self.get_msg(blk=True)
            print("%s" % rep)
        self.counter += 1

if __name__ == "__main__":
    NM = testNodeModule()

    try:
        while True:
            gevent.sleep(1)
    except KeyboardInterrupt:
        NM.stop()
        NM.join(timeout=5)
