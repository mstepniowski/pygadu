from pygadu.session import PyGadu
from pygadu.util import query_hub


class Echo(PyGadu):
    def __init__(self):
        super(Echo, self).__init__()
    
    def onWelcome(self, packet):
        print "Welcome!"
    
    def onLoginOk(self, packet):
        print "Login Ok!"
    
    def onLoginError(self, packet):
        print "Error!"
    
    def onRecvMessage(self, packet):
        self.sendMessage(packet.sender, packet.text)


if __name__ == '__main__':
    Echo().login(123456, '********', host=query_hub(5354504))


