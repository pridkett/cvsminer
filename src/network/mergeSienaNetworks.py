#!/usr/bin/python2.4
"""
mergeSienaNetworks.py

This program will merge two siena networks into a single new siena network
"""

import logging
import os
from optparse import OptionParser
import dynet

logging.basicConfig()
log = logging.getLogger("sienaNetworks.py")
log.setLevel(logging.INFO)

def mergeNetworks(infile1, infile2, outfile):
    """This method combines two files...simple enough"""
    outnetwork = []
    inlines1 = [x.split() for x in open(infile1).readlines()]
    inlines2 = [x.split() for x in open(infile2).readlines()]

    if len(inlines1) != len(inlines2):
        log.error("Files are not the same length")

    currentLen = len(inlines1[0])
    for x in inlines1 + inlines2:
        if len(x) != currentLen:
            log.error("line length disaggrees")
            
    outnetwork = [[0]*currentLen]*currentLen

    for x in xrange(0, currentLen):
        for y in xrange(0, currentLen):
            outnetwork[x][y] = str(int(inlines1[x][y]) + int(inlines2[x][y]))

    # of = open(outfile,"w")
    for l in outnetwork:
        print " ".join(l)
        
if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-l", "--loglevel", dest="loglevel",
                      help="Manually specify logging level (DEBUG, INFO, WARN, etc)",
                      default="INFO", action="store")   

    log.debug("parsing command line arguments")
    (options, args) = parser.parse_args()

    log.setLevel(getattr(logging,options.loglevel.upper()))

    infile1 = args[0]
    infile2 = args[1]
    outfile = args[2]

    mergeNetworks(infile1, infile2, outfile)
    


