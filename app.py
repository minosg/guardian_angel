#!/usr/bin/env python

"""app.py: Main Guardian Angel app running on PI device ..."""

from __future__ import print_function
import util.projectpath
from nodemessenger import NodeMessenger
from node import Node
import gevent

__author__ = "Minos Galanakis"
__license__ = "LGPL"
__version__ = "0.0.1"
__email__ = "minos197@gmail.com"
__project__ = "ga"
__date__ = "26-06-2017"


class App(Node):

    def node_init(self):
        """ All Initialisation code that runs once goes here """

        # Set the device name
        self.ul_messenger.set_metadata(name="Guardian Angel One")

        # Set the device location information for network registration
        self.ul_messenger.set_location(12.213, 34.2132,
                                       "Moufa Street",
                                       "Tall Building",
                                       "Floor 99",
                                       "Room 14",
                                       "Rapture",
                                       "Atlantis",
                                       "RPT ATL")

    def node_main(self):
        """ Main Logic """

        if self.has_msg():
            m = self.get_msg()
            # print("Node Relayed Message: %s" % m)
        gevent.sleep(0.1)

    # Override
    def _respond(self, req):
        """ Reponse """

        # Note: In production code this needs to be Async since tx over
        # the wire round trip time >= over the ram rtt. Alternatively it
        # should aknowledge the  inproc message and then manage the remote
        # connection without time contrains
        # return (self.upload("Nodemodule: %s" % req).replace("Nodemodule",

        # store all incoming messages to the queue
        # in order to proccess in the node_main
        self.rx_q.put(req, block=False, timeout=self._rx_timeout)

        # Detect and handle registration message
        if req.msg_type == NodeMessenger.REG:
            return self.node_register(req)

        print("Forwarding message")
        print(req)

        # Wrap it around an uplink message
        uplink_msg = self.remote.messenger.preamble_msg([req])

        # This is the part that uplink response message is stripped out
        # I am taking one wrong assumptions here, for demo purposes
        # That the message contains one peripheral peripheral[0]
        # TODO make it real code
        return (self.upload(uplink_msg).peripheral[0])


if __name__ == "__main__":
    app = App()
    try:
        while True:
            gevent.sleep(0.1)
    except KeyboardInterrupt:
        app.stop()
        app.join(timeout=5)
