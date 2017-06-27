#!/usr/bin/env python

"""node.py: Central Node. It acts as a inproc server for internal modules
and a client to a remote server ..."""

from __future__ import print_function
import projectpath
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

        # Read the message and register the module
        try:
            # Detect registration message
            if req.msg_type == NodeMessenger.REG:
                # create an index pointer for each module name
                namel = {v["name"]: k for k, v in self._modules.iteritems()}
                if not self._modules.keys():
                    mod_id = 1
                # If the name exists give module the same id
                elif req.device_name in namel:
                    mod_id = namel[req.device_name]
                # TODO make it clean old keys based on last time
                else:
                    print(max(self._modules.keys()) + 2)
                    mod_id = max(self._modules.keys()) + 1

                self._modules[mod_id] = {"name": req.device_name,
                                         "last": req.time}

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

        # TODO forward it to server, this is temporary for protobuf testing
        print("Forwarding message")
        print(req)

        # Wrap it around an uplink message
        uplink_msg = self.remote.messenger.preamble_msg([req])
        return (self.upload(uplink_msg))
        # Note: In production code this needs to be Async since tx over
        # the wire round trip time >= over the ram rtt. Alternatively it
        # should aknowledge the  inproc message and then manage the remote
        # connection without time contrains
        # return (self.upload("Nodemodule: %s" % req).replace("Nodemodule",
        #                                                    "Server"))

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
                    # This is the part that uplink message is stripped out
                    # I am taking one wrong assumptions here, for demo purposes
                    # That the message contains one peripheral peripheral[0]
                    # TODO make it real code
                    return self.remote.get_msg(blk=True).peripheral[0]
            raise Exception("Timeout waiting for response")
        self.remote.disconnect()


if __name__ == "__main__":
    pass
