#----------------------------------------------------------------------------#
# me.py                                                                      #
# Super access to me.                                                        #
#----------------------------------------------------------------------------#

### Imports ##################################################################
# Python Library Imports

# External Library Imports

# Local Imports

### Variables ################################################################
me = None

### Functions ################################################################
def init(node):
    """
    Initialize me with a new node.
    """
    global me
    me = node

def getUid():
    """
    convenience method to get the uid in hex of this node.
    """
    if me:
        return me.getUid()
    else:
        return None

def getMe():
    """
    Getter function for this node.
    """
    return me
