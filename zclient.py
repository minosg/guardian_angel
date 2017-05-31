#!/usr/bin/env python

"""zclient.py: Zmq Generic Async Client module ..."""

from __future__ import print_function
import gevent
import zmq.green as zmq
import zmq.error
from zgreenbase import zeroGreenBase

__author__ = "Minos Galanakis"
__license__ = "LGPL"
__version__ = "X.X.X"
__email__ = "minos197@gmail.com"
__project__ = "codename"
__date__ = "26-05-2017"


class ZClient(zeroGreenBase):

    def __init__(self,
                 hostname,
                 port,
                 transport,
                 zmq_mode,
                 max_workers=None):
        """ Instantiate an client object that will accept """

        super(ZClient, self).__init__(hostname,
                                      port,
                                      transport,
                                      zmq_mode)

    def connect(self):
        self.socket.connect(self.binding)

    def _send(self, **kwargs):
        self.socket.send(self._pack(kwargs["msg"]))

    def _recv(self):
        return self.socket.recv()

    def _main(self):
        """ Main server loop that blocks on receive and spawn a different thread
        to deal with it. """

        # Try to send a message to server i
        try:
            m = self.tx_q.get(block=False, timeout=self._tx_timeout)
            self._send(msg=m)
        except zmq.error.ZMQError:
            pass
        except gevent.queue.Empty:
            pass

        # After a send operations receive the response
        try:
            rep = self._recv()
            self.rx_q.put(rep, block=False, timeout=self._rx_timeout)
        except zmq.error.ZMQError:
            pass
        except gevent.queue.Empty:
            pass
        gevent.sleep(0.1)

if __name__ == "__main__":
    ZC = ZClient("localhost", 24124, "tcp", zmq.REQ)
    ZC.connect()
    ZC.start()
    test_msg = "Hello"
    try:
        while True:
            ZC.send_msg(test_msg)
            print("Sending %s" % test_msg)
            gevent.sleep(0.3)
            if ZC.has_msg():
                rep = ZC.get_msg(blk=True)
                print("Response %s" % rep)
            gevent.sleep(1)
    except KeyboardInterrupt:
        ZC.stop()
        ZC.join(timeout=5)
