##############################################################################
#        __  ___                                                             #
#       / / / (_)_________                                                   #
#      / /_/ / / ___/ ___/                                                   #
#     / __  / (__  |__  )                                                    #
#    /_/ /_/_/____/____/        Gossip with Python on Twisted                #
#                                                                            #
##############################################################################

#----------------------------------------------------------------------------#
# debug.py                                                                   #
# Module for debugging. Can be called directly, which compiles everything    #
# and then gives a total line count. Also handles internal printing.         #
#----------------------------------------------------------------------------#

### Imports ##################################################################

# Python Library Imports
import sys
import os
import string
import traceback

# Local Imports
import config
import me

### Constants ################################################################
DEBUG_FLG = True
THRESHOLD = 2 # scale of 1 to 10
INCLUDE_UID = True

### Variables ################################################################
shortUid = None

### Functions ################################################################
def printError(msg):
    """
    Print a message to standard error.
    """
    print >>sys.stderr, str(msg)
    sys.stderr.flush()

def logError(msg):
    """
    Log an error message
    """
    printError(msg)

def printMessage(msg):
    """
    Print a message to standard out
    """
    print >>sys.stdout, str(msg)
    sys.stdout.flush()

def logMessage(msg):
    """
    Log a message. (non error)
    """
    printMessage(msg)

def debug(
    msg, 
    threshold=5, 
    error=False, 
    success=False, 
    info=False, 
    strange=False,
    monitor=False):
    """
    Main debug function.
    """
    global shortUid

    if not shortUid:
        try:
            shortUid = me.getMe().getShortUid()
        except:
            shortUid = ""

    uidstr = (shortUid + "\t") if INCLUDE_UID else ""

    if type(msg) is str:
        if DEBUG_FLG and threshold >= THRESHOLD:
            if error:
                printError("! ERROR:  \t" + uidstr + msg)
            elif success:
                printMessage("* SUCCESS:\t" + uidstr + msg)
            elif info:
                printMessage("- INFO:   \t" + uidstr + msg)
            elif strange:
                printMessage("? STRANGE:\t" + uidstr + msg)
            elif monitor:
                printMessage("MONITOR: " + msg)
            else:
                printMessage(msg)
        else:
            if error and threshold >= THRESHOLD:
                printError("! ERROR:  \t" + uidstr + msg)
    else:
        print "! ERROR:  ", msg
        traceback.print_exc(file=sys.stderr)

def countLinesOfCode(path=".", extension='py'):
    """
    Procedure to count total lines of code in each file
    """
    total = 0
    listing = os.listdir(path)
    for fname in listing:
        if fname[-1*len(extension):] == extension:
            with open(os.path.join(path, fname)) as f:
                for i, l in enumerate(f):
                    if len(l) > 80:
                        print "line " + str(i) + " of " \
                            + fname + " is too long."
                    if l.find("TODO") > -1 and fname != 'debug.py':
                        print "line " + str(i) + " of " \
                            + fname + " has a todo: " + l
            subtotal = i + 1
            print string.rjust(fname, 25) + "\t" + str(subtotal)
            total += subtotal
    print total
    return total

if __name__ == "__main__":
    """
    TEST ALL THE THINGS!!!1!
    """
    import me
    import config
    import launch
    import nodes
    import gossip
    import logger
    import timber_exceptions
    import vectorClock
    import message
    import message_queue
    import membership
    import neighbors
    import simpledb
    import timber
    import stats
    import connections
    import aggregation
    import demo
    import controller


    py = countLinesOfCode('.', 'py')
    client = countLinesOfCode('./client/', 'py')
    jav = countLinesOfCode('monitor/', 'java')
    print 'Total:',str(py+client+jav)
