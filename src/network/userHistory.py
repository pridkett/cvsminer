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
from dynet import *
from pyx import *


# I don't have dbfpy installed in a normal home yet
sys.path.append("/home/pwagstro/src")

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
    currentDate = start
    ctr = 0
    lastActiveUsers = None
    allActiveUsers = Set()
    rows = []
    while (currentDate < stop):
        thisRow = {}
        nextDate = currentDate + timeutil.makeTimeDelta(weeks=weeks-overlap)
        stopDate = currentDate + timeutil.makeTimeDelta(weeks=weeks)
        activeUsers = Set([x.name for x in User.select(AND(User.q.id == CVSCommit.q.userID,
                                                       CVSCommit.q.startDate >= currentDate,
                                                       CVSCommit.q.startDate <= stopDate),
                                                       distinct=True)])
        if lastActiveUsers:
            hamInactive = len(lastActiveUsers.difference(activeUsers))
            hamActive = len(activeUsers.difference(lastActiveUsers))
            newActives = len(activeUsers.difference(allActiveUsers))
            try:
                percentDrop = float(hamInactive)/float(len(lastActiveUsers))
            except:
                percentDrop = 0.0
        else:
            hamInactive = None
            hamActive = None
            newActives = None
            percentDrop = None

        lastActiveUsers = activeUsers
        allActiveUsers = allActiveUsers.union(activeUsers)

        thisRow["hamInactive"] = hamInactive
        thisRow["hamActive"] = hamActive
        thisRow["newActives"] = newActives
        thisRow["percentDrop"] = percentDrop
        thisRow["allActives"] = len(allActiveUsers)

        rows.append(thisRow)
        currentDate = nextDate
        ctr = ctr + 1

    g = graph.graphxy(width=8,
                      key=graph.key.key(pos="mr", hinside=0),
                      x=graph.axis.linear(min=0, max=len(rows), title="Time Period"),
                      y=graph.axis.linear(min=0, max=rows[-1]["allActives"]+50, title="Developers"))
    dlist = graph.data.list(zip(range(len(rows)-1), [x["allActives"] for x in rows[1:-1]]),
                            x=1, y=2, title="total developers")
    
    g.plot([dlist], [graph.style.line([color.rgb.red, style.linestyle.solid, style.linewidth.thick])])
    g.writePDFfile("communityGrowth.pdf")

    g = graph.graphxy(width=8,
                      key=graph.key.key(pos="mr", hinside=0),
                      x=graph.axis.linear(min=0, max=len(rows), title="Time Period"),
                      y=graph.axis.linear(min=0, max=1, title="Proportion of Developers"))
    dlist = graph.data.list(zip(range(len(rows)-1), [1-x["percentDrop"] for x in rows[1:-1]]),
                            x=1, y=2, title="Retention Rate")
    g.plot([dlist], [graph.style.line([color.palette.Rainbow, style.linestyle.solid, style.linewidth.thick])])
    g.writePDFfile("retentionRates.pdf")
    
logging.basicConfig()
log = logging.getLogger("userHistory.py")
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
