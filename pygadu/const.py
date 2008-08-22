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
#---------------------------------------------------------------------#
#   WERSJA KLIENTA GADU-GADU                                          #
#---------------------------------------------------------------------#
CLIENT_VERSION         = 0x20    # wersja 6.0

#---------------------------------------------------------------------#
#   RODZAJE STATUSÓW                                                  #
#---------------------------------------------------------------------#
STATUS_NOT_AVAIL       = 0x0001  # Niedostępny
STATUS_NOT_AVAIL_DESC  = 0x0015  # Niedostępny (z opisem)
STATUS_AVAIL           = 0x0002  # Dostępny
STATUS_AVAIL_DESC      = 0x0004  # Dostępny (z opisem)
STATUS_BUSY            = 0x0003  # Zajęty
STATUS_BUSY_DESC       = 0x0005  # Zajęty (z opisem)
STATUS_INVISIBLE       = 0x0014  # Niewidoczny
STATUS_INVISIBLE_DESC  = 0x0016  # Niewidoczny z opisem
STATUS_BLOCKED         = 0x0006  # Zablokowany
STATUS_FRIENDS_MASK    = 0x8000  # Maska bitowa oznaczająca tryb tylko dla przyjaciół

#---------------------------------------------------------------------#
#   KLASY WIADOMOŚCI                                                  #
#---------------------------------------------------------------------#
CLASS_QUEUED = 0x0001  # Bit ustawiany wyłącznie przy odbiorze wiadomości, gdy wiadomość została wcześniej zakolejkowania z powodu nieobecności
CLASS_MSG    = 0x0004  # Wiadomość ma się pojawić w osobnym okienku
CLASS_CHAT   = 0x0008  # Wiadomość jest częścią toczącej się rozmowy i zostanie wyświetlona w istniejącym okienku
CLASS_CTCP   = 0x0010  # Wiadomość jest przeznaczona dla klienta Gadu-Gadu i nie powinna być wyświetlona użytkownikowi
CLASS_ACK    = 0x0020  # Klient nie życzy sobie potwierdzenia wiadomości

#---------------------------------------------------------------------#
#   RODZAJE UŻYTKOWNIKÓW                                              #
#---------------------------------------------------------------------#
USER_OFFLINE = 0x01    # Użytkownik, dla którego będziemy niedostępni, ale mamy go w liście kontaktów
USER_NORMAL  = 0x03    # Zwykły użytkownik dodany do listy kontaktów
USER_BLOCKED = 0x04    # Użytkownik, którego wiadomości nie chcemy otrzymywać

#---------------------------------------------------------------------#
#   FLAGI W NUMERZE UŻYTKOWNIKA                                       #
#---------------------------------------------------------------------#
UINFLAG_UNKNOWN1 = 0x10000000  # Nieznane
UINFLAG_UNKNOWN2 = 0x20000000  # Flaga spotykana, gdy użytkownik staje się niedostępny
UINFLAG_VOICE    = 0x40000000  # Użytkownik może prowadzić rozmowy głosowe


#===============================================================================
#   Metody katalogu użytkownika
#===============================================================================
PUBDIR_WRITE = 0x01
PUBDIR_READ = 0x02
PUBDIR_SEARCH = 0x03
PUBDIR_SEARCH_REPLY = 0x05

#===============================================================================
#   MessageAck
#===============================================================================
ACK_BLOCKED = 0x0001
ACK_DELIVERED = 0x0002
ACK_QUEUED = 0x0003
ACK_MBOX_FULL = 0x0004
ACK_NOT_DELIVERED = 0x0006

