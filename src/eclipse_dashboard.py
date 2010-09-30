#!/usr/bin/python
"""
This script connects to the Eclipse Dashboard website and downloads
the summary documents for each month
"""
import urllib2
import os
import time

YEAR=2001
MONTH=4

STOPYEAR=2008
STOPMONTH=6

BASEURL="""http://dash.eclipse.org/dash/commits/web-api/commit-count-loc.php?month=%04d%02d"""
output_dir = "eclipse_dashboard"

while True:
    print "Fetching data for %04d%02d" % (YEAR, MONTH)
    data = urllib2.urlopen(BASEURL % (YEAR, MONTH)).read()
    f = open(output_dir + os.sep + "%04d%02d" % (YEAR, MONTH), "w")
    f.write(data)
    f.close()

    time.sleep(30)
    
    if YEAR == STOPYEAR and MONTH == STOPMONTH:
        break
    MONTH = MONTH + 1
    if MONTH == 13:
        MONTH = 1
        YEAR = YEAR + 1