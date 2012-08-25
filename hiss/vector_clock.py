##############################################################################
#        __  ___                                                             #
#       / / / (_)_________                                                   #
#      / /_/ / / ___/ ___/                                                   #
#     / __  / (__  |__  )                                                    #
#    /_/ /_/_/____/____/        Gossip with Python on Twisted                #
#                                                                            #
##############################################################################

#----------------------------------------------------------------------------#
# vectorClock.py                                                             #
# Implements vector clocks using Lamport's logical clocks                    #
#----------------------------------------------------------------------------#

### Imports ##################################################################
# External Library Imports
import zope.interface

# Local Imports
import config
import connections
import message
from debug import debug

### Interfaces ###############################################################
class IVectorClock(zope.interface.Interface):
    """
    Vector Clock Interface
    """

    def incrementClock():
        """
        Increment this clock
        """

    def handleEvent(message):
        """
        Handle internal system event
        """

    def createMessage():
        """
        Create a message from this clock
        """

    def mergeClock(otherclock):
        """
        Merge this clock with another
        """

    def receiveMessage(vectorMessage):
        """
        Receive a message and merge
        """

    def cameBefore(otherclock):
        """
        Whether this came before another clock
        """

    def cameAfter(otherclock):
        """
        Whether this came after another clock
        """

    def certainOrder(otherclock):
        """
        Whether we cannot be sure about the order.
        """

    def getClocks():
        """
        Get internal clock
        """

    def getKey():
        """
        Get the key this one uses for its clock
        """

### Classes ##################################################################
class VectorClock(object):
    """
    Basic Vector Clock algorithm implementation for single-threaded web apps.
    """

    zope.interface.implements(IVectorClock)

    def __init__(self, key=None, initialClocks=None, externKeys=None):
        """
        Constructor
        """
        if initialClocks:
            self._clocks = initialClocks
        else:
            self._clocks = {}
            if externKeys:
                for externKey in externKeys:
                    self._clocks[externKey] = 0
        if key:
            self._key = key
        else:
            self._key = connections.getMe().getUid()

        if self._key not in self._clocks:
            self._clocks[self._key] = 0

    def incrementClock(self):
        """
        Increment this node's logical clock.
        """
        self._clocks[self._key] += 1

    def handleEvent(self, message):
        """
        handle an event. Increment this logical clock and return the value.
        """
        self.incrementClock()
        return self._clocks[self._key]

    def createMessage(self):
        """
        Send a message from this machine. returns the message to send.
        """
        self.incrementClock()
        return message.VectorMessage(self._clocks)

    def mergeClock(self, otherclock):
        """
        Merge another clock into this one.
        """
        if isinstance(otherclock, VectorClock):
            otherclock = otherclock.getClocks()
        for key in otherclock:
            if key in self._clocks:
                self._clocks[key] = max(otherclock[key], self._clocks[key])
            else:
                self._clocks[key] = otherclock[key] 
        debug("Merged Vector Clocks", success=True)


    def receiveMessage(self, vectorMessage):
        """
        Receive a message and update this clock.
        """
        self.incrementClock()
        self.mergeClock(vectorMessage.getPayload())

    def cameBefore(self, otherclock):
        """
        Return if this clock logically came before another.
        """
        if isinstance(otherclock, VectorClock):
            otherclock = otherclock.getClocks()
        oneStrictlySmall = False
        for key in otherclock:
            if self._clocks[key] > otherclock[key]:
                return False
            elif self._clocks[key] < otherclock[key]:
                oneStrictlySmall = True
        return oneStrictlySmall

    def cameAfter(self, otherclock):
        """
        Return if this clock logically came after another.
        """
        if isinstance(otherclock, VectorClock):
            otherclock = otherclock.getClocks()
        oneStrictlyLarger = False
        for key in otherclock:
            if self._clocks[key] < otherclock[key]:
                return False
            elif self._clocks[key] > otherclock[key]:
                oneStrictlyLarger = True
        return oneStrictlyLarger

    def certainOrder(self, otherclock):
        return self.cameBefore(otherclock) or self.cameAfter(otherclock)

    def getClocks(self):
        """
        Get the dictionary of clocks. (vector clock)
        """
        return self._clocks

    def getKey(self):
        """
        get the key of this vector clock. I assumed it would be the key of the
        current system, but that might not be the case for merges.
        """
        return self._key