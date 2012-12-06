##############################################################################
#        __  ___                                                             #
#       / / / (_)_________                                                   #
#      / /_/ / / ___/ ___/                                                   #
#     / __  / (__  |__  )                                                    #
#    /_/ /_/_/____/____/        Gossip with Python on Twisted                #
#                                                                            #
##############################################################################

#----------------------------------------------------------------------------#
# stats_poll2.py                                                             #
#----------------------------------------------------------------------------#

### Imports ##################################################################
# Python Library Imports
import time
import argparse

# External Library Imports
import requests

### Classes ##################################################################
class Args(object):
    """
    Holds arguments
    """
    pass

### Functions ################################################################
def parse_args():
    """
    Parse command line arguments
    """
    arguments = Args()
    parser = argparse.ArgumentParser(
        description="------------Stat Poll Settings ----------------",
        epilog="------------------------------------------------")

    parser.add_argument('--stat',
        default='all',
        type=str,
        help='which statistic to poll')

    parser.add_argument('--infinity', 
        default=False, 
        type=bool, 
        help='Run forever')

    parser.add_argument('--host',
        default='127.0.0.1',
        type=str,
        help='host address')

    parser.add_argument('--port',
        default='8121',
        type=int,
        help='host port')

    parser.add_argument('--interval',
        default=10,
        type=int,
        help='the interval to poll for statistics')

    parser.parse_args(namespace=arguments)
    return arguments

def buildUrl(host, port):
    """
    Construct a url
    """
    return "".join(["http://", host, ":", str(port), "/stats"])

### Main #####################################################################
if __name__ == "__main__":
    """
    Main function to run
    """
    args = parse_args()

    if args.infinity:
        while True:
            payload = {'name': args.stat}
            r = requests.get(buildUrl(args.host, args.port), params=payload)
            print r.text
            time.sleep(args.interval)
    else:
        payload = {'name': args.stat}
        r = requests.get(buildUrl(args.host, args.port), params=payload)
        print r.text
