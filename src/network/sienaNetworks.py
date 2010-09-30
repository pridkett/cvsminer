#!/usr/bin/python2.4
"""
sienaNetworks.py

Generates a set of networks for examination by Siena
"""

__author__ = "Patrick Wagstrom <pwagstro@andrew.cmu.edu>"
__copyright__ = "Copyright (c) 2006 Patrick Wagstrom"
__license__ = "GNU General Public License Version 2"

import logging
import timeutil
from optparse import OptionParser
from dbobjects import *
from sets import Set
import numpy
import scipy, scipy.io
import sys
from dynet import *

# these are default values for ths simulation, they can be overruled
# using the command line parameters
WEEKSWINDOW=8
WEEKSOVERLAP=2

def buildParentClassDict():
    """For each class in the database, this calculates what their root
    parent is.  For example for anything that is source code, it returns
    the ID for source code.  Slick eh?"""
    tdict = {}
    fdict = {}
    pc = FileClass.select()
    for t in pc:
        tdict[t.id] = t
    for t in tdict.keys():
        tid = t
        telem = tdict[t]
        while telem.parentID != None:
            telem = telem.parent
        fdict[t] = telem
    CLASSPARENTS = fdict
    return CLASSPARENTS

def buildEmailNetwork(project, startDate, stopDate, binary=False, removeNonAgents=False):
    """Builds a network of the interactions between developers based on their
    mailing list interactions.  It does this two different ways, the first way
    is based on direct mailing, the second is that all agents in a thread are
    connected to one another.
    """
    log.info("Building thread network from %s to %s", startDate, stopDate)

    # create the network
    network = DynamicNetwork()
    metaMatrix = MetaMatrix()
    network.addMetaMatrix(metaMatrix)
    devs = NodeSet(id="agent", type="agent")
    metaMatrix.addNodeSet(devs)
    devGraph = Graph(id="mail-dev-dev", sourceType=devs, targetType=devs, directed=True)
    metaMatrix.addGraph(devGraph)
    
    allNetwork = DynamicNetwork()
    allMetaMatrix = MetaMatrix()
    allNetwork.addMetaMatrix(allMetaMatrix)
    allMetaMatrix.addNodeSet(devs)
    threads = NodeSet(id="threads", type="resource")
    allMetaMatrix.addNodeSet(threads)
    allDevGraph = Graph(id="mail-all-dev-dev", sourceType=devs, targetType=devs, directed=True)
    allThreadGraph = Graph(id="mail-all-dev-thread", sourceType=devs, targetType=threads, directed=True)
    allMetaMatrix.addGraph(allDevGraph)
    allMetaMatrix.addGraph(allThreadGraph)
    
    # select all developers over the history of the project
    allDevs = Person.select(AND(CVSCommit.q.projectID == Project.q.id,
                                Project.q.masterProjectID == project.id,
                                User.q.id == CVSCommit.q.userID,
                                PersonUser.q.userID == User.q.id,
                                PersonUser.q.personID == Person.q.id),
                            distinct=True,
                            orderBy=Person.q.id)
    # add in all the developers
    for tempDev in allDevs:
        devNode = Node(id=tempDev.id)
        devs.addNode(devNode)
        devNode.addProperty(NodeProperty(name="name", type="string", value=tempDev.primaryAlias.name))
    
    
    # iterate over each of the messages that was posted on the list
    # NOTE: while it might be simpler to iterate over only the messages posted
    # by people who are developers, it potentially misses some thread issues
    messages = MailMessage.select(AND(MailMessage.q.listID == MailList.q.id,
                                      MailList.q.projectID == project.id,
                                      MailMessage.q.date <= stopDate,
                                      MailMessage.q.date > startDate),
                                  orderBy=MailMessage.q.date)

    for msg in messages:
        # first we process the direct message network

        # see if the message was written by a developer
        if msg.email != None and devs.has_key(msg.email.personID):
            sourceNode = devs[msg.email.personID]
            for recip in msg.recipients:
                # see if the recipient is another developer
                if recip.emailID != None and devs.has_key(recip.email.personID):
                    otherDev = devs[recip.email.personID]
                    # get the edge for the dev
                    thisEdge = devGraph.getEdge(sourceNode, otherDev)
                    if not thisEdge:
                        thisEdge = Edge(source=sourceNode, target=otherDev, type="int", value=0)
                        devGraph.addEdge(thisEdge)
                    # increment the value of the edge
                    thisEdge.value = thisEdge.value + 1
                    if binary: thisEdge.value = 1
                    
            # iterate over the parents
            pmsg = msg.parent
            lastThread = msg
            linkedUsers = [msg.email.personID]
            while pmsg != None:
                lastThread = pmsg
                if pmsg.emailID != None and devs.has_key(pmsg.email.personID):
                    otherDev = devs[pmsg.email.personID]
                    if not pmsg.email.personID in linkedUsers:
                        linkedUsers.append(pmsg.email.personID)
                    thisEdge = allDevGraph.getEdge(sourceNode, otherDev)
                    if not thisEdge:
                        thisEdge = Edge(source=sourceNode, target=otherDev, type="int", value=0)
                        allDevGraph.addEdge(thisEdge)
                    thisEdge.value = thisEdge.value + 1
                    if binary: thisEdge.value = 1
                pmsg = pmsg.parent

            if threads.has_key("thread%d" % (lastThread.id)):
                threadNode = threads["thread%d" % (lastThread.id)]
            else:
                threadNode = Node(id="thread%d" % (lastThread.id))
                threads.addNode(threadNode)
            for devId in linkedUsers:
                if devs.has_key(devId):
                    thisEdge = allThreadGraph.getEdge(devs[devId], threadNode)
                    if not thisEdge:
                        thisEdge = Edge(source=devs[devId], target=threadNode, type="int", value=0)
                        allThreadGraph.addEdge(thisEdge)
                    thisEdge.value = thisEdge.value + 1
                    if binary: thisEdge.value = 1
                    
    startString = "%04d%02d%02d" % (startDate.year, startDate.month, startDate.day)
    stopString = "%04d%02d%02d" % (stopDate.year, stopDate.month, stopDate.day)

    if removeNonAgents:
        for nn in [network, allNetwork]:
            # now see about removing nodesets that are not agents
            removeGraphs = []
            for g in nn.metaMatrix.graphs.itervalues():
                # if either is not agents, remove them
                if g.sourceType.type != "agent" or g.targetType.type != "agent":
                    removeGraphs.append(g)
            removeNodesets = []
            for ns in nn.metaMatrix.nodesets.itervalues():
                if ns.type != "agent":
                    removeNodesets.append(ns)
            map(nn.metaMatrix.removeGraph, removeGraphs)
            map(nn.metaMatrix.removeNodeSet, removeNodesets)

    fn = project.name.replace("/","_") + "-mail-%s-%s.dynetml" % (startString, stopString)
    log.info("Saving file to %s", fn)
    network.saveToFile(fn)
    fn = project.name.replace("/","_") + "-mail-all-%s-%s.dynetml" % (startString, stopString)
    log.info("Saving file to %s", fn)
    allNetwork.saveToFile(fn)
    
 
def buildSourceCodeNetwork(project, startDate, stopDate, devMap=None, binary=False, removeNonAgents=False):
    """Builds a network of agents based on shared file modifications.  THIS IS A
    DIRECTED NETWORK.  Edges only exist if Person B modified the file after
    Person A.  Assumes that we're not interested in Dead files.

    Also, assumes that we'd like all the developers to be in the networks
    """
    previousCommitters = devMap or {}
    
    log.info("Building network from %s to %s", startDate, stopDate)
    # pre-obtain the dead state
    deadState = CVSState.byName("dead")
    # figure out what the code classes are
    sc = FileClass.byName("Source Code")
    classParents = buildParentClassDict()
    codeClasses = [x.id for x in FileClass.select() if classParents[x.id].id == sc.id]

    # create the metamatrix setup -
    #  two sets of nodes: devs and files
    #  two graphs: devs->devs devs-files
    network = DynamicNetwork()
    metaMatrix = MetaMatrix()
    network.addMetaMatrix(metaMatrix)
    devs = NodeSet(id="agent", type="agent")
    files = NodeSet(id="files", type="resource")
    metaMatrix.addNodeSet(devs)
    metaMatrix.addNodeSet(files)
    devGraph = Graph(id="code-dev-dev", sourceType=devs, targetType=devs, directed=True)
    devFileGraph = Graph(id="dev-file", sourceType=devs, targetType=files, directed=False)
    metaMatrix.addGraph(devGraph)
    metaMatrix.addGraph(devFileGraph)

    # create a second metamatrix - that stores interactions over all time
    allNetwork = DynamicNetwork()
    allMetaMatrix = MetaMatrix()
    allNetwork.addMetaMatrix(allMetaMatrix)
    allMetaMatrix.addNodeSet(devs)
    allDevGraph = Graph(id="code-all-dev-dev", sourceType=devs, targetType=devs, directed=True)
    allMetaMatrix.addGraph(allDevGraph)
    
    # get all developers over the history of the project
    allDevs = Person.select(AND(CVSCommit.q.projectID == Project.q.id,
                                Project.q.masterProjectID == project.id,
                                User.q.id == CVSCommit.q.userID,
                                PersonUser.q.userID == User.q.id,
                                PersonUser.q.personID == Person.q.id),
                            distinct=True,
                            orderBy=Person.q.id)
    # add in all the developers
    for tempDev in allDevs:
        devNode = Node(id=tempDev.id)
        devs.addNode(devNode)
        devNode.addProperty(NodeProperty(name="name", type="string", value=tempDev.primaryAlias.name))

    # iterate over all the commits during this time period
    commits = CVSCommit.select(AND(CVSCommit.q.projectID == Project.q.id,
                                   Project.q.masterProjectID == project.id,
                                   CVSCommit.q.startDate > startDate,
                                   CVSCommit.q.startDate < stopDate),
                               orderBy=CVSCommit.q.startDate)
    for com in commits:
        # get the actual user behind this
        personSelect = Person.select(AND(CVSCommit.q.id == com.id,
                                         User.q.id == CVSCommit.q.userID,
                                         PersonUser.q.userID == User.q.id,
                                         PersonUser.q.personID == Person.q.id))
        if personSelect.count() == 0:
            log.error("No person attached to user %s for commit %d -- not processing", com.user.name, com.id)
            continue
        if personSelect.count() > 1:
            log.warn("Multiple persons attached to user %s for commit %d -- using first person '%s'", com.user.name, com.id, personSelect[0].primaryAlias.name)
        person = personSelect[0]
        # get the person behind the commit
        if not devs.has_key(person.id):
            devNode = Node(id=person.id)
            devs.addNode(devNode)
            devNode.addProperty(NodeProperty(name="name", type="string", value=person.primaryAlias.name))
        else:
            devNode = devs[person.id]
            
        # get just the files we're interested in, in this case, source
        cf = File.select(AND(File.q.id == FileCommit.q.fileID,
                             FileCommit.q.cvsCommitID == com.id,
                             FileCommit.q.stateID != deadState.id,
                             IN(File.q.fileClassID, codeClasses)))
        for f in cf:
            if not files.has_key(f.id):
                fileNode = Node(id=f.id)
                files.addNode(fileNode)
                fileNode.addProperty(NodeProperty(name="fileName", type="string", value=f.name))
            else:
                fileNode = files[f.id]
                # now we need to connect the developer to all the previous developers
                for dev in [te.source for te in fileNode.targetEdges if te.source.id != devNode.id]:
                    thisEdge = devGraph.getEdge(devNode, dev)
                    if not thisEdge:
                        thisEdge = Edge(source=devNode, target=dev, type="int", value=0)
                        devGraph.addEdge(thisEdge)
                    thisEdge.value = thisEdge.value + 1
                    if binary: thisEdge.value = 1
                
            # link this developer to the file
            thisEdge = devFileGraph.getEdge(devNode, fileNode)
            if not thisEdge:
                thisEdge = Edge(source=devNode, target=fileNode, type="int", value=0)
                devFileGraph.addEdge(thisEdge)
            thisEdge.value = thisEdge.value + 1 
            if binary: thisEdge.value = 1

            if not previousCommitters.has_key(f.id):
                previousCommitters[f.id] = [devNode.id]
            elif devNode.id not in previousCommitters[f.id]:
                previousCommitters[f.id].append(devNode.id)

            for op in previousCommitters[f.id]:
                if op == devNode.id: continue
                targetNode = devs[op]
                thisEdge = allDevGraph.getEdge(devNode, targetNode)
                if not thisEdge:
                    log.debug("adding edge %d->%d", devNode.id, targetNode.id)
                    thisEdge = Edge(source=devNode, target=targetNode, type="int", value=0)
                    allDevGraph.addEdge(thisEdge)
                thisEdge.value = thisEdge.value + 1
                if binary: thisEdge.value = 1

#             # link this developer to every previous developer of this file
#             otherPeople =  Person.select(AND(CVSCommit.q.startDate < com.startDate,
#                                              User.q.id == CVSCommit.q.userID,
#                                              PersonUser.q.userID == User.q.id,
#                                              PersonUser.q.personID == Person.q.id,
#                                              File.q.id == FileCommit.q.fileID,
#                                              File.q.id == f.id,
#                                              FileCommit.q.stateID != deadState.id,
#                                              FileCommit.q.cvsCommitID == CVSCommit.q.id),
#                                          distinct=True)
#             log.debug("Found %d other people who edited this file prior to %s", otherPeople.count(), com.startDate)
#             for op in otherPeople:
#                 if op.id == devNode.id: continue
#                 targetNode = devs[op.id]
#                 thisEdge = allDevGraph.getEdge(devNode, targetNode)
#                 if not thisEdge:
#                     log.debug("adding edge %d->%d", devNode.id, targetNode.id)
#                     thisEdge = Edge(source=devNode, target=targetNode, type="int", value=0)
#                     allDevGraph.addEdge(thisEdge)
#                 thisEdge.value = thisEdge.value + 1
                

    startString = "%04d%02d%02d" % (startDate.year, startDate.month, startDate.day)
    stopString = "%04d%02d%02d" % (stopDate.year, stopDate.month, stopDate.day)

    if removeNonAgents:
        for nn in [network, allNetwork]:
            # now see about removing nodesets that are not agents
            removeGraphs = []
            for g in nn.metaMatrix.graphs.itervalues():
                # if either is not agents, remove them
                if g.sourceType.type != "agent" or g.targetType.type != "agent":
                    removeGraphs.append(g)
            removeNodesets = []
            for ns in nn.metaMatrix.nodesets.itervalues():
                if ns.type != "agent":
                    removeNodesets.append(ns)
            map(nn.metaMatrix.removeGraph, removeGraphs)
            map(nn.metaMatrix.removeNodeSet, removeNodesets)

    fn = project.name.replace("/","_") + "-%s-%s.dynetml" % (startString, stopString)
    log.info("Saving file to %s", fn)
    network.saveToFile(fn)
    fn = project.name.replace("/","_") + "-all-%s-%s.dynetml" % (startString, stopString)
    log.info("Saving file to %s", fn)
    allNetwork.saveToFile(fn)

    # keep track of who previously comitted to the files
    return previousCommitters

def buildNetworks(project, startDate, stopDate, window, overlap, binary=False, removeNonAgents=False):
    """Iterate over each of the networks and build the data

    project - the masterproject to work on
    startDate - the first date to start
    stopDate - the last date to process
    window - the width of the sliding window, in weeks
    overlap - the overlap between windows, in weeks
    """
    currentDate = startDate
    devMap = {}
    while currentDate < stopDate:
        nextDate = currentDate + timeutil.makeTimeDelta(weeks=window-overlap)
        finishDate = currentDate + timeutil.makeTimeDelta(weeks=window)
        buildEmailNetwork(project, currentDate, finishDate, binary=binary, removeNonAgents=removeNonAgents)
        devMap = buildSourceCodeNetwork(project,currentDate, finishDate, devMap, binary=binary, removeNonAgents=removeNonAgents)
        currentDate = nextDate
        
                
logging.basicConfig()
log = logging.getLogger("sienaNetworks.py")
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
    parser.add_option("-p", "--project", action="store", dest="project",
                      type="string", default=None, help="load data only for this project")
    parser.add_option("-b", "--binary", action="store_true", dest="binary",
                      default=False, help="only create a binary network")
    # parameter not handled
    parser.add_option("--nonew", action="store_true", dest="nonew",
                      default=False, help="ignore new files")
    # parameter not handled
    parser.add_option("--nodead", action="store_true", dest="nodead",
                      default=False, help="ignore dead files")
    # parameter not handled
    parser.add_option("--onlysource", action="store_true", dest="onlySource",
                      default=False, help="Use only source code files")

    parser.add_option("--onlyagents", action="store_true", dest="removeNonAgents",
                      default=False, help="Remove all entities that are not agents from the networks")

    parser.add_option("-w", "--weeks", action="store", dest="weeks",
                      type="int", default=WEEKSWINDOW, help="number of weeks to look back, default=%d" % WEEKSWINDOW,
                      metavar="WEEKS")
    parser.add_option("-o", "--overlap", action="store", dest="overlap",
                      type="int", default=WEEKSOVERLAP, help="number of weeks to overlap, default=%d" % WEEKSOVERLAP,
                      metavar="WEEKS")
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

    # connect to the database
    log.debug("connecting to database: %s - debug=%s", options.uri, options.debug)
    connect(options.uri, debug=options.debug)

	# figure out what the start/stop dates were going to be
    startDate = timeutil.makeDateTimeFromShortString(options.startdate)
    stopDate = timeutil.makeDateTimeFromShortString(options.stopdate)

    if not options.project:
        log.error("must specify a project with -p")
        sys.exit()
    project = MasterProject.select(MasterProject.q.name == options.project)[0]
    buildNetworks(project, startDate, stopDate, options.weeks, options.overlap, binary=options.binary, removeNonAgents=options.removeNonAgents)
