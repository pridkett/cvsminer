"""
bugzillaObjects.py

This library provides an interface into all of the bugzilla related objects
that we've collected.
"""

import logging
import sys

logging.basicConfig()
log = logging.getLogger("bugzillaObjects")
log.setLevel(logging.INFO)

if (sys.version_info[0] == 2 and sys.version_info[1] < 4) or sys.version_info[0] < 2:
    log.exception("Unable to load library.  This library requires Python 2.4 or newer")
    raise Exception("Incorrect python version - use python 2.4 or higher")

from sqlobject import RelatedJoin, MultipleJoin, sqlbuilder, SQLObject
from sqlobject.col import IntCol, ForeignKey, UnicodeCol, DateTimeCol, BLOBCol, BoolCol

class Bug(SQLObject): #pylint: disable-msg=R0904
    """
    The Bug represents a single bug report from a database
    """
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        idName = "id"
        table = "bz_bugs"
    bugNum = IntCol(notNone=True, dbName="original_id")
    groupset = IntCol(notNone=True, default=0)
    assignedTo = ForeignKey('Profile', notNone=True, dbName="assigned_to")
    bugFileLoc = UnicodeCol(default=None)
    bugSeverity = UnicodeCol(length=12)
    bugStatus = UnicodeCol(length=12)
    createDate = DateTimeCol(dbName="creation_ts", default='1970-01-01 00:00:00')
    deltaDate = DateTimeCol(dbName="delta_ts", default=sqlbuilder.func.NOW())
    shortDesc = UnicodeCol()
    opSys = UnicodeCol(length=12, default='All')
    priority = UnicodeCol(length=12, default='Immediate')
    productName = UnicodeCol(length=64, notNone=True, default='', dbName="product")
    product = ForeignKey("Product", notNone=True)
    opSysDetails = UnicodeCol()
    reporter = ForeignKey('Profile', dbName="reporter")
    version = UnicodeCol(length=64, notNone=True, default='')
    component = UnicodeCol(length=50, notNone=True, default='')
    resolution = UnicodeCol(length=12, default='')
    target_milestone = UnicodeCol(length=20, default='---')
    qaContact = ForeignKey('Profile', dbName="qa_contact")
    statusWhiteboard = UnicodeCol(notNone=True)
    # votes = ForeignKey('BugVotes', dbName="votes", notNone=True, default=0)
    votes = IntCol(dbName="votes", notNone=True, default=0)
    keywords = UnicodeCol(notNone=True, default='')
    lastdiffed = DateTimeCol(notNone=True, default='1970-01-01 00:00:00')
    everConfirmed = IntCol(notNone=True, default=0, dbName="everconfirmed")
    versionDetails = UnicodeCol()
    externalcc = UnicodeCol()
    repPlatform = UnicodeCol(length=10, default=None)
    reporterAccessible = IntCol(notNone=True, default=1)
    ccListAccessible = IntCol(notNone=True, default=1, dbName="cclist_accessible")

    repository = ForeignKey("BugzillaRepo", notNone=True, dbName='bugzilla_repo_id')
    activity = MultipleJoin("BugActivity", joinColumn="bug_id")
    comments = MultipleJoin("BugComment", joinColumn="bug_id")

class BugzillaRepo(SQLObject): #pylint: disable-msg=R0904
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        idName = "id"
        table = "bugzilla_repo"
        idSequence = "bugzilla_repo_id_seq"
    name = UnicodeCol(length=32)
    community = ForeignKey("Community", notNone=True)
    createDate = DateTimeCol(notNone=True, default='1970-01-01 00:00:00')
    
class BugActivity(SQLObject): #pylint: disable-msg=R0904
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        idName = "bug_activity_id"
        table = "bz_bugs_activity"
        idSequence = "bz_bugs_activity_bug_activity_id_seq"
    bug = ForeignKey("Bug", notNone=True)
    who = ForeignKey("Profile", notNone=True, dbName="who")
    date = DateTimeCol(dbName="bug_when", default="1970-01-01 00:00:00")
    field = ForeignKey("FieldDef", notNone=True, dbName="fieldid")
    originalField = IntCol(notNone=True, dbName='original_fieldid')
    removed = UnicodeCol()
    removedResp = ForeignKey('BugActivityResponse', dbName='removed_id', default=None)
    added = UnicodeCol()
    addedResp = ForeignKey('BugActivityResponse', dbName='added_id', default=None)
    attachment = ForeignKey("Attachment", notNone=True, dbName="attach_id")

class BugActivityResponse(SQLObject): #pylint: disable-msg=R0904
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        idName = "id"
        table = "bz_bugs_activity_response"
    value = UnicodeCol(length=32, notNone=True, default=None)
    createDate = DateTimeCol(default='1970-01-01 00:00:00', notNone=True)
    
class Product(SQLObject): #pylint: disable-msg=R0904
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        idName = "product_id"
        table = "bz_products"
    name = UnicodeCol(length=64, default=None, dbName='product')
    description = UnicodeCol()
    milestoneurl = UnicodeCol()
    disallownew = IntCol(notNone=True, default=0)
    votesperuser = IntCol(notNone=True, default=0)
    maxvotesperbug = IntCol(notNone=True, default=10000)
    votestoconfirm = IntCol(notNone=True, default=0)
    defaultmilestone = UnicodeCol(length=20, default='---', notNone=True)
    isgnome = IntCol(notNone=True, default=0)
    projects = RelatedJoin('MasterProject', intermediateTable='bz_product_project',
                           joinColumn='product_id', otherColumn='project_id', createRelatedTable=False)
    bugs = MultipleJoin('Bug', joinColumn='product_id')

class ProductProject(SQLObject): #pylint: disable-msg=R0904
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        table = "bz_product_project"
        idSequence = "bz_product_project_id_seq"
    product = ForeignKey("Product")
    project = ForeignKey("MasterProject")
    
class Attachment(SQLObject): #pylint: disable-msg=R0904
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        idName = "attach_id"
        table = "bz_attachments"
        idSequence = "bz_attachments_id_seq"
    
    bug = ForeignKey("Bug", notNone=True)
    createDate = DateTimeCol(dbName="creation_ts", default='1970-01-01 00:00:00')
    description = UnicodeCol(notNone=True)
    mimetype = UnicodeCol(notNone=True)
    ispatch = IntCol(default=None)
    filename = UnicodeCol(notNone=True)
    data = BLOBCol(default=None, dbName="thedata", notNone=True)
    submitter = ForeignKey("Profile", default=0, notNone=True)
    obsolete = IntCol(default=0, notNone=True)
    
class Profile(SQLObject): #pylint: disable-msg=R0904
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        idName = "userid"
        table = "bz_profiles"
    loginName = UnicodeCol(length=255, notNone=True, default='', alternateID=True)
    cryptpassword = UnicodeCol(length=34)
    realName = UnicodeCol(length=255, default=None, dbName="realname")
    groupset = IntCol(default=0)
    disabledtext = UnicodeCol(notNone=True)
    myBugsLink = IntCol(notNone=True, default=1, dbName="mybugslink")
    blessgroupset = IntCol(default=0)
    emailFlags = UnicodeCol(dbName="emailflags")
    persons = RelatedJoin('Person',
                           intermediateTable='bz_profiles_person',
                           otherColumn='person_id',
                           joinColumn='bz_profile_id')
    comments = MultipleJoin("Comments", joinColumn="who")

    def getPrimaryPersonId(self):
        if self.persons:
            return self.persons[0].id
        return None
 
class ProfilePerson(SQLObject): #pylint: disable-msg=R0904
    """Pseudo class used to make profiles to persons.  Really it's only
    useful for doing queries on joins"""
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        table = "bz_profiles_person"
    profile = ForeignKey('Profile', dbName='bz_profile_id')
    person = ForeignKey('Person', dbName='person_id')
   
class FieldDef(SQLObject): #pylint: disable-msg=R0904
    """Represents a field in the bugzilla database.  In most cases you'll
    want to do something like:

    f = FieldDef.byName('priority')

    Other values that may be helpful are 'resolution', 'bug_status'
    """
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        idName = "fieldid"
        table = "bz_fielddefs"
    name = UnicodeCol(length=64, notNone=True, default='', alternateID=True)
    description = UnicodeCol(notNone=True)
    mailhead = IntCol(notNone=True, default=0)
    sortkey = IntCol(notNone=True)
    originalID = IntCol(notNone=True, dbName='original_id')
    repo = ForeignKey('BugzillaRepo', dbName='bugzilla_repo_id')
    obsolete = BoolCol()
    type = BoolCol()
    custom = BoolCol()
    enterBug = BoolCol()
    
class BugComment(SQLObject): #pylint: disable-msg=R0904
    """
    Represents a comment in the bugzilla database
    """
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        table = "bz_longdescs"
        idSequence = "bz_longdescs_id_seq"

    bug = ForeignKey("Bug", notNone=True)
    profile = ForeignKey("Profile", notNone=True, dbName="who")
    date = DateTimeCol(notNone=True, default='1970-01-01 00:00:00', dbName="bug_when")
    body = UnicodeCol(dbName="thetext")
    
class BugVotes(SQLObject): #pylint: disable-msg=R0904
    """
    Represents a bugzilla vote
    """
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        table = "bz_votes"
    who = ForeignKey("Profile", notNone=True, dbName="who")
    bug = ForeignKey("Bug", notNone=True, dbName="bug_id")
    count = IntCol(notNone=True, default=0)
    
class BugCVSCommit(SQLObject): #pylint: disable-msg=R0904
    """
    Linking object to link bugs and CVS commits
    """
    class sqlmeta: #pylint: disable-msg=R0903,W0232,C0111,C0103
        table="bz_bugs_cvs_commit"
    bug = ForeignKey("Bug", notNone=True, dbName="bug_id")
    commit = ForeignKey("CVSCommit", notNone=True, dbName="cvs_commit_id")

