##############################################################################
#        __  ___                                                             #
#       / / / (_)_________                                                   #
#      / /_/ / / ___/ ___/                                                   #
#     / __  / (__  |__  )                                                    #
#    /_/ /_/_/____/____/        Gossip with Python on Twisted                #
#                                                                            #
##############################################################################

#----------------------------------------------------------------------------#
# Aggregation.py                                                             #
#----------------------------------------------------------------------------#

### Imports ##################################################################
# Python Library imports
from __future__ import division
import time
import copy
import random

# External library imports
import psutil
import zope.interface

# Local imports
import me
import config
import connections
import stats

### Interfaces ###############################################################
class IAggregator(zope.interface.Interface):
    """
    IAggregation
    """

    def reduce(other):
        """
        Reduce from another object value.
        """

    def getValue():
        """
        Get the value of this aggregator
        """

    def getLocalValue():
        """
        Get the local value of the stat at this node.
        """

    def getStatistic():
        """
        Get this as a dictionary.
        """

class INamedAggregator(zope.interface.Interface):
    """
    Interface for aggregators with name.
    """

    def getName():
        """
        Get the name of this aggregator
        """

    def reduce(other):
        """
        Reduce from another object value.
        """

    def getValue():
        """
        get the value of this aggregator
        """

    def getLocalValue():
        """
        Get the local value of this stat at this node.
        """

    def getStatistic():
        """
        Get this as a dictionary.
        """

### Classes ##################################################################
class Aggregator(object):
    """
    AGGREGATOR. ABSTRACT CLASS
    ValueAggegation. Do not instanciate
    """

    zope.interface.implements(IAggregator)

    def __init__(self, statistic=None):
        """
        Constructor
        """
        self._key = me.getMe().getUid()
        self._statistic_function = statistic
        if statistic:
            self._value = self._statistic_function()
        else:
            self._value = None

    def getKey(self):
        """
        Return the key of the aggregation. This is usually a node's UID.
        """
        return self._key

    def getValue(self):
        """
        Return the value of the aggregation. 
        This is the value associated with that UID.
        """
        return self._value

    def reduce(self, other):
        """
        Reduce from another object value. 
        For example it might keep a Max by comparing
        successive reduced values.
        """
        pass #retain by default. subclass and override to implement.

    def refresh(self):
        """
        Refresh statistic from the current node to keep it updated.
        """
        tojoin = Aggregator(self._statistic_function)
        self.reduce(tojoin)

    def getLocalValue(self):
        """
        Get the local value of at this node of the given
        statistic.
        """
        return self._statistic_function()

    def getStatistic(self):
        """
        Get this stat as a dictionary.
        """
        toReturn = {}
        toReturn['key'] = self._key
        toReturn['value'] = self._value
        return toReturn

class NamedAggregator(Aggregator):
    """
    NAMED AGGREGATOR (SUPER CLASS)
    An aggregator with a name
    """
    zope.interface.implements(INamedAggregator)

    def __init__(self, name, statistic=None):
        """
        Constructor
        """
        super(NamedAggregator, self).__init__(statistic)
        self._name = name

    def refresh(self):
        """
        Refresh statistic from the current node to keep it updated.
        """
        tojoin = NamedAggregator(self.getName(), self._statistic_function)
        self.reduce(tojoin)

    def getName(self):
        """
        Get the name
        """
        return self._name

    def getStatistic(self):
        """
        Get as a dictionary
        """
        toReturn = super(NamedAggregator, self).getStatistic()
        toReturn['name'] = self._name
        return toReturn

class AverageAggregator(NamedAggregator):
    """
    AVERAGE AGGREGATOR
    Aggregator that keeps an average of a value.
    """

    def __init__(self, name, statistic=None):
        """
        Constructor
        """
        super(AverageAggregator, self).__init__(name, statistic)
        self._interval = random.randint(
            config.AGGREGATE_AVERAGE_REFRESH_MIN, 
            config.AGGREGATE_AVERAGE_REFRESH_MAX)
        self._counter = 0

    def refresh(self):
        """
        Refresh on a certain interval.
        """
        self._counter += 1
        if self._counter == self._interval:
            self._value = self.getLocalValue()
        else:
            pass

    def reduce(self, other):
        """
        Reduce from a received message.
        When we combine two the variance of the system converges
        to zero.
        """
        if self.getName() == other.getName():
            self._value = ((self.getValue() + other.getValue()) / 2)
            return self.getValue()
        else:
            error = "Cannot reduce different aggregators: (" + self.getName()
            error += ", " + other.getName() + ")"
            raise error

class SumAggregator(NamedAggregator):

    def __init__(self, name, statistic=None):
        """
        Constructor
        This might be a little tricky since a SUM is really
        just an average multiplied by the total node count.
        """

    def reduce(self, other):
        """
        reduce from a received message
        """
        pass


class MinAggregator(NamedAggregator):
    """
    MINIMUM AGGREGATOR
    Aggregator that keeps a reference to the minimum
    """

    def __init__(self, name, statistic=None):
        """
        Constructor
        """
        super(MinAggregator, self).__init__(name, statistic)

    def reduce(self, other):
        """
        Reduce to keep a minimum value and its key
        """
        if self.getName() == other.getName():
            if other.getValue() < self.getValue():
                self._value = other.getValue()
                self._key = other.getKey()
            return self.getValue()
        else:
            error = "Cannot reduce different aggregators: (" + self.getName()
            error += ", " + other.getName() + ")"
            raise error

class MaxAggregator(NamedAggregator):
    """
    MAXIMUM AGGREGATOR
    Aggregator that keeps a reference to the maximum value.
    """

    def __init__(self, name, statistic=None):
        """
        Constructor for MaxAggregator
        """
        super(MaxAggregator, self).__init__(name, statistic)

    def reduce(self, other):
        """
        Combine to keep a maximum value and its key
        """
        if self.getName() == other.getName():
            if other.getValue > self.getValue():
                self._value = other.getValue()
                self._key = other.getKey()
            return self.getValue()
        else:
            error = "Cannot reduce different aggregators: (" + self.getName()
            error += ", " + other.getName() + ")"
            raise error


class MinMaxAggregator(object):
    """
    MinMaxAggregator is a wrapper class for two related values
    so that min and max of the same statistic can be more easily
    tracked.
    """

    zope.interface.implements(INamedAggregator)

    def __init__(self, name, statistic):
        """
        Constructor
        """
        self._max = MaxAggregator(name, statistic)
        self._min = MinAggregator(name, statistic)
        self._name = name
        self._statistic_function = statistic

    def getName(self):
        """
        Get the name of the statistic that MinMaxAggregator holds.
        """
        return self._name

    def getMaxAggregator(self):
        """
        Getter for the max
        """
        return self._max

    def getMinAggregator(self):
        """
        Getter for the min
        """
        return self._min

    def reduce(self, other):
        """
        Combine the two.
        """
        assert other.__class__.__name__ == "MinMaxAggregator"
        self._max.reduce(other.getMaxAggregator())
        self._min.reduce(other.getMinAggregator())

    def refresh(self):
        """
        Refresh from local node.
        """
        self._max.refresh()
        self._min.refresh()

    def getValue(self):
        """
        Get the value of this aggregator (do nothing).
        """
        return None

    def getStatistic(self):
        ret = {}
        ret['min'] = self.getMinAggregator().getStatistic()
        ret['max'] = self.getMaxAggregator().getStatistic()
        return ret

    def localValue(self):
        """
        Return the statistic local to this node.
        """
        return self._statistic_function()


class MinMaxAverageAggregator(MinMaxAggregator):
    """
    Larger aggregator that measures Min, Max, and Sum
    """
    def __init__(self, name, statistic):
        """
        Constructor
        """
        super(MinMaxAverageAggregator, self).__init__(name, statistic)
        self._average = AverageAggregator(name, statistic)

    def getAverageAggregator(self):
        """
        Get the aggregator for the average
        """
        return self._average

    def reduce(self, other):
        """
        Combine the two.
        """
        assert other.__class__.__name__ == "MinMaxAverageAggregator"
        super(MinMaxAverageAggregator, self).reduce(other)
        self._avg.reduce(other.getAverageAggregator())

    def refresh(self):
        """
        Refresh from the local system
        """
        super(MinMaxAverageAggregator, self).refresh()
        self._average.refresh()

    def getStatistic(self):
        """
        Get the full statistic for thsi aggregator
        """
        ret = super(MinMaxAverageAggregator, self).getStatistic()
        ret['avg'] = self.getAverageAggregator().getStatistic()
        return ret

class MinMaxAverageSumAggregator(MinMaxAverageAggregator):
    """
    MINIMUM + MAXIMUM + AVERAGE + SUM
    super aggregator that measures four different values.
    """ 

    def __init__(self, name, statistic):
        """
        Constructor
        """
        super(MinMaxAverageSumAggregator, self).__init__(name, statistic)
        self._nodecount = len(connections.universe)

    def refresh(self):
        """
        Refresh from the local machine/sensor
        """
        super(MinMaxAverageSumAggregator, self).refresh()
        self._nodecount = len(connections.universe)

    def reduce(self, other):
        """
        Reduce from a received message.
        """
        assert other.__class__.__name__ == "MinMaxAverageSumAggregator"
        super(MinMaxAverageSumAggregator, self).reduce(other)

    def getStatistic(self):
        """
        Get the full statistic for this aggregator
        """
        ret = super(MinMaxAverageSumAggregator, self).getStatistic()
        ret['sum'] = {}
        ret['sum']['name'] = ret['avg']['name']
        ret['sum']['value'] = ret['avg']['value'] * self._nodecount
        return ret


class UpdateAggregator(NamedAggregator):
    """
    Update a value based on vector clock
    """

    def __init__(self, name, statistic, vectorClock=None):
        """
        Constructor
        """
        super(UpdateAggregator, self).__init__(name, statistic)
        if vectorClock:
            self._vectorClock = copy.deepcopy(vectorClock)
        else:
            self._vectorClock = copy.deepcopy(
                me.getMe().getVectorClock())


    def getVectorClock(self):
        """
        Get the vector clock
        """
        return self._vectorClock

    def setVectorClock(self, vectorClock):
        """
        Set the vector clock
        """
        self._vectorClock = copy.deepcopy(vectorClock)

    def reduce(self, other):
        """
        Only merge in value if other came later.
        """
        if self.getVectorClock().cameBefore(other.getVectorClock()):
            self._key = other.getKey()
            self._value = other.getValue()
            self.getVectorClock().mergeClocks(other)
        else:
            pass #irrelevant.

    def refresh(self):
        """
        Refresh value from the statistic function.
        (only if the current vector clock is late)
        """
        if me.getMe().getVectorClock().cameAfter(
            self.getVectorClock()):
            self._key = me.getMe().getUid()
            self._value = self._statistic_function()
        else:
            pass # not relevant


### Globals ##################################################################

STATISTICS = {}
"""
These are stats we would like to be accessible in the system
"""

### Functions ################################################################

def stats_init():
    global STATISTICS

    DISK_AVAILABLE = MinMaxAverageSumAggregator(
        'diskavailable', stats.disk_free)

    NETWORK_LOAD = MinMaxAverageAggregator(
        'networkload', stats.network_load_single_stat)

    DISK_LOAD = MinMaxAverageAggregator(
        'diskload', stats.disk_load_single_stat)

    CPU_LOAD = MinMaxAverageAggregator(
        'cpuload', stats.cpu_utilization)

    CPU_COUNT = MinMaxAverageSumAggregator(
        'cpucount', stats.cpu_count)

    PMEM_AVAILABLE = MinMaxAverageSumAggregator(
        'pmemavailable', stats.physical_mem_free)

    NODE_COUNT = UpdateAggregator(
        'nodecount', stats.timber_node_count)

    STATISTICS = {
        'diskavailable': DISK_AVAILABLE, 
        'networkload': NETWORK_LOAD, 
        'diskload': DISK_LOAD,
        'cpuload': CPU_LOAD,
        'cpucount': CPU_COUNT,
        'pmemavailable': PMEM_AVAILABLE, 
        'nodecount': NODE_COUNT, 
        'logcount':LOG_COUNT
        }

def getAggregation(name, local=False, minOnly=False, maxOnly=False):
    """
    Get aggregation.
    """
    toReturn = STATISTICS[name].getStatistic()
    if local:
        return STATISTICS[name].getLocalValue()
    elif minOnly and "min" in toReturn:
        return toReturn["min"]
    elif maxOnly and "max" in toReturn:
        return toReturn["max"]
    else:
        return toReturn

def refreshAll():
    """
    Refresh all the statistics.
    """
    for name in STATISTICS:
        STATISTICS[name].refresh()