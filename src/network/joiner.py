#!/usr/bin/python2.4
"""
jointer.py

join the data from lots of files
"""

__author__ = "Patrick Wagstrom <pwagstro@andrew.cmu.edu>"
__copyright__ = "Copyright (c) 2006 Patrick Wagstrom"
__license__ = "GNU General Public License Version 2"

import csv
import logging
import os
from optparse import OptionParser
import sys

class CSVNet:
    def __init__(self, col, name=None):
        self.keys = {}
        self.name = name or "Unknown"
        self.col = col

    def storeValue(self, id, col, val):
        if id not in self.keys.keys():
            self.keys[id] = [None] * (col + 1)
        if len(self.keys[id]) <= col:
            self.keys[id] = self.keys[id] + [None]*(col - len(self.keys[id]) + 1)
        try:
            self.keys[id][col] = val
        except:
            print "Current Net: ", self.keys[id]
            print "Adding: key=%s, column=%d, cal=%s, len=%d" % (id, col, val, len(self.keys[id]))
            raise Exception("FUCK")

    def dumpStream(self, stream=sys.stdout):
        writer = csv.writer(stream)
        for item in [[key] + val for key,val in self.keys.iteritems()]:
            writer.writerow(item)

def mergeData(files, skip=2, coldefs=None):
    nets = []
    count = 0
    if coldefs:
        for coldef in [x.strip() for x in coldefs.split(",")]:
            col, name = coldef.split("=")
            log.info("Creating network...")
            nets.append(CSVNet(name=name, col=int(col)))
    for fn in files:
        log.info(fn)
        reader = csv.reader(open(fn))
        ctr2 = 0
        for l in reader:
            if not nets:
                nets = []
                for x in xrange(len(l)-1):
                    nets.append(CSVNet(name="col%d"%x, col=x+1))
            ctr2 = ctr2 + 1
            if ctr2 <= skip: continue
            if len(l) == 0: continue
            id = l[0]
            for n in nets:
                n.storeValue(id, count, l[n.col])
        count = count + 1

    for n in nets:
        log.info("Dumping network to %s.out.csv" % (n.name))
        f = open("%s.out.csv" % n.name,"w")
        n.dumpStream(f)
        f.close()
        
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
    parser.add_option("-s", "--skiplines", dest="skiplines", default=1,
                      type="int", action="store")
    parser.add_option("-c", "--columns", dest="coldefs", default=None,
                      type="string", action="store",
                      help="Column Definitions (ie 1=Centrality,2=Foo,3=Bar)")
    log.debug("parsing command line arguments")
    (options, args) = parser.parse_args()

    if options.debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(getattr(logging,options.loglevel.upper()))

    mergeData(args,skip=options.skiplines, coldefs=options.coldefs)
