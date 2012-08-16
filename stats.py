#----------------------------------------------------------------------------#
# stats.py                                                                   #
# Statistics module                                                          #
#----------------------------------------------------------------------------#

### Imports ##################################################################
# Python Library imports
from __future__ import division
import os
import random
import platform
import ctypes
import math

# External Library Imports
import psutil

# Local Imports
import config
import me
import connections
from debug import debug

### Global Node Variables ####################################################
p = psutil.Process(os.getpid())

timber_io_stat = p.get_io_counters()
disk_io_stat = psutil.disk_io_counters()
network_io_stat = psutil.network_io_counters()

### Functions ################################################################
def freespace():
    """ 
    Return folder/drive free space (in bytes)
    """
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(
            ctypes.c_wchar_p(folder), 
            None, 
            None, 
            ctypes.pointer(free_bytes))
        return free_bytes.value
    else:
        st = os.statvfs(os.path.abspath("README.txt"))
        return st.f_bfree * st.f_bsize

### Stats for Current Node (requires psutil) #################################

def init_stats():
    """
    Initialization for stats. Not used currently
    """
    global p
    global timber_io_stat
    global disk_io_stat
    global network_io_stat

    p = psutil.Process(os.getpid())
    timber_io_stat = p.get_io_counters()
    disk_io_stat = psutil.disk_io_counters()
    network_io_stat = psutil.network_io_counters()

# Physical RAM #
def physical_mem_size():
    """
    Return the amount of total physical memory, in bytes.
    """
    return psutil.TOTAL_PHYMEM

def physical_mem_percent():
    """
    Return the percentage of physical memory in use. This might give an idea
    to performance.
    """
    return psutil.phymem_usage().percent

def physical_mem_free():
    """
    Return the amount of physical memory available, in bytes.
    """
    return psutil.phymem_usage().free

def physical_mem_used():
    """
    Return the amount of physical memory in use on this node.
    """
    return psutil.phymem_usage().used

# Virtual RAM #
def virtual_mem_percent():
    """
    Return the percentage of virtual memory used.
    """
    return psutil.virtmem_usage().percent

def virtual_mem_free():
    """
    Return the amount of virtual memory available to the node, in bytes.
    """
    return psutil.virtmem_usage().free

def virtual_mem_used():
    """
    Return the amount of virtual memory used on this node, in bytes.
    """
    return psutil.virtmem_usage().used

def virtual_mem_size():
    """
    Return the total amount of virtual memory available on the system.
    """
    return psutil.virtmem_usage().total

# Total RAM #
def total_mem_free():
    """
    Return the total memory available (physical and virtual)
    """
    return virtual_mem_free() + physical_mem_free()

def total_mem_used():
    """
    Return the total memory used (physical and virtual)
    """
    return virtual_mem_used() + physical_mem_used()

def total_mem_size():
    """
    Return all the memory in the system
    """
    return virtual_mem_size() + physical_mem_size()

# CPU #
def cpu_count():
    """
    Return the number of CPUs on this node.
    """
    return psutil.NUM_CPUS

def cpu_utilization():
    """
    Return the CPU utilization on this node. Helpful to see if there's a
    processor bottleneck.
    """
    return psutil.cpu_percent(interval=.1)

def cpu_pid_list():
    """
    Return a list of running process pids.
    """
    return psutil.get_pid_list()

def cpu_pid_count():
    """
    Return the number of running processes on this node.
    """
    return len(psutil.get_pid_list())

# Disk #
def disk_total():
    """
    Return the total size of peristant (or soft state in cloud environments)
    on this node, in bytes.
    """
    return psutil.disk_usage('/').total

def disk_used():
    """
    Return the number of bytes used on peristant/softstate storage.
    """
    return psutil.disk_usage('/').used

def disk_free():
    """
    Return the number of bytes available on this node's persistant storage
    """
    return psutil.disk_usage('/').free

def disk_percent():
    """
    Return the percentage of persistant storage in use.
    """
    return psutil.disk_usage('/').percent

def disk_load():
    """
    Return a 6-tuple of statistics relating to the disk usage between calls
    of this function.
    """
    global disk_io_stat
    try:
        new_stat = psutil.disk_io_counters()

        readCount = new_stat.read_count - disk_io_stat.read_count
        writeCount = new_stat.write_count - disk_io_stat.write_count
        readBytes = new_stat.read_bytes - disk_io_stat.read_bytes
        writeBytes = new_stat.write_bytes - disk_io_stat.write_bytes
        readTime = new_stat.read_time - disk_io_stat.read_time
        writeTime = new_stat.write_time - disk_io_stat.write_time

        disk_io_stat = new_stat
        return readCount,writeCount,readBytes,writeBytes,readTime,writeTime
    except Exception as e:
        debug(e)
        debug("Disk load data pull failed", error=True)

def disk_load_single_stat():
    """
    Give back a single number to represent disk load.
    """
    readCount,writeCount,readBytes,writeBytes,readTime,writeTime = disk_load()
    return writeCount + (readCount / 2)

# Network #
def network_connections():
    """
    Reutnra list of all the network connections.
    """
    return psutil.get_connections(kind='inet')

def network_connection_count():
    """
    Return the number of open network connections
    """
    return len(network_connections())

def network_load():
    """
    Return a 4-tuple describing data about network load and usage measured as
    between calls of this function.
    """
    global network_io_stat
    try:
        new_stat = psutil.network_io_counters()

        receivedPackets = new_stat.packets_recv - network_io_stat.packets_recv
        sentPackets = new_stat.packets_sent - network_io_stat.packets_sent
        receivedBytes = new_stat.bytes_recv - network_io_stat.bytes_recv
        sentBytes = new_stat.bytes_sent - network_io_stat.bytes_sent

        network_io_stat = new_stat #apply new values
        return receivedPackets,sentPackets,receivedBytes,receivedPackets
    except Exception as e:
        debug(e)
        debug("Network load data pull failed", error=True)

def network_load_single_stat():
    """
    Give back a single number to represent network load.
    """
    receivedPackets,sentPackets,receivedBytes,sentBytes = network_load()

    debug("Load#"+me.getUid()+"#"+str(receivedPackets+sentPackets), 
        monitor=True)
    
    return receivedBytes + sentBytes


def averagePacketSize():
    """
    Return the average packet size from this node in the system.
    """
    receivedPackets,sentPackets,receivedBytes,receivedPackets = network_load()
    return math.ceil(
        (receivedBytes + sentBytes) / (receivedPackets + sentPackets))


# Application & Process #
def timber_thread_count():
    """
    Return the number of threads in this application
    """
    return p.get_num_threads()

def timber_load():
    """
    Calculate Timber's IO load since the last call
    """
    #io(read_count=454556, write_count=3456, read_bytes=110592, write_bytes=0)
    global timber_io_stat
    try:
        new_stat = p.get_io_counters()
        readCount = new_stat.read_count - timber_io_stat.read_count
        writeCount = new_stat.write_count - timber_io_stat.write_count
        readBytes = new_stat.read_bytes - timber_io_stat.read_bytes
        writeBytes = new_stat.write_bytes - timber_io_stat.write_bytes

        timber_io_stat = new_stat

        return readCount,writeCount,readBytes,writeBytes
    except Exception as e:
        debug(e)
        debug("Timber load data pulled failed", error=True)

def timber_node_count():
    """
    The number of nodes this thinks are in the system
    """
    return len(connections.universe)
