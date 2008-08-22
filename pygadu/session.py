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
import threading, time
import asyncore, asynchat
from socket import AF_INET, SOCK_STREAM
from pygadu.util import login_hash
from pygadu.packets import GGPacket, parse_header, ChangeStatus, \
            SendMessage, FriendList, PubdirRequest, Ping, Login
from pygadu.const import PUBDIR_SEARCH, STATUS_AVAIL


class PyGadu(object): #IGNORE:R0904
    """
    Klient Gadu-Gadu.
    """
    
    def __init__(self):
        self.host = ""          # adres serwera Gadu-Gadu
        self.port = 0           # port, na którym słucha serwer
        self.uin = 0            # numer użytkownika
        self.passwd = ""        # hasło użytkownika
        self._sock = None       # gniazdo, na którym ustanawiamy połączenia
        self._connected = False # czy połączony

    def login(self, uin, passwd, host = "", port = 8074):    
        """
        Loguje się do serwera Gadu-Gadu o podanym adresie i porcie.
        """
        self.host   = host
        self.port   = port
        self.uin    = uin
        self.passwd = passwd
        self._connect(self.host, self.port)
    
    def logout(self):        
        """
        Zrywa połączenie z serwerem Gadu-Gadu, zmieniając status na niedostępny i zamykając gniazdo.
        """
        self._close()        
    
    def changeStatus(self, status, description="", time_away=0):
        """
        Zmienia status na podany.
        """
        packet = ChangeStatus()
        packet.status = status
        packet.description = description
        packet.time = time_away
        self.sendPacket(packet)
    
    def sendMessage(self, recipient, text):
        """
        Wysyła wiadomość do innego użytkownika.
        """
        packet = SendMessage()
        packet.recipient = recipient
        packet.seq = 0
        packet.msg_class = 0
        packet.text = text
        self.sendPacket(packet)
    
    def sendFriendList(self, friends):
        """
        Wysyła listę użytkowników do serwera w celu sprawdzenia ich statusu.
        """
        packet = FriendList()
        packet.friends = friends
        self.sendPacket(packet)
        
    def sendPacket(self, packet):    
        """
        Wysyła pakiet packet do gniazda.
        """
        self._sock.push(str(packet))    
    
    def search_pubdir(self, search_terms=""):
        packet = PubdirRequest()
        packet.method = PUBDIR_SEARCH
        packet.seq = 1
        packet.request = search_terms
        self.sendPacket(packet)
        
    def ping(self):    
        """
        Pinguje serwer Gadu-Gadu.
        """
        packet = Ping()
        self.sendPacket(packet)
        
    def isConnected(self):
        """
        Zwraca wartość True jeśli jesteśmy połączeni z serwerem Gadu-Gadu.
        """
        return self._connected
    
    def _connect(self, host, port):    
        """
        Ustanawia połączenie z serwerem Gadu-Gadu o podanym adresie i porcie.
        """    
        if self._connected:
            self._close()
            time.sleep(0.000001) # XXX: Poczekaj na zamknięcie gniazda
        
        self._sock = GGSocket(self, host, port)    
        threading.Thread(name = "PyGadu", target = asyncore.loop).start()
            
    def _close(self):        
        """
        Zrywa poﾳﾹczenie z serwerem Gadu-Gadu, zamykajﾹc gniazdo.
        """         
        self._sock.close()
        # Ręcznie usuwamy obiekt gniazda, aby uniknąć wycieków pamięci.
        del(self._sock)
    
    def m_on_connect(self):
        self._connected = True
        self.onConnect()
        
    def m_on_close(self):
        self._connected = False
        self.onClose()
    
    def _onWelcome(self, packet):
        """
        Odbiera pakiet z seed'em i odsyła pakiet logowania.
        """
        seed = packet.seed
        login_packet = Login()
        login_packet.uin = self.uin
        login_packet.hash = login_hash(self.passwd, seed)
        login_packet.status = STATUS_AVAIL
        self.sendPacket(login_packet)
        
        # Po wszystkim wywołujemy funkcję zdefiniowaną przez użytkownika.
        self.onWelcome(packet)

    def _onFriendStatus2(self, packet):
        """
        Jakiś docstring.
        """
        self.onFriendStatus(packet)
        
    #===========================================================================
    #    Handlery.
    # Wywoływane automagicznie, kiedy zajdzie powiązane z nimi zdarzenie.
    #===========================================================================
    
    def onConnect(self):    
        """
        Wywoływana po połączeniu z serwerem.
        """
        pass
        
    def onClose(self):    
        """
        Wywoływana po rołączeniu z serwerem.
        """
        pass
    
    def onWelcome(self, packet):
        """
        Wywoływana po otrzymaniu pierwszego pakietu od serwera.
        """        
        pass
        
    def onLoginOk(self, packet):
        """
        Wywoływana kiedy logowanie powiodﾳo się.
        """
        pass

    def onLoginFailed(self, packet):
        """
        Wywoływana kiedy logowanie nie powiodﾳo się.
        """
        pass
        
    def onFriendStatus(self, packet):
        """
        Wywoływana po otrzymaniu statusu użytkownika.
        """
        pass
        
    def onFriendListStatus(self, packet):
        """
        Wywoﾳywana po otrzymaniu statusu wielu u﾿ytkownik￳w.
        """
        pass

    def onRecvMessage(self, packet):
        """
        Wywoﾳywana po otrzymaniu nowej wiadomoﾜci.
        """
        pass

    def onPubdirReply(self, packet):
        pass
    
    def onMessageAck(self, packet):
        pass
    
    def onUnknown(self, packet):
        """
        Wywoﾳywana po otrzymaniu nieznanego pakietu.
        """
        pass


class GGSocket(asynchat.async_chat): #IGNORE:R0904
    """
    Gniazdo Gadu-Gadu.
    """
    
    def __init__(self, handler, host, port):
        asynchat.async_chat.__init__(self)
        
        self._handler = handler   # obiekt obsługujący zdarzenia
        self.type = 0             # typ odbieranego pakietu
        self.length = 0           # długość odbieranego pakietu
        self.data = ""            # pobrane dane
        self._header = True       # czy został odebrany nagłówek pakietu
        self.set_terminator(8)
        
        self.create_socket(AF_INET, SOCK_STREAM)
        self.connect((host, port))
        
    def collect_incoming_data(self, data):
        """
        Jakiś docstring.
        """
        self.data = self.data + data
    
    def found_terminator(self):
        """
        Jakiś docstring.
        """
        if self._header:
            # Analiza nagłówka pekietu.
            self.type, self.length = parse_header(self.data)
            self.data = self.data[8:]            
            if self.length > 0:
                # Trzeba pobrać treść pakietu.
                self.set_terminator(self.length)
                self._header = False
            else:
                # Otrzymaliśmy pusty pakiet.
                self.handle_packet()        
        else:
            # Analiza zawartości pakietu
            self.handle_packet()
        
    def handle_packet(self):
        """
        Obsługa pakietu. Funkcja wywoływana po odebraniu całego pakietu.
        """    
        # Sprawdź typ pakietu i wywołaj odpowiednie zdarzenie
        packet = GGPacket.get_packet_by_type(self.type, self.data)
        packet.type = self.type
        try:
            getattr(self._handler, "_on"+packet.__class__.__name__)(packet)
        except AttributeError:
            getattr(self._handler, "on"+packet.__class__.__name__)(packet)
        except AttributeError:
            self._handler.onUnknown(packet)
            
        # Przygotuj się do odebrania kolejnego pakietu
        self.data = self.data[self.length:]
        self._header = True
        self.set_terminator(8)
                
    def handle_connect(self):
        """
        Funkcja wywoływana po połączeniu.
        """
        self._handler.m_on_connect()
                            
    def handle_close(self):
        """
        Funkcja wywoływana po zamknięciu gniazda.
        """
        self._handler.m_on_close()
        asynchat.async_chat.handle_close(self)

