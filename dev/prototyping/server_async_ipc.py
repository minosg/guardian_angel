#!/usr/bin/env python

"""server_async_ipc.py: Asynchronous Router Server using inter proccess
posix signalling """

from __future__ import print_function
import gevent
import time
import zmq.green as zmq
import ga_messages_pb2 as gmessages


__author__ = "Minos Galanakis"
__license__ = "GPL3"
__version__ = "0.0.1"
__email__ = "minos197@gmail.com"
__project__ = "ga"
__date__ = "19-05-2017"


def compose_ack(ack="ACK"):
    """ Compose a standard acknowlege message """

    # Add the metadata
    msg = gmessages.Message()
    msg.metadata.message_type = 0
    msg.metadata.device_id = 0
    msg.metadata.network_id = 0
    msg.metadata.application_id = 0
    msg.metadata.tx_time = int(time.time())
    msg.metadata.sequence = 1
    msg.metadata.periph_count = 0
    msg.metadata.device_name = "Server"

    # Add an ACK command
    msg.control.key = 0
    msg.control.is_indexed = False
    msg.control.cmd = ack
    return msg


def server():

    # Set up port and protocol
    port = "24124"
    binding = "tcp://*:%s" % port
    binding_ipc = "ipc:///tmp/zmqtest"

    # Set up 0MQ as Request/Response topology
    context = zmq.Context()
    server_socket = context.socket(zmq.ROUTER)

    # Bind to the socket
    ##server_socket.setsockopt(zmq.IDENTITY, 'reader')
    server_socket.bind(binding_ipc)
    time.sleep(0.1)
    while True:
        # Receive the mesasage
        id_frame, empty_frame, message = server_socket.recv_multipart()

        try:
            # De-Serialize it
            msg = gmessages.Message()
            msg.ParseFromString(message)

            # Report it
            print(("Message of type \"%d\"received from \"%s\" "
                  "with %d peripherals") % (msg.metadata.message_type,
                                            msg.metadata.device_name,
                                            msg.metadata.periph_count))
            for p in msg.peripheral:
                print(("Peripheral \"%s\" with id: \"%d\""
                      " contains payload of \"%s\"") % (p.peripheral_name,
                                                        p.peripheral_id,
                                                        repr(p.payload)[1:-1]))
            print("")
            ack = compose_ack("ACK")
        except Exception:
            ack = compose_ack("NACK")

        # Respond to client
        server_socket.send_multipart([id_frame,
                                      empty_frame,
                                      ack.SerializeToString()])


if __name__ == "__main__":

    try:
        server = gevent.spawn(server)
        server.join()
    except KeyboardInterrupt:
        print("Shutting Down Server")
