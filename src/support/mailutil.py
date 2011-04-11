#!/usr/bin/python
"""
mailutil.py

This is a set of functions related to opening and manipulation of mailbox
files on unix systems. Usually these files are taken from mailing list
archive programs.

Eventually this class should provide a subclassed object of a unix mailbox
file that handles all of this file I/O transparently.
"""

__author__ = "Patrick Wagstrom"
__copyright__ = "Copyright (c) 2005 Patrick Wagstrom"
__license__ = "GNU General Public License version 2 or later"

import gzip
import email
import mailbox
import re
import logging
import rfc822
import sys
import os
import timeutil
import tempfile

# BZ2 format is only on Python 2.3 and newer
try:
    import bz2
    HAS_BZ2 = True
except:
    HAS_BZ2 = False

from optparse import OptionParser

def openMailList(filename, cache=False):
    """Simple handler to try and see if a file is gzipped or not and then open
    it up properly.

    In general, if you're dealing with compressed files, you'll want to use the
    cached file whenever dealing with compressed files as the python mbox commands
    end up doing a lot of seeking, which is very slow on compressed file.  The
    cache commend uncompresses the file to a TemporaryFile, which you don't have to
    worry about removing.

    @param filename: the name of the file to open up
    @param cache: whether or not to return a temporary file as the handle
    """
    ext = os.path.splitext(filename)
    ok = False
    if ext[-1] == ".gz":
        fp = gzip.GzipFile(filename,"rb")
        try:
            fp.read(1)
            fp.rewind()
            ok = True
        except Exception, e:
            ok = False
            fp.close()
    elif HAS_BZ2 and ext[-1] == ".bz2":
        fp = bz2.BZ2File(filename, "rb")
        try:
            fp.read(1)
            fp.rewind()
            ok = True
        except:
            ok = False
            fp.close()
    if ok==True and cache == True:
        fp2 = tempfile.TemporaryFile()
        while 1:
            data = fp.read(1024)
            if not data: break
            fp2.write(data)
        fp.close()
        fp = fp2
    if ok == False:
        fp = open(filename)
    return fp

class MailList(mailbox.PortableUnixMailbox):
    """Simple wrapper class that also handles issues with opening and closing
    of the files

    example:
    import mailutil
    mbox = mailutil.MailList('list-archive-2001-05.txt.gz')
    msg = mbox.next()
    while msg != None:
        print msg['subject'], msg['from']
        msg = mbox.next()
    """
    def __init__(self, filename, cache=True):
        """Initializes a mailbox object.

        @param filename: filename to open up
        @param cache: should we create a temporary file, useful for compressed archives
        """
        self.fp = openMailList(filename, cache)
        mailbox.PortableUnixMailbox.__init__(self, self.fp, email.message_from_file)

    def close(self):
        """Closes the remaining file handles"""
        self.fp.close()
        self.fp = None

    def __del__(self):
        """Ensure that the file handle has actually been closed
        """
        if self.fp != None:
            self.fp.close()
        if hasattr(mailbox.UnixMailbox, '__del__'):
            mailbox.UnxiMailbox.__del__(self)
        
        
