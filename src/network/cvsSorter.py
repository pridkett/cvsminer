#!/usr/bin/python2.4
"""
cvsSorter.py

sorts the networks based on a property.


run this file on the output of CVSNetwork to get some nifty
graphs.
"""

__author__ = "Patrick Wagstrom <pwagstro@andrew.cmu.edu>"
__copyright__ = "Copyright (c) 2006 Patrick Wagstrom"
__license__ = "GNU General Public License Version 2"

import logging
from optparse import OptionParser
from sets import Set
import sys
import csvutil
from dynet import *
import csv
from pyx import *

def buildData(args):
    files = []
    for f in args:
        files.append(csvutil.CSVFile(f))

    data = []
    for f in files:
        f.sort("devs")
        f.reverse()
        data.append([x[0] for x in f.data])

    hds = []
    for dist in [5,10,25,50,100]:
        thisCol = []
        for d in xrange(0,len(data)-1):
            s = Set(data[d][:dist] + data[d+1][:dist])
            thisCol.append(len(s) - dist)
        hds.append(thisCol)
    hds = apply(zip, hds)
    f = open("topDevsHamming.csv", "wb")
    writer = csv.writer(f)
    writer.writerow(["# top 5", "top 10", "top 25", "top 50", "top 100"])
    map(writer.writerow, hds)
    f.close()
        
    devs = apply(zip, data)
    f = open("topDevsProjects.csv", "wb")
    writer = csv.writer(f)
    map(writer.writerow, devs)
    f.close()
    
    # Initialize graph object
    g = graph.graphxy(width=8,
                      key=graph.key.key(pos="mr", hinside=0),
                      x=graph.axis.linear(min=0, max=len(hds), title="Time Period"),
                      y=graph.axis.linear(min=0, max=30, title="Changes"))

    dlists = []
    for x in ((0,"top 5"), (1, "top 10"), (2, "top 25"), (3, "top 50"), (4, "top 100")):
        dlists.append(graph.data.list(zip(range(len(hds)), [y[x[0]] for y in hds]), x=1, y=2, title=x[1]))
        
    # Plot the function
    g.plot(dlists, [graph.style.line([color.palette.Rainbow, style.linewidth.thick])])
    # Write pdf
    g.writePDFfile("hammingDevs.pdf")

    data = []
    for f in files:
        f.sort("commits")
        f.reverse()
        data.append([x[0] for x in f.data])

    hds = []
    for dist in [5,10,25,50,100]:
        thisCol = []
        for d in xrange(0,len(data)-1):
            s = Set(data[d][:dist] + data[d+1][:dist])
            thisCol.append(len(s) - dist)
        hds.append(thisCol)
    hds = apply(zip, hds)
    f = open("topCommitsHamming.csv", "wb")
    writer = csv.writer(f)
    writer.writerow(["# top 5", "top 10", "top 25", "top 50", "top 100"])
    map(writer.writerow, hds)
    f.close()
        
    devs = apply(zip, data)
    f = open("topCommitsProjects.csv", "wb")
    writer = csv.writer(f)
    map(writer.writerow, devs)
    f.close()

    # Initialize graph object
    g = graph.graphxy(width=8,
                      key=graph.key.key(pos="mr", hinside=0),
                      x=graph.axis.linear(min=0, max=len(hds), title="Time Period"),
                      y=graph.axis.linear(min=0, max=30, title="Changes"))

    dlists = []
    for x in ((0,"top 5"), (1, "top 10"), (2, "top 25"), (3, "top 50"), (4, "top 100")):
        dlists.append(graph.data.list(zip(range(len(hds)), [y[x[0]] for y in hds]), x=1, y=2, title=x[1]))
        
    # Plot the function
    g.plot(dlists, [graph.style.line([color.palette.Rainbow, style.linewidth.thick])])
    # Write pdf
    g.writePDFfile("hammingCommits.pdf")
    
logging.basicConfig()
log = logging.getLogger("cvsSorter.py")
log.setLevel(logging.INFO)

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-d", "--debug", action="store_true",
                      dest="debug", default=False,
                      help="sqlobject debugging messages")
    parser.add_option("-v", "--verbose", action="store_true",
                      dest="verbose", default=False,
                      help="verbose messages")
    parser.add_option("-l", "--loglevel", dest="loglevel",
                      help="Manually specify logging level (DEBUG, INFO, WARN, etc)",
                      default="INFO", action="store")   

    log.debug("parsing command line arguments")
    (options, args) = parser.parse_args()

    if options.debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(getattr(logging,options.loglevel.upper()))

    buildData(args)
