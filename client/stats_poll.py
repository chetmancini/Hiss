##############################################################################
#        __  ___                                                             #
#       / / / (_)_________                                                   #
#      / /_/ / / ___/ ___/                                                   #
#     / __  / (__  |__  )                                                    #
#    /_/ /_/_/____/____/        Gossip with Python on Twisted                #
#                                                                            #
##############################################################################

#----------------------------------------------------------------------------#
# stats_poll.py                                                              #
#----------------------------------------------------------------------------#

### Imports ##################################################################
import httplib
import urllib2
import argparse
import time

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
        default='8101',
        type=int,
        help='host port')

    parser.add_argument('--interval',
        default=10,
        type=int,
        help='the interval to poll for statistics')

    parser.parse_args(namespace=arguments)
    return arguments

def buildUrl(host, port, stat):
    """
    Construct a url
    """
    return "".join(["http://", host, ":", str(port), "/stat?name=", stat])

def request(url):
    """
    Make a request
    """
    try:
        with urllib2.urlopen(url) as f:
            print f.read()
            f.close()
    except Exception as e:
        print e


### Main #####################################################################
if __name__ == "__main__":
    """
    Main function to run
    """
    args = parse_args()

    if args.infinity:
        while True:
            request(buildUrl(args.host, args.port, args.stat))
            time.sleep(args.interval)
    else:
        request(buildUrl(args.host, args.port, args.stat))
