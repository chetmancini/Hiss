##############################################################################
#        __  ___                                                             #
#       / / / (_)_________                                                   #
#      / /_/ / / ___/ ___/                                                   #
#     / __  / (__  |__  )                                                    #
#    /_/ /_/_/____/____/        Gossip with Python on Twisted                #
#                                                                            #
##############################################################################

### Imports ##################################################################
import sys
import os
import subprocess


### Functions ################################################################
def doHelp():
    """
    Show a help menu.
    """
    print "'help', 'kill', 'new', 'exit'"

def doExit():
    """
    Exit the applicaiton
    """
    print "Exiting"
    sys.exit()

def doKill():
    """
    Kill a node in the demo app (watches for kill file)
    """
    path = os.path.abspath('./kill')
    open(path, 'w').close()
    print "Executing kill node request to demo app."

def doNew():
    """
    Create a node in the demo app (watches for new file)
    """
    path = os.path.abspath('./new')
    open(path, 'w').close()
    print "Executing new node request to demo app"

### Main #####################################################################
if __name__ == "__main__":

    while True:
        inputstr = raw_input("Enter a command ('help'):")

        if inputstr == 'help':
            doHelp()
        elif inputstr == 'kill':
            doKill()
        elif inputstr == 'new':
            doNew()
        elif inputstr == 'exit':
            doExit()
