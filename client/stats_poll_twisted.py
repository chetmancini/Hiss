##############################################################################
#        __  ___                                                             #
#       / / / (_)_________                                                   #
#      / /_/ / / ___/ ___/                                                   #
#     / __  / (__  |__  )                                                    #
#    /_/ /_/_/____/____/        Gossip with Python on Twisted                #
#                                                                            #
##############################################################################


### Imports ##################################################################
import os
import sys
import argparse
import json
import time
import twisted.internet.protocol
import twisted.internet.reactor
import twisted.web.client
import twisted.web.http_headers

### Constants ################################################################
STATISTICS = []

### Variables ################################################################
count = 10

### Arguments ################################################################
 
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
        description="------------Timber/Hiss Settings ----------------",
        epilog="-------------------------------------------------")

    parser.add_argument('--stat',
        default='all',
        type=str,
        help='which statistic to poll')

    parser.add_argument('--infinity', 
        default=True, 
        type=bool, 
        help='Run forever')

    parser.add_argument('--delay',
        default=5,
        type=int,
        help='time between requests')

    parser.add_argument('--host',
        default='127.0.0.1',
        type=str,
        help='host address')

    parser.add_argument('--port',
        default='8080',
        type=int,
        help='host port')

    parser.parse_args(namespace=arguments)
    return arguments

def poll(name, host='127.0.0.1', port=8090):
    """
    Poll for a specific statistic.
    """
    print "starting to poll",host + ":" + str(port), "with name",name
    agent = twisted.web.client.Agent(twisted.internet.reactor)

    d = agent.request(
        'GET',
        'http://' + host + ":" + str(port) + "/stat?name=" + name,
        twisted.web.http_headers.Headers(
            {'User-Agent': ['Twisted Web Client Example'],
             'Content-Type': ['text/json']
             }),
            data)

    def cbShutdown(ignored):
        twisted.internet.reactor.stop()

    def cbResponse(ignored):
        global count
        print 'Response received'
        count += 1
        agent = twisted.web.client.agent(twisted.internet.reactor)
        d = agent.request(
            'GET',
            'http://' + host + ":" + str(port) + "/stat",
            twisted.web.http_headers.Headers(
                {'User-Agent': ['Twisted Web Client Example'],
                'Content-Type': ['text/json']
                }),
                data)
        d.addCallback(cbResponse)
        d.addBoth(cbShutdown)
        
    d.addCallback(cbResponse)
    d.addBoth(cbShutdown)


### Main #####################################################################
if __name__ == "__main__":
    """
    Main
    """
    args = parse_args()
    poll('pmemavailable')
    """
    while True:

        if args.stat == 'all':
            for stat in STATISTICS:
                poll(stat)
        elif args.stat == 'input':
            stat = raw_input(
                "Enter a stat to poll. Choices: " + "|".join(STATISTICS))
            poll(stat.strip())
        else:
            print "got here"
            poll(args.stat.strip())
        
        else:
            exit()
    """
    twisted.internet.reactor.run()