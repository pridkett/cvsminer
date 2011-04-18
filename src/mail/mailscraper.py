#!/usr/bin/python
"""
mailscraper.py

This takes a set of mail archives, either specified as a set of
archives on the command line or by name from a mailing list site,
and downloads the archives.

unusual libraries required:

mechanize
"""

import gzip
import email
import mechanize
import re
import logging
import sys
import os
import stat
import time
from BeautifulSoup import BeautifulSoup

from optparse import OptionParser
from urllib2 import HTTPError

SHORT_SLEEP=5
LONG_SLEEP=30

def pull_all_gnome():
    # regular expression to calculate the size
    sizeRe = re.compile(r"^\[ Gzip'd Text (\d+) bytes \]$")
    mech = mechanize.Browser()
    baseUrl = "http://mail.gnome.org/archives"
    basePath = "/home/data/gnome/maillist/"
    try:
        mech.open(baseUrl)
    except Exception, e:
        log.error("Exception in opening page: %s", e)
    soup = BeautifulSoup(mech.response().read())

    # build the list of all of the urls -- this is a little tenuous right now
    urls = [baseUrl + "/" + x.findAll('a')[0]['href'][:-2] for x in soup.findAll('li')]
    for url in urls:
        projectName = [x for x in url.split("/") if x != ""][-1]
        log.info("Examining and downloading lists for project: %s", projectName)
        if url[-1] != "/": url = url + "/"
        log.debug("opening url: %s", url)
        try:
            mech.open(url)
        except Exception, e:
            log.error("Unable to open url: %s", url)
            continue
        soup = BeautifulSoup(mech.response().read())
        links = soup.findAll(href=re.compile(r".txt.gz$"))
        for link in links:
            fn = os.path.normpath(basePath + os.sep + projectName + "-" + link["href"])
            log.debug("Examining file: %s", fn)
            newSize = int(sizeRe.search(link.string).groups()[0])
            try:
                currentFileSize = os.stat(fn)[stat.ST_SIZE]
            except OSError, e:
                log.debug("File does not exist -- will download")
                currentFileSize = -1
            if currentFileSize >= newSize:
                log.debug("Not downloading archive - current size: %d, remote size: %d", currentFileSize, newSize)
                continue
            log.debug("Downloading file: %s", url + link['href'])
            mech.open(url+link['href'])
            response = mech.response()
            log.debug("Writing to file: %s", fn)
            f = file(fn,"wb")
            while 1:
                # read some data
                data = response.read(1024)
                if not data: break
                # save some data
                f.write(data)
            # close the file
            f.close()
            log.debug("Sleeping for %d seconds", SHORT_SLEEP)
            time.sleep(SHORT_SLEEP)
        log.debug("Sleeping for %d seconds", LONG_SLEEP)
        time.sleep(LONG_SLEEP)
            
            
            
        
def pull_archives(baseUrl, lists):
    downloaded_archives = {}
    mech = mechanize.Browser()
    # mech.set_handle_robots(robots)
    log.debug("opening up %s", baseUrl)
    try:
        mech.open(baseUrl)
    except HTTPError, e:
        log.exception("Error pulling down url: %s" % (url))
        return downloaded_archives
    log.debug("Page title: %s", mech.title())
    links = {}
    for listName in lists:
        log.debug("looking for links related to %s", listName)
        # now we find all of the links that we need
        try:
            links[listName] = mech.links(text_regex=re.compile(listName))
            log.debug("found %d lists", len(links[listName]))
        except Exception ,e:
            links[listName] = []
            log.warn("Could not find any links with the text '%s' at %s",
                     listName, mech.geturl())
            print e

    for listName in lists:
        log.info("Following links for %s [%d links]", listName, len(links[listName]))
        downloaded_archives[listName] = []
        for link in links[listName]:
            # click on that link
            log.debug("Following link: %s", link)
            mech.follow_link(link)
            # now search for gzip'd text links
            archiveLinks = mech.links(text_regex=re.compile("Gzip'd Text"))
            # open each of the links
            for archive in archiveLinks:
                fn = listName+"-"+archive.url.split("/")[-1]
                # open the url for the archive
                r=mech.follow_link(archive)
                # get the response
                # r = mech.response()
                # open the save file
                log.info("Downloading file %s", fn)
                downloaded_archives[listName].append(fn)
                f = file(fn,"wb")
                while 1:
                    # read some data
                    data = r.read(1024)
                    if not data: break
                    # save some data
                    f.write(data)
                # close the file
                f.close()
                mech.back()
            mech.back()
    return downloaded_archives

def pull_pipermail(listName, mech):
    foundLinks = []
    # now search for gzip'd text links
    archiveLinks = mech.links(text_regex=re.compile("Gzip'd Text"))
    # open each of the links
    for archive in archiveLinks:
        fn = listName+"-"+archive.url.split("/")[-1]
        # open the url for the archive
        r=mech.follow_link(archive)
        # get the response
        # r = mech.response()
        # open the save file
        log.info("Downloading file %s", fn)
        foundLinks.append(fn)
        # downloaded_archives[listName].append(fn)
        f = file(fn,"wb")
        while 1:
            # read some data
            data = r.read(1024)
            if not data: break
            # save some data
            f.write(data)
        # close the file
        f.close()
        mech.back()
    return foundLinks
    
def pull_listinfo(baseUrl, lists):
    """Assumes that the starting URL given is a Mailman page of mailing lists.
    """
    downloaded_archives = {}
    mech = mechanize.Browser()
    log.debug("opening up %s", baseUrl)

    try:
        mech.open(baseUrl)
    except HTTPError, e:
        log.exception("Error pulling down url: %s", url)
        return downloaded_archives

    links = {}
    for listname in lists:
        log.debug("looking for links related to %s", listname)
        try:
            links[listname] = mech.links(text=listname)
            log.debug("found %d lists", len(links[listname]))
        except:
            links[listname] = []
            log.warn("Could not find any links with the text '%s' at '%s'",
                     listname, mech.geturl())

    for listname in lists:
        log.info("Following links for %s [%d links]", listname, len(links[listname]))
        for link in links[listname]:
            mech.follow_link(link)
            log.debug("Now at: %s", mech.geturl())
            nextLink = mech.links(text="%s Archives" % listname)[0]
            mech.follow_link(nextLink)
            log.debug("Now at: %s", mech.geturl())
            downloaded_archives[listname] = pull_pipermail(listname, mech)
            mech.back()
            mech.back()
    return downloaded_archives
            
            
logging.basicConfig()
log = logging.getLogger("mailscraper")
log.setLevel(logging.WARN)
            
if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-d", "--debug", action="store_true",
                      dest="verbose", default=False,
                      help="Print verbose debugging messages")
    parser.add_option("-a", "--archives", dest="archives",
                      help="page listing is an archives page (see http://lists.gnome.org/archives)",
                      default=False, action="store_true")
    parser.add_option("-l", "--listinfo", dest="listinfo",
                      help="page listing is a listinfo page (see http://lists.ximian.com/ for example)",
                      default=False, action="store_true")
    parser.add_option("-p", "--pipermail", dest="pipermail",
                      help="page listing is a pipermail page (default)", 
                      default=False, action="store_true")
    parser.add_option("--allgnome", dest="allgnome",
                      default=False, action="store_true",
                      help="download all gnome.org mailing lists")
    
    (options, args) = parser.parse_args()

    if options.verbose:
        log.setLevel(logging.DEBUG)

    if options.allgnome:
        log.info("Pulling all gnome mailing list data")
        pull_all_gnome()
        sys.exit()
    
    if (options.archives and options.listinfo) or \
       (options.archives and options.pipermail) or \
       (options.listinfo and options.pipermail):
        log.error("only specify one of listinfo, pipermail, or archives")
        sys.exit()
        
    if not options.archives and not options.listinfo:
        options.pipermail = True

    if len(args) < 2:
        log.error("need to specify URL and list name on the command line")

    # if we were told to pull the archives, then pull them
    if options.archives:
        log.info("Using archive processing engine")
        an = pull_archives(args[0], args[1:])
    elif options.listinfo:
        log.info("Using listinfo processing engine")
        an = pull_listinfo(args[0], args[1:])
    elif options.pipermail:
        log.info("Using pipermail processing engine")
        log.error("pulling directly from a pipermail URL is not yet enabled")
        sys.exit()
    
