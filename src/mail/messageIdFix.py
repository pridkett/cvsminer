#!/usr/bin/python
"""
messageIdFix.py

This script performs several useful functions on messages in the database

1. removes duplicate messages
2. fixes message reply-to headers so they have no semicolons
3. finds messages that have no parent set and reparents them
"""

__author__ = "Patrick Wagstrom <patrick@wagstrom.net>"
__copyright__ = "Copyright (c) 2006-2011 Patrick Wagstrom"
__license__ = "GNU General Public License version 2 or layer"

from dbobjects import *
import logging
from optparse import OptionParser

def removeDups():
    """
    Iterates over all messages in the database, removing duplicates
    """
    mls = MailList.select()
    for ml in mls:
        mms = MailMessage.select(MailMessage.q.listID==ml.id)
        found = {}
        dups = 0
        reparent = 0
        killList = []
        for mm in mms:
            if found.has_key(mm.messageID) and found[mm.messageID] != mm:
                dups = dups + 1
                # reparent everything to the other node
                omms = MailMessage.select(MailMessage.q.parentID==mm.id)
                if omms.count() > 0:
                    log.debug("%d messages to reparent", omms.count())
                    for omm in omms:
                        reparent = reparent + 1
                        omm.parent = found[mm.messageID]
                # delete the current message
                mrs = MailRecipient.select(MailRecipient.q.messageID==mm.id)
                mrids = [x.id for x in mrs]
                map(MailRecipient.delete, mrids)
                MailMessage.delete(mm.id)
            else:
                found[mm.messageID] = mm
        log.info("List %s - %d dups, %d messages reparented", ml.name, dups, reparent)
    
if __name__ == "__main__":
    logging.basicConfig()
    log = logging.getLogger("messageIdFix")
    log.setLevel(logging.INFO)

    parser = OptionParser()
    parser.add_option("-d", "--debug", action="store_true",
                      dest="verbose", default=False,
                      help="verbose debugging messages")
    parser.add_option("--dburi", "-u", dest="uri",
                      help="database name to connect to",
                      default="postgres://"+os.getenv("USER")+"@/cvsminer",
                      action="store")
    parser.add_option("--list", "-l", dest="list",
                      help="list name to fix",
                      default=None, action="store")
    parser.add_option("--dups", dest="dups",
                      help="remove duplicate message postings (SLOW)",
                      default=None, action="store_true")
    
    (options, args) = parser.parse_args()

    if options.verbose:
        log.setLevel(logging.DEBUG)
    connect(options.uri, debug=options.verbose)

    # first fix all the messages that have a ";" in the replyTo - those
    # aren't all that useful
    messages = MailMessage.select(MailMessage.q.replyTo.contains(';'))
    log.info("%d messages to go through...", messages.count())

    for msg in messages:
        print msg.replyTo, msg.replyTo.split(";")[0], msg.date, msg.fromEmail, msg.list.id, msg.list.name
        msg.replyTo = msg.replyTo.split(";")[0].strip()

    if options.dups:
        removeDups()

    # now, go through and fix all the reply tos...yes, this is a pain
    messages = MailMessage.select("""mail_message.in_reply_to is not NULL and mail_message.message_parent is NULL""")
    log.info("%d potential messages to reparent", messages.count())
    sameList = 0
    otherList = 0
    for msg in messages:
        nmsg = MailMessage.select(AND(MailMessage.q.messageID==msg.replyTo,
                                      MailMessage.q.id != msg.id,
                                      MailMessage.q.messageID!=msg.messageID))
        if nmsg.count() > 0:
            # first see if we can find a message on the same list as this message
            newParent = None
            goodMessage = [x for x in nmsg if x.list.id == msg.list.id]
            if goodMessage:
                newParent = goodMessage[0]
                sameList = sameList + 1
            else:
                # otherwise just use the the first message with that id -- NOT SURE IF THIS IS A GOOD IDEA
                newParent = nmsg[0]
                otherList = otherList + 1
            msg.parent = newParent
    log.info("%d messages reparented (%d same list, %d other list)", sameList + otherList, sameList, otherList)
 

