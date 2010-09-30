#!/usr/bin/python2.4
"""
exportSienaNetworks.py

This program takes all of the output from sienaNetworks and exports it
to a series of RAW files.
"""

import subprocess
import logging
import os
from optparse import OptionParser
import dynet

logging.basicConfig()
log = logging.getLogger("sienaNetworks.py")
log.setLevel(logging.INFO)

DYNETML_EXPORT="/home/pwagstro/usr/bin/dynetml_export"

def processNetworks(files):
    logging.getLogger("isolateRemove.py").setLevel(logging.DEBUG)
    nets = dynet.util.isolateRemoveFiles(files)
    basenames = [os.path.splitext(fn)[0] for fn in files]
    for i in xrange(0,len(files)):
        # if there are no edges, do not process this graph
        if sum([len(x.edges) for x in nets[i].metaMatrix.graphs.values()]) == 0:
            log.debug("Not processing network %s - no edges!", basenames[i])
            continue

        
        # now see about removing nodesets that are not agents
        removeGraphs = []
        for g in nets[i].metaMatrix.graphs.itervalues():
            # if either is not agents, remove them
            if g.sourceType.type != "agent" or g.targetType.type != "agent":
                removeGraphs.append(g)
        removeNodesets = []
        for ns in nets[i].metaMatrix.nodesets.itervalues():
            if ns.type != "agent":
                removeNodesets.append(ns)
        map(nets[i].metaMatrix.removeGraph, removeGraphs)
        map(nets[i].metaMatrix.removeNodeSet, removeNodesets)
        
        fn = basenames[i]+".noisolates.dynetml"
        log.debug("Dumping dynetml to %s", fn)
        nets[i].saveToFile(fn)
        mm = nets[i].metaMatrix
        for gid, graph in mm.graphs.iteritems():
            fn = basenames[i]+".%s.dat" % gid
            log.debug("Dumping raw graph to %s",fn)
            f = open(fn, "w")
            graph.dumpRaw(f)
            f.close()
            log.debug("Calling unix2dos on %s", fn)
            p = subprocess.Popen("unix2dos %s" % fn, shell=True)
            sts = os.waitpid(p.pid, 0)

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-l", "--loglevel", dest="loglevel",
                      help="Manually specify logging level (DEBUG, INFO, WARN, etc)",
                      default="INFO", action="store")   

    log.debug("parsing command line arguments")
    (options, args) = parser.parse_args()

    log.setLevel(getattr(logging,options.loglevel.upper()))

    processNetworks(args)
    


