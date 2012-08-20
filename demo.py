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
import sys
import os
import subprocess
import argparse
import threading
import time
import fcntl
import select
import random
import string

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty

# External Library Imports

# Local Imports
import config
import simpledb

### Constants ################################################################

### Variables ################################################################
nextReceivePort = 0
nextLogPort = 0
nextSendPort = 0

ON_POSIX = 'posix' in sys.builtin_module_names

q = Queue()
qmonitor = Queue()

colordict = {}

processes = []

### Classes ##################################################################
class Args(object):
    """
    Holds arguments
    """
    pass

class ThreadWorker(threading.Thread):
    def __init__(self, callable, *args, **kwargs):
        super(ThreadWorker, self).__init__()
        self.callable = callable
        self.args = args
        self.kwargs = kwargs
        self.setDaemon(True)

    def run(self):
        try:
            self.callable(*self.args, **self.kwargs)
        #except wx.PyDeadObjectError:
        #    pass
        except Exception, e:
            print e

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


### Functions ################################################################
def handleMonitor(line):
    #try new node
    """
    for item in array:
        if item.find("Init called") >= 0:
            elements = item.split(" ")
            for element in elements:
                if len(element) == 32:
                    uid = element.strip()
                    short = array[1].strip()
                    qmonitor.put_nowait("#".join(["New", short, uid]))
    """
    if line.find("MONITOR:") > -1:
        towrite = string.replace(line, "MONITOR: ", "").strip() + "\n"
        qmonitor.put(towrite)
        #print 'putting: "' + towrite + '"'
        return True
    else:
        return False



def handleLine(line, header=False, monitor=False):
    """
    Handle receipt of line.
    """
    if not line or len(line) == 0:
        return
    isSuccess = line[0] == "*"
    isInfo = line[0] == "-"
    isStrange = line[0] == "?"
    isError = line[0] == "!"

    if monitor:
        if handleMonitor(line):
            return

    array = line.split("\t")

    if len(array) < 3:
        print line
        return

    if isSuccess:
        #array[0] = chetcolors.GREENBG + array[0] + chetcolors.DEFAULTBG
        array[0] = bcolors.OKGREEN + array[0] + bcolors.ENDC
        array[2] = bcolors.OKGREEN + array[2] + bcolors.ENDC
    if isError:
        array[0] = bcolors.FAIL + array[0] + bcolors.ENDC
        array[2] = bcolors.FAIL + array[2] + bcolors.ENDC    

    letterCode = array[1].strip()
    if letterCode in colordict:
        color = colordict[letterCode]
    else:
        colordict[letterCode] = chetcolors.randomBGColor()
        color = colordict[letterCode]
    array[1] = color + "  " + array[1] + "  " + chetcolors.DEFAULTBG

    if len(array)>2:
        if string.find(array[2], "[") > 0:

            tagToColor = {}
            for shortCode in colordict:
                tagToColor["[ " + shortCode + " ]"] = "[" \
                    + colordict[shortCode] + " " + shortCode + " " \
                    + chetcolors.DEFAULTBG + "]"

            for tag in tagToColor:
                array[2] = string.replace(array[2], tag, tagToColor[tag])

    print '\t'.join(array)

def make_async(fd):
    fcntl.fcntl(
        fd, 
        fcntl.F_SETFL, 
        fcntl.fcntl(fd, fcntl.F_GETFL) | os.O_NONBLOCK)

def read_async(fd):
    try:
        return fd.read()
    except IOError, e:
        if e.errno != errno.EAGAIN:
            raise e
        else:
            return ''

def getNextReceivePort():
    """
    Get the next receive port
    """
    global nextReceivePort
    ret = nextReceivePort
    nextReceivePort += 1
    return ret

def getNextLogPort():
    """
    Get the next log port
    """
    global nextLogPort
    ret = nextLogPort
    nextLogPort += 1
    return ret

def getNextSendPort():
    """
    Get the next send port
    """
    global nextSendPort
    ret = nextSendPort
    nextSendPort += 1
    return ret

def buildCommandArgs():
    """
    Build a command to execute
    """
    toReturn = ['python', 'launch.py']
    toReturn.extend(['--port', str(getNextReceivePort())])
    toReturn.extend(['--logport', str(getNextLogPort())])
    toReturn.extend(['--interval', str(config.DEFAULT_GOSSIP_WAIT_SECONDS)])
    toReturn.extend(['--sendport', str(getNextSendPort())])
    return toReturn

def readWorker(pipe):
    """
    read worker.
    """
    while True:
        line = pipe.readline()
        if line == '':
            break
        else:
            q.put_nowait(line.strip())

def writeWorker(pipe):
    """
    write worker
    """
    while True:
        line = qmonitor.get(True) #block
        if line:
            #print "FOUND:",line
            pipe.write(line)
            pipe.flush()

def createProcess():
    """
    Create process and return it.
    """
    argList = buildCommandArgs()
    print "Running: ",' '.join(argList)
    process = subprocess.Popen(argList, 
        shell=False, 
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE)
    return process

def killProcess():
    """
    Simulate destroying a process.
    """ 
    procDict = processes.pop()
    procDict['stdout'].join(1)
    procDict['stderr'].join(1)
    procDict['proc'].kill()

def newProcess():
    """
    Simulate creating a new process
    """
    proc = createProcess()
    app = {}
    stdout_worker = ThreadWorker(readWorker, proc.stdout)
    stderr_worker = ThreadWorker(readWorker, proc.stderr)
    stdout_worker.start()
    stderr_worker.start()
    app['proc'] = proc
    app['stdout'] = stdout_worker
    app['stderr'] = stderr_worker
    processes.append(app)


def parse_args():
    """
    Parse command line arguments
    """
    arguments = Args()
    parser = argparse.ArgumentParser(
        description="------------Timber/Hiss Settings ----------------",
        epilog="-------------------------------------------------")

    parser.add_argument('--count', 
        default=3, 
        type=int, 
        help='number of nodes to launch')

    parser.add_argument('--monitor', 
        default=False, 
        type=bool, 
        help='show the monitor')

    parser.parse_args(namespace=arguments)
    return arguments

### Main #####################################################################

if __name__ == "__main__":
    """
    Run demo application.
    """
    nextLogPort = config.DEFAULT_LOG_PORT
    nextReceivePort = config.DEFAULT_RECEIVE_PORT
    nextSendPort = config.DEFAULT_SEND_PORT

    simpledb.deleteAll("members")

    args = parse_args()

    if args.monitor:
        command = 'java -cp ' \
            + './lib/Jung/jung-visualization-2.0.1.jar:' \
            + './lib/collections-generic-4.01.jar:' \
            + './lib/Jung/jung-graph-impl-2.0.1.jar:. ' \
            + 'monitor.TimberMonitor'
        print "Running: ", command
        proc = subprocess.Popen(
            command, 
            shell=True,
            stdin=subprocess.PIPE)
        stdin_worker = ThreadWorker(writeWorker, proc.stdin)
        stdin_worker.start()

    for i in range(args.count):
        next = {}
        proc = createProcess()
        stdout_worker = ThreadWorker(readWorker, proc.stdout)
        stderr_worker = ThreadWorker(readWorker, proc.stderr)
        stdout_worker.start()
        stderr_worker.start()
        next['proc'] = proc
        next['stdout'] = stdout_worker
        next['stderr'] = stderr_worker
        processes.append(next)
        time.sleep(1)

    while True: 
        try:
            line = q.get_nowait()
        except Empty:
            pass
        else:
            handleLine(line, monitor=args.monitor)

        """
        Handle killing and creating nodes on the fly
        through the controller.
        """
        if os.path.exists('./kill'):
            os.unlink('kill')
            killProcess()  
        if os.path.exists('./new'):
            os.unlink('new')
            newProcess()
            
