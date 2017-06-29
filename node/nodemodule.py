#!/usr/bin/env python

"""nodemodule.py: Module Description ..."""

from __future__ import print_function
import sys
import projectpath
import zmq.green as zmq
import zmq.error
import gevent
from zclient import ZClient
from abc import ABCMeta, abstractmethod
from nodemessenger import NodeMessenger
from colorlogger import CLogger as log

__author__ = "Minos Galanakis"
__license__ = "LGPL"
__version__ = "0.0.1"
__email__ = "minos197@gmail.com"
__project__ = "ga"
__date__ = "30-05-2017"

log.setup(__file__, projectpath.log_level)


class NodeModule(ZClient):
    """ Communications module that implemts a request/response logic """

    __metaclass__ = ABCMeta

    def __init__(self,
                 ipcfname="zmqnode",
                 modulename="NodeModule"):
        """ Instantiate an client object that will accept """

        super(NodeModule, self).__init__(ipcfname,
                                         None,
                                         "ipc",
                                         zmq.REQ)
        # Node Modules should automatically start/connect
        self.connect()
        self.start()

        self.messenger = NodeMessenger(modulename)
        self._name = modulename
        # Core logic of the node should run independantly of rx/tx
        self.node_core = gevent.spawn(self._node_loop)

    def _node_loop(self):
        """ Parallel greenlet for user code """

        self.node_init()
        self.node_register()
        while self.running:
            self.node_main()
            gevent.sleep(1)

    def node_register(self):
        """ User accessible method for handling registration message """

        try:
            # Prepare and send the registration message
            init_msg = self.messenger.register_msg()

            self._send(msg=init_msg)
            # Accept the new module_id from server
            reginfo = self._recv()

            # If server accepted registration continue
            if reginfo.msg_type == NodeMessenger.ACK:

                node_id = [n for n in reginfo.payload][0].msg
                node_id = int(node_id)
                self.messenger.set_id(node_id)
                log.info("Registration Accepted, new id %d" % node_id)
                return
            else:
                raise Exception()
        except Exception as e:
            log.error("Failed to register module %s" % e)
            sys.exit(1)

    @abstractmethod
    def node_main(self):
        """ User implemented main loop for node """

        pass

    @abstractmethod
    def node_init(self):
        """ Initialisation of node """

        pass

    def _pack(self, msg):
        """ Set protobuf messenger as serialiser """
        return self.messenger.pack(msg)

    def _unpack(self, msg):
        """ Set protobuf messenger as de-serialiser """
        return self.messenger.unpack(msg)

if __name__ == "__main__":
    pass
