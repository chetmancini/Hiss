# Hiss
=============================================================================
Gossip with Python on Twisted

                    __  ___     
                   / / / (_)_________      
                  / /_/ / / ___/ ___/   
                 / __  / (__  |__  )     
                /_/ /_/_/____/____/        Gossip with Python on Twisted

## Version

- Version 0.0.1

## What is it?
Hiss is a gossip-driven distributed application framework using the popular asynchronous Python networking library, Twisted. Gossip is a network communication protocol used between nodes in a distributed system. There exist other gossip systems, but as of spring 2023 there was no robust open source Python implementation. Hiss is a straightforward framework to allow the developer to write a linearly scalable distributed application and not worry about inter-node communication. One may create a message with any sort of information, specify an action upon receipt, and simply call "send()." This message will be propogated throughout the system in logarithmic time.

Hiss offers many other features one might expect in a complete framework such as this. It can perform aggregations, and several sample aggregations for network and node system load are provided out of the box.

Hiss also offers a choice of network topologies, as well as the ability to define new ones. The type of gossip performed may differ between environments--perhaps one implementation is within the same datacenter with a bounded number of nodes, trying to optimize for performance, and perhaps another has a variety of connections and needs to support a large number of nodes.

Hiss is very much a work in progress and is only past the "floor demo" stage. Fork requests are appreciated!

## Dependencies
### Requried Python Packages:

- twisted (for network infrastructure)
- boto (for Amazon Web Services)
- psutil (for server statistics)
- networkx (for visualization)

### Potential Python Packages:

- txLoadBalancer (for load balancing)

## Author
Chet Mancini

- cam479 at cornell dot edu
- http://chetmancini.com

## Legal

- License: MIT
- Warranty: None of any kind

## Installation
Put files in directory

## Instructions
Execute:

```
    $ python launch.py

    Command line arguments:
    -h                  Print help
    --version           Print version
    --port              Hiss port
    --interval          Gossip interval (seconds)
    --iface             Interface (default localhost)
```

## Changelog
* 08/25/2012 Cleaned out most of the old code from school project.
