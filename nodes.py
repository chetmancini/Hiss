##############################################################################
#        __  ___                                                             #
#       / / / (_)_________                                                   #
#      / /_/ / / ___/ ___/                                                   #
#     / __  / (__  |__  )                                                    #
#    /_/ /_/_/____/____/        Gossip with Python on Twisted                #
#                                                                            #
##############################################################################

### Imports ##################################################################
# Library imports
import random
import uuid
import socket
import cPickle
import sys
import traceback

# External Library imports
import zope.interface
import twisted.internet.tcp
import twisted.internet.reactor

# Local Imports
import config
import connections
import me
import vectorClock
from debug import debug
from timber_exceptions import GeneralError

### Classes ##################################################################
class INode(zope.interface.Interface):

    def getIp():
        """
        Get this nodes IP address
        """

    def getPort():
        """
        Get this node's port
        """

    def getUid():
        """
        Get this node's UID as a hexadecimal string
        """

    def getShortUid():
        """
        Get a short version of this uid.
        """

    def getUidAsObject():
        """
        Get this node's uid as a python UID object.
        """

    def getSerialized():
        """
        Get this node in a serialized form
        """

    def getCompressed():
        """
        Get comrpessed version of this node.
        """

    def __eq__(other):
        """
        Equivalence
        """

    def __str__():
        """
        Get this as a string
        """


class BaseNode(object):
    """
    Base class for all other nodes. Minimal to implement interface.
    """

    zope.interface.implements(INode)

    def __init__(self, ip, port=None, uid=None):
        """
        Constructor
        """
        self._ip = ip

        if port:
            self._port = port
        else:
            self._port = config.RECEIVE_PORT

        if uid:
            if type(uid) is uuid.UUID:
                self._uid = uid
            else:
                debug("Can't construct with a uid string!", error=True)
                debug(uid, error=True)
                raise GeneralError("Can't construct with a uid string.")
        else:
            self._uid = uuid.uuid1()

    def getIp(self):
        """
        Get the ip for this connection.
        """
        return self._ip

    def getPort(self):
        """
        get the port for this connection
        """
        return self._port

    def getUidAsObject(self):
        """
        get the unique identifier
        """
        return self._uid

    def getUid(self):
        """
        Return the uid as a hex string.
        """
        return self._uid.hex

    def getShortUid(self):
        """
        Get a short version of this uid
        """
        return chr((self.getUid().__hash__() % 26) + 65) + \
            chr((self.getUid().__hash__() % 9) + 48)

    def getSerialized(self):
        """
        Get a serialized version of this node. Uses Pickle (cPickle)
        """
        return cPickle.dumps(self)

    def getBaseData(self):
        """
        Just get the basenode type data (compressed form)
        """
        toReturn = BaseNode(self._ip)
        toReturn._uid = self._uid
        toReturn._port = self._port
        toReturn._ip = self._ip    
        return toReturn

    def getCompressed(self):
        """
        get a compressed and serialized verion.
        """
        return self.getBaseData().getSerialized()

    def __eq__(self, other):
        """
        Equivalence checking
        """
        return (self.getUid() == other.getUid())

    def __str__(self):
        """
        Get a string representation of this node. Used mostly for debug.
        """
        toReturn = self.getIp() + ":" + str(self.getPort())

class ExternalNode(BaseNode):
    """
    A node of an external node.
    """

    def __init__(self, ip, port, uid=None):
        """
        Constructor
        """
        super(ExternalNode, self).__init__(ip, port, uid)
        self._tcpConnection = None
        self._knownAlive = True

    def openTCPConnection(self, bindAddress=None):
        """
        Open a new TCP connection from the local node to this node.
        """
        debug("Trying to a new connection to [ " + self.getShortUid() + " ]",
            info=True)
        connector = connections.openConnection(self.getIp(), self.getPort())
        
        if not bindAddress:
            bindAddress = (me.getMe().getIp(), config.getNextSendPort())
            #bindAddress = twisted.internet.address.IPv4Address(
            #    'TCP', me.getMe().getIp(), config.SEND_PORT)
            #config.getNextSendPort()
        """
        c = connections.HissTCPClientConnection.fromPrimitives(
            self,
            self.getIp(), 
            self.getPort(), 
            bindAddress,
            connector)
        """
        '''
        c = connections.HissTCPClientConnection.fromPrimitives(
            self,
            self.getIp(), 
            self.getPort(), 
            None,
            connector)
        self._tcpConnection = c
        '''
        c = connections.HissConnection.fromPrimitives(
            self,
            self.getIp(), 
            self.getPort(), 
            None,
            connector)
        self._tcpConnection = c

    def setTCPConnection(self, tcpConn):
        """
        Assign a TCP connection to this node.
        """
        debug("Setting up connection to [ " + self.getShortUid() + " ]", 
            info=True)
        #self._tcpConnection = connections.HissTCPClientConnection(
        #    self, tcpConn)
        self._tcpConnection = connections.HissConnection(
            self, tcpConn)

    def getTCPConnection(self):
        """
        return the TCP Connection (twisted Client) to this node.
        """
        if not self.hasTCPConnection():
            self.openTCPConnection()
        return self._tcpConnection

    def hasTCPConnection(self):
        """
        Return if a TCP Connection to this node exists.
        """
        return (self._tcpConnection is not None)

    def destroyTCPConnection(self):
        """
        Destroy the TCP connection 
        """
        try:
            debug("Destroying connection to [ " + self.getShortUid() + " ]", 
                info=True)
            if self.hasTCPConnection():
                self.getTCPConnection().loseConnection()
            self._tcpConnection = None
        except:
            debug("error destroying tcp connection", error=True)

    @staticmethod
    def fromBase(basenode):
        """
        Factory method.
        """
        return ExternalNode(basenode._ip, basenode._port, basenode._uid)



class CurrentNode(BaseNode):
    """
    Wrapper class to represent current node.
    """

    def __init__(self, ip=None, port=None):
        """
        Constructor
        """
        if ip == None:
            ip = socket.gethostbyname(socket.gethostname())
        if port == None:
            port = config.RECEIVE_PORT
        super(CurrentNode, self).__init__(ip, port, None)

        self._vectorClock = vectorClock.VectorClock(self.getUid())

    def getVectorClock(self):
        """
        get the vector clock at this position.
        """
        return self._vectorClock


class DoorNode(BaseNode):
    """
    Node that acts as entryway. Only used in entryway code.
    """

    def __init__(self, doornodeip, doornodeport, uid=None):
        """
        constructor
        """
        super(DoorNode, self).__init__(doornodeip, doornodeport, uid)
        self._nodes = {}

    def randomnodes(self, count):
        """
        Get random nodes from the set
        """
        count = min(count, self._nodes.size()) #handle bad input error case.
        return random.sample(self._nodes.keys(), count)

    def addNode(self, node):
        """
        Add a node to the connection pool
        """
        self._nodes.add(node.getId(), node)

    def nodeDead(self, nodeid):
        """
        Notify doorkeeper of a bad node.
        """
        self._nodes.remove(nodeid)

### Functions ################################################################

def buildNode(nodestr):
    """
    Build a node from serialized form
    """
    try:
        return cPickle.loads(str(nodestr))
    except Exception as e:
        debug("Could not depickle node:" + nodestr, error=True)
        debug(e)
