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
import random

# External Library Imports
import zope.interface

# Local Imports
import me
import connections


### Interfaces ###############################################################
class INeighborStrategy(zope.interface.Interface):
    """
    Neighbor strategy interface.
    """

    def getNeighbors():
        """
        Get the neighbors of this node.
        """

### Classes ##################################################################
class BaseNeighborStrategy(object):
    """
    Base Class for Neighbor Strategies
    """

    zope.interface.implements(INeighborStrategy)

    def __init__(self):
        """
        Constructor
        """
        self.neighborSet = set([])
        self.removedSet = set([])

    def getNeighbors(self):
        """
        Get neighbors
        """
        pass

    def removeNeighbor(self, uid):
        self.removedSet.add(uid)
        if uid in self.neighborSet:
            self.neighborSet.remove(uid)
        return self.neighborSet

    def isNeighbor(self, uid):
        return uid in self.neighborSet

    def _universeUids(self):
        """
        Helper method to get uids.
        """
        return sorted(connections.universe.keys())

class DefaultNeighborStrategy(BaseNeighborStrategy):

    def __init__(self):
        """
        Constructor
        """
        super(DefaultNeighborStrategy, self).__init__()
        self.count = 2

    def getNeighbors(self):
        """
        Get Neighbors
        """
        unilength = len(self._universeUids())
        if unilength > 2:
            if not self.count:
                idealcount = int(math.ceil(math.log10(unilength)))
                self.count = max(2, idealcount)
            samplespace = self._universeUids()
            if me.getUid() in samplespace:
                samplespace.remove(me.getMe().getUid())
            self.neighborSet = random.sample(samplespace, self.count)
            return set(self.neighborSet)
        else:
            return set([])


class RandomNeighborStrategy(BaseNeighborStrategy):
    """
    Class to pick neighbors at random (every time)
    Can result in a lot of open TCP connections.
    """

    def __init__(self):
        """
        Constructor
        """
        super(RandomNeighborStrategy, self).__init__()

    def getNeighbors(self):
        """
        Get random neighbors.
        """
        return None


class AllNeighborStrategoy(BaseNeighborStrategy):
    """
    Avoid. Completely defeats point of gossip! 
    Very effective for small systems though
    """

    def __init__(self):
        """
        Constructor
        """
        super(AllNeighborStrategoy, self).__init__()

    def getNeighbors(self):
        """
        Get all neighbors
        """
        self.neighborSet = self._universeUids()
        return self.neighborSet()

class SingleNeighborStrategy(BaseNeighborStrategy):
    """
    Very slow to propogate information.
    """

    def __init__(self):
        """
        Constructor
        """
        super(SingleNeighborStrategy, self).__init__()

    def getNeighbors(self):
        """
        Get a single neighbor.
        """
        sortedkeys = self._universeUids()
        ix = sortedkeys.index(me.getUid())
        if ix == (len(sortedkeys)-1):
            self.neighborSet = sortedkeys[0]
        else:
            self.neighborSet = sortedkeys[ix+1]
        return self.neighborSet

class LogarithmicNeighborStrategy(BaseNeighborStrategy):
    """
    Return a number of neighbors logarithmic in size of the universe.
    Scales well, but not infinitely.
    """

    def __init__(self, base=10):
        """
        Constructor
        """
        super(LogarithmicNeighborStrategy, self).__init__()
        self._base = base

    def getNeighbors(self):
        """
        Get logarithmic count of neighbors
        """


class ConstantNeighborStrategy(BaseNeighborStrategy):
    """
    Return the same neighbors of constant number. May change
    when nodes die or leave system.
    """

    def __init__(self, count):
        """
        Constructor
        """
        super(ConstantNeighborStrategy, self).__init()
        self._count = count
        self.neighborSet = set([])

    def getNeighbors(self):
        """
        Get constant set of neighbors
        """
        return None

### Functions ################################################################
def neighborStrategyFactory(name):
    """
    Factory method.
    """
    if name == "default":
        return DefaultNeighborStrategy()
    elif name == "random":
        return RandomNeighborStrategy()
    elif name == "all":
        return AllNeighborStrategoy()
    elif name == "single":
        return SingleNeighborStrategy()
    elif name == "logarithmic":
        return LogarithmicNeighborStrategy()
    elif name == "constant":
        return ConstantNeighborStrategy()
    else:
        return None