#!/usr/bin/python2.4
"""
guessGrapher.py

Builds a network where agents are tied together if they modified the same
file within a specific interval
"""

__author__ = "Patrick Wagstrom <pwagstro@andrew.cmu.edu>"
__copyright__ = "Copyright (c) 2006 Patrick Wagstrom"
__license__ = "GNU General Public License Version 2"

import logging
import timeutil
from optparse import OptionParser
import os

class DeveloperInfo:
    def __init__(self, idName, commercial, nodeName):
        self.idName = idName
        self.commercial = commercial
        self.nodeName = nodeName
        self.edges = {}
        self.clustCoeff = None
        self.nonCommClust = None
        self.commClust = None
        
    def clear(self):
        self.edges = {}
        self.clustCoeff = None
        self.nonCommClust = None
        self.commClust = None

def calcClustering(project):
    fnBase = project.replace(os.sep, "_")
    graphFiles = [nn for nn in os.listdir(".") if nn.startswith(fnBase+".d.")]
    graphFiles.sort()

    # load the information for the developers
    f = open(fnBase + ".gdf").readlines()
    readingNodes = False
    devs = {}
    for tl in f:
        if tl.startswith("nodedef> name"):
            readingNodes = True
            continue
        if tl.startswith("edgedef>"):
            readingNodes = False
            break
        if readingNodes:
            elems = [x.strip() for x in tl.split(",")]
            if elems[0][0] == 'p':
                devs[elems[0]] = DeveloperInfo(elems[0], elems[4] == 'true', elems[5])

    # now iterate over each of the graph files
    for fn in graphFiles:
        log.debug("processing file: %s", fn)
        # clear out all the old stuff
        map(lambda x: x.clear(), devs.itervalues())
        f = (x for x in open(fn).readlines() if not x.startswith("#"))
        for tl in f:
            src,dest = tl.split(",")[0].split("-")
            if src[0] == 'p' and dest[0] == 'p' and dest != src:
                devs[src].edges[dest] = 1
                devs[dest].edges[src] = 1

        # iterate over each of the developers calculating the clustering coefficient
        for dev in [td for td in devs.itervalues() if td.edges]:
            # generic clustering coefficient
            numLinks = len(dev.edges)
            totalSum = 0
            mapped = {}
            for odev in dev.edges.iterkeys():
                mapped[odev] = 1
                sm = sum(map(lambda x: devs[odev].edges.has_key(x), [td for td in dev.edges.keys() if not mapped.has_key(td)]))
                totalSum = totalSum + sm
            try:
                dev.clustCoeff = float(totalSum)/float(numLinks*(numLinks-1)/2)
                if dev.clustCoeff < 0 or dev.clustCoeff > 1:
                    log.warning("Incorrect clustering coefficient: %0.2f, %d, %d", dev.clustCoeff, totalSum, numLinks * (numLinks-1))
                    raise Exception("Clustering coefficient error")
            except ZeroDivisionError:
                pass

            # corporate clustering coefficient
            commLinks = [x for x in dev.edges.keys() if devs[x].commercial]
            numLinks = len(commLinks)
            totalSum = 0
            mapped = {}
            for odev in commLinks:
                mapped[odev] = 1
                sm = sum(map(lambda x: devs[odev].edges.has_key(x), [td for td in commLinks if not mapped.has_key(td)]))
                totalSum = totalSum + sm
            try:
                dev.commClust = float(totalSum)/float(numLinks*(numLinks-1)/2)
                if dev.commClust < 0 or dev.commClust > 1:
                    log.warning("Incorrect clustering coefficient: %0.2f, %d, %d", dev.commClust, totalSum, numLinks * (numLinks-1))
                    raise Exception("Clustering coefficient error")
            except ZeroDivisionError:
                dev.commClust = None

            # non-commercial clustering coefficient
            nonCommLinks = [x for x in dev.edges.keys() if not devs[x].commercial]
            numLinks = len(nonCommLinks)
            totalSum = 0
            mapped = {}
            for odev in nonCommLinks:
                mapped[odev] = 1
                sm = sum(map(lambda x: devs[odev].edges.has_key(x), [td for td in nonCommLinks if not mapped.has_key(td)]))
                totalSum = totalSum + sm
            try:
                dev.nonCommClust = float(totalSum)/float(numLinks*(numLinks-1)/2)
                if dev.nonCommClust < 0 or dev.nonCommClust > 1:
                    log.warning("Incorrect clustering coefficient: %0.2f, %d, %d", dev.clustCoeff, totalSum, numLinks * (numLinks-1))
                    raise Exception("Clustering coefficient error")
            except ZeroDivisionError:
                dev.nonCommClust = None

        # calculate the overall averages
        output = []
        averages = getClustAvgs(devs.values())
        output = output + [len(devs), getActiveCount(devs.values())] + list(averages)

        nonCommDevs = [x for x in devs.values() if not x.commercial]
        nonCommAvgs = getClustAvgs(nonCommDevs)
        output = output + [len(nonCommDevs), getActiveCount(nonCommDevs)] + list(nonCommAvgs)

        commDevs = [x for x in devs.values() if x.commercial]
        commAvgs = getClustAvgs(commDevs)
        output = output + [len(commDevs), getActiveCount(commDevs)] + list(commAvgs)

        print "%s " % (fn.split(".")[-1]) + " ".join(map(niceFormat, output))

def niceFormat(inp):
    if inp.__class__ == float:
        return "%0.2f" % (inp)
    return "%d" % (inp)

        
def getActiveCount(devs):
    return len([x for x in devs if len(x.edges)])

def getClustAvgs(devs):
    clustCoeff = [x.clustCoeff for x in devs if x.clustCoeff != None]
    log.debug("average: %s",clustCoeff)
    clustCoeff = sum(clustCoeff) / max(len(clustCoeff),1)
    
    nonCommClust = [x.nonCommClust for x in devs if x.nonCommClust != None]
    log.debug("noncomm: %s", nonCommClust)
    nonCommClust = sum(nonCommClust) / max(len(nonCommClust), 1)

    commClust = [x.commClust for x in devs if x.commClust != None]
    log.debug("comm: %s", commClust)
    commClust = sum(commClust) / max(len(commClust),1)
    
    return clustCoeff, nonCommClust, commClust

        

    
        
logging.basicConfig()
log = logging.getLogger("guessClustering.py")
log.setLevel(logging.INFO)

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-d", "--debug", action="store_true",
                      dest="debug", default=False,
                      help="verbose debugging messages")
    parser.add_option("-l", "--loglevel", dest="loglevel",
                      help="Manually specify logging level (DEBUG, INFO, WARN, etc)",
                      default="INFO", action="store")   
    parser.add_option("-p", "--project", action="store", dest="project",
                      type="string", default=None, help="load data only for this project")
                      
    log.debug("parsing command line arguments")
    (options, args) = parser.parse_args()

    if options.debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(getattr(logging,options.loglevel.upper()))

    if not(options.project):
        log.error("Must specify a project")
    else:
        calcClustering(options.project)
