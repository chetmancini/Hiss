##############################################################################
#        __  ___                                                             #
#       / / / (_)_________                                                   #
#      / /_/ / / ___/ ___/                                                   #
#     / __  / (__  |__  )                                                    #
#    /_/ /_/_/____/____/        Gossip with Python on Twisted                #
#                                                                            #
##############################################################################

#----------------------------------------------------------------------------#
# aggregation_test.py                                                        #
#----------------------------------------------------------------------------#

### Imports ##################################################################
# Python Library Imports
import unittest

# Local Imports
import Hiss.hiss.aggregation

### Test Classes #############################################################

class TestFunctions(unittest.TestCase):
    """
    Test the functions
    """

    def setUp(self):
        pass

    def test_stats_init(self):
        pass

    def test_getAggregation(self):
        pass

    def test_refreshAll(self):
        pass

class TestAggregator(unittest.TestCase):

    def setUp(self):
        pass

    def test_getKey(self):
        pass

    def test_getValue(self):
        pass

    def refresh(self):
        pass

    def getLocalValue(self):
        pass

    def getStatistic(self):
        pass


class TestNamedAggregator(unittest.TestCase):

    def setUp(self):
        pass

    def test_refresh(self):
        pass

    def test_getName(self):
        pass

    def test_getStatistic(self):
        pass    

class TestAverageAggregator(unittest.TestCase):

    def test_refresh(self):
        pass

    def test_reduce(self, other):
        pass

class TestSumAggregator(unittest.TestCase):

    def test_reduce(self):
        pass

class TestMinAggregator(unittest.TestCase):

    def test_reduce(self):
        pass

class TestMaxAggregator(unittest.TestCase):

    def test_reduce(self):
        pass

class TestMinMaxAggregator(unittest.TestCase):

    def test_getName(self):
        pass

    def test_getMaxAggregator(self):
        pass

    def test_getMinAggregator(self):
        pass

    def test_reduce(self, other):
        pass

    def test_refresh(self):
        pass

    def test_getValue(self):
        pass

    def test_getStatistic(self):
        pass

    def test_localValue(self):
        pass

class TestMinMaxAverageAggregator(unittest.TestCase):
    def test_getAverageAggregator(self):
        pass

    def test_reduce(self):
        pass

    def test_refresh(self):
        pass

    def test_getStatistic(self):
        pass

class TestMinMaxAverageSumAggregator(unittest.TestCase):

    def test_refresh(self):
        pass

    def test_reduce(self, other):
        pass

    def test_getStatistic(self):
        pass

class TestUpdateAggregator(unittest.TestCase):

    def test_getVectorClock(self):
        pass

    def test_setVectorClock(self):
        pass

    def test_reduce(self):
        pass

    def test_refresh(self):
        pass


if __name__ == '__main__':
    unittest.main()