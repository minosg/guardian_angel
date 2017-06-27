#!/usr/bin/env python

"""ulinkmessenger.py: Exteranl Node message helper """

from __future__ import print_function
import projectpath
import time
import crcmod
from node_messages_pb2 import ULinkMessage, MetaData, Control, Location
from collections import namedtuple
from nodemessenger import NodeMessenger

__author__ = "Minos Galanakis"
__license__ = "LGPL"
__version__ = "0.0.1"
__email__ = "minos197@gmail.com"
__project__ = "ga"
__date__ = "16-06-2017"


class ULinkMessengerError(Exception):
    __module__ = 'exceptions'


class ULinkMessengerTypes(type):
    """ Metaclass that maps the messages types to human readable format """

    def __init__(cls, name, bases, dict):
        TYPE = {"ACK": 1,    # Aknowledgement
                "NACK": 2,   # Negative Aknowledgement
                "REG": 3,    # Gegistration
                "UPD": 4,    # Update
                "RST": 8,    # Reset
                "REB": 9,    # Reboot
                "PRE": 10,   # Preample
                "MAN": 11,   # Main
                "FULL": 12,  # Full message (with metadata)
                "CON": 13,   # Controll
                "LOC": 14,   # Location message
                "RET": 15,   # Retransmission
                "HBT": 16}   # Heartbeat

        for t, v in TYPE.iteritems():
            setattr(cls, t, v)
        super(ULinkMessengerTypes, cls).__init__(name, bases, dict)


class ULinkMessenger(object):

    __metaclass__ = ULinkMessengerTypes

    _location_tpl = namedtuple("Location", ("lat long street building floor "
                                            "room city country postcode"))

    def __init__(self, name="Node"):
        self._seq = 1
        self._device_id = -0
        self._network_id = 0
        self._app_id = 0
        self._periph_count = 0
        self._name = name
        self._crc = crcmod.predefined.mkPredefinedCrcFun("crc-16-genibus")

    def set_metadata(self,
                     dev_id=None,
                     net_id=None,
                     app_id=None,
                     periph_count=None,
                     name=None):

        if dev_id:
            self._device_id = dev_id
        if net_id:
            self.net_id
        if app_id:
            self.app_id
        if name:
            self._name = name
        if periph_count:
            self._periph_count = 0

    def set_location(self,
                     lat,
                     long,
                     street=None,
                     building=None,
                     floor=None,
                     room=None,
                     city=None,
                     country=None,
                     postcode=None):

        self._location = self._location_tpl(lat=lat,
                                            long=long,
                                            street=street,
                                            building=building,
                                            floor=floor,
                                            room=room,
                                            city=city,
                                            country=country,
                                            postcode=postcode)

    def _new_msg(self, msg_type=None, seq=None):
        """ Generate the basic common base for a message """
        nm = ULinkMessage()
        if msg_type:
            self._add_metadata(nm, msg_type, seq)
        return nm

    def _add_metadata(self, ulmsg, msg_type, seq=None):
        mt = ulmsg.metadata
        mt.message_type = msg_type
        mt.device_id = self._device_id
        mt.time = int(time.time())
        mt.sequence = self._seq if seq is None else seq

        # Optional fields
        if self._network_id:
            mt.network_id = self._network_id
        if self._app_id:
            mt.app_id = self._app_id
        if self._periph_count:
            mt.periph_count = self._periph_count
        if self._name:
            mt.device_name = self._name

        # If the sequence is user provided do not increment the counter
        if seq is None:
            self._seq += 1

    def _add_location(self, ulmsg):

        lc = ulmsg.location
        if self._location.lat:
            lc.lat = self._location.lat
        if self._location.long:
            lc.long = self._location.long
        if self._location.street:
            lc.street = self._location.street
        if self._location.building:
            lc.building = self._location.building
        if self._location.floor:
            lc.floor = self._location.floor
        if self._location.room:
            lc.room = self._location.room
        if self._location.city:
            lc.city = self._location.city
        if self._location.country:
            lc.country = self._location.country
        if self._location.postcode:
            lc.postcode = self._location.postcode

    def _add_peripheral(self, ulmsg, per):
        periph = ulmsg.peripheral.add()

        periph.device_name = per.device_name
        periph.device_id = per.device_id
        periph.time = per.time

        for service in per.payload:
            periph_service = periph.payload.add()
            if service.name:
                periph_service.name = service.name
            if service.msg:
                periph_service.msg = service.msg
            if service.payload:
                periph_service.payload = service.payload
                periph_service.crc = service.crc

    def _add_control(self,
                     ulmsg,
                     key=None,
                     cmd=None,
                     params=None,
                     cmd_index=None,
                     cmd_index_params=None):

        ctrl_msg = ulmsg.control
        if cmd:
            ctrl_msg.is_indexed = False
            ctrl_msg.cmd = cmd
            for p in params:
                ctrl_msg.params.append(p)

        elif cmd_index:
            ctrl_msg.is_indexed = True
            ctrl_msg.cmd_index = cmd_index
            for p in cmd_index_params:
                ctrl_msg.cmd_par.append(p)

    #
    # User exposed messages
    #

    def ack_msg(self, seq=None, **control):
        """ General aknowledgement message """

        msg = self._new_msg(self.ACK, seq)

        # Control messages can be attached if passed as keyword arguments
        if control:
            self._add_control(msg, **control)
        return msg

    def nack_msg(self, seq=None, **control):
        """ General negative aknowledgement message """

        msg = self._new_msg(self.NACK, seq)

        # Control messages can be attached if passed as keyword arguments
        if control:
            self._add_control(msg, **control)
        return msg

    def register_msg(self, seq=None):
        """ General registration message """

        rm = self._new_msg(seq)

        # registration message should be only sent once and can use
        # the extra overhead of non volatile information such as location
        # and metadata
        self._add_metadata(rm, self.REG, seq)
        self._add_location(rm)
        return rm

    def upgrade_msg(self, seq=None):
        """ Message that initiates a firmware upgrade """
        pass

    def reset_msg(self, seq=None):
        """ Message that clears configuration """
        return self._new_msg(self.RST, seq)

    def restart_msg(self, seq=None):
        """ Reboot device message """
        return self._new_msg(self.REB, seq)

    def preamble_msg(self, periph_list, seq=None):
        """ First stage of event driven uplink """

        pr_msg = self._new_msg(self.PRE, seq)
        for periph in periph_list:
            self._add_peripheral(pr_msg, periph)
        return pr_msg

    def main_msg(self, periph_list, seq=None):
        """ Complete message of event driven uplnk """
        mn_msg = self._new_msg(self.PRE, seq)

        # Popuplate the list of the peripherals
        for periph in periph_list:
            self._add_peripheral(mn_msg, periph)
        return mn_msg

    def full_msg(self, periph_list, seq=None):
        """ Message that includes all details from node with the uplink """
        fl_msg = self._new_msg(self.FULL, seq)

        # Popuplate the list of the peripherals
        for periph in periph_list:
            self._add_peripheral(fl_msg, periph)

        # Include metadata and location to message
        self._add_location(fl_msg)
        self._add_metadata(fl_msg, self.FULL)
        return fl_msg

    def heartbeat_msg(self, seq=None):
        """ Mesage to test connection status """

        return self._new_msg(self.HBT, seq)

    def Retrans_msg(self, periph_list, seq=None):
        """ Repeated message that server requested """
        rt_msg = self._new_msg(self.RET, seq)

        # Popuplate the list of the peripherals
        for periph in periph_list:
            self._add_peripheral(rt_msg, periph)
        return rt_msg

    def pack(self, msg):
        return msg.SerializeToString()

    def unpack(self, data):
        nm = ULinkMessage()
        nm.ParseFromString(data)
        if not nm.ByteSize():
            raise ULinkMessengerError("Could not unpack message")
        return nm

if __name__ == "__main__":

        # create the uplink message hanlder
        ul = ULinkMessenger()

        # Set the unique identifiers
        ul.set_metadata(name="moufa")
        ul.set_location(12.213, 34.2132,
                        "Moufa Street",
                        "Tall Building",
                        "Floor 99",
                        "Room 14",
                        "Rapture",
                        "Atlantis",
                        "RPT ATL")

        # create a node message handler anda  fake peripheral
        nm = NodeMessenger()
        # Change the periheral id
        nm.set_id(123)
        nm.set_name("Fake Peripheral")
        pl = nm.new_service("Test Service")
        periph = nm.solicited_msg(pl)

        pad_size = 50
        padx = lambda x: (50 - len(x)) / 2
        header = lambda x: "%(pad)s %(msg)s %(pad)s" % {"pad": "*" * padx(x),
                                                        "msg": x}

        print(header("Testing ACK"))
        print(ul.ack_msg())

        print(header("Testing ACK with payload"))
        print(ul.ack_msg(cmd="register", params=["-full", "-extra"]))

        print(header("Testing Register Message"))
        print(ul.register_msg())

        print(header("Testing PreAmble Message"))
        print(ul.preamble_msg([periph]))

        print(header("Testing Main Message"))
        print(ul.main_msg([periph]))

        print(header("Testing Full Message"))
        print(ul.full_msg([periph]))
