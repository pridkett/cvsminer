#!/usr/bin/python

"""
loadMailLists.py

Loads a set of mailing lists into the database.  By default it assumes that the
mailing list name can be obtained from the filename passed in.  It will check to
see if the the messages for a list have already been loaded, and if they have, not
load them again.

unsual libraries required:
mailutil - from support SVN archive
timeutil - from support SVN archive
"""

__author__ = "Patrick Wagstrom"
__copyright__ = "Copyright (c) 2005-2011 Patrick Wagstrom"
__license__ = "GNU General Public License version 2 or later"

import sys
import os
sys.path.append(os.path.join(os.path.split(os.path.abspath(__file__))[0], os.path.pardir))
sys.path.append(os.path.join(os.path.split(os.path.abspath(__file__))[0], os.path.pardir, "support"))

import logging
import sys
from optparse import OptionParser
import timeutil
import mailutil
import decodeh
import rfc822
import random
import re
from sets import Set

from dbobjects import *
from sqlobject import AND

def removeDupes():
    """This routine removes duplicates from the database
    """
    # XXX: this routine may actually be overly aggresive with removing entities
    # need to check this out in more detail.  The other alternative is that there
    # are hundreds of thousands of duplicate email messages in the GNOME mail
    # archives

    # first we get all of the message_ids
    query = """SELECT mail_message_id, message_id, mailing_list_id FROM mail_message
                WHERE message_id != '##UNKNOWN##'
                ORDER BY mailing_list_id"""
    results = MailMessage._connection.queryAll(query)
    log.debug("Retreived information for %d messages", len(results))

    sqlhub = get_sql_hub()
    connection = sqlhub.getConnection()
    currentList = None
    for res in results:
        if res[2] != currentList:
            currentDict = {}
            currentList = res[2]
        # see if we currently have a key for this message
        if currentDict.has_key(res[1]):
            conn = connection.transaction()
            sqlhub.threadConnection = conn
            log.debug("found a dupe: %s - list: %d", res[1], res[2])
            updateStatement = Update(MailMessage.sqlmeta.table, {sqlrepr(MailMessage.q.parentID).split(".")[-1]: currentDict[res[1]]},
                                     where=(MailMessage.q.parentID==res[0]))
            log.debug("executing: %s", sqlrepr(updateStatement))
            conn.query(sqlrepr(updateStatement))
            
            deleteToStatement = Delete(MailRecipient.sqlmeta.table, where=(MailRecipient.q.messageID == res[0]))
            log.debug("executing: %s", sqlrepr(deleteToStatement))
            conn.query(sqlrepr(deleteToStatement))

            deleteRefStatement = Delete(MailReference.sqlmeta.table, where=(MailReference.q.messageID == res[0]))
            log.debug("executing: %s", sqlrepr(deleteRefStatement))
            conn.query(sqlrepr(deleteRefStatement))
            
            deleteStatement = Delete(MailMessage.sqlmeta.table, where=(MailMessage.q.id == res[0]))
            log.debug("executing: %s", sqlrepr(deleteStatement))
            conn.query(sqlrepr(deleteStatement))
            log.debug("committing");
            conn.commit()
            sqlhub.threadConnection = connection
        else:
            currentDict[res[1]] = res[0]
            
def random_string(length=40):
    """Builds a random string comprised of letters and numbers.  Needed to give
    identification to some meessages that don't have proper identification
    """
    letters = "abcdefghijklmnopqrstuvwxyz"
    letters += letters.upper() + "0123456789"
    
    # The random starts out empty, then 40 random possible characters
    # are appended.
    random_string = ''
    for i in range (length):
        random_string += random.choice (letters)
        
    # Return the random string.
    return random_string

def uniq(alist):    # Fastest without order preserving
    set = {}
    map(set.__setitem__, alist, [])
    return set.keys()


def print_usage():
    """Simple method to give some usage help on the program
    """
    print """loadMailLists.py -

This program is designed to automatically load lots of mailing lists into the
bug database.  Please make sure that maillists.sql has been imported FIRST or
this program will die.

USAGE:

loadMailLists.py [options] SOURCEFILE1 [SOURCEFILE2, ...]

For more help on command line arguments, use the -h flag"""
    sys.exit()


reassigned = Set()
def reparentMessage(child_id, parent_id, child_list=None, parent_list=None):
    global reassigned
    if child_id in reassigned:
        if child_list == None or child_list != parent_list:
            log.info("Message %d has already been reparented" % child_id)
        log.debug("reparenting to appropriate parent in same list")
    reassigned.add(child_id)
    child_id = int(child_id)
    parent_id = int(parent_id)
    child = MailMessage.get(child_id)
    parent = MailMessage.get(parent_id)
    child.parent = parent
    log.debug("Update parent for message: %d=>%d (%s, %s)", child_id, parent_id, child.replyTo, parent.messageID)
    
def reparentMessages():
    """Just executes the query to reparent all of the messages in the system"""
    log.info("Reparenting all unparented messages.  This will take a VERY long time")
#     query ="""UPDATE mail_message set message_parent=a.mail_message_id
#                 FROM (SELECT a.mail_message_id FROM mail_message a where a.message_id = in_reply_to) AS a
#                WHERE message_parent is null and in_reply_to is not null"""
#     MailMessage._connection.query(query)
    INCREMENT=1000
    sqlhub = get_sql_hub()
    ctr = 0
    while True:
        oldConn = sqlhub.getConnection()
        conn = oldConn.transaction()
        sqlhub.threadConnection = conn
        query = """select a.mail_message_id, b.mail_message_id, a.mailing_list_id, b.mailing_list_id from mail_message a, mail_message b where a.in_reply_to = b.message_id and a.message_parent is null limit %d""" % (INCREMENT)
        res = conn.queryAll(query)
        ctr = ctr + INCREMENT
        log.debug("Loaded through message %d", ctr)
        if len(res) == 0: break
        map(lambda x: reparentMessage(x[0],x[1], x[2], x[3]), res)
        conn.commit()
        sqlhub.threadConnection = oldConn
        if ctr % 2500 == 0:
            log.info("clearning cache")
            oldConn.cache.clear()

def updateMessageToEmail(message_to_id, email_id):
    query = """UPDATE mail_message_to set email_address_id=%d WHERE mail_message_to_id=%d""" % (message_to_id, email_id)
    # MailMessage._connection.query(query)
    mr = MailRecipient.get(message_to_id)
    em = EmailAddress.get(email_id)
    mr.email = em
    log.debug("Updated email_to for message: %d email: %d", message_to_id, email_id)

def updateMessageEmail(message_id, email_id):
    query = """UPDATE mail_message set email_address_id=%d WHERE mail_message_id=%d""" % (message_id, email_id)
    # MailMessage._connection.query(query)
    mm = MailMessage.get(message_id)
    em = EmailAddress.get(email_id)
    mm.email = em
    log.debug("Updated email for message: %d email: %d", message_id, email_id)
    
def linkMessages():
    """Links messages based on email addresses to the users they belong to"""
#     query = """UPDATE mail_message SET email_address_id=email_address.email_address_id
#                  FROM email_address WHERE email_address.email = mail_message.email
#                       AND mail_message.email_address_id is null"""
#     MailMessage._connection.query(query)


    # XXX: this is an alternative method to do this that provides status information
    INCREMENT=4000
    addressHash = {}
    map(lambda x: addressHash.__setitem__(x[0],x[1]), MailMessage._connection.queryAll("SELECT email, email_address_id FROM email_address"))
    log.info("loaded %d email addresses", len(addressHash))

    ctr = 0
    sqlhub = get_sql_hub()
    while True:
        oldConn = sqlhub.getConnection()
        conn = oldConn.transaction()
        sqlhub.threadConnection = conn
        query = """select mail_message_id, mail_message.email from mail_message, email_address where mail_message.email = email_address.email and mail_message.email_address_id is null limit %d""" % (INCREMENT)
        ctr = ctr + INCREMENT;
        log.debug("loaded through message %d", ctr)
        results = MailMessage._connection.queryAll(query)
        if len(results) == 0:
            break
        map(lambda x: updateMessageEmail(x[0], x[1]), ([y[0], addressHash[y[1]]] for y in results if addressHash.has_key(y[1])))
        conn.commit()
        sqlhub.threadConnection = oldConn
        if ctr % 2500 == 0:
            log.info("clearing cache")
            oldConn.cache.clear()

    # on to the next stage, where we try to link up the mail_message_to
    ctr = 0
    while True:
        oldConn = sqlhub.getConnection()
        conn = oldConn.transaction()
        sqlhub.threadConnection = conn
        query = """select mail_message_to_id, email_address.email_address_id from mail_message_to, email_address where mail_message_to.email = email_address.email and mail_message_to.email_address_id is null limit %d""" % (INCREMENT)
        ctr = ctr + INCREMENT;
        log.debug("loaded through message recipient %d", ctr)
        results = MailMessage._connection.queryAll(query)
        if len(results) == 0:
            break
        map(lambda x: updateMessageToEmail(x[0], x[1]), results)
        conn.commit()
        sqlhub.threadConnection = oldConn
        if ctr % 2500 == 0:
            log.info("clearing cache")
            oldConn.cache.clear()

def deList(it):
    """Recursively goes through a list and breaks out the elements, then concatenates
    all of the elements together that were in the list.  This routine makes no effort
    at all to handle spacing, and assumes that the elements in the file have spacing
    already included in the strings.

    For example:
    deList(["hello", "world"]) => "helloworld"
    deList(["this", [" is a ", [ "test" ]]]) => "this is a test"
    """
    if hasattr(it,"append"):
        tmpPL = ""
        for pl in it:
            tmpPL = tmpPL + deList(pl)
        return tmpPL
    return str(it)

    
def loadFile(filename, maillist, fromHack=False, purge=False, purge_only=False):
    """Loads and archive of mailing list messages into the database. Right
    now this function does not handle running multiple times over the
    same mailing list.  That's an outsanding bug.

    @param filename: - the filename to load
    @param mc: a dict to cache messages into
    @param maillist: a dbobjects.MailList object to set as the list object

    The in-reply to isn't specified anymore, instead, the following SQL
    command will hopefully load all of the data and set everything right.
    
    UPDATE mail_message set message_parent=a.mail_message_id
      FROM (SELECT a.mail_message_id FROM mail_message a where a.message_id = in_reply_to) AS a
     WHERE message_parent is null and in_reply_to is not null;
    """
    nummsgs = 0
    referencesRE = re.compile(r"(<[^>]+>)")

    log.info("processing file %s", filename)

    shortFN = os.path.split(filename)[1]
    archive = MailFileArchive.select(AND(MailFileArchive.q.filename==shortFN,
                                     MailFileArchive.q.listID==maillist.id))

    # FIXME: this is an outstanding bug that needs to be addressed, basically
    # we can't double load a file, in the future we should check to see if the
    # entries have already been handled
    if archive.count() > 0:
        if not purge:
            log.error("Archive %s has already been loaded.  For right now, we don't handle this, in the future, we will.", filename)
            return 0
        else:
            log.warn("Archive %s has already been loaded, proceeding with purge", filename)
            query = """DELETE FROM mail_message_to WHERE mail_message_id IN
                                   (select mail_message_id from mail_message where mail_file_archive_id=%d)""" % (archive[0].id)
            log.debug("executing query: %s", query)
            MailMessage._connection.query(query)
            query = """DELETE FROM mail_message_reference WHERE mail_message_id IN
                                   (select mail_message_id from mail_message where mail_file_archive_id=%d)""" % (archive[0].id)
            log.debug("executing query: %s", query)
            MailMessage._connection.query(query)
            query = "DELETE FROM mail_message WHERE mail_file_archive_id=%d" % (archive[0].id)
            log.debug("executing query: %s", query)
            MailMessage._connection.query(query)
            archive = archive[0]
    else:
        archive = None
    if purge_only:
        log.info("purge only called, returning")
        return 0
    # try to get the month from archive
    short = os.path.splitext(shortFN)
    if short[1] == '.gz':
        short = os.path.splitext(short[0])
    month = short[0].split("-")[-1]
    year = short[0].split("-")[-2]

    # build the start and stop dates for the archive
    startDate=timeutil.makeDateTimeFromShortString("%04d%02d01" % (int(year), timeutil.getMonth(month)))
    stopDate=timeutil.addMonths(startDate,1) - timeutil.makeTimeDelta(seconds=1)

    if not archive:
        archive = MailFileArchive(filename=shortFN, list=maillist,
                                  startDate=startDate, stopDate=stopDate)
    
    mbox = mailutil.MailList(filename)
    msg = mbox.next()
    lastDate = None
    while msg != None:
        log.debug("processing message: %s", msg['Message-Id'])
        fromList =  [x for x in rfc822.AddressList(msg['From']).addresslist]
        toList = [x[1].lower() for x in rfc822.AddressList(msg['To']).addresslist]
        toNames = [x[0].lower() for x in rfc822.AddressList(msg['To']).addresslist]
        ccList = [x[1].lower() for x in rfc822.AddressList(msg['cc']).addresslist]
        ccNames = [x[0].lower() for x in rfc822.AddressList(msg['cc']).addresslist]
        try:
            msgFrom = fromList[0][1].lower()
        except:
            log.warn("From not properly defined")
            msgFrom = "CVSMINERFAILURE@CVSMINER.ORG"
        try:
            msgFromName = fromList[0][0].lower()
        except:
            log.warn("From name not properly defined")
            msgFromName = None

        if fromHack:
            msgFrom = msg['From'].replace(" at ","@").split()[0]

        try:
            timestamp = timeutil.makeDateTimeFromTuple(rfc822.parsedate(msg['date']))
        except:
            log.warn("Error parsing date: %s - setting to None", msg['date'])
            timestamp = None

        try:
            messageId = msg['Message-Id'].split(";")[0]
        except:
            messageId = None
        if not messageId:
            messageId = "::CVSMINER::-"+random_string(length=64)
        # FIXME: messageID should be a little more robust in searching out
        # properly formatted messages

        pl = deList(msg.get_payload())
        # pl = str(msg.get_payload())
        if hasattr(pl,"append"):
            log.debug("is list")
            tmpPl = ""
            for payload in pl:
                tmpPl = tmpPl + payload.get_payload()
            pl = tmpPl

        if msg['In-Reply-To']:
            replyTo = msg['In-Reply-To'][:255].split(";")[0].strip()
        else:
            replyTo = None
            
        if msgFrom: msgFrom = msgFrom[:255]
        if msgFromName: msgFromName = msgFromName[:255]
        if msg['Subject']:
            subject = msg['Subject'][:255]
        else:
            subject = "::CVSMINER:: Subject Not Defined"
        if messageId: messageId = messageId[:255]

        try:
            m = create_mail_message(fromemail=msgFrom, fromname=msgFromName, subject=subject, body=pl,
                                    date=timestamp, messageid=messageId, maillist=maillist,
                                    archive=archive, replyto=replyTo)
        except UnicodeError:
            log.error("Unable to parse message no matter how hard I try...")
            msg = mbox.next()
            continue
                

        # map all of the references for the message
        if msg['References']: map(lambda x: create_mail_reference(message=m, reference=x), referencesRE.findall(msg['References']))

        # seen is a dict that we use to track already captured email
        # addresses
        seen = {}
        for recip in zip(toList, toNames):
            if not seen.has_key(recip[0]):
                try:
                    mr = create_mail_recipient(message=m, toemail=recip[0], toname=recip[1], isto=True)
                    seen[recip[0]] = 1
                except UnicodeDecodeError:
                    pass
        for recip in zip(ccList,ccNames):
            if not seen.has_key(recip[0]):
                try:
                    
                    mr = create_mail_recipient(message=m, toemail=recip[0], toname=recip[1], isto=False)
                    seen[recip[0]] = 1
                except UnicodeDecodeError:
                    pass
            
        msg = mbox.next()
        nummsgs = nummsgs + 1
    return nummsgs

def create_mail_message(fromemail, fromname, subject, body, date, messageid, maillist, archive, replyto):
    try:
        return MailMessage(fromEmail=fromemail, fromName=fromname, subject=subject, body=body,
                            date=date, messageID=messageid, list=maillist,
                            archive=archive, replyTo=replyto)
    except UnicodeDecodeError:
        pass
    return MailMessage(fromEmail=decodeh.decode(fromemail), fromName=decodeh.decode(fromname),
                       subject=decodeh.decode(subject), body=decodeh.decode(body),
                       date=date, messageID=decodeh.decode(messageid), list=maillist,
                       archive=archive, replyTo=decodeh.decode(replyto))
    

def create_mail_recipient(message, toemail, toname, isto):
    """
    Attempts to create a MailRecipient object handling nasty unicode issues
    """
    try:
        return MailRecipient(message=message, toEmail=toemail,
                             toName=toname, isTo=isto)
    except UnicodeDecodeError:
        pass
    return MailRecipient(message=message, toEmail=decodeh.decode(toemail),
                         toName=decodeh.decode(toname), isTo=isto)
    
    
def create_mail_reference(message, reference):
    """
    Attempts to create a mail reference object.  First tries the easy
    method where everything is assumed to be proper unicode.  If that
    doesn't work then it uses decodeh.decode to brute force whatever
    it is.

    @param message: a dbobjects.MailMessage
    @param reference: the string reference
    """
    try:
        return MailReference(message=message, reference=reference)
    except UnicodeDecodeError:
        pass
    return MailReference(message=message, reference=decodeh.decode(reference))
    
def get_list(masterproject, listname):
    """
    Queries the database to find a mailing list belonging to a master project
    
    If the list cannot be found, then it will be created
    
    @param masterproject: the name of the master project that owns the list (eg gnome/beagle)
    @param listname: the name of the mailing list (eg dashboard-hackers)
    @return: a dbobjects.MailList object for the list
    """
    mproject = MasterProject.select(MasterProject.q.name==masterproject)
    if not mproject.count():
        log.error("Master project with name [%s] does not exist.  Aborting.", masterproject)
        sys.exit()
    mproject = mproject[0]
    maillist = MailList.select(AND(MailList.q.name == listname, MailList.q.projectID == mproject.id))
    if not maillist.count():
        log.debug("Mailing list [%s] for project [%s] does not exist -- creating it", listname, masterproject)
        maillist = MailList(name=listname, projectID=mproject.id)
    else:
        maillist = maillist[0]
    return maillist

        
if __name__ == "__main__":
    logging.basicConfig()
    log = logging.getLogger("loadMailLists")
    log.setLevel(logging.INFO)

    parser = OptionParser()
    parser.add_option("-d", "--debug", action="store_true",
                      dest="verbose", default=False,
                      help="verbose debugging messages")
    parser.add_option("--dburi", "-u", dest="uri",
                      help="database name to connect to",
                      default="postgres://"+os.getenv("USER")+"@/cvsminer",
                      action="store")
    parser.add_option("--fromhack", "-f", dest="fromhack",
                      help="Hack for from addresses being mangled in some lists",
                      default=False, action="store_true")
    parser.add_option("--project", "-p", dest="project",
                      help="project to map mailing list to",
                      default=None, action="store")
    parser.add_option("-l", "--loglevel", dest="loglevel",
                      help="Manually specify logging level (DEBUG, INFO, WARN, etc)",
                      default="INFO", action="store")   
    parser.add_option("--purge", dest="purge",
                      help="Purge old records from file",
                      default=False, action="store_true")
    parser.add_option("--purge_only", dest="purge_only",
                      help="Only purge records, do not reload archive",
                      default=False, action="store_true")
    parser.add_option("--nopurgeconfirm", dest="purge_confirm",
                      help="Don't prompt for a purge confirmation",
                      default=False, action="store_true")
    parser.add_option("--reparent", dest="reparent", default=False,
                      help="Reparent all messages", action="store_true")
    parser.add_option("--link", dest="linkMessages", default=False,
                      help="Link all messages up with user ids", action="store_true")
    parser.add_option("--removedupes", dest="removeDupes", default=False,
                      help="remove duplicate messages", action="store_true")
    parser.add_option("--listname", dest="listname", default=None,
                      help="name of mailing list", action="store")
    
    (options, args) = parser.parse_args()

    if options.verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(getattr(logging,options.loglevel.upper()))

#     if len(args) < 1:
#         print_usage()

    connect(options.uri, debug=options.verbose)

    if options.linkMessages:
        linkMessages()
        print "linking!"
 
    if options.reparent:
        reparentMessages()

    if not options.project:
        if options.reparent or options.linkMessages:
            log.info("No project specified, looks like we're done here")
        else:
            log.error("Must specifiy --project")
        sys.exit()
        
    if not options.listname:
        log.error("Must specify --listname")
        sys.exit()
        
    maillist = get_list(options.project, options.listname)
    
    if (options.purge or options.purge_only) and not options.purge_confirm:
        confirm = raw_input("Confirm purge by typing 'yes':")
        if confirm.lower() != 'yes':
            log.error("You must type 'yes' to confirm a purge. Exiting")
            sys.exit()
 
    nummsgs = 0
    for fn in args:
        nummsgs = nummsgs + loadFile(fn, maillist=maillist, fromHack=options.fromhack, purge=options.purge, purge_only=options.purge_only)
    print "total messages: ", nummsgs

    if options.removeDupes:
        removeDupes()
                     
       
