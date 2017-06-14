#!/usr/bin/env python

"""nodemesseger.py: Internal Node IPC message helper ..."""

import time
import crcmod
from node_messages_pb2 import *
from collections import namedtuple

__author__ = "Minos Galanakis"
__license__ = "LGPL"
__version__ = "0.0.1"
__email__ = "minos197@gmail.com"
__project__ = "ga"
__date__ = "13-06-2017"


class NodeMessengerError(Exception):
    __module__ = 'exceptions'


class NodeMessengerTypes(type):
    """ Metaclass that maps the messages types to human readable format """

    def __init__(cls, name, bases, dict):
        TYPE = {"ACK": 1,
                "NACK": 2,
                "REG": 3,
                "RST": 8,
                "REB": 9,
                "SOL": 10,
                "EVT": 11,
                "PER": 11}

        for t, v in TYPE.iteritems():
            setattr(cls, t, v)
        super(NodeMessengerTypes, cls).__init__(name, bases, dict)


class NodeMessenger(object):
        """ Helper function that facilitates nodemodules message handling """

        __metaclass__ = NodeMessengerTypes

        _service = namedtuple("Service", "name msg payload crc")

        def __init__(self, name="Node"):
            self.seq = 1
            self.id = -1
            self._crc = crcmod.predefined.mkPredefinedCrcFun("crc-16-genibus")
            self._name = name

        @staticmethod
        def _crcgen():
            """ overridden by the crc selected in init"""
            pass

        def set_id(self, id):
            """ Update the NodeId after a register command """

            self.id = id

        def set_sequence(self, seq):
            """" Change the internally stored sequence number """

            self.seq = seq

        def set_name(self, name):
            self._name = name

        def _new_msg(self, seq=None):
            """ Generate the basic common base for a message """
            nm = NodeMessage()
            nm.device_id = self.id
            nm.sequence = self.seq if seq is None else seq
            nm.time = int(time.time())

            # If the sequence is user provided do not increment the counter
            if seq is None:
                self.seq += 1
            return nm

        def nack_msg(self, payload_list=None, seq=None):
            """ Negative Aknowledgement """

            nm = self._new_msg()
            nm.msg_type = self.NACK
            self._add_service(nm, payload_list)
            return nm

        def ack_msg(self, payload_list=None, seq=None):
            """ Aknowledgement """

            nm = self._new_msg()
            nm.msg_type = self.ACK
            self._add_service(nm, payload_list)
            return nm

        def register_msg(self, seq=None):
            """ Register new module """

            nm = self._new_msg()
            nm.device_name = self._name
            nm.msg_type = self.REG
            return nm

        def reset_msg(self, seq=None):
            """ Reset module """

            nm = self._new_msg()
            nm.msg_type = self.RST
            return nm

        def restart_msg(self, seq=None):
            """ Restart module """

            nm = self._new_msg()
            nm.msg_type = self.REB
            return nm

        def solicited_msg(self, payload_list, seq=None):
            """ Handshake conversation """

            nm = self._new_msg()
            nm.msg_type = self.SOL
            self._add_service(nm, payload_list)
            return nm

        def periodic_msg(self, payload_list, seq=None):
            """ Periodic unsolicited message """

            nm = self._new_msg()
            nm.msg_type = self.PER
            self._add_service(nm, payload_list)
            return nm

        def event_msg(self, payload_list, seq=None):
            """ Event triggered message """

            nm = self._new_msg()
            nm.msg_type = self.EVT
            self._add_service(nm, payload_list)
            return nm

        def new_service(self, name=None, msg=None, payload=None):
            """ Allow caller to create payload services """

            crc = self._crc("\x01\x02")
            return self._service(name=name, msg=msg, payload=payload, crc=crc)

        def pack(self, msg):
            return msg.SerializeToString()

        def unpack(self, data):
            nm = NodeMessage()
            nm.ParseFromString(data)
            if not nm.ByteSize():
                raise NodeMessengerError("Could not unpack message")
            return nm

        def _add_service(self, message, payload_list):
            """Internal method that attaches payload to message """

            if not payload_list:
                return
            if not isinstance(payload_list, list):
                payload_list = [payload_list]

            for service in payload_list:
                pl_entry = message.payload.add()
                if service.name:
                    pl_entry.name = service.name
                if service.msg:
                    pl_entry.msg = service.msg
                if service.payload:
                    pl_entry.payload = service.payload
                    pl_entry.crc = service.crc

if __name__ == "__main__":

    # create a message handler
    nm = NodeMessenger()

    # Create a simple nack message
    print nm.register_msg()

    # Change the id
    nm.set_id(123)

    # print ACK message
    print nm.ack_msg()

    # Create a full message
    pl = nm.new_service("Test Service")
    print("DDEEGB %s" % type(pl))
    print nm.solicited_msg(pl)
