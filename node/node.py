#!/usr/bin/env python

"""node.py: Central Node. It acts as a inproc server for internal modules
and a client to a remote server ..."""

from __future__ import print_function
import projectpath
import sys
import zmq
import gevent
import time
from zserver import ZServer
from abc import ABCMeta, abstractmethod
from nodemessenger import NodeMessenger
from nodeclient import NodeClient

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
        self.remote = NodeClient(remote,
                                 remote_port,
                                 remote_transport,
                                 remote_zmq_mode)

        # Protobuf
        self.messenger = NodeMessenger("Node")

        # Id client for remote server
        self._network_id = -1

        # LIst of all the modules connected using the module id
        self._modules = {}

        # Nodes should autostart
        self.remote.start()
        self.connect()
        self.start()

        self.ul_messenger = self.remote.messenger

        # Core logic of the node should run independantly of rx/tx
        self.core = gevent.spawn(self._node_loop)

    def _pack(self, msg):
        """ Set protobuf messenger as serialiser """
        return self.messenger.pack(msg)

    def _unpack(self, msg):
        """ Set protobuf messenger as de-serialiser """
        return self.messenger.unpack(msg)

    def _node_loop(self):
        """ Parallel greenlet for user code """

        self.node_init()
        self.network_register()
        while self.running:
            self.node_main()
            gevent.sleep(1)

    def network_register(self):

        try:
            reg_msg = self.ul_messenger.register_msg()

            # Attempt to register and get the response
            reginfo = self.upload(reg_msg)

            # If server accepted registration continue
            if reginfo.metadata.message_type == self.ul_messenger.ACK:

                node_id = int([n for n in reginfo.control.params][0])
                self.messenger.set_id(node_id)
                print("Registration Accepted, new id %d" % node_id)
                return
            else:
                raise Exception()
        except Exception as e:
            print("Failed to register to network %s" % e)
            sys.exit(1)
        print(reg_msg)

    @abstractmethod
    def node_main(self):
        """ User implemented main loop for node """

        pass

    @abstractmethod
    def node_init(self):
        """ Initialisation of node """

        pass

    def node_register(self, message):
        """ Module registration authority handling. Can be overriden by user"""

        try:
            # create an index pointer for each module name
            namel = {v["name"]: k for k, v in self._modules.iteritems()}
            if not self._modules.keys():
                mod_id = 1
            # If the name exists give module the same id
            elif message.device_name in namel:
                mod_id = namel[message.device_name]
            # TODO make it clean old keys based on last time
            else:
                print(max(self._modules.keys()) + 2)
                mod_id = max(self._modules.keys()) + 1

            self._modules[mod_id] = {"name": message.device_name,
                                     "last": message.time}

            # prepare the payload for the acknowlegement
            pl = self.messenger.new_service(msg="%d" % mod_id)
            response = self.messenger.ack_msg(pl)

            # Repond to node with the module id
            return(response)
        except Exception as e:
            print("Exception %s" % e)
            pl = self.messenger.new_service(name="%s" % e)
            response = self.messenger.ack_msg(pl)

            # Repond to node with exception
            return(response)

    def _respond(self, req):
        """ The Node's primary role is to relay the message and return the
        reponse to the calling module """

        # store all incoming messages to the queue
        # in orde to proccess in the node_main
        self.rx_q.put(req, block=False, timeout=self._rx_timeout)

        # Detect and handle registration message
        if req.msg_type == NodeMessenger.REG:
            return self.node_register(req)

        # ACK is default response
        return(self.messenger.ack_msg())

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


if __name__ == "__main__":
    pass
