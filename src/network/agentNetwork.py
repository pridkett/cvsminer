#!/usr/bin/python2.4
"""
agentNetwork.py

build a series of agent networks
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
import subprocess

# I don't have dbfpy installed in a normal home yet
sys.path.append("/home/pwagstro/src")
from dbfpy import *


WEEKSOVERLAP=2
WEEKSWINDOW=8
def buildData(weeks, start, stop, overlap):
    """Build an agentxagent network in weeks intervals, also spit
    out some CSV files with statistics for each of the agents.

    @param weeks - the number of weeks to use for each interval
    @param start - the date to start
    @param stop - the date to stop
    @param overlap - number of weeks to overlap analysis
    """
    agents = User.select()
    currentDate = start
    users = {}
    lagUsers1 = {}
    lagUsers2 = {}
    ctr = 0
    while (currentDate < stop):
        nextDate = currentDate + timeutil.makeTimeDelta(weeks=weeks-overlap)
        stopDate = currentDate + timeutil.makeTimeDelta(weeks=weeks)
        log.info("Processing data from %s to %s", currentDate, nextDate)
        lagUsers2 = lagUsers1
        lagUsers1 = users
        map(lambda x: users.__setitem__(x, {"name": x,
                                            "dev": 0,
                                            "projects": 0,
                                            "commits": 0,
                                            "devLag1": 0,
                                            "devLag2": 0,
                                            "files": 0,
                                            "totalCommits": 0,
                                            "totalProjects": 0,
                                            "totalFiles": 0,
                                            "commitTime": 0}), [y.name for y in agents])
        map(lambda x: users[x[0]].__setitem__("id", x[1]), [[x.name, x.id] for x in agents])

        log.info("Building global data on users")
        # fill in some of the stat information for all of the users
        for user in users.itervalues():
            # get the total commits to this point:
            totalCommits = CVSCommit.select(AND(CVSCommit.q.startDate > start,
                                                CVSCommit.q.startDate <= stopDate,
                                                CVSCommit.q.userID == user["id"])).count()
            totalProjects = Project.select(AND(Project.q.id == CVSCommit.q.projectID,
                                               CVSCommit.q.startDate > start,
                                               CVSCommit.q.startDate <= stopDate,
                                               CVSCommit.q.userID == user["id"]),
                                           distinct=True).count()
            totalFiles = File.select(AND(CVSCommit.q.startDate > start,
                                         CVSCommit.q.startDate <= stopDate,
                                         CVSCommit.q.userID == user["id"],
                                         FileCommit.q.cvsCommitID == CVSCommit.q.id,
                                         FileCommit.q.fileID == File.q.id),
                                     distinct=True).count()
            firstCommit = CVSCommit.select(AND(CVSCommit.q.startDate > start,
                                               CVSCommit.q.userID == user["id"]),
                                           orderBy=CVSCommit.q.startDate,
                                           limit=1)[0]
            if firstCommit.startDate < stopDate:
                commitTime = (stopDate - firstCommit.startDate).days
            else:
                commitTime = 0
            users[user["name"]]["totalCommits"] = totalCommits
            users[user["name"]]["totalProjects"] = totalProjects
            users[user["name"]]["totalFiles"] = totalFiles
            users[user["name"]]["commitTime"] = commitTime
            if lagUsers1.has_key(user["name"]):
                users[user["name"]]['devLag1'] = lagUsers1[user["name"]]["dev"]
            else:
                users[user["name"]]['devLag1'] = 0
            if lagUsers2.has_key(user["name"]):
                users[user["name"]]['devLag2'] = lagUsers2[user["name"]]["dev"]
            else:
                users[user["name"]]['devLag2'] = 0
            
        projects = {}
        # create the basic network
        network = DynamicNetwork()
        metaMatrix = MetaMatrix()
        network.addMetaMatrix(metaMatrix)
        devs = NodeSet(id="agent", type="agent")
        metaMatrix.addNodeSet(devs)
        graph = Graph(sourceType=devs, targetType=devs, directed=False)
        metaMatrix.addGraph(graph)

        activeUsers = User.select(AND(User.q.id == CVSCommit.q.userID,
                                       CVSCommit.q.startDate >= currentDate,
                                       CVSCommit.q.startDate <= stopDate), distinct=True)
        log.info("Building additional data on %d active users", activeUsers.count())
        for user in activeUsers:
            users[user.name]["dev"] = 1
            projs  = Project.select(AND(CVSCommit.q.userID == user.id,
                                        CVSCommit.q.startDate >= currentDate,
                                        CVSCommit.q.startDate <= stopDate,
                                        CVSCommit.q.projectID == Project.q.id),
                                    distinct=True)
            log.debug("user: %s - active projects: %d", user.name, projs.count())
            users[user.name]["projects"] = projs.count()
            commits = CVSCommit.select(AND(CVSCommit.q.userID == user.id,
                                           CVSCommit.q.startDate >= currentDate,
                                           CVSCommit.q.startDate <= stopDate))
            users[user.name]["commits"] = commits.count()
            users[user.name]["file"] = File.select(AND(CVSCommit.q.startDate > currentDate,
                                                       CVSCommit.q.startDate <= stopDate,
                                                       CVSCommit.q.userID == user.id,
                                                       FileCommit.q.cvsCommitID == CVSCommit.q.id,
                                                       FileCommit.q.fileID == File.q.id),
                                                   distinct=True).count()
            
            for proj in projs:
                if not projects.has_key(proj.name):
                    projects[proj.name] = []
                projects[proj.name].append(user.name)


        # create nodes for each of the agents
        userNodes = {}
        for u in users.iterkeys():
            userNodes[u] = Node(id=u)
            devs.addNode(userNodes[u])

        # link the nodes together in a clique
        for p in projects.itervalues():
            if len(p) <= 1:
                continue
            for i in xrange(len(p)):
                for j in xrange(i+1,len(p)):
                    e = graph.getEdge(userNodes[p[i]], userNodes[p[j]])
                    if e:
                        e.value = e.value + 1
                    else:
                        e = Edge(source=userNodes[p[i]], target=userNodes[p[j]],
                                 type="int", value=1)
                        graph.addEdge(e)
        fn = "agentNetwork%02d.xml" % (ctr)
        s = network.toXml().serialize(format=1)
        f = open(fn, "w")
        f.write(s)
        f.close()

        # now create the GWT file from the network
        outputFile = "agentNetwork%02d%s.dl" % (ctr, graph.id)
        p = subprocess.Popen("/home/pwagstro/bin/dynetml_export -m dl -o agentNetwork%02d %s" % (ctr, fn), shell=True)
        sts = os.waitpid(p.pid, 0)
        os.rename(outputFile, "agentNetwork%02d.dl" % (ctr))
        p = subprocess.Popen("/usr/bin/python2.4 dl2gwt.py agentNetwork%02d.dl" % (ctr), shell=True)
        sts = os.waitpid(p.pid, 0)
        
        # write the definition of the dbf file
        # dbfs hhave a limit of 11 characters for the title of each row
        dbfn=dbf_new()
        dbfn.add_field("id",'N',5)
        dbfn.add_field("name",'C',80)
        dbfn.add_field("dev",'N',2)
        dbfn.add_field("devLag1", 'N', 2)
        dbfn.add_field("devLag2", 'N', 2)
        dbfn.add_field("projects", 'N', 3)
        dbfn.add_field("commits", 'N', 5)
        dbfn.add_field("files", 'N', 5)
        dbfn.add_field("totalCommit", 'N', 5)
        dbfn.add_field("totalFiles", 'N', 5)
        dbfn.add_field("totalProj", 'N', 5)
        dbfn.add_field("commitTime", 'N', 5)
        dbfn.write("agentNetwork%02d.dbf" % (ctr))

        # write the DBF file
        dbft = Dbf()
        dbft.openFile("agentNetwork%02d.dbf" % (ctr), readOnly=0)
        # dbft.reportOn()
        ctr2 = 1
        for key,val in users.iteritems():
            rec = DbfRecord(dbft)
            rec['id'] = ctr2
            rec['name'] = key
            rec['dev'] = val['dev']
            rec['devLag1'] = val['devLag1']
            rec['devLag2'] = val['devLag2']
            rec['projects'] = val['projects']
            rec['commits'] = val['commits']
            rec['files'] = val['files']
            rec['totalCommit'] = val['totalCommits']
            rec['totalFiles'] = val['totalFiles']
            rec['totalProj'] = val['totalProjects']
            rec['commitTime'] = val['commitTime']
            rec.store()
            ctr2 = ctr2 + 1
        dbft.close()

        # dump out the stats to a CSV file too
        fn = "agentNetwork%02d.csv" % (ctr)
        f = open(fn, "w")
        writer = csv.writer(f)
        ctr2 = 1
        writer.writerow(["#ctr", "name", "dev", "projects", "commits", "files", "totalCommits", "totalFiles", "totalProjects", "commitTime"])
        for item in [[key, val["dev"], val["projects"], val["commits"], val["files"], val["totalCommits"],
                      val["totalFiles"], val["totalProjects"], val["commitTime"]] for key,val in users.iteritems()]:
            writer.writerow([ctr2] + item)
            ctr2 = ctr2 + 1
        f.close()

        expire_all()
        currentDate = nextDate
        ctr = ctr + 1
           
logging.basicConfig()
log = logging.getLogger("agentNetwork.py")
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

    startDate = timeutil.makeDateTimeFromShortString(options.startdate)
    stopDate = timeutil.makeDateTimeFromShortString(options.stopdate)
    
    # connect to the database
    log.debug("connecting to database: %s - debug=%s", options.uri, options.debug)
    connect(options.uri, debug=options.debug)

    buildData(weeks=options.weeks, start=startDate, stop=stopDate, overlap=options.overlap)
#    buildData(weeks=options.weeks)
