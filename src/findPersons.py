import os
import logging
import sys
from optparse import OptionParser
# import timeutil
# import mailutil
import rfc822
import random
from dbobjects import *
from personobjects import *

PUNCTUATION_RE=re.compile("[^\d\w\s-]")
SPACE_RE=re.compile(r"\s+")

def print_usage():
    print """findPersons.py -

This program is designed to automatically find persons in mail and other
data and populate the Perons and EmailAddresses tables.

USAGE:

findPersons.py [options]

For more help on command line arguments, use the -h flag"""
    sys.exit()
    
   
##def mergePerson(p, ea, mm.fromName):
##    if ea.person <> p:
##        print ea.person.id
##        print 'ea.person = ' + ea.person.name
##        print p.id
##        print 'p.name = ' + p.name

def mineMailMessage():
    totalProcessed = 0
    mms = MailMessage.select()
    for mm in mms:
        if options.verbose:
            if mm.fromName:
                print '<' + mm.fromName + '> ' + mm.fromEmail
        if mm.fromName and \
           (mm.fromName.find('=') == -1) and \
           (5 > len(mm.fromName.split()) > 1) and \
           (len(mm.fromEmail) > 0):
            als = Alias.select(Alias.q.name==mm.fromName)
            if als.count() == 0:
                a = Alias(person=None, name=mm.fromName, source1='MailMessage', source1Id=mm.id)
            else:
                if als.count() > 1:
                    print "WARNING: Duplicate name in Alias table: %s" % (mm.fromName)
                a = als[0]
            
            eas = EmailAddress.select(EmailAddress.q.email==mm.fromEmail)
            if eas.count() == 0:
                ea = EmailAddress(person=None, email=mm.fromEmail, source1='MailMessage', source1Id=mm.id)
            else:
                if eas.count() > 1:
                    print "WARNING: Duplicate email in EmailAddress table: %s" % (mm.fromEmail)
                ea = eas[0]
           
            # four cases ea.person == None or not crossed with a.person == None or not
            if ea.person:
                if a.person:
                    if ea.person <> a.person:
                        print ''
                        print "WARNING: Need to merge"
                        print "  %s email=%s points to %s" % (ea.id, ea.email, ea.person.name)
                        print "  %s alias=%s points to %s" % (a.id, a.name, a.person.name)
                        print "  %s mail message ties %s to %s" % (mm.id, mm.fromEmail, mm.fromName)
                else:
                    a.person = ea.person
            else:
                if a.person:
                    ea.person = a.person
                else:
                    p = Person(primaryAlias=a, source1='MailMessage', source1Id=mm.id)
                    ea.person = p
                    a.person = p
            totalProcessed += 1
        print '\r',
        print 'Processed: ',
        print totalProcessed,

def stripPunctuation(s):
    return SPACE_RE.sub(" ",PUNCTUATION_RE.sub("",s)).strip()

def buildTryNames(p):
    tryNames = []
    for a in p.aliases:
        aName = stripPunctuation(a.name)
        splitNames = aName.split()
        if hasattr(splitNames, '__getitem__') and len(splitNames) > 0:
            firstName = splitNames[0]
            if hasattr(firstName,'__getitem__') and len(firstName) > 0:
                firstInitial = firstName[0]
        if hasattr(splitNames, '__getitem__') and len(splitNames) >= 2:
            # TODO: Need to strip jr, III, etc.
            lastName = splitNames[-1]
            lastInitial = lastName[0]
            tryNames += [''.join([firstName,lastName])]
            tryNames += [''.join([firstInitial,lastName])]
            tryNames += [''.join([firstName,lastInitial])]
        else:
            lastName = None
            lastInitial = None
        if hasattr(splitNames, '__getitem__') and len(splitNames) >= 3:
            secondName = splitNames[1]
            secondInitial = secondName[0]
            tryNames += [''.join([firstName,secondName,lastName])]
            tryNames += [''.join([firstName,secondInitial,lastName])]
            tryNames += [''.join([firstInitial,secondInitial,lastName])]
            tryNames += [''.join([firstInitial,secondInitial,lastInitial])]
        else:
            secondName = None
            secondInitial = None
    return tryNames

def buildEmailStarts(p):
    emailStarts = []
    for ea in p.emailAddresses:
        candidate = ea.email.split('@')[0].split('+')[0]
        emailStarts += [ candidate ]
    return emailStarts
    
def buildFirstNames(p):
    firstNames = []
    for a in p.aliases:
        aName = stripPunctuation(a.name)
        splitNames = aName.split()
        if len(splitNames) >= 1:
            firstNames += [ splitNames[0] ]
    return firstNames
    
def connectPersonsToUsers():
    log.info("Selecting all persons")
    ps = Person.select()
    log.info("%d persons selected", ps.count())
    log.info("Selecting all users")
    us = User.select()
    log.info("%d users selected", us.count())
    matched = 0
    totalProcessed = 0
    tryNamesDict = {}
    log.info("Building possible name combinations")
    ctr = 0
    for p in ps:
        ctr = ctr + 1
        if ctr%100 == 0:
            log.info("Created %d sets of possible names", ctr)
        tryNames = buildTryNames(p)
        firstNames = buildFirstNames(p)
        emailStarts = buildEmailStarts(p)
        tryNames += emailStarts
        tryNamesDict[p.id] = tryNames
    for u in us:
        if True:  # I had this here to not process them if they were duplicates
            log.info("User: %s (%d)", u.name, u.id)
            possiblePersonIds = []
            for p in ps:
                if tryNamesDict.has_key(p.id) and u.name in tryNamesDict[p.id]:
                    possiblePersonIds += [ p.id ]
            if len(possiblePersonIds) > 1:
                print 'Multiple candidates:'
                for pid in possiblePersonIds:
                    p = Person.get(pid)
                    print 'ID:' + '(',
                    print p.id,
                    print ') has aliases:'
                    for a in p.aliases:
                        print '        ' + a.name
                    print '    and email addresses:'
                    for e in p.emailAddresses:
                        print '        ' + e.email
                print 'Enter number for correct match, 0=None, -1=Stop prompting and make single connections:'
                # TODO: Need to let user pick
                # if user selects just one, then edit possiblePersonIds so code below will work
            if len(possiblePersonIds) == 1:
                p = Person.get(possiblePersonIds[0])
                if options.verbose:
                    print '  Connecting to:' + p.name
                try:
                    pu = PersonUser(person=p, user=u, source1='User', source1Id=u.id, source2='Person', source2Id=p.id)
                    matched += 1
                except:
                    pass
        totalProcessed += 1
        log.info("Matched %d out of %d (%02.2f)", matched, totalProcessed, 100*matched/totalProcessed)
                        
if __name__ == "__main__":
    logging.basicConfig()
    log = logging.getLogger("findPersons")
    log.setLevel(logging.INFO)

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
    parser.add_option("--nomine", dest="nomine",
                      help="don't perform person mining process",
                      default=False, action="store_true")
    parser.add_option("-l", "--loglevel", dest="loglevel",
                      help="Manually specify logging level (DEBUG, INFO, WARN, etc)",
                      default="INFO", action="store")

    (options, args) = parser.parse_args()

    if options.debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(getattr(logging,options.loglevel.upper()))

    connect(options.uri, debug=options.debug)

    if not options.nomine: 
        print 'Starting person mining process'
        mineMailMessage()
    
    print ''
    print 'Starting person to user connection process'
    connectPersonsToUsers()
    


