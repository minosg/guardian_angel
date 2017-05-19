#!/usr/bin/env python

"""read_proto_msg: Test protobuffer implementation by read a message from file..."""

import sys
import os
import time
import ga_messages_pb2 as gmessag

__author__ = "Minos Galanakis"
__license__ = "GPL V3"
__version__ = "0.0.1"
__email__ = "minos197@gmail.com"
__project__ = "ga"
__date__ = "19-05-2017"


def printMessage(msg):
    print "Message Type:", msg.metadata.message_type
    print "Device ID:", msg.metadata.device_id
    print "Network ID:", msg.metadata.network_id
    print "Aplication ID:", msg.metadata.application_id
    print "Msg time:", msg.metadata.tx_time
    print "Sequence:", msg.metadata.sequence
    print "Peripheral Count:", msg.metadata.periph_count
    print "Device Name:", msg.metadata.device_name
    for p in msg.peripheral:
        print "Peripheral ID", p.peripheral_id
        print "Payload ID", p.payload_id
        print "Peripheral Name", p.peripheral_name
        print "Payload Name", p.payload_name
        print "Payload Attached", p.payload_attached
        print "payload", repr(p.payload)[1:-1]
        print "payload crc", p.payload_crc


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage:", sys.argv[0], "INPUT_FILE"
        sys.exit(1)

    msg = gmessages.Message()

    try:
        with open(sys.argv[1], "rb") as f:
            msg.ParseFromString(f.read())
    except IOError:
        print sys.argv[1] + ": File not found."
        sys.exit(1)

    printMessage(msg)

