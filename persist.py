#----------------------------------------------------------------------------#
# persist.py                                                                 #
# contains all the stuff for persistant storage                              #
#----------------------------------------------------------------------------#

### Imports ###################################################################
# Python Library Imports
import time
import datetime

# External Library Imports
import bson
import pymongo.connection
import pymongo.database
import pymongo.collection

# Local Imports
import me
import config
from debug import debug

### Variables #################################################################
mongoConnection = None
mongoDatabase = None
mongoCollection = None

### Script  ###################################################################
mongoConnection = pymongo.connection.Connection(
    config.MONGO_DB_HOST, 
    config.MONGO_DB_PORT)

if mongoConnection:
     debug("PyMongo Established connection", success=True)

mongoDatabase = pymongo.database.Database(
    mongoConnection, 
    config.MONGO_DB_NAME)

if mongoDatabase:
    debug("PyMongo Initialized DB", success=True)

    mongoDatabase.authenticate(
        config.MONGO_DB_USER, 
        config.MONGO_DB_PASSWORD)

    debug("PyMongo database authenticated.", success=True)

validation_data = mongoDatabase.validate_collection(
    config.MONGO_DB_LOG_COLLECTION)

debug("PyMongo validating database collection", info=True)

try:
    mongoDatabase.create_collection(
        config.MONGO_DB_LOG_COLLECTION)
except:
    pass

debug("PyMongo could not find collection. Creating collection.", info=True)

mongoCollection = pymongo.collection.Collection(
    mongoDatabase, 
    config.MONGO_DB_LOG_COLLECTION)

if mongoCollection:
    debug("PyMongo: Database collection set up successfully.", success=True)
else:
    debug("PyMongo: Database collection initialization failed.", error=True)

### Connection Functions #####################################################

def mongoConnectionInit():
    """
    Initialize connection to mongodb
    """
    global mongoConnection

    if not mongoConnection:
        try:
            mongoConnection = pymongo.connection.Connection(
                config.MONGO_DB_HOST, 
                config.MONGO_DB_PORT)
            debug("PyMongo Established connection", success=True)
        except Exception as e:
            debug(e)
            debug("PyMongo could not establish connection", error=True)

def mongoDatabaseInit():
    """
    Initialize mongodb database
    """
    global mongoDatabase

    if not mongoDatabase:
        try:
            mongoDatabase = pymongo.database.Database(
                mongoConnection, 
                config.MONGO_DB_NAME)
            debug("PyMongo Initialized DB", success=True)

            mongoDatabase.authenticate(
                config.MONGO_DB_USER, 
                config.MONGO_DB_PASSWORD)

            debug("PyMongo database authenticated.", success=True)
        except Exception as e:
            debug(e)
            debug("PyMongo could not init DB", error=True)

def mongoCollectionInit():
    """
    Initialize MongoDB Collection
    """
    global mongoCollection
    global validation_data
    if not mongoCollection:
        try:
            validation_data = mongoDatabase.validate_collection(
                config.MONGO_DB_LOG_COLLECTION)

            debug("PyMongo validating database collection", info=True)

            mongoDatabase.create_collection(
                config.MONGO_DB_LOG_COLLECTION)

            debug("PyMongo could not find collection. Creating collection.", 
                info=True)

            mongoCollection = pymongo.collection.Collection(
                mongoDatabase, 
                config.MONGO_DB_LOG_COLLECTION)

        except Exception as e:
            debug(e)
            debug("PyMongo could not create collection", error=True)


### Access Functions  ########################################################
def insert(items):
    """
    Insert one or more items into the collection.
    """
    global mongoCollection
    mongoCollection.insert(items)


def find(searchDict):
    """
    Return a message
    """
    global mongoCollection
    return mongoCollection.find(searchDict)


def insertMessage(message):
    """
    Insert a message into the collection.
    """
    value = {
        "payload": message.getPayload(),
        "time": message.getTime(),
        "code": message.getCode
        }
    insert(value)

def findMessages(searchDict):
    """
    Find messages in the collection.
    """
    global mongoCollection
    return mongoCollection.find(searchDict)

def log(typ, msg, level, ordered=True):
    """
    Log a received piece of data from the api.
    Can be ordered or not. 
    """
    try:
        item = {"type":typ,"message":msg,"level":level,"time":time.time()}
        if ordered:
            item["machine"] = me.getUid()
            item["clock"] = me.getMe().getVectorClock().getClocks()
        insert(item)
        debug("logged item", success=True)
    except Exception, e:
        debug(e, error=True)
        debug("did not log message (ordered:" + str(ordered) + ")", error=True)
        
