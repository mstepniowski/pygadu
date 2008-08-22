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
__revision__ = "$Revision: 8 $"


import httplib


HUB_URL = "appmsg.gadu-gadu.pl"
BROWSER = "Mozilla/4.0 (compatible; MSIE 5.0; Windows NT)"
PATH = "/appsvc/appmsg4.asp?fmnumber=%s&version=%s&lastmsg=%s"
HEADERS = {"Host": HUB_URL,
           "User-Agent": BROWSER,
           "Pragma": "no-cache",
           "Accept-Language": "pl"}


def login_hash(password, seed):
    """
    Zwraca hash hasła wysyłany do serwera Gadu-Gadu podczas logowania.
    """
    INTEGER_MASK = 0xFFFFFFFF

    x = z = 0L
    y = long(seed)
    
    for char in password.encode("cp1250", "replace"):
        x = (x & INTEGER_MASK) | ord(char)
        y = (y ^ x)  & INTEGER_MASK
        y = (y + x)  & INTEGER_MASK
        x = (x << 8) & INTEGER_MASK
        y = (y ^ x)  & INTEGER_MASK
        x = (x << 8) & INTEGER_MASK
        y = (y - x)  & INTEGER_MASK
        x = (x << 8) & INTEGER_MASK
        y = (y ^ x)  & INTEGER_MASK
        z = y & 0x1f & INTEGER_MASK
        y = ((y << z) | (y >> (32 -z))) & INTEGER_MASK
    
    return int(y)


def query_hub(number):
    """
    Wypytuje HUB Gadu-Gadu o adres działającego serwera.
    """
    path = PATH % (number, "6, 0, 0, 0", 0)
    connection = httplib.HTTPConnection(HUB_URL)
    connection.request("GET", path, headers=HEADERS)
    data = connection.getresponse().read()
#    print data
    server = data.split()[3]
    return server


if __name__ == '__main__':
    print query_hub(5354504)
    

