#!/usr/bin/env python

"""client_ipc.py: Synchronous REQ client using inter proccess
posix signalling """

from __future__ import print_function
import sys
import time
import gevent
import zmq.green as zmq
import ga_messages_pb2 as gmessages

__author__ = "Minos Galanakis"
__license__ = "GPL3"
__version__ = "0.0.1"
__email__ = "minos197@gmail.com"
__project__ = "ga"
__date__ = "19-05-2017"


def client(msg):

    # Set up port and protocol
    port = "24124"
    binding = "tcp://localhost:%s" % port
    binding_ipc = "ipc:///tmp/zmqtest"
    ipc_envelope_tag = "client_ipc"

    # Set up 0MQ as Request/Response topology
    context = zmq.Context()
    client_socket = context.socket(zmq.REQ)

    # Name the envelope/frameID so the receiver knows who sent it
    client_socket.setsockopt(zmq.IDENTITY, 'ipc_envelope_tag')
    client_socket.connect(binding_ipc)
    time.sleep(0.1)

    # Send one message and exit
    print("Sending Message of type \"%d\"" % msg.metadata.message_type)
    client_socket.send(msg.SerializeToString())

    # Wait for response
    message = client_socket.recv()

    # De-Serialize response
    ack = gmessages.Message()
    ack.ParseFromString(message)
    print("Received reply [%s]" % (ack.control.cmd))

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage:", sys.argv[0], "INPUT_FILE")
        sys.exit(1)

    msg = gmessages.Message()

    try:
        with open(sys.argv[1], "rb") as f:
            msg.ParseFromString(f.read())
    except IOError:
        print(sys.argv[1] + ": File not found.")
        sys.exit(1)

    clnt = gevent.spawn(client, msg)
    clnt.join()
