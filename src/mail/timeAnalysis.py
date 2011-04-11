#!/usr/bin/python
"""
timeAnalysis.py

prints out time series information about mailing list netowkrs
"""

__author__ = "Patrick Wagstrom"
__copyright__ = "Copyright (c) 2006 Patrick Wagstrom"
__license__ = "GNU General Public License version 2 or later"

from pylab import *
from dbobjects import *
import logging
from optparse import OptionParser
import timeutil
import datetime
MINDATE=datetime.datetime(1,1,1)

def dumpMailList(mlname, firstDate=None, lastDate=None, delta=7):
    ml = MailList.select(MailList.q.name==mlname)
    if ml.count() < 1:
        raise KeyError("""Mailing List "%s" not found""" % (mlname))
    if ml.count() > 1:
        raise KeyError("""Mailing List "%s" specifies multiple lists""" % (mlname))
    ml = ml[0]

    # ignore all the messages we can't get a date for
    messages = MailMessage.select(AND(MailMessage.q.listID==ml.id,
                                      MailMessage.q.date!=None),
                                  orderBy=MailMessage.q.date)
    if not firstDate:
        firstDate = messages[0].date
    if not lastDate:
        lastDate = messages.reversed()[0].date
    print firstDate, lastDate

    firstDate = timeutil.makeDateTimeFromShortString("%04d%02d%02d" %
                                                     (firstDate.year,
                                                      firstDate.month,
                                                      firstDate.day))

    bins = [[],[],[],[]]
    
    while firstDate < lastDate:
        nextDate = firstDate + timeutil.makeTimeDelta(days=delta)
        messages = MailMessage.select(AND(MailMessage.q.listID==ml.id,
                                          MailMessage.q.date >= firstDate,
                                          MailMessage.q.date < nextDate))
        numMessages = messages.count()
        newThreads = 0
        oldThreads = 0
        for msg in messages:
            if msg.replyTo == None:
                newThreads = newThreads + 1
            else:
                oldThreads = oldThreads + 1
        print "%04d-%02d-%02d, %d, %d, %d" % (firstDate.year,
                                              firstDate.month,
                                              firstDate.day,
                                              numMessages,
                                              newThreads,
                                              oldThreads)
        bins[0].append(abs(firstDate-MINDATE).days)
        bins[1].append(numMessages)
        bins[2].append(newThreads)
        bins[3].append(oldThreads)
        
        firstDate = nextDate

    return bins
    
if __name__ == "__main__":
    colors = "bgrcmyk"
    logging.basicConfig()
    log = logging.getLogger("timeAnalysis")
    log.setLevel(logging.INFO)

    parser = OptionParser()
    parser.add_option("-d", "--debug", action="store_true",
                      dest="verbose", default=False,
                      help="verbose debugging messages")
    parser.add_option("--dburi", "-u", dest="uri",
                      help="database name to connect to",
                      default="postgres://"+os.getenv("USER")+"@/cvsminer",
                      action="store")
    parser.add_option("--startdate", dest="startdate",
                      help="date to start graphs on",
                      default=None, action="store")
    parser.add_option("--stopdate", dest="stopdate",
                      help="date to stop graphs on",
                      default=None, action="store")
    
    (options, args) = parser.parse_args()

    if options.verbose:
        log.setLevel(logging.DEBUG)
    connect(options.uri, debug=options.verbose)

    clf()
    grid(True)
    xlabel("Date")
    ylabel("Number of posts")
    ax = subplot(111)
    ctr = 0
    if options.startdate or options.stopdate:
        if options.stopdate:
            endPoint = timeutil.makeDateTimeFromShortString(options.stopdate)
            endPoint = abs(endPoint - MINDATE).days
        else:
            endPoint = ax.get_xlim()[1]
        if options.startdate:
            startPoint = timeutil.makeDateTimeFromShortString(options.startdate)
            startPoint = abs(startPoint - MINDATE).days
        else:
            startPoint = ax.get_xlim()[0]
        ax.set_xlim(startPoint, endPoint)

    for x in args:
        bins = dumpMailList(x, delta=30)
        plot_date(bins[0],bins[1], fmt="%s-" % (colors[ctr]))
        plot_date(bins[0],bins[2], fmt="%s--" % (colors[ctr]))
        plot_date(bins[0],bins[3], fmt="%s:" % (colors[ctr]))

        ctr = ctr + 1

    savefig("newMessages.png")
