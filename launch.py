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
import argparse
import sys
import traceback

# External Library Imports
from twisted.internet import reactor

# Local Imports
import aggregation
import gossip
import config
import logger
import connections
from debug import debug

### Classes ##################################################################
class Args(object):
    """
    Hold arguments
    """
    pass

### Functions ################################################################
def parse_args():
    """
    Parse command line arguments
    --port
    --logport
    --interval
    --iface
    --version
    """
    arguments = Args()

    parser = argparse.ArgumentParser(
        description="-------------- Hiss Settings --------------------",
        epilog="--------------------------------------------------")

    parser.add_argument('--port', 
        default=config.DEFAULT_RECEIVE_PORT, 
        type=int,
        help='The port for the gossip system to listen on. \
            (Integer, default: %(default)s)')

    parser.add_argument('--sendport',
        default=config.DEFAULT_SEND_PORT,
        type=int,
        help='the port for the gossip system to send on \
            (Integer, default %(default)s)')

    parser.add_argument('--interval', 
        default=config.DEFAULT_GOSSIP_WAIT_SECONDS, 
        type=int,
        help='The interval to send gossip messages. \
            (Integer, default: %(default)s)')

    parser.add_argument('--iface', 
        default='localhost',
        help='The interface to communicate on. \
            (String, default: %(default)s)')

    parser.add_argument('--version', 
        action='version', 
        version=timber.__version__,
        help='Report system version.')

    parser.parse_args(namespace=arguments)
    return arguments

def applyArgs(namespace):
    """
    Apply the arguments to the config file
    """
    config.RECEIVE_PORT = namespace.port
    config.SEND_PORT = namespace.sendport
    config.GOSSIP_WAIT_SECONDS = namespace.interval
    config.INTERFACE = namespace.iface


### Main #####################################################################
def main():
    """
    In seperate method so it can be called from other modules.
    """
    args = parse_args()
    applyArgs(args)

    connections.init()
    aggregation.stats_init()
    reactor.run()

if __name__ == "__main__":
    main()
