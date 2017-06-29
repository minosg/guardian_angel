#!/usr/bin/env python

"""backend.py: Module Description ..."""

from __future__ import print_function
import util.projectpath
import gevent
from nodeserver import NodeServer
from ulinkmessenger import ULinkMessenger
from zmq import ROUTER
from colorlogger import CLogger as log

__author__ = "Minos Galanakis"
__license__ = "LGPL"
__version__ = "X.X.X"
__email__ = "minos197@gmail.com"
__project__ = "codename"
__date__ = "26-06-2017"

log.setup(__file__, util.projectpath.log_level)


class Backend(NodeServer):

    def __init__(self,
                 hostname,
                 port,
                 transport,
                 zmq_mode,
                 max_workers=None):

        super(Backend, self).__init__(hostname,
                                      port,
                                      transport,
                                      zmq_mode)
        self.worker_pool = gevent.pool.Pool(size=max_workers)
        self.messenger = ULinkMessenger("Backend")

    def _respond(self, req):
        """ Method defines how the data should be proccessed and
         return a response to caller. Should be overridden by user """

        log.info("Server Received message")
        print(req)

        # Detect and handle registration message
        if req.metadata.message_type == self.messenger.REG:
            return self.network_register(req)
        # I am taking two wrong assumptions here, for demo purposes
        # That the message contains one peripheral peripheral[0]
        # And that it contains one service payload[0]
        # TODO make it real code
        msg = req.peripheral[0].payload[0].msg
        req.peripheral[0].payload[0].msg = "%s to you too" % msg
        return req

if __name__ == "__main__":
    Zs = Backend("*", 24124, "tcp", ROUTER)
    Zs.connect()
    Zs.start()
    try:
        while True:
            gevent.sleep(0.1)
    except KeyboardInterrupt:
        Zs.stop()
        Zs.join(timeout=5)
