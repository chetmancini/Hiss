##############################################################################
#        __  ___                                                             #
#       / / / (_)_________                                                   #
#      / /_/ / / ___/ ___/                                                   #
#     / __  / (__  |__  )                                                    #
#    /_/ /_/_/____/____/        Gossip with Python on Twisted                #
#                                                                            #
##############################################################################

### Imports ##################################################################
# Python library imports.

# External Library Imports
import boto

# Local Imports
import config
from hiss_exceptions import GeneralError
from debug import debug

### Variables ################################################################
sdbConnection = None
sdbDomain = None

### Functions ################################################################
def sdbConnect():
    """
    Connect to SimpleDB
    """
    global sdbConnection

    if not sdbConnection:
        try:
            sdbConnection = boto.connect_sdb(
                config.AWS_ACCESS_KEY,
                config.AWS_SECRET_KEY)
            if sdbConnection:
                debug("Connection to SimpleDB initialized", 
                    success=True, 
                    threshold=1)
        except Exception as e:
            print e
            raise
    else:
        return

def initDomain():
    """
    Initialize the domain so items can be stored.
    """
    global sdbConnection
    global sdbDomain

    sdbConnect()

    if not sdbDomain:
        try:
            sdbDomain = sdbConnection.create_domain(config.AWS_SDB_DOMAIN_NAME)
            debug("SDB Domain " + config.AWS_SDB_DOMAIN_NAME + " created", 
                success=True)
        except Exception as e:
            debug(e)
            raise
    else:
        return

def putSet(item, inputDict):
    """
    Push a particular value for item and name, overwriting the old value.
    """
    sdbConnect()
    initDomain()

    try:
        if len(inputDict) > 0:
            sdbDomain.put_attributes(item, inputDict, replace=True)
        else:
            debug("NO INPUT", error=True)
    except Exception as e:
        debug(e)
        raise

def getSet(item):
    """
    Get a particular value for an item and name.
    """
    sdbConnect()
    initDomain()

    try:
        return sdbDomain.get_attributes(item, consistent_read=True)
    except Exception as e:
        debug(e)
        raise

def deleteSet(item, keys=None):
    """
    Remove keys
    """
    sdbConnect()
    initDomain()

    try:
        sdbDomain.delete_attributes(item, keys)
    except Exception as e:
        debug(e)
        raise

def destroyDomain():
    """
    Delete the domain. Warning, deletes all items as well!
    """
    global sdbConnection
    global sdbDomain

    sdbConnect()

    try:
        sdbConnection.delete_domain(config.AWS_SDB_DOMAIN_NAME)
        sdbDomain = None
        return
    except Exception as e:
        debug(e)
        raise

def deleteAll(item):
    deleteSet(item)
