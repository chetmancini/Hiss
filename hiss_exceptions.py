##############################################################################
#        __  ___                                                             #
#       / / / (_)_________                                                   #
#      / /_/ / / ___/ ___/                                                   #
#     / __  / (__  |__  )                                                    #
#    /_/ /_/_/____/____/        Gossip with Python on Twisted                #
#                                                                            #
##############################################################################

### Imports ##################################################################
import zope.interface

class IError(zope.interface.Interface):
    pass

### Classes ##################################################################
class Error(Exception):
    """
    Base class for exceptions in this module.
    """

    zope.interface.implements(IError)

    def __init__(self, value):
        """
        Constructor
        """
        self._value = value

    def __str__(self):
        """
        Get string representation
        """
        return repr(self._value)

class GeneralError(Error):
    """
    General errors
    """
    def __init__(self, value):
        """
        Constructor
        """
        super(GeneralError, self).__init__(value)

class ConnectionError(Error):
    """
    Connection errors.
    """
    pass

class InvalidPeerIDError(Error):
    """
    Invalid peer id (UID doesnt exist)
    """
    pass

class InvalidAddressError(Error):
    """
    Invalid IP address exception
    """
    pass

class InvalidPortError(Error):
    """
    Invalid port exception
    """
    pass

class UnknownUidError(Error):
    """
    Unknown UID exception
    """
    pass
