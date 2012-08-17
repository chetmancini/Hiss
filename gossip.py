##############################################################################
#        __  ___                                                             #
#       / / / (_)_________                                                   #
#      / /_/ / / ___/ ___/                                                   #
#     / __  / (__  |__  )                                                    #
#    /_/ /_/_/____/____/        Gossip with Python on Twisted                #
#                                                                            #
##############################################################################

### Imports ##################################################################
# Python Libary Imports
import sys
import traceback
import random
try:
    from Queue import Queue, Empty
except ImportError: #Hack for Python2to3
    from queue import Queue, Empty

# External Library Imports
from zope.interface import Interface, implements
from twisted.web import server, resource, util
from twisted.application import internet, service
from twisted.internet import task, reactor
from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ServerFactory
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.python import components, log

# Local Imports
import me
import config
import connections
import message
import aggregation
import membership
import message_queue
from timber_exceptions import GeneralError, ConnectionError
from debug import debug

### Globals ##################################################################

### Editable
APIS = {
    'stats': HissStatsResource(),
    }

### No-edit
__name__ = "Hiss"
__summary__ = "Gossip on Twisted in Python"
__version__ = "0.0.1"
__web__ = "github.com/chetmancini"
__author__ = "Chet Mancini"
__author_email__ = "cam479 at cornell dot edu"
__licence__ = "Apache"
__warranty__ = "None"

gossipqueue = Queue()


### Interfaces ###############################################################
class IGossipServerProtocol(Interface):
    """
    GossipServerProtocol Interface
    """

class IGossipClientProtocol(Interface):
    """
    GossipClientProtocol Interface
    """

class IGossipServerFactory(Interface):
    """
    GossipServerFactory Interface
    """

class IGossipClientFactory(Interface):
    """
    GossipClientFactory Interface
    """

### Methods ##################################################################

def catchError(err):
    return "Internal error in server"

def getHead():
    return """
    <div style='font-family:sans-serif;'>
    <h1>Hiss API Access</h1>
    """

def getFoot():
    return """
    </div>
    """

### Classes ##################################################################

class GossipServerProtocol(Protocol):
    """
    Gossip server protocol
    """

    implements(IGossipServerProtocol)

    def connectionMade(self):
        """
        Callback called once a connection is made with a client.
        """
        debug("Server protocol connection made!", 
            success=True, threshold=1)
        self.factory.clientConnectionMade(self)

        # Send a response
        #response = message.MeMessage()
        #response.send(self.transport)
        self.transport.write(me.getUid())

    def connectionLost(self, reason):
        """
        Callback called when a connection is lost.
        Pretty much just ignore. client connection losses
        more important.
        """
        self.factory.clientConnectionLost(self, reason)

    def dataReceived(self, data):
        """
        When gossip data is received.
        """
        debug("DATA RECEIVED BOOYAH!", success=True, threshold=1)
        if len(data) == 32:
            connections.assignTransport(data, self.transport)
        else:
            try:
                msg = message.buildMessage(data)
                msg.respond() # just respond polymorphically.
            except:
                debug(data, error=True)

class GossipClientProtocol(Protocol):
    """
    Gossip client protocol
    """
    implements(IGossipClientProtocol)

    def connectionMade(self):
        """
        Callback when a connection is made.
        """
        debug("Client Protocol connection made", 
            success=True, threshold=1)
        connections.clientConnectionMade(self.transport)

        ### Send a message to respond.
        #response = message.MeMessage()
        #response.send(self.transport)
        self.transport.write(me.getUid())

    def connectionLost(self, reason):
        """
        Callback when a connection is lost.
        """
        debug("Client Protocol connection lost", 
            error=True, threshold=2)
        connections.clientConnectionLost(self.transport.addr)


    def dataReceived(self, data):
        """
        Data received? this seems a little odd.
        """
        debug("Data received via client", 
            strange=True, threshold=1)
        if len(data) == 32:
            connections.assignTransport(data, self.transport)
        else:
            try:
                msg = message.buildMessage(data)
                msg.respond()
            except:
                debug("data: " + data, error=True)


class GossipServerFactory(ServerFactory):
    """
    Gossip Factory
    """

    implements(IGossipServerFactory)

    protocol = GossipServerProtocol
    """
    This factory will create gossip protocol objects on connections.
    """

    def __init__(self):
        """
        Factory Constructor
        """
        # We want to run members refresh every once in awhile
        self.membersLoop = task.LoopingCall(connections.maintainMembers)
        self.membersLoop.start(membership.getRandomWaitTimeSecs(), True)

        self.aggregationLoop = task.LoopingCall(aggregation.refreshAll)
        self.aggregationLoop.start(config.STATS_REFRESH_INTERVAL, False)

        debug("Gossip Server Factory created!", 
            success=True, threshold=1)


    def clientConnectionMade(self, client):
        """
        When a node is found
        """
        debug("Server: Receiving client " + str(client.transport.getPeer()), 
            success=True, threshold=1)

        connections.foundClientAsServer(client.transport)

    def clientConnectionLost(self, client, reason):
        """
        When a node is lost.
        """
        debug("Server: Lost client " + str(client.transport.getPeer()) + \
            " for reason " + str(reason), error=True, threshold=2)

        connections.lostClientAsServer(client.transport)

    def startFactory(self):
        """
        Start Factory
        """
        pass

    def stopFactory(self):
        """
        Stop Factory
        """
        pass

    def membersRefreshDone(self):
        """
        Quit the members refresh operation.
        """
        self.membersLoop.stop()
        debug("Members Refresh Operation Ceased. Universe Stable.", 
            info=True, threshold=2)


class GossipClientFactory(ReconnectingClientFactory):
    """
    Factory for gossip clients
    """

    implements(IGossipServerFactory)

    protocol = GossipClientProtocol

    def __init__(self, callback=None, errback=None):
        """
        Constructor.
        """
        debug("Client Factory Init", 
            info=True, threshold=1)
        # Run gossip on a timer.
        self.gossipLoop = task.LoopingCall(self.gossip)
        self.gossipLoop.start(config.GOSSIP_WAIT_SECONDS, False)

        self.callback = callback
        self.errback = errback

    def clientConnectionFailed(self, connector, reason):
        """
        Callback when the client connection fails.
        """
        debug("Client Connection failed", 
            info=True, threshold=3)
        if self.errback:
            self.errback(reason)
        connections.deadNodeByConnector(connector)

    def clientConnectionLost(self, connector, unused_reason):
        """
        Callback for when the client connection is lost.
        """
        debug("Client Connection lost!", 
            info=True, threshold=1)
        if self.errback:
            self.errback(reason)

    def startedConnecting(self, connector):
        """
        Called when a connection is starting
        """
        debug("Client Factory started connecting...", 
            info=True, threshold=1)

    def startFactory(self):
        """
        Called when the factory is started
        """
        debug("Client Factory Started...", 
            info=True, threshold=1)
        pass #good for connectiong, opening fiels, etc..

    def stopFactory(self):
        """
        Called when the factory is stopped.
        """
        debug("Client Factory Stopped...", 
            info=True, threshold=1)
        pass #good for disconnectiong databases, closing files.


    def gossip(self):
        """
        Gossip procedure. This is basic. Hope to improve later.
        """
        if connections.connectToNeighbors():
            debug("Connections in process. deferred gossip", info=True)
            return

        # Get my neighbors
        recipients = connections.getNeighbors()

        if len(recipients) > 0:
            shortids = []
            for uid in recipients:
                shortids.append(connections.lookupNode(uid).getShortUid())
            debug("Gossipping with: [ " + " ][ ".join(shortids) + " ]", 
                info=True)
        else:
            debug("No neighbors to gossip with this interval.", 
                error=True, threshold=1)
            return

        # Put all messages in a list.
        gossipMessages = []

        # Get a vector clock message
        vcMessage = message.VectorMessage.createVectorClockMessage()
        vcMessage.setRecipients(recipients)
        gossipMessages.append(vcMessage)

        # Put in each aggreggation. Tae out for now.

        for aggName in aggregation.STATISTICS:
            agg = aggregation.STATISTICS[aggName]
            aggMessage = message.AggregateMessage.createAggregateMessage(agg)
            aggMessage.setRecipients(recipients)
            gossipMessages.append(aggMessage)
        """
        agg = random.choice(aggregation.STATISTICS.values())      
        aggMessage = message.AggregateMessage.createAggregateMessage(agg)
        aggMessage.setRecipients(recipients)
        gossipMessages.append(aggMessage)
        """
        # Get a network message
        gossipmsg = gossipPrepare()
        while gossipmsg:
            gossipmsg.setRecipients(recipients)
            toAppend = copy.deepcopy(gossipmsg)
            gossipMessages.append(toAppend)
            gossipmsg = gossipPrepare()

        debug("There are " \
            + str(len(gossipMessages)) + " to send.", threshold=2, info=True)

        # Send out the messages
        for msg in gossipMessages:
            try:
                msg.send()
            except ConnectionError as ce:
                debug(ce.__str__(), error=True)
            except GeneralError as ge:
                debug(ge.__str__(), error=True)


class HissRootResource(resource.Resource):
    """
    Hiss api root resource
    """

    def render_GET(self, request):
        """
        get response method for the root resource
        localhost:8000/
        """
        debug("GET request received at Root on " + \
            me.getMe().getIp(), info=True, threshold=3)
        return 'Welcome to the REST API'

    def getChild(self, name, request):
        """
        We overrite the get child function so that we can handle invalid
        requests
        """
        if name == '':
            return self
        else:
            if name in APIS.keys():
                return resource.Resource.getChild(self, name, request)
            else:
                return PageNotFoundError()

class HissStatsResource(resource.Resource):
    """
    Resource for getting server stats.
    """

    def render_GET(self, request):
        """
        Get statistics for this node and the system
        """
        debug("Recevied GET on stat resouce")
        requestDict = request.__dict__
        requestArgs = request.args

        if 'name' in requestArgs:
            name = requestArgs['name'][0]
            if name == 'all':
                aggDict = {}
                for name in aggregation.STATISTICS:
                    aggDict[name] = aggregation.getAggregation(name)
                return json.dumps(aggDict)
            elif name in aggregation.STATISTICS:
                aggDict = aggregation.getAggregation(name)
                debug("Sent Stat response for " + name, 
                    success=True, threshold=2)
                return json.dumps(aggDict)
            else:
                return "Not a valid statistic name. Try: '" + \
                    + "' | '".join(aggregation.STATISTICS.keys()) + "'"
        else:
            ret = getHead()
            ret += "<p>Set a 'name' GET parameter to:</p><ul>"
            for key in aggregation.STATISTICS:
                ret += "<li><a href='?name="+key+"'>"+key+"</a></li>"
            ret += "</ul>"
            ret += getFoot()
            return ret

    def render_POST(self, request):
        """
        Post data to statistics. Not currently supported.
        """
        debug("Invalid stats POST access", info=True)
        ret = getHead()
        ret += "<p>POST access not provided.</p>"
        ret += "<p>Set a 'name' GET parameter to:</p><ul>"
        for key in aggregation.STATISTICS:
            ret += "<li><a href='?name="+key+"'>"+key+"</a></li>"
        ret += "</ul>" + getFoot()
        return ret

class PageNotFoundError(resource.Resource):
    """
    Page not found error.
    """

    def render_GET(self, request):
        """
        Render page not found for GET requests
        """
        debug("404 error")
        return '404 Error: Not Found.'

    def render_POST(self, request):
        """
        Render page not found for POST requests
        """
        debug("POST to page not found? wtf.")
        return '404 Error: Not found.'

### Factories ################################################################
gossipServerFactory = None
gossipClientFactory = None

### Functions ################################################################
def gossipClientConnect(host, port):
    """
    connect as a client. returns a connector
    """
    try:
        connector = reactor.connectTCP(host, port, gossipClientFactory)
        debug("Reactor is connecting to " + host + ":" + str(port), 
            info=True)
        return connector
    except:
        debug("FAILED TO CONNECT", error=True)

def gossipRun():
    """
    Execute the gossip logic.
    """
    global gossipClientFactory
    global gossipServerFactory

    gossipServerFactory = GossipServerFactory()
    gossipClientFactory = GossipClientFactory()

    debug("Launching Hiss Listener on port " + \
        str(config.RECEIVE_PORT) + ".", info=True)

    reactor.listenTCP(config.RECEIVE_PORT, gossipServerFactory)

def gossipThis(msg):
    """
    Receive a gossiped Message from another node.
    """
    global gossipqueue

    debug("Received Gossip message: " + msg.__class__.__name__ + 
        " from " + msg.getSender() + " (" + msg.getCode() + ")", success=True)

    gossipqueue.put_nowait(msg)

def gossipPrepare():
    """
    Get the next Message object to gossip to friends
    """
    if not gossipqueue.empty():
        return gossipqueue.get_nowait()
    else:
        return None

def quitMembersRefresh():
    """
    End members refresh operation and rely on gossip for rest
    """
    gossipServerFactory.membersRefreshDone()

def apiRun():
    """
    Run the Timber API on the reactor.
    """
    root = HissRootResource()
    for name,resource in enumerate(APIS):
        root.putChild(name, resource)

    hiss_factory = server.Site(root)

    debug("Launching Hiss api listener on port " \
        + str(config.LOG_PORT) + ".", info=True)
    
    reactor.listenTCP(config.LOG_PORT, hiss_factory)

### Main #####################################################################
if __name__ == "__main__":
    """
    This allows one to run gossip directly without other APIs
    """
    gossipRun()
    apiRun()
    reactor.run()