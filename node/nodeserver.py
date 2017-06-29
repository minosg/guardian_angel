#!/usr/bin/env python

"""nodeserver.py: Remote backend server that talks protobuf ..."""

from __future__ import print_function
import sys
import projectpath
import gevent
import zmq.green as zmq
from zserver import ZServer
from ulinkmessenger import ULinkMessenger
from colorlogger import CLogger as log

__author__ = "Minos Galanakis"
__license__ = "LGPL"
__version__ = "0.0.1"
__email__ = "minos197@gmail.com"
__project__ = "ga"
__date__ = "16-06-2017"

log.setup(__file__, projectpath.log_level)


class NodeServer(ZServer):
    """ NodeServer is just a zclient instance with a protocol buffer messenger
    and a registration mechanism built in """

    def __init__(self,
                 hostname,
                 port,
                 transport,
                 zmq_mode,
                 max_workers=None):

        super(NodeServer, self).__init__(hostname,
                                         port,
                                         transport,
                                         zmq_mode)
        self.worker_pool = gevent.pool.Pool(size=max_workers)
        self.messenger = ULinkMessenger("NodeServer")

        # LIst of all the clieants connected
        self._clients = {}

    def _respond(self, req):
        """ Method defines how the data should be proccessed and
         return a response to caller. Should be overridden by user """

        # Note: Returning None will cancell server response but can block
        # Socket based on zmq configuration
        log.info("Server Received message")
        print(req)
        # Detect and handle registration message
        if req.msg_type == self.ul_messenger.REG:
            return self.network_register(req)
        return req

    def network_register(self, message):
        try:
            metadata = message.metadata
            loc = message.location
            # create an index pointer for each module name
            namel = {v["name"]: k for k, v in self._clients.iteritems()}
            if not self._clients.keys():
                client_id = 1
            # If the name exists give module the same id
            elif metadata.device_name in namel:
                client_id = namel[metadata.device_name]
            # TODO make it clean old keys based on last time
            else:
                client_id = max(self._clients.keys()) + 1

            if loc:
                location = self.messenger._location_tpl(lat=loc.lat,
                                                        long=loc.long,
                                                        street=loc.street,
                                                        building=loc.building,
                                                        floor=loc.floor,
                                                        room=loc.room,
                                                        city=loc.city,
                                                        country=loc.country,
                                                        postcode=loc.postcode)
            self._clients[client_id] = {"name": metadata.device_name,
                                        "app_id": metadata.app_id,
                                        "network_id": metadata.network_id,
                                        "last": metadata.time,
                                        "location": location}

            # prepare the payload for the acknowlegement
            response = self.messenger.ack_msg(cmd="register",
                                              params=["%s" % client_id])
            # Repond to node with the module id
            return(response)
        except Exception as e:
            log.error("Exception %s" % e)
            # prepare the payload for the acknowlegement
            response = self.messenger.nack_msg(cmd="register",
                                               params=["%s" % e])

            # Repond to node with exception
            return(response)

    def _pack(self, msg):
        """ Set protobuf messenger as serialiser """
        return self.messenger.pack(msg)

    def _unpack(self, msg):
        """ Set protobuf messenger as de-serialiser """
        return self.messenger.unpack(msg)

if __name__ == "__main__":
    pass
