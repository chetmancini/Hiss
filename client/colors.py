##############################################################################
#        __  ___                                                             #
#       / / / (_)_________                                                   #
#      / /_/ / / ___/ ___/                                                   #
#     / __  / (__  |__  )                                                    #
#    /_/ /_/_/____/____/        Gossip with Python on Twisted                #
#                                                                            #
##############################################################################

### Imports ##################################################################
import random

### Classes ##################################################################
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

class chetcolors:
    """
    Define colors.
    """
    BLACKFG = '\x1b[30m'
    REDFG = '\x1b[31m'
    GREENFG = '\x1b[32m'
    YELLOWFG = '\x1b[33m'
    BLUEFG = '\x1b[34m'
    MAGENTAFG = '\x1b[35m'
    CYANFG = '\x1b[36m'
    WHITEFG = '\x1b[37m'
    DEFAULTFG = '\x1b[39m'
    fgcolors = [BLACKFG, REDFG, GREENFG, 
        YELLOWFG, BLUEFG, MAGENTAFG, CYANFG, WHITEFG]


    BLACKBG = '\x1b[40m'
    REDBG = '\x1b[41m'
    GREENBG = '\x1b[42m'
    YELLOWBG = '\x1b[43m'
    BLUEBG = '\x1b[44m'
    MAGENTABG = '\x1b[45m'
    CYANBG = '\x1b[46m'
    WHITEBG = '\x1b[47m'
    DEFAULTBG = '\x1b[49m'
    bgcolors = [BLACKBG, REDBG, GREENBG, 
        YELLOWBG, BLUEBG, MAGENTABG, CYANBG, WHITEBG]

    @staticmethod
    def randomFGColor():
        return random.choice(chetcolors.fgcolors)

    @staticmethod
    def randomBGColor():
        return random.choice(chetcolors.bgcolors)
