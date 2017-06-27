#!/usr/bin/env python

"""fakemodule.py: Module Description ..."""

from __future__ import print_function
import util.projectpath
import gevent
from nodemodule import NodeModule


__author__ = "Minos Galanakis"
__license__ = "LGPL"
__version__ = "X.X.X"
__email__ = "minos197@gmail.com"
__project__ = "codename"
__date__ = "26-06-2017"


class fakeNodeModule(NodeModule):

    def node_init(self):
        """ Initialisation of node """

        self.message_base = "Hello %d"
        self.counter = 0

    def node_main(self):
        """ User implemented main loop for node """

        test_msg_pl = self.messenger.new_service("Hello %d" % self.counter)
        test_msg = self.messenger.solicited_msg(test_msg_pl)
        self.send_msg(test_msg)
        print("Nodemodule: Sending")
        print(test_msg)

        gevent.sleep(0.3)
        if self.has_msg():
            print("Nodemodule: Received")
            rep = self.get_msg(blk=True)
            print("%s" % rep)
        self.counter += 1

if __name__ == "__main__":
    NM = fakeNodeModule()

    try:
        while True:
            gevent.sleep(1)
    except KeyboardInterrupt:
        NM.stop()
        NM.join(timeout=5)
