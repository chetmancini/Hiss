##############################################################################
#  .___________. __  .___  ___. .______    _______ .______                   #
#  |           ||  | |   \/   | |   _  \  |   ____||   _  \                  #
#  `---|  |----`|  | |  \  /  | |  |_)  | |  |__   |  |_)  |                 #
#      |  |     |  | |  |\/|  | |   _  <  |   __|  |      /                  #
#      |  |     |  | |  |  |  | |  |_)  | |  |____ |  |\  \----.             #
#      |__|     |__| |__|  |__| |______/  |_______|| _| `._____|             #
#                                                                            #
##############################################################################

#----------------------------------------------------------------------------#
# request_generator.py                                                       #
#----------------------------------------------------------------------------#

### Imports ##################################################################
import httplib
import urllib
import multiprocessing
import threading
import argparse
import time

### Parameters ###############################################################
args = None

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
        description="---------Timber Load Tester Settings -------------",
        epilog="-------------------------------------------------")

    parser.add_argument('--infinity', 
        default=False, 
        type=bool, 
        help='Run forever')

    parser.add_argument('--interval',
        default=.5,
        type=int,
        help='time between requests')

    parser.add_argument('--host',
        default='127.0.0.1',
        type=str,
        help='host address')

    parser.add_argument('--port',
        default='8101',
        type=int,
        help='host port')

    parser.add_argument('--threads',
        default=10,
        type=int,
        help='number of threads to use')

    parser.add_argument('--requests',
        default=100,
        type=int,
        help='number of requests to generate PER THREAD')

    parser.add_argument('--timeout',
        default=10,
        type=int,
        help='seconds before connection timeout')

    parser.add_argument('--verbose',
        default=True,
        type=bool,
        help='whether to print out the response data.')

    parser.parse_args(namespace=arguments)
    return arguments

def executeRequest(connection):
    params = {
        'message': 'message I want to log', 
        'level': 5, 
        'type': 'info'
        }
    headers = {
        "Content-type": "application/x-www-form-urlencoded", 
        "Accept": "text/plain"
        }
    connection.request("POST", "", urllib.urlencode(params), headers)
    response = connection.getresponse()
    if args.verbose:
        print "Status",response.status
        print "Reason",response.reason
        print "Data",response.read()

def createConnection():
    return httplib.HTTPConnection(args.host, args.port, timeout=args.timeout)

def threadExecute():
    try:
        connection = createConnection()
        for i in range(args.requests):
            executeRequest(connection)
            time.sleep(args.interval)
        connection.close()
    except Exception as e:
        if args.verbose:
            print e

### Main #####################################################################
if __name__ == "__main__":
    """
    Main function to run
    """
    global args
    args = parse_args()

    pool = multiprocessing.Pool(None)

    threads = []
    for i in range(args.threads):
        nextthread = threading.Thread(
            None, threadExecute, "thread"+str(i), (), {})
        threads.append(nextthread)
        nextthread.start()
        time.sleep(1)