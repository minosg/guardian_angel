#!/usr/bin/env python

"""create_proto_msg: Test protobuffer implementation by creating a message to bytes on file..."""

import sys
import os
import time
import ga_messages_pb2 as gmessages

__author__ = "Minos Galanakis"
__license__ = "GPL V3"
__version__ = "0.0.1"
__email__ = "minos197@gmail.com"
__project__ = "ga"
__date__ = "19-05-2017"


class PythonTemplate():

    def __init__(self):
        pass

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage:", sys.argv[0], "OUTPUT_FILE"
        sys.exit(1)

    # Add the metadata
    msg = gmessages.Message()
    msg.metadata.message_type = 0
    msg.metadata.device_id = 123
    msg.metadata.network_id = 0
    msg.metadata.application_id = 0
    msg.metadata.tx_time = int(time.time())
    msg.metadata.sequence = 1
    msg.metadata.periph_count = 1
    msg.metadata.device_name = "test device"

    # Add one Peripheral
    peripheral1 = msg.peripheral.add()
    peripheral1.peripheral_id = 0
    peripheral1.payload_id = 1
    peripheral1.peripheral_name = "Fake Sensor"
    peripheral1.payload_name = "fake_recording.data"
    peripheral1.payload_attached = False
    peripheral1.payload = "\x00\x01"
    peripheral1.payload_crc = 213


    # Write the new address book back to disk.
    with open(sys.argv[1], "wb") as f:
        f.write(msg.SerializeToString())

