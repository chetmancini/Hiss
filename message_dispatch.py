### Imports ##################################################################
# Python Library Imports
import time

# External Library Imports
from zope.interface import Interface, implements

# Local Imports
import config
from debug import debug

### Interfaces ###############################################################
class IMessageDispatcher(Interface):
    """
    Message dispatcher interface
    """

    def dispatch(message):
        """
        Dispatch a message
        """

### Classes ##################################################################
class MessageDispatcher:
    """
    Concrete message dispatcher
    """
    implements(IMessageDispatcher)

    def __init__(self):
        """
        Constructor
        """
        pass

    def _hasConnectionTo(self, remote):
        """
        Internal method if this has a connection to a remote server.
        """
        return False

    def dispatch(self, message):
        """
        Not sureo how to make this work...the idea was going to be having
        a basci point to point communication.
        """
        if self._hasConnectionTo(message.getRecipients()):
            self.send(message.getSender(), 
                      message.getRecipient(), 
                      message.getPayload())
        else:
            raise "Connection not valid"
