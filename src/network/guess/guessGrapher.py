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
CLASSPARENTS = {}

def buildParentClassDict():
    global CLASSPARENTS
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

def buildInitialNetwork(project):
    mp = MasterProject.select(MasterProject.q.name == project)[0]
    pids = []
    for p in mp.projects:
        for u in p.users:
            for person in u.persons:
                pids.append(person.id)
    pids = Set(pids)
    output = ["nodedef> name, x, y, isPerson BIT default false, isCommercial BIT default false, nodeName VARCHAR(100), fileClass VARCHAR(25) default null, corporations VARCHAR(512) default null"]
    for p in pids:
        person = Person.get(p)
        commercial = "false"
        if len(person.personCorporations) > 0:
            commercial = "true"
        corporations = []
        for corp in person.personCorporations:
            corporations.append(corp.corporation.name)
        corporations = list(Set(corporations))
        corporations.sort()
        output.append("p%d, 0, 0, true, %s, %s, ,%s" % (person.id, commercial, person.primaryAlias.name, "-".join(corporations)))
    for p in mp.projects:
        for f in p.files:
            fc = f.fileClassID or 6
            output.append("f%d, 0, 0, false, false, %s, %s" % (f.id, f.name, CLASSPARENTS[fc].name))
            
    output.append("edgedef> node1, node2, freq INT default 0")
    f = open("%s.gdf" % (mp.name.replace(os.sep,"_")), "w")
    f.write("\n".join(output))
    f.close()

def dumpNetworks(project, startDate, stopDate, window, overlap):
    currentDate = startDate
    mp = MasterProject.select(MasterProject.q.name == project)[0]
    ctr = 0
    while currentDate < stopDate:
        thisLinks = {}
        userFileLinks = {}
        nextDate = currentDate + timeutil.makeTimeDelta(weeks=window)
        for com in CVSCommit.select(AND(CVSCommit.q.startDate >= currentDate,
                                        CVSCommit.q.startDate <= nextDate,
                                        CVSCommit.q.projectID == Project.q.id,
                                        Project.q.masterProjectID == mp.id)):
            try:
                pid = com.user.persons[0].id
            except IndexError:
                log.warn("index error on user %d - ctr %d", com.userID, ctr)
                continue
            thisCommitFiles = [f.id for f in com.files]
            thisCommitFiles.sort()
            for f in thisCommitFiles:
                hkey = "p%d-f%d" % (pid, f)
                thisLinks[hkey] = thisLinks.get(hkey,0) + 1
                userFileLinks[f] = userFileLinks.get(f,[]) + [pid]
                
            for i in xrange(0, len(thisCommitFiles)):
                for j in xrange(i, len(thisCommitFiles)):
                    hkey="f%d-f%d" % (thisCommitFiles[i], thisCommitFiles[j])
                    thisLinks[hkey] = thisLinks.get(hkey,0) + 1


        for ufl in userFileLinks.values():
            uflNoDupe = list(Set(ufl))
            for i in xrange(0, len(uflNoDupe)):
                for j in xrange(i, len(uflNoDupe)):
                    hkey = "p%d-p%d" % (uflNoDupe[i], uflNoDupe[j])
                    thisLinks[hkey] = thisLinks.get(hkey,0) + 1
            
        f = open("%s.d.%03d" % (mp.name.replace(os.sep,"_"), ctr), "w")
        f.write("# StartDate: %s\n" % (currentDate))
        f.write("# StopDate: %s\n" % (stopDate))
        for key,val in thisLinks.iteritems():
            f.write("%s, %d\n" % (key, val))
        f.close()
        ctr = ctr + 1
        currentDate = currentDate + timeutil.makeTimeDelta(weeks=window-overlap)
    
logging.basicConfig()
log = logging.getLogger("guessGrapher.py")
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

    buildParentClassDict()
    buildInitialNetwork(options.project)
    dumpNetworks(options.project, startDate, stopDate, options.weeks, options.overlap)
