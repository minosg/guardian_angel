#!/usr/bin/env python

"""app.py: Main Guardian Angel app running on PI device ..."""

from __future__ import print_function
import util.projectpath

from node import Node
import gevent

__author__ = "Minos Galanakis"
__license__ = "LGPL"
__version__ = "X.X.X"
__email__ = "minos197@gmail.com"
__project__ = "codename"
__date__ = "26-06-2017"


class App(Node):

    def node_init(self):
        pass

    def node_main(self):
        """ User implemented main loop for node """

        if self.has_msg():
            m = self.get_msg()
            # print("Node Relayed Message: %s" % m)
        gevent.sleep(0.1)

if __name__ == "__main__":
    app = App()
    try:
        while True:
            gevent.sleep(0.1)
    except KeyboardInterrupt:
        app.stop()
        app.join(timeout=5)
