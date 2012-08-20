##############################################################################
#        __  ___                                                             #
#       / / / (_)_________                                                   #
#      / /_/ / / ___/ ___/                                                   #
#     / __  / (__  |__  )                                                    #
#    /_/ /_/_/____/____/        Gossip with Python on Twisted                #
#                                                                            #
##############################################################################

### Imports ##################################################################
# Python Library imports
try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty

# External Library Imports
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import reactor
from twisted.internet.protocol import ClientCreator

from txamqp.protocol import AMQClient
from txamqp.client import TwistedDelegate
from txamqp.content import Content
import txamqp.spec

# Local Imports
import config
from debug import debug

### Constants ################################################################
DURABLE = False
DURABLE_MODE = 2 if DURABLE else 1

VHOST = "/"
EXCHANGE_NAME = "timber_exchange"
QUEUE_NAME = "timber_queue"
ROUTING_KEY = "timber_routing_key"
CONSUMER_TAG = "timber_consumer_tag"

NON_PERSISTENT = 1
PERSISTENT = 2

queue = Queue()


def put(item):
    global queue

    if not queue:
        queue = Queue()
    
    queue.put_nowait(item)

    debug("size:" + str(queue.qsize()), info=True)

def getQueue():
    return queue

### Common Functions #########################################################
@inlineCallbacks
def getConnection(client):
    conn = yield client.connectTCP(
        config.QUEUE_HOST, config.QUEUE_PORT)
    # start the connection negotiation process, sending security mechanisms
    # which the client can use for authentication
    yield conn.start(config.QUEUE_CREDENTIALS)
    returnValue(conn)

@inlineCallbacks
def getChannel(conn):
    # create a new channel that we'll use for sending messages; we can use any
    # numeric id here, only one channel will be created; we'll use this channel
    # for all the messages that we send
    chan = yield conn.channel(3)
    # open a virtual connection; channels are used so that heavy-weight TCP/IP
    # connections can be used my multiple light-weight connections (channels)
    yield chan.channel_open()
    returnValue(chan)

### Producer Functions #######################################################
@inlineCallbacks
def producer_pushText(chan, body):
    msg = Content(body)
    # we don't want to see these test messages every time the consumer connects
    # to the RabbitMQ server, so we opt for non-persistent delivery
    msg["delivery mode"] = common.NON_PERSISTENT
    # publish the message to our exchange; use the routing key to decide which
    # queue the exchange should send it to
    yield chan.basic_publish(
        exchange=common.EXCHANGE_NAME, content=msg,
        routing_key=common.ROUTING_KEY)
    returnValue(None)


@inlineCallbacks
def producer_cleanUp(conn, chan):
    yield chan.channel_close()
    # the AMQP spec says that connection/channel closes should be done
    # carefully; the txamqp.protocol.AMQPClient creates an initial channel with
    # id 0 when it first starts; we get this channel so that we can close it
    chan = yield conn.channel(0)
    # close the virtual connection (channel)
    yield chan.connection_close()
    reactor.stop()
    returnValue(None)

### Consumer Functions #######################################################
@inlineCallbacks
def consumer_getQueue(conn, chan):
    # in order to get the queue, we've got some setup to do; keep in mind that
    # we're not interested in persisting messages
    #
    # create an exchange on the message server
    yield chan.exchange_declare(
        exchange=common.EXCHANGE_NAME, type="direct",
        durable=False, auto_delete=True)
    # create a message queue on the message server
    yield chan.queue_declare(
        queue=common.QUEUE_NAME, durable=False, exclusive=False,
        auto_delete=True)
    # bind the exchange and the message queue
    yield chan.queue_bind(
        queue=common.QUEUE_NAME, exchange=common.EXCHANGE_NAME,
        routing_key=common.ROUTING_KEY)
    # we're writing a consumer, so we need to create a consumer, identifying
    # which queue this consumer is reading from; we give it a tag so that we
    # can refer to it later
    yield chan.basic_consume(
        queue=common.QUEUE_NAME,
        consumer_tag=common.CONSUMER_TAG)
    # get the queue that's associated with our consumer
    queue = yield conn.queue(common.CONSUMER_TAG)
    returnValue(queue)

@inlineCallbacks
def consumder_processMessage(chan, queue):
    msg = yield queue.get()
    print "Received: %s from channel #%s" % (
        msg.content.body, chan.id)
    processMessage(chan, queue)
    returnValue(None)
