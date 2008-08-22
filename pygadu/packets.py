# -*- coding: utf-8 -*-
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Boston, MA 02111.
#
import struct
import binascii
import const


def parse_header(data):
    """
    Odczytuje nagłówek pakietu data i zwraca krotkę (type, length).
    """
    return struct.unpack("<ii", data)


def has_description(status):
    """
    Zwraca True jeśli status zawiera opis, False w przeciwnym przypadku.
    """
    return status in (const.STATUS_NOT_AVAIL_DESC, const.STATUS_AVAIL_DESC, 
                      const.STATUS_BUSY_DESC, const.STATUS_INVISIBLE_DESC)


class GGPacketMeta(type):
    """
    Metaklasa dla wszystkich pakietów Gadu-Gadu. Odpowiada za automatyczną
    rejestrację pakietów według typu.
    """
    packets = {}
    
    def __new__(mcs, name, bases, classdict):
        class_ = super(GGPacketMeta, mcs).__new__(mcs, name, bases, classdict)
        if "type" in classdict:
            mcs.packets[classdict["type"]] = class_
        return class_


class GGPacket(object):
    """
    Nadklasa wszystkich pakietów Gadu-Gadu.
    """
    __metaclass__ = GGPacketMeta

    def __init__(self, data = ""):
        self.data = data     # struktura z danymi pakietu
        if self.data != "":
            self.unpack(data)
        self.length = 0      # długość pakietu

    @staticmethod
    def get_packet_by_type(packet_type, data):
        """
        Zwraca pakiet o typie packet_type, zainicjalizowany wartością data.
        Jeśli taki pakiet nie istnieje, zwraca pakiet typu Unknown.
        """
        try:
            return GGPacketMeta.packets[packet_type](data)
        except KeyError:
            return Unknown(data)
        
    def pack(self):
        pass

    def unpack(self, data):
        pass
    
    def __str__(self):
        if self.data == "":
            self.pack()
        return self.data


class Unknown(GGPacket):
    """
    Unknown
    """

    def pack(self):
        pass

    def unpack(self, data):
        pass
    
    def __repr__(self):
        return "Unknown(%s)" % binascii.hexlify(self.data)


#===============================================================================
#   Pakiety wysyłane
#===============================================================================
class GGOutPacket(GGPacket):
    u""" Abstrakcyjna klasa skupiająca pakiety wysyłane przez klienta. """
    pass
    

class Ping(GGOutPacket):
    """
    Ping
    """
    type = 0x0008

    def pack(self):
        header = struct.pack("<ii", self.type, self.length)
        self.data = header


class Login(GGOutPacket): #IGNORE:R0902
    """
    Login
    """
    type = 0x0015
    
    def __init__(self, data=""):
        super(Login, self).__init__(data)
        self.uin = 0                # numer konta
        self.hash = 0               # hash hasﾳa
        self.status = const.STATUS_AVAIL  # status po zalogowaniu
        self.version = const.CLIENT_VERSION # wersja klienta
        self.localaddr = 0          # lokalny adres IP (jako liczba 32-bitowa)
        self.localport = 0          # lokalny port
        self.externaladdr = 0       # zewn￪trzny adres IP
        self.externalport = 0       # zewn￪trzny port
        self.maximgsize = 0         # maksymalny rozmiar pobieranych obrazk￳w
        self.description = ""       # opis (nie musi wystﾹpi￦)
        self.time = 0               # czas (nie musi wystﾹpi￦)

    def pack(self):
        data = struct.pack("<4Icihih2c", 
                           self.uin, self.hash, self.status, self.version,
                           chr(0x00), self.localaddr, self.localport, 
                           self.externaladdr, self.externalport, 
                           chr(self.maximgsize), chr(0xbe))
        length = struct.calcsize("<4icihih2c")
        if self.description:
            # status opisowy
            desc_length = len(self.description) + 1
            data += struct.pack("<%is" % desc_length, self.description)
            length += desc_length
        if self.time:
            # status z czasem powrotu
            data += struct.pack("<i", self.time)
            length += 4
        header = struct.pack("<ii", self.type, length)
        self.length = length
        self.data = header + data


class FriendList(GGOutPacket):
    """
    FriendList
    """
    type = 0x0010
    
    def __init__(self, data=""):
        super(FriendList, self).__init__(data)
        self.friends  = [] # lista krotek (numer konta, typ użytkownika)

    def pack(self):
        data = ""
        length = 0
        for uin, user_type in self.friends:
            data += struct.pack("<ic", int(uin), chr(user_type))
            length += 5 
        header = struct.pack("<ii", self.type, length)
        self.length = length
        self.data = header + data


class ListEmpty(GGOutPacket):
    """
    ListEmpty
    """
    type = 0x0012

    def pack(self):
        self.length = 0
        header = struct.pack("<ii", self.type, self.length)
        self.data = header


class AddFriend(GGOutPacket):
    """
    AddFriend
    """
    type = 0x000d
    
    def __init__(self, data=""):
        super(AddFriend, self).__init__(data)
        self.uin = 0
        self.user_type = chr(0)
    
    def pack(self):
        data = struct.pack("<ic", int(self.uin), chr(self.user_type))
        self.length = 5
        header = struct.pack("<ii", self.type, self.length)
        self.data = header + data


class RemoveFriend(GGOutPacket):
    """
    RemoveFriend
    """
    type = 0x000e
    
    def __init__(self, data=""):
        super(RemoveFriend, self).__init__(data)
        self.uin = 0
        self.user_type = chr(0)
    
    def pack(self):
        data = struct.pack("<ic", int(self.uin), chr(self.user_type))
        self.length = 5
        header = struct.pack("<ii", self.type, self.length)
        self.data = header + data
    

class ChangeStatus(GGOutPacket):
    """
    ChangeStatus
    """
    type = 0x0002
    
    def __init__(self, data=""):
        super(ChangeStatus, self).__init__(data)
        self.status = const.STATUS_AVAIL  # status
        self.description = ""       # opis (nie musi wystﾹpi￦)
        self.time = 0               # czas (nie musi wystﾹpi￦)

    def pack(self):
        data = struct.pack("<i", self.status)
        length = 4
        if self.description:
            # status opisowy
            desc_length = len(self.description) + 1
            data += struct.pack("<%is" % desc_length, self.description)
            length += desc_length
        if self.time:
            # status z czasem powrotu
            data += struct.pack("<i", self.time)
            length += 4
        header = struct.pack("<ii", self.type, length)
        self.length = length
        self.data = header + data


class SendMessage(GGOutPacket):
    """
    SendMessage
    """
    type = 0x000b 
    
    def __init__(self, data=""):
        super(SendMessage, self).__init__(data)
        self.recipient = 0      # odbiorca wiadomoﾜci
        self.seq = 0            # numer sekwencyjny
        self.msg_class = 0      # klasa wiadomoﾜci
        self.text = ""          # treﾜ￦

    def pack(self):
        text_length = len(self.text) + 1
        data = struct.pack("<3i%is" % text_length, self.recipient, 
                           self.seq, self.msg_class, self.text)
        length = 12 + text_length
        header = struct.pack("<ii", self.type, length)
        self.length = length
        self.data = header + data


class PubdirRequest(GGOutPacket):
    """
    PubdirRequest
    """
    type = 0x0014
    
    def __init__(self, data=""):
        super(PubdirRequest, self).__init__(data)
        self.method = const.PUBDIR_SEARCH
        self.seq = 1
        self.request = ""
        
    def pack(self):
        request_length = len(self.request) + 1
        data = struct.pack("<ci%is" % request_length, chr(self.method), self.seq, self.request)
        length = 5 + request_length
        header = struct.pack("<ii", self.type, length)
        self.length = length
        self.data = header + data


#===============================================================================
#   Pakiety odbierane
#===============================================================================
class GGInPacket(GGPacket):
    u""" Abstrakcyjna klasa skupiajﾹca pakiety odbierane przez klienta. """
    pass

class Welcome(GGInPacket):
    """
    Welcome
    """
    type = 0x0001
    
    def __init__(self, data=""):
        self.seed = 0  # seed używany do hashowania hasła
        super(Welcome, self).__init__(data)

    def unpack(self, data):
        self.seed = struct.unpack("<i", data)[0]


class LoginOk(GGInPacket):
    """
    LoginOk
    """
    type = 0x0003

    def unpack(self, data):
        pass


class LoginFailed(GGInPacket):
    """
    LoginFailed
    """
    type = 0x0009

    def unpack(self, data):
        pass


class FriendListStatus(GGInPacket):
    """
    friends - lista złożona z krotek: 
    (numer konta, status, zewnętrzny adres IP, zewnętrzny port,
     wersja klienta, maksymalny rozmiar pobieranych obrazków,
     opis (nie musi wystąpić), czas (nie musi wystąpić￦)).
    """
    type = 0x0011
    
    def __init__(self, data=""):
        self.friends  = []
        super(FriendListStatus, self).__init__(data)

    def unpack(self, data):
        while data:
            description = ""
            time        = 0
            uin, status, externaladdr, externalport, version, maximgsize, _ = \
                    struct.unpack("<icih3c", data[:14])
            status = ord(status)
            data = data[14:]
            if has_description(status):
                desc_length = struct.unpack("<c", data[:1])[0]
                desc_length = ord(desc_length)
                data = data[1:]
                raw = struct.unpack("<%is" % desc_length, data[:desc_length])
                raw = raw[0].split("\0", 1)
                description = raw[0]
                try:
                    time = ord(raw[1])
                except IndexError:
                    time = 0
                data = data[desc_length:]
            self.friends.append((uin, status, externaladdr, externalport, 
                                 version, maximgsize, description, time))


class FriendStatus(GGInPacket): #IGNORE:R0902
    """
    FriendStatus
    """
    type = 0x000f
    
    def __init__(self, data=""):
        self.uin = 0
        self.status = chr(0)
        self.externaladdr = 0
        self.externalport = 0
        self.version = chr(0)
        self.maximgsize = chr(0)
        self.description = ""
        self.time = 0   
        super(FriendStatus, self).__init__(data)

    def unpack(self, data):
        self.uin, self.status, self.externaladdr, \
                self.externalport, self.version, self.maximgsize, _ = \
                        struct.unpack("<icih3c", data[:14])
        self.status = ord(self.status)
        data = data[14:]
        if has_description(self.status):
            desc_length = len(data)
            raw = struct.unpack("<%is" % desc_length, data)
            raw = raw[0].split("\0", 1)
            self.description = raw[0]
            try:
                self.time = ord(raw[1])
            except IndexError:
                self.time = 0


class FriendStatus2(GGInPacket):
    type = 0x0002
    
    def __init__(self, data=""):
        self.uin = 0
        self.status = chr(0)
        self.description = ""
        self.time = 0
        super(FriendStatus2, self).__init__(data)
    
    def unpack(self, data):
        self.uin, self.status = struct.unpack("<ii", data[:8])
        data = data[8:]
        if has_description(self.status):
            desc_length = len(data)
            raw = struct.unpack("<%is" % desc_length, data)
            raw = raw[0].split("\0", 1)
            self.description = raw[0]
            try:
                self.time = int(raw[1])
            except IndexError:
                self.time = 0


class RecvMessage(GGInPacket):
    """
    RecvMessage
    """
    type = 0x000a
    
    def __init__(self, data=""):
        self.text = ""
        self.sender = 0     # nadawca wiadomoﾜci
        self.seq = 0        # numer sekwencyjny
        self.time = 0       # czas nadania
        self.msg_class = 0  # klasa wiadomoﾜci
        super(RecvMessage, self).__init__(data)
        
    def unpack(self, data):
        length = len(data)
        self.sender, self.seq, self.time, self.msg_class = \
                            struct.unpack("<4i", data[:16])
        data = data[16:]
        text_length = length - 16
        self.text = struct.unpack("%is" % text_length, data[:text_length])[0]


class MessageAck(GGInPacket):
    """Doctype for MessageAck."""
    type = 0x0005
    
    def __init__(self, data=""):
        self.status = const.ACK_DELIVERED
        self.recipient = 0
        self.seq = 0
        super(MessageAck, self).__init__(data)
        
    def unpack(self, data):
        self.status, self.recipient, self.seq = struct.unpack("<3i", data)
        

class PubdirReply(GGInPacket):
    """Doctype for PubdirReply."""
    type = 0x000e
    
    def __init__(self, data=""):
        self.method = const.PUBDIR_SEARCH
        self.seq = 1
        self.reply = ""
        super(PubdirReply, self).__init__(data)
        
    def unpack(self, data):
        self.method, self.seq = struct.unpack("<ci", data[:5])
        data = data[5:]
        self.reply = struct.unpack("<%is" % len(data), data)[0]
    
    