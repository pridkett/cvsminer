#!/usr/bin/python2.4
"""
cvsNetwork.py

Build a network based on CVS commits
"""

__author__ = "Patrick Wagstrom <pwagstro@andrew.cmu.edu>"
__copyright__ = "Copyright (c) 2006 Patrick Wagstrom"
__license__ = "GNU General Public License Version 2"

import logging
import timeutil
from optparse import OptionParser
from dbobjects import *
from sets import Set
import sys
import gc 
import math
from dynet import *
import csv

WEEKSWINDOW=8
WEEKSOVERLAP=2

def buildData(weeks, start, stop, overlap):
    currentDate = start
    ctr = 0
    while (currentDate < stop):
        nextDate = currentDate + timeutil.makeTimeDelta(weeks=weeks-overlap)
        stopDate = currentDate + timeutil.makeTimeDelta(weeks=weeks)
        network = DynamicNetwork()
        metaMatrix = MetaMatrix()
        network.addMetaMatrix(metaMatrix)
        devs = NodeSet(id="agent", type="agent")
        projs = NodeSet(id="resource", type="resource")
        metaMatrix.addNodeSet(devs)
        metaMatrix.addNodeSet(projs)
        graph = Graph(sourceType=devs, targetType=projs, directed=False)
        metaMatrix.addGraph(graph)
        fnBase = "gnome%02d" % (ctr)
        fn = "%s.xml" % (fnBase)
        cvsFn = "%s.csv" % (fnBase)
        print "Date: %s - output: %s" % (currentDate, fn)
        commits = CVSCommit.select(AND(CVSCommit.q.startDate >= currentDate,
                                       CVSCommit.q.startDate <= stopDate))

        # add in all the nodes into the network
        for p in Project.select():
            projNode = Node(id=p.name)
            projs.addNode(projNode)

        for commit in commits:
            user = commit.user
            proj = commit.project
            
            userNode = devs[user.name]
            projNode = projs[proj.name]
            if not userNode:
                userNode = Node(id=user.name)
                devs.addNode(userNode)
            if not projNode:
                projNode = Node(id=proj.name)
                projs.addNode(projNode)
            e = graph.getEdge(userNode, projNode)
            if e:
                e.value = e.value + 1
            else:
                e = Edge(source=userNode, target=projNode, type="int", value=1)
                graph.addEdge(e)

        log.info("writing CSV file to %s", cvsFn)
        f = open(cvsFn,"wb")
        writer = csv.writer(f)
        writer.writerow(["# name", "devs", "commits"])
        for nd in projs.iternodes():
            numAgents = len(nd.targetEdges)
            numCommits = sum([x.value for x in nd.targetEdges])
            writer.writerow([nd.id, numAgents, numCommits])
        f.close()

        log.info("removing isolates")
        projs.removeIsolates()
        devs.removeIsolates()

        log.info("serializing network to %s", fn)
        s = network.toXml().serialize(format=1)
        f = open(fn,"w")
        f.write(s)
        f.close()
        
        expire_all()
        ctr = ctr + 1
        currentDate = nextDate

logging.basicConfig()
log = logging.getLogger("cvsNetwork.py")
log.setLevel(logging.INFO)

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-d", "--debug", action="store_true",
                      dest="debug", default=False,
                      help="sqlobject debugging messages")
    parser.add_option("-v", "--verbose", action="store_true",
                      dest="verbose", default=False,
                      help="verbose messages")
    parser.add_option("--dburi", "-u", dest="uri",
                      help="database name to connect to",
                      default="postgres://"+os.getenv("USER")+"@/cvsminer",
                      action="store")
    parser.add_option("-l", "--loglevel", dest="loglevel",
                      help="Manually specify logging level (DEBUG, INFO, WARN, etc)",
                      default="INFO", action="store")   
    parser.add_option("-w", "--weeks", action="store", dest="weeks",
                      type="int", default=WEEKSWINDOW, help="number of weeks to look back",
                      metavar="WEEKS")
    parser.add_option("--startdate", action="store", dest="startdate",
                      type="string", default="19970501", help="date to start analysis on")
    parser.add_option("--stopdate", action="store", dest="stopdate",
                      type="string", default="20050801", help="date to stop analysis")
    parser.add_option("-o", "--overlap", action="store", dest="overlap",
                      type="int", default=WEEKSOVERLAP, help="number of weeks to overlap, default=%d" % WEEKSOVERLAP,
                      metavar="WEEKS")
                      
    log.debug("parsing command line arguments")
    (options, args) = parser.parse_args()

    if options.debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(getattr(logging,options.loglevel.upper()))

    startDate = timeutil.makeDateTimeFromShortString(options.startdate)
    stopDate = timeutil.makeDateTimeFromShortString(options.stopdate)
    
    # connect to the database
    log.debug("connecting to database: %s - debug=%s", options.uri, options.debug)
    connect(options.uri, debug=options.debug)

    buildData(weeks=options.weeks, start=startDate, stop=stopDate, overlap=options.overlap)
