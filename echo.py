import time

from pygadu.session import PyGadu
from pygadu.util import query_hub
from pygadu.const import STATUS_BUSY


class Echo(PyGadu):
    def __init__(self):
        super(Echo, self).__init__()
    
    def onWelcome(self, packet):
        print repr(packet)
        print "Welcome!"
    
    def onLoginOk(self, packet):
        print repr(packet)
        print "Login Ok!"
        # self.sendMessage(5354504, "Halo!")
        # print "message sent"
        print "send status"
        self.changeStatus(STATUS_BUSY)
    
    def onConnect(self):
        print "Connect"
    
    def onClose(self):
        print "Close"
    
    def onSendMessage(self, packet):
        print repr(packet)
        print "on send message?"
    
    def onLoginError(self, packet):
        print repr(packet)
        print "Error!"
    
    def onRecvMessage(self, packet):
        print repr(packet)
        print packet.sender, packet.text
        self.sendMessage(packet.sender, packet.text)
        
    def onUnknown(self, packet):
        print repr(packet)


if __name__ == '__main__':
    try:
        host = query_hub(10533767)
        print host
        gg = Echo()
        gg.login(10533767, "123456", host=host)
        while True:
            time.sleep(300)
            gg.ping()
        
    except KeyboardInterrupt:
        gg.logout()

