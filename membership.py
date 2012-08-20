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
import random
import sys
import traceback
import copy

# External library imports

# Local Imports
import simpledb
import me
import nodes
import gossip
import connections
from debug import debug

### Variables ################################################################
members = {}
members_to_delete = set([])

### Constants ################################################################
ITEMKEY = "members"

### Functions ################################################################
def getRandomWaitTimeMillis():
    """
    Generate a random wait time between member refresh operations.
    """
    return random.randint(20000, 60000)

def getRandomWaitTimeSecs():
    """
    Generate a random wai ttime between member refresh ops
    """
    return random.randint(30, 60)

def getPersistedString():
    """
    Get persisted string direct from SDB
    """
    return simpledb.getAttribute(ITEMKEY, ATTRIBUTENAME)

def getCurrentMemberDict():
    """
    Get the local member set.
    """
    return members

### Functions ################################################################
def membersRefresh():
    """
    Run members refresh operation
    """
    global members

    try:
        oldKeys = set(members.keys())
        for key in members:
            members_to_delete.add(key)
        members.clear()

        newMembersDict = simpledb.getSet(ITEMKEY)
        if (newMembersDict != None) and (len(newMembersDict) > 0):
            #newmembers = joined.split(GLUE)
            for memberUid in newMembersDict:
                if len(memberUid) > 6:
                    memberNode = nodes.buildNode(newMembersDict[memberUid])
                    if not me.getMe().__eq__(memberNode):
                        result = True # TODO Really should send a noop.
                        if result:
                            members[memberNode.getUid()] = memberNode
                        else:
                            debug("Noop failed. Node removed.", info=True)
                    else:
                        pass
        members[me.getUid()] = me.getMe().getBaseData()

        for key in members:
            if key in members_to_delete:
                members_to_delete.remove(key)

        debug("Members refresh procedure ran.", success=True)
        debug("There are " + str(len(members)) + " members in the system.", 
            info=True)

        if set(members.keys()) == oldKeys:
            """ We have reached stable state """
            gossip.quitMembersRefresh()
            connections.informAlive()
            
    except Exception as e:
        debug(e)
        traceback.print_exc(file=sys.stdout)

    persistSet()

def persistSet():
    """
    Persist this member set to SimpleDB
    """
    try:
        toWrite = {}
        for member in members:
            toWrite[member] = members[member].getCompressed()
        debug("String to persist built", info=True)
        simpledb.putSet(ITEMKEY, toWrite)
        if len(members_to_delete) > 0:
            simpledb.deleteSet(ITEMKEY, members_to_delete)
            debug("DELETing members", info=True)
        debug("Member set persisted correctly", success=True)

    except Exception as e:
        debug(e)
        traceback.print_exc(file=sys.stdout)
