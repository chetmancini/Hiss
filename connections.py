### Imports ##################################################################
# Python Library Imports
import uuid
import random
import sys
import traceback
import math

# External Library Imports
import twisted.internet.tcp
import twisted.internet.interfaces
import twisted.internet.reactor
import zope.interface

# Local Imports
import config
import me
import gossip
import message
import nodes
import membership
import neighbors
from debug import debug

### Classes ##################################################################

class HissConnection(object):
    """
    Functionally extends the twisted client connection.
    Would make sense to extend, but that was difficult, so for now we'll
    use composition instead of inheritence.
    """

    zope.interface.implements(twisted.internet.interfaces.ITCPTransport)
    """
    Implements all the TCPTransport methods.
    """

    def __init__(self, parentNode, client):
        """
        Constructor
        """
        self._client = client
        self._parentNode = parentNode

    @classmethod
    def fromPrimitives(
        cls, 
        parentNode, 
        host, 
        port, 
        bindAddress, 
        connector, 
        reactor=None):
        """
        Initialize HissTCPConnection from client.
        """
        if not reactor:
            client = twisted.internet.tcp.Client(
                host, port, bindAddress, connector, twisted.internet.reactor)
        else:
            client = twisted.internet.tcp.Client(
                host, port, bindAddress, connector, reactor)
        return cls(parentNode, client)

    def loseWriteConnection():
        self._client.loseWriteConnection()
    def abortConnection():
        self._client.abortConnection()
    def getTcpNoDelay():
        return self._client.getTcpNoDelay()
    def setTcpNoDelay(enabled):
        self._client.setTcpNoDelay(enabled)
    def getTcpKeepAlive():
        return self._client.getTcpKeepAlive()
    def setTcpKeepAlive(enabled):
        return self._client.setTcpKeepAlive(enabled)
    def getHost():
        return self._client.getHost()
    def getPeer():
        return self._client.getPeer()
    def write(data):
        self._client.write(data)
    def writeSequence(data):
        self._client.writeSequence(data)
    def loseConnection():
        self._client.loseConnection


    def connectionLost(self, reason):
        """
        Callback called when this connection is lost
        """
        super.connectionLost()
        _parentNode.destroyTCPConnection()

    def dispatchMessage(self, msg):
        """
        wrapper for super.write(). Add some sanity checking and debugging.
        """
        try:
            self._client.write(msg.getSerialized())
        except:
            debug("Connection failed to write msg: " + msg.getCode(), 
                error=True)
            traceback.print_exc(file=sys.stdout)


class HissTCPClientConnection(twisted.internet.tcp.Client):
    """
    HissTCPClientConnection. An subtype of tcp client for use in Hiss.
    """

    def __init__(self, parentNode, client):
        """
        Constructor
        """
        self = client
        self._parentNode = parentNode

    @classmethod
    def fromPrimitives(cls, parentNode, host, port, bindAddress, connector):
        """
        Initialize HissTCPConnection from client.
        """
        client = twisted.internet.tcp.Client(
            host, port, bindAddress, connector, twisted.internet.reactor)

        return cls(parentNode, client)


    def connectionLost(self, reason):
        """
        Callback called when this connection is lost
        """
        super.connectionLost()
        debug("Connection lost for reason: " + str(reason), info=True)
        _parentNode.destroyTCPConnection()

    def dispatchMessage(self, msg):
        """
        wrapper for super.write(). Add some sanity checking and debugging.
        """
        try:
            self.write(msg.getSerialized())
        except:
            debug("Connection failed to write msg: " + msg.getCode(), 
                error=True)
            traceback.print_exc(file=sys.stdout)


### Variables ################################################################

universe = {}
"""
Dictionary of nodes in the system. UID -> ExternalNode. 
Those contain the TCPConnections
"""

knownDead = set([])
"""
UIDs known to be dead.
"""

neighborStrategy = None
"""
Neighbor Strategy
"""

### Functions ################################################################

def init():
    """
    Initialize the connections.
    Let's get it started...in here!
    Developer note: the advantage of putting it here is
    that me.py doesn't need to import anything.
    """
    global neighborStrategy

    me.init(nodes.CurrentNode())
    debug("Init called. Node is " + me.getUid(), info=True)
    debug("#".join(["New", me.getMe().getShortUid(), me.getUid()]), 
        monitor=True)

    neighborStrategy = neighbors.neighborStrategyFactory(
        config.GOSSIP_NEIGHBOR_STRATEGY)

def maintainMembers():
    """
    use the membersrefresh operation to maintain
    the universe of known nodes.
    """
    global universe
    
    debug("Running maintain members.", 
        info=True, threshold=1)

    possibledead = set(universe.keys())

    membership.membersRefresh()

    # Add in new nodes.
    tempUniverse = membership.getCurrentMemberDict()
    for uid in tempUniverse:
        if uid not in universe and not me.getMe().__eq__(tempUniverse[uid]):
            universe[uid] = nodes.ExternalNode.fromBase(tempUniverse[uid])
        if uid in possibledead:
            possibledead.remove(uid)

    # Remove dead nodes
    for dead in possibledead:
        deadNode(dead)

    # should I add me in here? not sure.
    universe[me.getMe().getUid()] = me.getMe()

    debug("has a universe of size: " + str(len(universe)), info=True)

def lookupNode(uid):
    """
    Find a neighbor in the neighbor dict.
    """
    return universe[uid]

def isNeighbor(uid):
    """
    Is the id a neighbor of this node?
    """
    return neighborStrategy.isNeighbor()

def removeNeighbor(uid):
    """
    Remove a node from the neighbor set
    """
    neighborStrategy.removeNeighbor(uid)

def getNeighbors():
    """
    Return the nodes to gossip with.
    This algorithm might be expanded later. Right now we just have a 
    constant group. Theoretically it would try a few and optimize to gossip 
    with the nearest nodes. Definitely an area for further design and 
    implementation.
    """
    global neighborStrategy
    if not neighborStrategy:
        neighborStrategy = neighbors.neighborStrategyFactory(
            config.GOSSIP_NEIGHBOR_STRATEGY)

    return neighborStrategy.getNeighbors()

def connectToNeighbors():
    """
    Make sure there's a client connection to all our neighbors
    """
    madeConnection = False
    for uid in getNeighbors():
        externalnode = lookupNode(uid)
        if not externalnode.hasTCPConnection():
            #debug("opening a client connection", info=True)
            externalnode.openTCPConnection()
            madeConnection = True
        else:
            pass #all good.
    return madeConnection

def openConnection(host, port):
    """
    Open a connection. Passthru to gossip. returns connector.
    """
    return gossip.gossipClientConnect(host, port)

def clientConnectionMade(client):
    """
    Called when a connection is made. Not sure how to use this yet.
    Probably can use when on seperate nodes, but unfortunately on a
    local system we cannot grap IP addresses
    """
    #debug("connections.py: Connection has been made?", info=True)
    pass

def createNode(uid, ip, port=None):
    create = Node(ip, port, uid)
    universe[create.getUid()] = create
    knownalive.add(uid)
    return create

def clientConnectionLost((host, port)):
    """
    Called when a connection is lost. Not sure how to use this yet.
    """
    debug("connections.py: Connection has been lost?", info=True)
    """
    Remove the connection from the node.
    """
    todelete = None
    for uid in universe:
        if universe[uid].getPort() == port and universe[uid].getIp() == host:
            todelete = uid
            break
    if todelete:
        deadNode(todelete)

def assignTransport(uid, transport):
    """
    Assign a transport to a given UID.
    """
    try:
        lookupNode(uid).setTCPConnection(transport)
    except KeyError as ke:
        pass
    except Exception as e:
        debug(e)

def informAlive():
    """
    Inform my peers I exist (for new nodes to system)
    """
    alivemessage = message.NewNodeMessage(
        (me.getMe().getUidAsObject(), me.getMe().getPort()))
    alivemessage.send()
    debug("Informing friends I am alive", info=True)

def deadNodeByConnector(connector):
    dest = connector.getDestination()
    todelete = None
    for uid in universe:
        if universe[uid].getIp() == dest.host \
            and universe[uid].getPort() == dest.port:
            todelete = uid
            break
    if todelete:
        deadNode(todelete)

def deadNode(uid):
    """
    Remove a node from the neighbors.
    """
    global universe
    try:
        lookupNode(uid).destroyTCPConnection()
        neighborStrategy.removeNeighbor(uid)
        del universe[uid]
        deadMessage = message.DeadNodeMessage(uid)
        deadMessage.send()
    finally:
        knownDead.add(uid)
        debug("Dead#"+uid, monitor=True)
    debug("removing dead node uid:" + uid, info=True)

def foundClientAsServer(transport):
    """
    When a TCP Connection is created.
    Would work well on external nodes, but since EVERYTHING
    has same IP we have no way to distinguish.
    """

    """
    global universe
    ip = transport.getPeer().host
    for node in universe.values():
        if node.getIp() == ip:
            node.setTCPConnection(transport)
            debug("set transport to" + ip, success=True)
            return True
    """
    #### TODO: Create node.
    #nodes.ExternalNode()
    #debug("Node " + ip + "does not exist yet. Creating it", info=True)
    return False

def lostClientAsServer(transport):
    """
    When a TCP Connection is lost.
    """
    """
    global universe

    ip = transport.getPeer().host
    for node in universe.values():
        if node.getIp() == ip:
            node.destroyTCPConnection()
            debug("Lost connection with " + ip, info=True)
            return True
    debug("Could not find connection with " + ip + " to lose", info=True)
    """
    return False

def createVectorClockMessage():
    """
    Create a new vector clock message
    """
    return me.getMe().getVectorClock().createMessage()

def localReset():
    """
    Kill off this node.
    """
    pass

def globalReset():
    """
    RESENT EVERYTHING BACK TO ZERO!! CAREFUL!!
    """
    debug("GLOBAL RESET. AAAGGG!", info=True)
    me = None
    while(len(universe)) > 0:
        deadNode(universe.keys()[0])
    universe = {}
    simpledb.deleteAll("members")
    init()
