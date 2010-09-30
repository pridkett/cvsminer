#!/usr/bin/python2.4
"""
agentFileNetwork.py

Builds a network where agents are tied together if they modified the same
file within a specific interval
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
import subprocess
from dynet import *
# these are default values for ths simulation, they can be overruled
# using the command line parameters
WEEKSWINDOW=8
WEEKSOVERLAP=2

BADFILES = ["ChangeLog", "README", "AUTHORS", "NEWS", "INSTALL", "COPYING"]
BADEXTS = [".gif", ".png", ".jpg", ".html", ".xml", ".po"]

def buildData(weeks, overlap, start, stop, project=None):
    if project:
        log.info("Only generating data from project %s", project)
    currentDate = start
    ctr = 0
    devs = NodeSet(id="agent", type="agent")
    userNodes = {}
    
    # create all of the nodes for the users
    # do this only once
    # hack for getting only evolution users...
    if project != None:
        projectId = Project.select(Project.q.name == project)[0].id
        users = User.select(AND(User.q.id == CVSCommit.q.userID,
                                CVSCommit.q.projectID == projectId), distinct=True)
    else:
        users = User.select()
    for user in users:
        userNodes[user.id] = Node(id=user.name)
        devs.addNode(userNodes[user.id])

    ctr = 0
    while (currentDate < stop):
        fileUsers = {}
        devs.clearEdges()
        nextDate = currentDate + timeutil.makeTimeDelta(weeks=weeks-overlap)
        stopDate = currentDate + timeutil.makeTimeDelta(weeks=weeks)
        log.info("Starting Date: %s - Ending Date: %s", currentDate, stopDate)

        # set up the meta matrix stuff
        network = DynamicNetwork()
        metaMatrix = MetaMatrix()
        network.addMetaMatrix(metaMatrix)
        files = NodeSet(id="resource", type="resource")
        metaMatrix.addNodeSet(devs)
        metaMatrix.addNodeSet(files)

        agentGraph = Graph(sourceType=devs, targetType=devs, directed=False)
        metaMatrix.addGraph(agentGraph)

        # get all of the CVS Commit information
        if project:
            commits = CVSCommit.select(AND(CVSCommit.q.startDate >= currentDate,
                                           CVSCommit.q.stopDate <= stopDate,
                                           CVSCommit.q.projectID == projectId), distinct=True)
        else:
            commits = CVSCommit.select(AND(CVSCommit.q.startDate >= currentDate,
                                           CVSCommit.q.stopDate <= stopDate,
                                           CVSCommit.q.projectID == 141), distinct=True)
        log.debug("Commits: %d", commits.count())
        for com in commits:
            for fl in com.files:
                filename = com.project.name + "/" + fl.name
                base, ext = os.path.splitext(filename)
                if ext in BADEXTS:
                    log.debug("Extension ignore file: %s", filename)
                    continue
                path, fn = os.path.split(filename)
                if fn in BADFILES:
                    log.debug("Name ignore file: %s", filename)
                    continue
                if not fileUsers.has_key(filename):
                    fileUsers[filename] = Set()                    
                fileUsers[filename].add(com.userID)

        for val in fileUsers.itervalues():
            flList = list(val)
            for i in xrange(0,len(flList)):
                for j in xrange(i+1, len(flList)):
                    e = agentGraph.getEdge(userNodes[flList[i]], userNodes[flList[j]])
                    if e:
                        e.value = e.value + 1
                    else:
                        e = Edge(source=userNodes[flList[i]],
                                 target=userNodes[flList[j]],
                                 type="int", value=1)
                        agentGraph.addEdge(e)

        fn = "agentFileNetwork%02d.xml" % (ctr)
        log.info("Writing network to file %s - %d nodes, %d edges", fn, len(devs), len(agentGraph))
        s = network.toXml().serialize(format=1)
        f = open(fn,"w")
        f.write(s)
        f.close()

        # now create the GWT file from the network
        outputFile = "agentFileNetwork%02d%s.dl" % (ctr, agentGraph.id)
        p = subprocess.Popen("/home/pwagstro/bin/dynetml_export -m dl -o agentFileNetwork%02d %s" % (ctr, fn), shell=True)
        sts = os.waitpid(p.pid, 0)
        os.rename(outputFile, "agentFileNetwork%02d.dl" % (ctr))
        p = subprocess.Popen("/usr/bin/python2.4 dl2gwt.py agentFileNetwork%02d.dl" % (ctr), shell=True)
        sts = os.waitpid(p.pid, 0)


        fn = "agentFileNetwork%02d.dat" % (ctr)
        log.info("Writing network to raw file - %s", fn)
        f = open(fn,"w")
        agentGraph.dumpRaw(f)
        f.close()
        
        p = subprocess.Popen("unix2dos %s" % (fn), shell=True)
        sts = os.waitpid(p.pid, 0)

        ctr = ctr + 1
        currentDate = nextDate
        expire_all()
        
                

logging.basicConfig()
log = logging.getLogger("agentFileNetwork.py")
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
                      type="int", default=WEEKSWINDOW, help="number of weeks to look back, default=%d" % WEEKSWINDOW,
                      metavar="WEEKS")
    parser.add_option("-o", "--overlap", action="store", dest="overlap",
                      type="int", default=WEEKSOVERLAP, help="number of weeks to overlap, default=%d" % WEEKSOVERLAP,
                      metavar="WEEKS")
    parser.add_option("-p", "--project", action="store", dest="project",
                      type="string", default=None, help="load data only for this project")
    parser.add_option("--startdate", action="store", dest="startdate",
                      type="string", default="19970301", help="date to start analysis on")
    parser.add_option("--stopdate", action="store", dest="stopdate",
                      type="string", default="20050801", help="date to stop analysis")
                      
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

    buildData(weeks=options.weeks, overlap=options.overlap, start=startDate, stop=stopDate, project=options.project)
