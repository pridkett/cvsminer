from dbobjects import *
import os
import logging
import sys
from optparse import OptionParser
from dbobjects import *

def print_usage():
    print """projectJoiner.py - loads a series of projects and joins them together."""
    print """ usage: projectJoiner.py COMMUNITY INPUTFILE"""
    
if __name__ == "__main__":
    logging.basicConfig()
    log = logging.getLogger("projectJoiner")
    log.setLevel(logging.INFO)

    parser = OptionParser()
    parser.add_option("-d", "--debug", action="store_true",
                      dest="verbose", default=False,
                      help="verbose debugging messages")
    parser.add_option("--dburi", "-u", dest="uri",
                      help="database name to connect to",
                      default="postgres://"+os.getenv("USER")+"@/cvsminer",
                      action="store")
    
    (options, args) = parser.parse_args()

    if options.verbose:
        log.setLevel(logging.DEBUG)

    if len(args) < 2:
        print_usage()
        sys.exit()
        
    connect(options.uri, debug=options.verbose)

    comm = Community.select(Community.q.name == args[0])[0]
    
    for fn in args[1:]:
        for pairing in ([y.strip() for y in x.strip().split(",")] for x in open(fn).readlines() if x.strip() and not x.strip().startswith("#")):
            fail = False
            mp = MasterProject.select(AND(MasterProject.q.name==pairing[0], MasterProject.q.communityID==comm.id))
            if not mp.count():
                print "Master Project: %s not found, will need to create" % (pairing[0])
                mp = MasterProject(name=pairing[0], community=comm)
            else:
                mp = mp[0]
            sp = map(lambda x: Project.select(Project.q.name==x), pairing[1:])
            for z in sp:
                if not z.count():
                    print "Sub Project: %s not found" % (z)
                    fail = True
            if fail:
                continue
            sp = (x[0] for x in sp)
            for thisProj in sp:
                oldMaster = thisProj.masterProject
                if thisProj.masterProject == mp:
                    continue
                thisProj.masterProject = mp
                if len(oldMaster.projects) == 0:
                    print "Old Master %s is empty - could remove" % (oldMaster.name) 
                
        

