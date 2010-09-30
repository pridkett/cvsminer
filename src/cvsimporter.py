#!/usr/bin/python2.4
"""
cvsimporter.py

@author: Patrick Wagstrom
@contact: patrick@wagstrom.net
"""
import subprocess
import datetime
import re
import time
import codecs
import logging
import os
from optparse import OptionParser

MEMBER_RE = re.compile("(.*):([A-Z0-9\.]+)->([0-9\.]+)(\([A-Z]+\))?")

# Constants for parsing patch set information
PATCHSET_SPLIT = "---------------------"
DATE_FORMAT = "%Y/%m/%d %H:%M:%S"
MODE_NORMAL, MODE_MEMBERS, MODE_PATCHES, MODE_LOG = range(1, 5)
TAG_MEMBERS = "Members:"
TAG_PATCH = "Index:"
TAG_PATCH_ALT = "---"

# Set up the logging facilities
logging.basicConfig()
log = logging.getLogger("cvsimporter")

class FileDelta(object):
    """
    Represents a single change on a file.  Used as part of a patch set
    """
    def __init__(self, filename, oldver, newver, state=None):
        object.__init__(self)
        self.filename = filename
        self.oldver = oldver
        self.newver = newver
        self.state = state
        self.linesadded = 0
        self.linesremoved = 0
    
    def add_line(self):
        """
        Increments the counter indicating how many lines this file delta added
        """
        self.linesadded += 1
        
    def remove_line(self):
        """
        Increments the counter indicating how many lines this file delta removed
        """
        self.linesremoved += 1

    def __repr__(self):
        return "FileDelta [%s - added: %d, removed: %d, %s->%s, state: %s]" % (self.filename, self.linesadded, self.linesremoved, self.oldver, self.newver, self.state)

class PatchSet(object):
    """
    Represents a collection of files that were all modified at the same time
    """
    def __init__(self):
        """
        The default constructor doesn't set any properties
        """
        object.__init__(self)
        self.patchid = None
        self.author = None
        self.branch = None
        self.tag = None
        self.log = None
        self.date = None
        self.deltas = {}
        self.text = []
        
    def add_filedelta(self, delta):
        """
        Adds the delta of a single file to the collection of deltas for this
        patch set
        
        @param delta: a FileDelta object
        """
        self.deltas[delta.filename] = delta
        
    def __repr__(self):
        return "PatchSet [id=%s, %d files]\n    " % (self.patchid, len(self.deltas)) + "\n    ".join([str(x) for x in self.deltas.values()])
    
    def set_id(self, val):
        """
        Set the id number for this PatchSet
        
        @param val: an integer representing the value for this patch
        """
        self.patchid = unicode(val)
    
    def set_date(self, val):
        """
        Sets the date for the PatchSet
        
        @param val: a python datetime object
        """
        self.date = val
    
    def set_author(self, val):
        """
        Sets the name the author of this patchset
        
        @param val: the string name of the author
        """
        self.author = unicode(val)

    def set_branch(self, val):
        """
        Sets the branch of the code that this revision was committed to
        
        @param val: the name of the branch, something like HEAD
        """
        self.branch = unicode(val)
        
    def set_tag(self, val):
        """
        Sets the tag applied to this commit operation
        
        Strictly speaking, this is probably not always correct.  Mainly because
        of the fact that tags are sorta strange and may apply to only some files
        that were committed together.
        
        @param val: the name of the tag
        """
        self.tag = unicode(val)
        
    def set_log(self, val):
        """
        
        @param val:
        """
        self.log = unicode(val)

    def add_line(self, filename):
        """
        Informs the patch to add a line to the filedelta for a given file
        
        @param filename: the name of the file
        """
        altfilename = filename.replace("+++ -", "&")
        if self.deltas.has_key(filename):
            self.deltas[filename].add_line()
        elif self.deltas.has_key(altfilename):
            self.deltas[altfilename].add_line()
        else:
            log.warn("patch requested file [%s] -- not found", filename)
    
    def remove_line(self, filename):
        """
        Informs the patch to remove a line to the filedelta for a given file
        
        @param filename: the name of the file
        """
        try:
            self.deltas[filename].remove_line()
        except KeyError:
            log.warn("patch requested file [%s] -- not found", filename)
    
    def append_text(self, newtext):
        """
        The text item keeps track of all the text for a given patchset
        
        @param newtext: the line of text to add
        """
        self.text.append(unicode(newtext)) 
        
    def length(self):
        """
        Gets the lengths of the patchset in lines.  This includes all the other
        assorted stuff that goes with the patchset.
        
        @return: the length of the patch in lines
        @rtype: integer
        """
        return len(self.text)

def import_module(cvsroot, module, diffs=True, fromFile=False, cache=False):
    """
    
    @param cvsroot:
    @param module:
    @param diffs:
    @param fromFile: boolean on if we should force to read from file
    @param cache: boolean if we should try to open 
    """

    filename = "cvsps-%s-%s.txt" % ("_".join([x for x in cvsroot.split("/") if x]), module)
    if cache:
        try:
            open(filename)
            fromFile = True
            log.info("loading from file: %s", filename)
        except IOError:
            log.info("cache file %s not found", filename)
            pass
    if not fromFile:
        # make certain we're working with a directory here
        if not os.path.isdir(cvsroot + os.sep + module):
            raise IOError("Location %s is not a directory")
        if diffs:
            commandstr = ["cvsps", "--cvs-direct", "-g", "--root", cvsroot, module]
        else:
            commandstr = ["cvsps", "--cvs-direct", "--root", cvsroot, module]
        log.debug("executing command: %s", " ".join(commandstr))
        proc = subprocess.Popen(commandstr,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True, bufsize=1024)
        # trash all that stuff
        proc.stderr.close()
        data = unicode(proc.stdout.read(), encoding="latin-1")
        
        # save a copy of the data
        outfile = codecs.open(filename, "w", "latin-1")
        outfile.write(data)
        outfile.close()
    else:
        log.debug("reading file: %s", filename)
        data = codecs.open(filename, "r", "latin-1").read()
    log.debug("%d bytes of output from cvsps obtained", len(data))
    patchsets = process_data(data)
    return patchsets
    
def parse_member(member, patchset):
    """
    Parses elements of the cvsps output that indicate the members of a patchset.
    
    For example, in the following output, it should create FileDelta objects
    for config and loginfo.
    
    PatchSet 11
    Date: 2001/10/10 20:21:35
    Author: kmoir
    Branch: HEAD
    Tag: (none)
    Log:
    config

    Members:
        config:1.3->1.4
        loginfo:1.5->1.6

    @param patchset: the PatchSet the member is from
    @param member: the line from the output of cvsps like this 
                   "scenarios/PDEScenarios3_3.html:1.2->1.3"
    """
    member = member.strip()
    res = MEMBER_RE.match(member)
    if res:
        filename, originalversion, newversion, newstate = res.groups()
        delta = FileDelta(filename=filename, oldver=originalversion, newver=newversion, state=newstate)
        patchset.add_filedelta(delta)
    else:
        raise Exception("Unable to parse member completely")
        
def process_data(data):
    """
    
    @param data: output from cvsps
    """
    patchsets = []
    currentline = 0
    # split the data if it's just a string
    if data.__class__ == str or data.__class__ == unicode:
        data = data.splitlines()
    while currentline < len(data):
        newpatchset = process_patchset(data[currentline:])
        patchsets.append(newpatchset)
        currentline = currentline + newpatchset.length()
        log.debug("properly imported patchset %s -- up to line %d", newpatchset.patchid, currentline)
    return patchsets
        
def process_patchset(data):
    """
    Processes the data for a single patchset information
    
    This has some interesting peculiarities that arise when parsing.  Namely, the output
    must be exactly that of cvsps -- this means that tabs must remain tabs.
    
    @param data: string of the data from cvsps
    @rtype: a two tuple of a PatchSet and the last line
    """
    if data.__class__ == str or data.__class__ == unicode:
        data = data.splitlines()
    currentpatch = PatchSet()
    currentmode = MODE_NORMAL
    currentlog = ""
    currentfilepatch = None
    for lineno, thisline in enumerate(data):
        currentpatch.append_text(thisline)
        if thisline == PATCHSET_SPLIT:
            if lineno == 0:
                continue
            # this handles a very odd degenerate case...yech
            if currentmode == MODE_PATCHES and len(data) > lineno+1 and not data[lineno+1].startswith("PatchSet"):
                pass
            else:
                return currentpatch
        if currentmode == MODE_NORMAL and thisline.strip():
            try:
                key, val = thisline.strip().split(" ", 1)
            except ValueError:
                key = thisline.strip()
                val = None
            if key == "PatchSet":
                currentpatch.set_id(int(val))
            elif key == "Date:":
                ttime = time.strptime(val, DATE_FORMAT)
                currentpatch.set_date(apply(datetime.datetime, ttime[:7]))
            elif key == "Author:":
                currentpatch.set_author(val)
            elif key == "Branch:":
                currentpatch.set_branch(val)
            elif key == "Tag:":
                if val != "(none)":
                    currentpatch.set_tag(val)
            elif key == "Log:":
                currentmode = MODE_LOG
                currentlog = ""
            elif key == TAG_MEMBERS:
                currentmode = MODE_MEMBERS
            elif key == TAG_PATCH:
                currentmode = MODE_PATCHES
                currentfilepatch = val.split("/", 1)[1]
                patchcounting = False
            elif key == TAG_PATCH_ALT:
                currentmode = MODE_PATCHES
                currentfilepatch = get_patch_file(thisline, data[lineno+1])
                patchcounting = False
            else:
                raise Exception("Unknown key value in parsing line %d: %s" %
                                 (lineno, key))
            
        elif currentmode == MODE_LOG:
            try:
                if data[lineno+1].strip() == TAG_MEMBERS:
                    currentpatch.set_log(currentlog)
                    currentlog = ""
                    currentmode = MODE_NORMAL
                else:
                    currentlog = currentlog + thisline + "\n"
            except:
                raise Exception("end of data stream: " + thisline)
                
        
        elif currentmode == MODE_MEMBERS:
            if not(thisline.strip()):
                currentmode = MODE_NORMAL
            else:
                parse_member(thisline, currentpatch)
            
        elif currentmode == MODE_PATCHES:
            if thisline.startswith("@@"):
                patchcounting = True
            if patchcounting and thisline.startswith("--- ") and len(data) > lineno + 2 and data[lineno+1].startswith("+++ ") and data[lineno+2].startswith("@@ "):
                try:
                    currentfilepatch = get_patch_file(thisline, data[lineno+1])
                    patchcounting = False
                except:
                    print "strange patch formatting on line %d of patch %s" % (lineno, currentpatch.patchid)
            if patchcounting:
                if thisline and thisline[0] == "+":
                    currentpatch.add_line(currentfilepatch)
                if thisline and thisline[0] == "-":
                    currentpatch.remove_line(currentfilepatch)
                if len(data) > lineno + 1 and data[lineno+1].startswith(TAG_PATCH):
                    currentmode = MODE_NORMAL
        
    return currentpatch

def get_patch_file(thisline, nextline):
    """
    Given a patch information header, get the filename we're really concerned about

    Here's an example string to parse:
    
--- pde-ui-home/scenarios/PDEScenarios3_0.html     2008-03-27 17:59:08.785562000 -0400
+++ /dev/null      2004-06-24 14:05:26.000000000 -0400
    
    @param thisline: first line of header
    @param nextline: second line of header
    """

    # fix edge case error where & is replaced with +++ -
    try:
        if thisline.startswith("--- /dev/null"):
            patchfile = nextline.split("\t")[0].split("/", 1)[1]
        else:
            patchfile = thisline.split("\t")[0].split("/", 1)[1]
        return patchfile
    except IndexError:
        raise Exception("l1[%s] - l2[%s]" % (thisline, nextline))

def save_patchset(cvsroot, module, patch):
    """
    saves a given patch to the database
    
    @param patch: a PatchSet object
    """
    print patch


def main_test():
    parser = OptionParser()
    parser.add_option("-l", "--loglevel", dest="loglevel",
                      help="Manually specify logging level (DEBUG, INFO, WARN, etc)",
                      default="INFO", action="store") 
    parser.add_option("-c", "--cvsroot", dest="cvsroot",
                      help="root CVS directory",
                      action="store", default="/home/data/eclipse/cvsroot")
    parser.add_option("-m", "--module", dest="module",
                      help="module to examine",
                      action="store", default="org.eclipse.platform")
    parser.add_option("--usecache", dest="usecache",
                      help="try to use a cache",
                      action="store_true", default=False)
    (options, args) = parser.parse_args() # IGNORE:W0612
    log.setLevel(getattr(logging, options.loglevel.upper()))

    # cvsroot = "/home/data/eclipse/cvsroot/eclipse"
    # module = "org.eclipse.platform"
    patchsets = import_module(options.cvsroot, options.module, cache=options.usecache)
    for pset in patchsets:
        save_patchset(options.cvsroot, options.module, pset)
             
if __name__ == "__main__":
    main_test()
