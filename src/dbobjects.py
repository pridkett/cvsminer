"""
dbobjects.py

This is the core interface to the database for CVSMiner, which includes GNOME
and Eclipse data.  To utilize this data, what you'll usually want to do is
something like this:

>>> import os
>>> from dbobjects import *
>>> connect("postgres://"+os.getenv("USER")+"@/cvsminer")
>>> print User.get(1)

@author: Patrick Wagstrom
@contact: patrick@wagstrom.net
@copyright: Copyright (c) 2005-2008 Patrick Wagstrom
"""
import logging
import sys
import gc

logging.basicConfig()
log = logging.getLogger("dbobjects")
log.setLevel(logging.INFO)
connection = None

if (sys.version_info[0] == 2 and sys.version_info[1] < 4) or sys.version_info[0] < 2:
    log.exception("Unable to load library.  This library requires Python 2.4 or newer")
    raise Exception("Incorrect python version - use python 2.4 or higher")

from sqlobject import SQLObject, RelatedJoin, MultipleJoin, sqlbuilder, connectionForURI, sqlhub
from sqlobject.col import DateTimeCol, BoolCol, IntCol, ForeignKey, UnicodeCol
from sqlobject import OR
from bugzillaobjects import Bug, BugActivity, Product, ProductProject, Attachment, Profile, ProfilePerson, FieldDef, BugComment, BugVotes, BugzillaRepo, BugCVSCommit, BugActivityResponse #pylint: disable-msg=W0611
# from personobjects import Person, Alias, PersonUser, EmailAddress, Corporation, CorporationDomain, PersonCorporation #pylint: disable-msg=W0611

class Study(SQLObject): #pylint: disable-msg=R0904
    """
    A basic object to represent a group of projects we're examining
    for a particular study.
    
    @deprecated
    """
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        idName = "study_id"
        idSequence = "study_id_seq"
    name = UnicodeCol(length=255, notNone=True, alternateID=True)
    createDate = DateTimeCol(default=sqlbuilder.func.NOW())
    projects = RelatedJoin('MasterProject', intermediateTable='study_project',
                        joinColumn='study_id', otherColumn='master_project_id')
    conferences = RelatedJoin('Conference', intermediateTable='study_conference',
                              joinColumn='study_id', otherColumn='conference_id')
    
class Conference(SQLObject): #pylint: disable-msg=R0904
    """
    A conference that a community or communities participated in
    """
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        idName = "conference_id"
        idSequence = "conference_id_seq"
    name = UnicodeCol(length=255, notNone=True)
    startDate = DateTimeCol()
    stopDate = DateTimeCol()
    city = UnicodeCol(length=255)
    country = UnicodeCol(length=255)
    createDate = DateTimeCol(default=sqlbuilder.func.NOW())
    presentations = MultipleJoin('Presentation', joinColumn='conference_id')
    communities = RelatedJoin('Community', intermediateTable='conference_community',
                              joinColumn='conference_id', otherColumn='community_id')
    people = RelatedJoin('Person', intermediateTable='conference_person',
                         joinColumn='conference_id', otherColumn='person_id')
    
class Presentation(SQLObject): #pylint: disable-msg=R0904
    """
    A presentation given at a conference
    """
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        idName = "presentation_id"
        idSequence = "presentation_id_seq"
    name = UnicodeCol(length=255)
    startDate = DateTimeCol(default=None)
    stopDate = DateTimeCol(default=None)
    conference = ForeignKey('Conference', notNone=True)
    projects = RelatedJoin('MasterProject', intermediateTable='presentation_project',
                        joinColumn='presentation_id', otherColumn='master_project_id')
    people = RelatedJoin('Person', intermediateTable='presentation_person',
                         joinColumn='presentation_id', otherColumn='person_id')
    
class MailList(SQLObject): #pylint: disable-msg=R0904
    """
    A mailing list related to a particular project
    """
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        table = "mailing_list"
        idName = "mailing_list_id"
        idSequence = "mailing_list_id_seq"
    name = UnicodeCol(length=255, notNone=True)
    project = ForeignKey('MasterProject', default=None)
    createDate = DateTimeCol(notNone=True, default=sqlbuilder.func.NOW())
    messages = MultipleJoin("MailMessage", joinColumn='mailing_list_id')
    archives = MultipleJoin("MailFileArchive", joinColumn='mailing_list_id')
    
class MailFileArchive(SQLObject): #pylint: disable-msg=R0904
    """
    Mail archives on the internet are typically packaged in monthly archives.
    This object represents a source mail archive and can be used for
    back references and provenance to show where a piece of data originated.
    """
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        idName = "mail_file_archive_id"
        idSequence = "mail_file_archive_id_seq"
    filename = UnicodeCol(length=255, notNone=True)
    list = ForeignKey('MailList', dbName="mailing_list_id")
    startDate = DateTimeCol(notNone=True)
    stopDate = DateTimeCol(notNone=True)
    createDate = DateTimeCol(notNone=True, default=sqlbuilder.func.NOW())
                             
class MailMessage(SQLObject): #pylint: disable-msg=R0904
    """
    A single message on a single mailing list.  Currently the system does not
    handle cross posting nicely.
    """
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        table = "mail_message"
        idName = "mail_message_id"
        idSequence = "mail_message_id_seq"
    fromName = UnicodeCol(length=255, default=None)
    fromEmail = UnicodeCol(length=255, notNone=True, dbName="email")
    email = ForeignKey('EmailAddress', dbName='email_address_id', default=None)
    subject = UnicodeCol(length=255, notNone=True)
    body = UnicodeCol(default=None)
    date = DateTimeCol(dbName="message_date", default=None)
    archive = ForeignKey('MailFileArchive', dbName='mail_file_archive_id', notNone=True)
    list = ForeignKey('MailList', dbName="mailing_list_id", notNone=True)
    messageID = UnicodeCol(length=255, notNone=True, dbName='message_id')
    parent = ForeignKey('MailMessage', dbName="message_parent", default=None)
    children = MultipleJoin('MailMessage', joinColumn="message_parent")
    recipients = MultipleJoin("MailRecipient", joinColumn='mail_message_id')
    replyTo = UnicodeCol(length=255, dbName="in_reply_to", default=None)

class MailRecipient(SQLObject): #pylint: disable-msg=R0904
    """
    A message has a number of receipients.  In most cases, we try to keep the
    recipients as real people, but sometimes cross-posted lists sneak through.
    
    This object attempts to have resolution between the email address in the
    message and that in the database, but it isn't always guaranteed.
    """
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        table = "mail_message_to"
        idName = "mail_message_to_id"
        idSequence = "mail_message_to_id_seq"
    toName = UnicodeCol(length=255)
    toEmail = UnicodeCol(length=255, notNone=True, dbName="email")
    email = ForeignKey('EmailAddress', dbName='email_address_id', default=None)
    message = ForeignKey('MailMessage', dbName='mail_message_id', notNone=True)
    isTo = BoolCol(notNone=True, default=False, dbName='message_to')

class MailReference(SQLObject): #pylint: disable-msg=R0904
    """
    Mailing list messages often have a "in-reference-to" header somewhere in the
    message.  These values are typically message-ids of other messages.  We save
    this information in the database on the off chance that we need them sometime
    in the future.
    """
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        table = "mail_message_reference"
        idName = "mail_message_reference_id"
        idSequence = "mail_message_reference_id_seq"
    message = ForeignKey('MailMessage', dbName='mail_message_id', notNone=True)
    reference = UnicodeCol(length=255, notNone=True)
    
class User(SQLObject): #pylint: disable-msg=R0904
    """
    A user in a CVS repository
    """
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        table = "users"
        idName = "user_id"
        idSequence = "user_id_seq"
    name = UnicodeCol(length=64, dbName="user_name")
    createDate = DateTimeCol(default=sqlbuilder.func.NOW())
    community = ForeignKey('Community', notNone=True)
    projects = RelatedJoin('Project', intermediateTable='project_user',
                           joinColumn='user_id', otherColumn='project_id')
    persons = RelatedJoin('Person', intermediateTable='person_user',
                           joinColumn='user_id', otherColumn='person_id')
    commits = MultipleJoin('CVSCommit', joinColumn='user_id')
    def get_primary_person(self):
        """
        Performs cross referencing work to get the primary person object
        """
        if self.persons: 
            return self.persons[0]
        return None
    
    def getPrimaryPerson(self):
        """
        @deprecated use get_primary_person instead
        """
        log.warn("Person.getPrimaryPerson called -- use Person.get_primary_person instead")
        return self.get_primary_person()
    
    def get_primary_person_id(self, default=None):
        """
        Gets the id number of the primary person object.
        
        @param default: default value to return if no person associated.
        """
        if self.persons:
            return self.persons[0].id
        return default

    def getPrimaryPersonId(self, default=None):
        """
        @deprecated use get_primary_person_id instead
        """
        log.warn("Person.getPrimaryPersonId called -- use Person.get_primary_person_id instead")
        return self.get_primary_person_id(default)
    
class File(SQLObject): #pylint: disable-msg=R0904
    """
    Represents a single file in a CVS archive for a project.  The primary key
    for a project is the filename.  Files with the same name may exist in
    multiple different projects.
    """
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        idName = "file_id"
        idSequence = "file_id_seq"
    project = ForeignKey('Project', notNone=True)
    name = UnicodeCol(length=1024, dbName="file_name")
    createDate = DateTimeCol(default=sqlbuilder.func.NOW())
    commits = MultipleJoin('FileCommit', joinColumn='file_id')
    fileClass = ForeignKey('FileClass', default=None)
    
class CVSState(SQLObject): #pylint: disable-msg=R0904
    """
    On each commit to CVS, we track the state of the files that were just
    commited.  In most cases, the only states that are used are:
    Exp, new, and dead
    Some data has elements such as Release and Stable, but these are
    rarely used in archives.
    
    In general it seems as though no one really looks at the CVSState
    """
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        idName = "cvs_state_id"
        idSequence = "cvs_state_id_seq"
    name = UnicodeCol(length=255, dbName='cvs_state_name', notNone=True, alternateID=True)
    createDate = DateTimeCol(notNone=True, default=sqlbuilder.func.NOW())

class CVSCommit(SQLObject): #pylint: disable-msg=R0904
    """
    A single commit by a user of a set of files to a particular project.
    """
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        idName = "cvs_commit_id"
        idSequence = "cvs_commit_id_seq"
    project = ForeignKey('Project', notNone=True)
    user = ForeignKey('User', notNone=True)
    startDate = DateTimeCol(notNone=True)
    stopDate = DateTimeCol(notNone=True)
    intro = UnicodeCol(length=255, notNone=True, dbName='message_intro')
    message = UnicodeCol(notNone=True)
    branch = UnicodeCol(length=255, default=None)
    createDate = DateTimeCol(notNone=True, default=sqlbuilder.func.NOW())
    commits = MultipleJoin('FileCommit', joinColumn='cvs_commit_id')
    files = RelatedJoin('File', intermediateTable='file_cvs_commit',
                        joinColumn='cvs_commit_id', otherColumn='file_id', createRelatedTable=False)
    
        
class Project(SQLObject): #pylint: disable-msg=R0904
    """
    A conceptual group of files within a community.  Typically these represent a
    single directory (module) within a CVS archive
    """
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        idName = 'project_id'
        idSequence = "project_id_seq"
    name = UnicodeCol(length=64, dbName="project_name")
    path = UnicodeCol(length=255, dbName="project_path")
    createDate = DateTimeCol(default=sqlbuilder.func.NOW(), notNone=True)
    modifyDate = DateTimeCol(default=sqlbuilder.func.NOW(), notNone=True)
    masterProject = ForeignKey('MasterProject')
    # bugs = MultipleJoin('Bug', joinColumn='project_id')
    files = MultipleJoin('File', joinColumn='project_id')
    users = RelatedJoin('User', intermediateTable='project_user',
                        joinColumn='project_id', otherColumn='user_id')
    commits = MultipleJoin('CVSCommit', joinColumn='project_id')
    
class MasterProject(SQLObject): #pylint: disable-msg=R0904
    """
    A conceptual project within a community.  These are often comprised of several
    projects, although for GNOME there are a few MasterProjects which have only
    a single Project
    """
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        idName = 'master_project_id'
        idSequence = 'master_project_id_seq'
    name = UnicodeCol(length=255, dbName='master_project_name')
    createDate = DateTimeCol(default=sqlbuilder.func.NOW())
    community = ForeignKey('Community', default=None)
    projects = MultipleJoin('Project', joinColumn='master_project_id')
    products = RelatedJoin('Product', intermediateTable='bz_product_project',
                           joinColumn='project_id', otherColumn='product_id', createRelatedTable=False)
    mailLists = MultipleJoin('MailList', joinColumn='project_id')
    parent = ForeignKey('MasterProject', dbName="parent_id", default=None)

class Community(SQLObject): #pylint: disable-msg=R0904
    """
    The top level conceptual element for source code, the community is used
    to indicate where all the code and users for a set of CVS archives come from.
    
    Right now there are only two communities.
    """
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        idName = 'community_id'
        idSequence = 'community_id_seq'
    name = UnicodeCol(length=255, dbName='community_name')
    createDate = DateTimeCol(default=sqlbuilder.func.NOW())
    projects = MultipleJoin('MasterProject', joinColumn='community_id')
    
    
class FileCommit(SQLObject): #pylint: disable-msg=R0904
    """In the most technical sense, this is a join table, but because there is
    additional per file information for each commit, we can't have a standard
    join table here"""
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        idName = "file_cvs_commit_id"
        table = "file_cvs_commit"
        idSequence = "file_cvs_commit_id_seq"
    file = ForeignKey('File',  notNone=True, dbName='file_id')
    cvsCommit = ForeignKey('CVSCommit', notNone=True, dbName='cvs_commit_id')
    date = DateTimeCol(notNone=True)
    revision = UnicodeCol(length=32, notNone=True)
    state = ForeignKey('CVSState', dbName='cvs_state_id', notNone=True)
    linesAdded = IntCol(default=None)
    linesRemoved = IntCol(default=None)
    createDate = DateTimeCol(notNone=True, default=sqlbuilder.func.NOW())
    tags = RelatedJoin('Tag', intermediateTable='file_cvs_commit_tag')
    
class Tag(SQLObject): #pylint: disable-msg=R0904
    """
    A Tag that can be applied to a particular version of a file.  Tags were pretty
    widely used in CVS, but they weren't ever consistently used.  cvsps tends to do
    an okay job of figuring out what tag was applied to what files, but misses quite
    a few files at the time of tagging.  I wouldn't consider this to be entirely
    accurate.
    """
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        idName = 'tag_id'
        idSequence = "tag_id_seq"
    project = ForeignKey('Project', notNone=True)
    name = UnicodeCol(length=255, notNone=True)
    createDate = DateTimeCol(notNone=True, default=sqlbuilder.func.NOW())
    commits = RelatedJoin('FileCommit', intermediateTable='file_cvs_commit_tag')

class FileClass(SQLObject): #pylint: disable-msg=R0904
    """
    A simple way to filter files by their type.  For example, C-Source code.
    This is a self referencing class, so we have graphics->png images.  To get
    all of the elements, you'll need to do a crawl of this table.  Suckage.  LDAP
    would be much better for this.
    """
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        idName = 'file_class_id'
        idSequence = "file_class_id_seq"
    name = UnicodeCol(length=255, notNone=True, dbName='file_class_desc', alternateID=True)
    parent = ForeignKey('FileClass', dbName='parent_file_class_id')
    createDate = DateTimeCol(notNone=True)
    regexs = MultipleJoin('FileRegex', joinColumn='file_class_id')
    def get_root_parent(self):
        """
        Recursively crawls back through the elements parent to find its top level parent.
        """
        rootparent = self.parent
        if not rootparent:
            rootparent = self
        while rootparent.parent != None:
            rootparent = rootparent.parent
        return rootparent

    def getRootParent(self):
        """
        @deprecated: use FileClass.get_root_parent instead
        """
        log.warn("FileClass.getRootParent is deprecated, use FileClass.get_root_parent instead")
        return self.get_root_parent()
    
class FileClassRegex(SQLObject): #pylint: disable-msg=R0904
    """
    Regular expressions we can use for setting the FileClass of a File
    """
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        idName = "file_class_regex_id"
        idSequence = "file_class_regex_id_seq"
    regex = UnicodeCol(length=255, notNone=True, dbName="file_class_regex")
    fileClass = ForeignKey('FileClass', notNone=True)
    createDate = DateTimeCol(notNone=True)


class Person(SQLObject): #pylint: disable-msg=R0904
    """A physical person.  May have many user ids and email addresses.
    """
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        table = "person"
        idName = "person_id"
    _inheritable = False
    primaryAlias = ForeignKey('Alias', dbName="primary_alias")
    aliases = MultipleJoin('Alias', joinColumn='person_id')
    users = RelatedJoin('User', intermediateTable='person_user',
                        joinColumn='person_id', otherColumn='user_id')
    profiles = RelatedJoin('Profile',
                           intermediateTable='bz_profiles_person',
                           joinColumn='person_id',
                           otherColumn='bz_profile_id')
    corporations = RelatedJoin('Corporation',
                               intermediateTable='person_corporation',
                               joinColumn='person_id',
                               otherColumn='corporation_id')
    personCorporations = MultipleJoin('PersonCorporation', joinColumn='person_id')
    emailAddresses = MultipleJoin('EmailAddress', joinColumn='person_id')
    needsWork = BoolCol(default=None)
    def _get_name(self):
        """
        Gets the name of the primary alias for this user
        """
        return self.primaryAlias.name
    
class Alias(SQLObject): #pylint: disable-msg=R0904
    """Alias for persons.
    """
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        table = "alias"
        idName = "alias_id"
    _inheritable = False
    name = UnicodeCol(length=255, notNone=True)
    person = ForeignKey('Person', dbName='person_id', default=None)

class PersonUser(SQLObject): #pylint: disable-msg=R0904
    """The intermediate table between Person and User
    I created this SQLObject so I could add the record_source information"""
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        table = "person_user"
        idName = "person_user_id"
    _inheritable = False
    person = ForeignKey('Person', dbName='person_id')
    user = ForeignKey('User', dbName='user_id')
 
class EmailAddress(SQLObject): #pylint: disable-msg=R0904
    """An email address tied to a person and used as a conneciton to
    other data"""
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        table = "email_address"
        idName = "email_address_id"
    _inheritable = False
    email = UnicodeCol(length=255, alternateID=True)
    person = ForeignKey('Person', dbName='person_id', default=None)
    def _get_bugComments(self):
        return BugComment.select(BugComment.q.author==self.email)
    def _get_bugsByReporter(self):
        return Bug.select(Bug.q.reporter==self.email)
    def _get_bugsByAssignedTo(self):
        return Bug.select(Bug.q.assignedTo==self.email)
    def _get_bugsByQAContact(self):
        return Bug.select(Bug.q.qaContact==self.email)
    def _get_bugsByComments(self):
        return Bug.select(BugComment.q.author==self.email)
    def _get_bugs(self):
        return Bug.select(OR(Bug.q.reporter==self.email, 
                             Bug.q.assignedTo==self.email,
                             Bug.q.qaContact==self.email,
                             BugComment.q.author==self.email))
    def _get_mailMessagesByFrom(self):
        return MailMessage.select(MailMessage.q.fromEmail==self.email)
    def _get_mailMessagesByRecipients(self):
        return MailMessage.select(MailRecipient.q.toEmail==self.email)
    def _get_mailMessages(self):
        return MailMessage.select(OR(MailRecipient.q.toEmail==self.email,
                                     MailMessage.q.fromEmail==self.email))

class Corporation(SQLObject): #pylint: disable-msg=R0904
    """Contains information about a corporation that employs developers"""
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        table = "corporation"
        idName = "corporation_id"
        idSequence = "corporation_id_seq"
    name = UnicodeCol(length=255, alternateID=True, notNone=True)
    homepage = UnicodeCol(length=255, default=None)
    icon = UnicodeCol(length=255, default=None)
    createDate = DateTimeCol(default=sqlbuilder.func.NOW())
    modifyDate = DateTimeCol(default=sqlbuilder.func.NOW())
    people = RelatedJoin('Person',
                         intermediateTable = 'person_corporation',
                         joinColumn='corporation_id',
                         otherColumn='person_id')
    domains = MultipleJoin('CorporationDomain', joinColumn='corporation_id')
    distributor = BoolCol(default=None, dbName='prop_distributor')
    manufacturer = BoolCol(default=None, dbName='prop_manufacturer')

class CorporationDomain(SQLObject): #pylint: disable-msg=R0904
    """Contains information about a domain name owned by a corporation"""
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        table = "corporation_domain"
        idName = "corporation_domain_id"
        idSequence = "corporation_id_seq"
    corporation = ForeignKey('Corporation', dbName='corporation_id')
    domain = UnicodeCol(length=255, notNone=True)
    createDate = DateTimeCol(default=sqlbuilder.func.NOW())
    modifyDate = DateTimeCol(default=sqlbuilder.func.NOW())
    
class PersonCorporation(SQLObject): #pylint: disable-msg=R0904
    """Contains linking information for a person and a corporation"""
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        table = "person_corporation"
        idName = "person_corporation_id"
        idSequence = "person_corporation_id_seq"
    person = ForeignKey('Person', dbName='person_id')
    corporation = ForeignKey('Corporation', dbName='corporation_id')
    startDate = DateTimeCol(default=None)
    stopDate = DateTimeCol(default=None)
    createDate = DateTimeCol(default=sqlbuilder.func.NOW())
    modifyDate = DateTimeCol(default=sqlbuilder.func.NOW())

class ProjectInvolvement(SQLObject): #pylint: disable-msg=R0904
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        table = "user_corporation_project"
        idSequence = "person_corporation_project_id_seq"
    user = ForeignKey('User', dbName='user_id')
    corporation = ForeignKey('Corporation', dbName='corporation_id')
    project = ForeignKey('MasterProject', dbName='project_id')
    year = IntCol()
    month = IntCol()
    date = DateTimeCol()
    numCommits = IntCol()
    linesAdded = IntCol()
    linesRemoved = IntCol(default=None)
    linesDelta = IntCol(default=None)
    createDate = DateTimeCol(default=sqlbuilder.func.NOW())
    
def expire_all():
    """Simple function to expire the cache from everything.  Call
    it periodically to keep stuff happy

    taken from: http://mikewatkins.net/categories/technical/2004-07-14-1.html
    """
    c = Study._connection
    for k in c.cache.caches.keys():
        c.cache.caches[k].expireAll()
    gc.collect()

def set_connection(conn):
    """
    Helper function to set the connection object for all applicable objects
    
    @param conn: the sql object connection to remap all elements to
    """
    for x in [y for y in globals().values() if hasattr(y,'setConnection')
              and y.__class__.__name__ == 'DeclarativeMeta'
              and not y.__module__.startswith('sqlobject')]:
        x.setConnection(conn)
        print "setting connection on ", x

def get_sql_hub():
    """
    Simple helper function to get the sqlobject.sqlhub
    """
    return sqlhub

def get_connection():
    """
    Gets the current SQL connection
    """
    global connection
    return connection

def connect(uri, debug=False, cache=None, process=True, autocommit=True):
    """
    Connect to a database and begin using the data objects
    
    @param uri: the SQLObject formatted URI as a string
    @param debug: boolean if we should debug connection
    @param cache: an alternative cache if you need to save on memory
    @param process: boolean on whether or not the connection is set for the whole process
                    as opposed to just a thread.
    @param autocommit: boolean if results should be automatically saved
    """
    global connection
    connection = connectionForURI(uri, autoCommit=autocommit)
    if process:
        sqlhub.processConnection = connection

    if debug:
        connection.debug = True
    if cache != None:
        connection.cache = cache
    return connection

def raw_query(sqlquery, qobject=None):
    """
    Performs a raw SQL query on the database
    
    @param sqlquery: string to query the database
    @param qobject: an optional object to seek connection from
    """
    if qobject:
        return qobject._connection.queryAll(sqlquery)
    else:
        return get_connection().queryAll(sqlquery)
    

def raw_execute(sqlquery, qobject=None):
    """
    Performs a raw SQL query on the database, but don't really return any
    results
    
    @param sqlquery: string to query the database
    @param qobject: an optional object to seek connection from
    """
    if qobject:
        return qobject._connection.query(sqlquery)
    else:
        return get_connection().query(sqlquery)
