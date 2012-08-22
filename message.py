##############################################################################
#        __  ___                                                             #
#       / / / (_)_________                                                   #
#      / /_/ / / ___/ ___/                                                   #
#     / __  / (__  |__  )                                                    #
#    /_/ /_/_/____/____/        Gossip with Python on Twisted                #
#                                                                            #
##############################################################################

### Imports ##################################################################
# Python Library Imports
import time
import cPickle

# External Library Imports
import zope.interface

# Local Imports
import config
import me
import vectorClock
import connections
from hiss_exceptions import GeneralError, ConnectionError
from debug import debug

### Message Interface ########################################################
class IMessage(zope.interface.Interface):
    """
    Interface for all messages.
    """

    def getSender():
        """
        Get the sender of a message
        """

    def getRecipients():
        """
        Get the recipient for a message.
        """

    def getPayload():
        """
        Get the message body.
        """

    def getSerialized():
        """
        Data of the payload for transfer.
        """

    def getTime():
        """
        Get the messages created time.
        """

    def send():
        """
        Send a message
        """

    def getCode():
        """
        Get the message code.
        """

    def __str__():
        """
        Messages must have a string representation
        """

class IMessageDispatcher(Interface):
    """
    Message dispatcher interface
    """

    def dispatch(message):
        """
        Dispatch a message
        """

### Message Functions ########################################################
def buildMessage(serializedMessage):
    """
    build a message from a serialized code.
    """
    try:
        return cPickle.loads(serializedMessage)
    except:
        debug("Could not de-pickle serialized message", error=True)

### Classes of Message #######################################################
class GenericMessage(object):
    """
    Message class
    """

    zope.interface.implements(IMessage)

    def __init__(self, payload, sender=None, recipients=None):
        """
        Constructor
        """
        self._payload = payload
        self._time = time.time()
        self._code = "?"

        if sender:
            self._sender = sender
        else:
            self._sender = me.getMe().getBaseData()
            # just assign basic node data to the sender.

        if recipients:
            self._recipients = recipients
        else:
            self._recipients = []

    def getSender(self):
        """
        Get the sender of this message. Ideally a node object.
        """
        return self._sender

    def setSender(self, sender):
        """
        Set the sender of this message with a new node object.
        """
        self._sender = sender

    def getRecipients(self):
        """
        Get the recipient for the message. Ideally a list of UID strings.
        """
        return self._recipients

    def setRecipients(self, recipients):
        """
        Set the recipients for the message
        """
        self._recipients = recipients

    def getPayload(self):
        """
        Get the message body
        """
        return self._payload

    def getSerialized(self):
        """
        get a string of the payload.
        """
        try:
            return cPickle.dumps(self)
        except:
            debug("Failed to pickle message", error=True)

    def getTime(self):
        """
        Get the time created
        """
        return self._time

    def send(self, transport=None):
        """
        Send the message. Assume we don't have multicast, 
        so just do point to point for now.
        """
        if not self._recipients or len(self.getRecipients()) == 0:
            debug("No recipients specified.", error=True)
            raise GeneralError("No recipients specified.")

        if len(self.getRecipients()) == 1 and transport:
            node = connections.lookupNode(self.getRecipients()[0])
            hissclient = connections.HissConnection(node, transport)
            hissclient.dispatchMessage(self)

        recs = []
        for recipient in self.getRecipients():

            uid = recipient
            if not isinstance(recipient, str):
                # Handles exception case if this were a node instead of a UID.
                uid = recipient.getUid()

            if uid in connections.universe:
                node = connections.lookupNode(uid)
                if not node.hasTCPConnection():
                    debug("No connection to " + node.getShortUid(), 
                        error=True)
                else:
                    # Ok, stop messing around and send the message!
                    try:
                        tcpConn = node.getTCPConnection().dispatchMessage(
                            self)
                        recs.append(node.getShortUid())
                        debug("#".join(
                            ["Msg", me.getUid(), uid, self.getCode()]),
                            monitor=True)
                    except:
                        debug("Failed to send message to [ " \
                            + node.getShortUid() + " ]", error=True)
            else:
                raise GeneralError(
                    "recipient " + uid + " not found.")
        if self.getCode() != 'AG':
            debug("(" + self.getCode() + ") message sent to [ " \
                + " ][ ".join(recs) + " ]", success=True)

    def getCode(self):
        """
        Generic messages have a "?" code.
        """
        return self._code

    def compress(self):
        """
        Compress down a message for sending across the network.
        """
        del self._recipients[:]

    def __str__(self):
        """
        Get a string representation of the message
        """
        return self.getSerialized()

class VectorMessage(GenericMessage):
    """
    A message where the payload is specifically a vector clock dictionary
    (just a dictionary, not the wrapper class)
    """

    def __init__(self, vClock, sender=None, recipients=None):
        """
        Constructor
        """
        if type(vClock) is vectorClock.VectorClock:
            super(VectorMessage, self).__init__(
                vClock.getClocks(), sender, recipients)

            self._clockKey = vClock.getKey()

        else:
            super(VectorMessage, self).__init__(
                vClock, sender, recipients)
            if sender:
                self._clockKey = sender.getUid()
            else:
                self._clockKey = me.getMe().getUid()

        self._code = "V"
        
    def getVectorClock(self):
        """
        Get a VectorClock object from this message.
        """
        return vectorClock.VectorClock(self._clockKey, self.getPayload())

    def respond(self):
        """
        How the systemm should respon to receiving this vector clock message.
        """
        try:
            me.getMe().getVectorClock().receiveMessage(self)
            debug("Responded to vector message.", 
                info=True, threshold=2)
        except Exception as e:
            debug(e)

    @staticmethod
    def createVectorClockMessage():
        try:
            return me.getMe().getVectorClock().createMessage()
        except Exception as e:
            debug(e)

    @staticmethod
    def isVectorMessage(msg):
        """
        Return whether the given message is a VectorMessage
        """
        return msg.getCode() == "V"

class NetworkStatusMessage(GenericMessage):
    """
    Network maintenance message. Contains information about dead nodes, 
    new nodes or whatever. This should be treated as an abstract class 
    and not implemented directly.
    """

    def __init__(self, updates, sender=None, recipients=None):
        """
        Constructor.
        """
        super(NetworkStatusMessage, self).__init__(updates, sender, recipients)
        self._code = 'S'

    def respond(self):
        """
        Don't do anything here. Let subclasses decide
        """
        pass

    @staticmethod
    def isNetworkStatusMessage(msg):
        """
        Parent for any message.
        """
        return msg.getCode() in [
            'S', 'A', 'D', 'G', 'AG', 'M', 'U', 'NRQ', 'NRS']


class IsAliveMessage(NetworkStatusMessage):
    """
    Message to tell if another node is alive
    """

    def __init__(self, sender=None, recipients=None):
        super(IsAliveMessage, self).__init__("", sender, recipients)
        self._code = 'A'

    def respond(self):
        """
        Response to IsAliveMessage
        """
        debug('Respnding to an IsAliveMessage with a MeMessage', 
            info=True)
        try:
            responseMsg = MeMessage(
                me.getMe().getUid(), 
                [self._sender.getUid()])
            responseMsg.send()
            debug('Sent MeMessage', success=True)
        except:
            debug("Error sending MeMessage", error=True)

    @staticmethod
    def isIsAliveMessage(msg):
        return msg.getCode() == 'A'


class MeMessage(NetworkStatusMessage):
    """
    Message containing node information
    """
    def __init__(self, sender=None, recipients=None):
        """
        Constructor. Set the payload to be the node data of the current node.
        """
        super(MeMessage, self).__init__("", sender, recipients)
        self._code = 'M'
        self._payload = me.getMe().getCompressed()

    def respond(self):
        """
        Insert the received node into this table.
        """
        try:
            nodeData = node.buildNode(self._payload)
            if nodeData.getUid() not in connections.universe:
                connections.universe[nodeData.getUid()] = \
                    nodes.ExternalNode.fromBase(nodeData)
            connections.universe[nodeData.getUid()].knownAlive = True
            debug('Reponded to a MeMessage', success=True)
        except:
            debug('Failed to respond to MeMessage', error=True)

    @staticmethod
    def isMeMessage(msg):
        """
        If this message contains a payload of a single node data.
        """
        return msg.getCode() == 'M'

class NodeRequestMessage(NetworkStatusMessage):
    """
    Ask for node information
    """
    
    def __init__(self, uid, sender=None, recipients=None):
        """
        Constructor
        """
        super(NodeRequestMessage, self).__init__(uid, sender, recipients)
        self._code = 'NRQ'

    def respond(self):
        """
        Repond to a node request message
        """
        response = NodeResponseMessage()
        pass
        # TODO fill in.

    @staticmethod
    def isNodeRequestMessage(msg):
        return msg.getCode() == 'NRQ'



class NodeResponseMessage(NetworkStatusMessage):
    """
    Repond to a Node Request. Contains Node Data
    """

    def __init__(self, node, sender=None, recipients=None):
        """
        Constructor
        """
        super(NodeResponseMessage, self).__init__(node, sender, recipients)
        self._code = 'NRS'

    def respond(self):
        """
        Respond to a Node Response Message. Assign to self!
        """
        try:
            uid = self._payload.getUid()
            if uid not in connections.universe:
                connections.universe[uid] = self._payload
        except:
            pass


class GossipNetworkStatusMessage(NetworkStatusMessage):
    """
    Network maintenance message that should be gossiped around.
    """

    def __init__(self, updates, sender=None, recipients=None):
        """
        Constructor
        """
        if not recipients:
            recipients = connections.getNeighbors()
        super(GossipNetworkStatusMessage, self).__init__(
            updates, sender, recipients)

        self._gossipttl = config.GOSSIPTTL
        self._code = 'G'

    def decrementTtl(self):
        self._gossipttl -= 1

    def getTtl(self):
        return self._gossipttl

    def respond(self):
        """
        Defines how to respond when one of these messages is recieved
        No defined behavior in parent class yet.
        """
        try:
            self.decrementTtl()
            if self.getTtl() > 0:
                self._sender = me.getMe().getBaseData()
                self._recipients = []
                # retain the same payload.
                gossip.gossipThis(self)
            debug("Responded to gossip status message", success=True)
        except:
            debug("failed to respond to gossip status message", error=True)

    @staticmethod
    def isGossipNetworkStatusMessage(msg):
        """
        Return if this is any type of GossipNetworkStatusMessage
        """
        return msg.getCode() in ['G', 'D', 'N', 'U']


class UniverseMessage(GossipNetworkStatusMessage):
    """
    Tell others about all the UIDs in the system.
    """

    def __init__(self, unikeys, sender=None, recipients=None):
        """
        Constructor
        """
        super(UniverseMessage, self).__init__(unikeys, sender, recipients)
        self._code = 'U'

    def respond(self):
        """
        Respond to a universe message.
        """
        # Compare with my vector clock.
        # If newer, add keys > None
        # Send info messages
        # Put in newer vector clock.
        super(UniverseMessage, self).respond()

    @staticmethod
    def isUniverseMessae(msg):
        """
        Is this message a universe message
        """
        return msg.getCode() == 'U'


class DeadNodeMessage(GossipNetworkStatusMessage):
    """
    Dead node message.
    Remove from connection collection and gossip.
    Payload: a uid
    """

    def __init__(self, uid, sender=None, recipients=None):
        """
        Constructor
        """
        super(DeadNodeMessage, self).__init__(uid, sender, recipients)
        self._code = "D"

    def respond(self):
        """
        Respond to a dead node.
        """
        try:
            uid = self.getPayload()
            if uid in connections.universe:
                connections.removeNode(uid)
                super(DeadNodeMessage, self).respond()
                debug("Dead#"+uid, monitor=True)
            else:
                pass #don't gossip if we've already gossipped this.
            debug("Responded to dead node message.", success=True)
        except:
            debug("failed to respond to dead node message", error=True)

    @staticmethod
    def isDeadNodeMessage(msg):
        """
        Return if this message is a dead node message
        """
        return msg.getCode() == 'D'
        

class NewNodeMessage(GossipNetworkStatusMessage):
    """
    New node message. A node has entered the system.
    """

    def __init__(self, node, sender=None, recipients=None):
        """
        Constructor
        """
        super(NewNodeMessage, self).__init__(node, sender, recipients)
        self._code = "N"

    def respond(self):
        """
        How to respond to a new node message.
        """
        try:
            (uidObject, ip) = self.getPayload()
            if uidObject.hex not in connections.universe: 
                connections.createNode(
                    uidObject, ip, connections.DEFAULT_SEND_PORT)
                super(NewNodeMessage, self).respond()
            else:
                pass # don't need to gossip if we've already gossipped this.
            debug("Successfully responded to new node message", success=True)
        except:
            debug("Failed to respond to new node message", error=True)

    @staticmethod
    def isNewNodeMessage(msg):
        """
        Return if this message is a NewNodeMessage
        """
        return msg.getCode() == 'N'


class AggregateMessage(GossipNetworkStatusMessage):
    """
    Message that contains aggregation statistics.
    """

    def __init__(self, aggstat, sender=None, recipients=None):
        """
        Constructor. Takes a statistic name to track.
        """
        super(AggregateMessage, self).__init__(aggstat, sender, recipients)
        self._code = "AG"

    def respond(self):
        """
        Respond to an AggregateMessage
        """
        try:
            aggstat = self.getPayload()
            aggregation.STATISTICS[aggstat.getName()].reduce(aggstat)
            debug("Responded to AggregateMessage: " + aggstat.getName(), 
                success=True)
        except:
            debug("Did not respond to aggregation message.", error=True)

    @staticmethod
    def createAggregateMessage(agg):
        """
        Build an aggregate message for the aggregation in the param.
        """
        return AggregateMessage(agg, me.getUid())

    @staticmethod
    def isAggregateMessage(msg):
        """
        Static method to tell whether the provided 
        message is an AggregateMessage
        """
        return msg.getCode() == "AG"



### Logging Messages #########################################################
class LogMessage(GenericMessage):
    """
    Message representing information that the application might wish to log.
    """

    def __init__(self, payload, level=None):
        """
        Constructor
        """
        super(LogMessage, self).__init__(payload)
        self._level = level

    def setLevel(self, level):
        """
        Set the level of this message
        """
        self._level = level

    def getLevel(self):
        """
        Get the level of this messsage
        """
        return self._level

    def getCode(self):
        """
        Get the code for a logging message (L)
        """
        return 'L'

    def respond(self):
        pass

    @staticmethod
    def isLogMessage(msg):
        """
        Return whether a given message is any type of LogMessage
        """
        return msg.getCode() in ['L', 'IL', 'EL']

class InternalLogMessage(LogMessage):
    """
    Interanl Log Message
    """

    def __init__(self, payload, level=None):
        """
        Constructor
        """
        super(InternalLogMessage, self).__init__(payload, level)

    def getCode(self):
        """
        Internal log message code
        """
        return 'IL'

    def respond(self):
        pass

    @staticmethod
    def isInternalLogMessage(msg):
        """
        Return whether a message is an internal logging message.
        """
        return msg.getCode() == 'IL'

class ExternalLogMessage(LogMessage):
    """
    External Log Message
    """
    def __init__(self, payload, level=-1, logType='Default'):
        """
        Constructor
        """
        super(ExternalLogMessage, self).__init__(payload, level)
        self._type = logType

    def getCode(self):
        """
        External log message code
        """
        return 'EL'

    def respond(self):
        pass

    @staticmethod
    def isExternalLogMessage(msg):
        """
        Return whether a message is an external logging message.
        """
        return msg.getCode() == 'EL'


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
