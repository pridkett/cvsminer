#!/usr/bin/python

__author__ = "Patrick Wagstrom <patrick@wagstrom.net>"
__copyright__ = "Copyright (c) 2011 Patrick Wagstrom"
__license__ = "GNU General Public License version 2 or later"

import sys
import os
sys.path.append(os.path.join(os.path.split(os.path.abspath(__file__))[0], os.path.pardir, os.path.pardir))
sys.path.append(os.path.join(os.path.split(os.path.abspath(__file__))[0], os.path.pardir, os.path.pardir, "support"))

import logging
import logging.config
import ColorFormatter

import random
from optparse import OptionParser

from dbobjects import *
from sqlobject import AND

logging.config.fileConfig("logging.conf")
logger = logging.getLogger("nameimporter")
logger.setLevel(logging.DEBUG)

def read_address_file(infile="names.txt", delim="::"):
    names = [(x[0].strip(), x[1].strip()) for x in [y.split(delim) for y in open(infile).readlines()]]
    return names

def load_alias_cache():
    alias_dict = [(x[0].lower(), {"alias_id": x[1], "person_id": x[2], "alias": x[0]}) for x in Alias._connection.queryAll("SELECT name, alias_id, person_id FROM alias")]
    return dict(alias_dict)

def load_email_cache():
    email_dict = [(x[0].lower(), {"email_address_id": x[1], "person_id": x[2], "email": x[0]}) for x in Alias._connection.queryAll("SELECT email, email_address_id, person_id FROM email_address")]
    return dict(email_dict)

def process_names(names, alias_cache, email_cache):
    for tname in names:
        name = tname[0].lower()
        email = tname[1].lower()
        if (alias_cache.has_key(name) and email_cache.has_key(email)):
            if alias_cache[name]["person_id"] != email_cache[email]["person_id"]:
                logger.warn("Mismatched Person: %s => %s", name, email)
                logger.warn("      Email Cache: %s", email_cache[email])
                logger.warn("      Alias Cache: %s", alias_cache[name])
        elif alias_cache.has_key(name):
            logger.info("Person: %s - New Email: %s", name, email)
            email_cache[email] = {"person_id": alias_cache[name]["person_id"]}
            person_object = alias_cache[name].get("person_obj", Person.get(alias_cache[name]["person_id"]))
            alias_cache[name]["person_obj"] = person_object
            email_obj = EmailAddress(email=email, person=person_object)
            email_cache[email] = {"email_address_id": email_obj.id, "person_id": email_obj.person.id, "email": email_obj.email, "person_obj": person_object}

        elif email_cache.has_key(email):
            logger.info("Email: %s - New Alias: %s", email, name)
            alias_cache[name] = {"person_id": email_cache[email]["person_id"]}
            person_object = email_cache[email].get("person_obj", Person.get(email_cache[email]["person_id"]))
            email_cache[email]["person_obj"] = person_object
            alias_obj = Alias(name=name, person=person_object)
            alias_cache[name] = {"alias_id": alias_obj.id, "person_id": alias_obj.person.id, "alias": alias_obj.name, "person_obj": person_object}

        else:
            logger.info("New Person: %s", tname)
            alias_obj = Alias(name=name)
            person_obj = Person(primaryAlias=alias_obj)
            alias_obj.person = person_obj
            email_obj = EmailAddress(email=email, person=person_obj)
            alias_cache[name] = {"alias_id": alias_obj.id, "person_id": alias_obj.person.id, "alias": alias_obj.name, "person_obj": person_obj}
            email_cache[email] = {"email_address_id": email_obj.id, "person_id": email_obj.person.id, "email": email_obj.email, "person_obj": person_obj}

            # pid = random.randint(0,100000000000)
            # email_cache[email] = {"person_id": pid}
            # alias_cache[name] = {"person_id": pid}

if __name__ == "__main__":
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

    connect(options.uri, debug=options.verbose)
    names = read_address_file()
    alias = load_alias_cache()
    email = load_email_cache()
    process_names(names, alias, email)

    sys.exit()
 
    if options.linkMessages:
        linkMessages()
        print "linking!"
        
    if not options.project:
        log.error("Must specifiy --project")
        sys.exit()
        
    if not options.listname:
        log.error("Must specify --listname")
        sys.exit()
        
    maillist = get_list(options.project, options.listname)
        
    nummsgs = 0
    for fn in args:
        nummsgs = nummsgs + loadFile(fn, maillist=maillist, fromHack=options.fromhack, purge=options.purge)
    print "total messages: ", nummsgs

    if options.removeDupes:
        removeDupes()
                     
    if options.reparent:
        reparentMessages()
        
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
        
    if not options.project:
        log.error("Must specifiy --project")
        sys.exit()
        
    if not options.listname:
        log.error("Must specify --listname")
        sys.exit()
        
    maillist = get_list(options.project, options.listname)
        
    nummsgs = 0
    for fn in args:
        nummsgs = nummsgs + loadFile(fn, maillist=maillist, fromHack=options.fromhack, purge=options.purge)
    print "total messages: ", nummsgs

    if options.removeDupes:
        removeDupes()
                     
    if options.reparent:
        reparentMessages()
 
