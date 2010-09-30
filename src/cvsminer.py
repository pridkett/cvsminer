#!/usr/bin/python
"""
cvsminer

This script mines a CVS archive and associates all of the logs together,
it can be run on a non-local repository, but I would not recommend it.
"""

__author__ = "Patrick Wagstrom"
__copyright__ = "Copyright (c) 2005 Patrick Wagstrom"
__license__ = "GNU General Public License version 2 or later"

try:
	import cvs
except ImportError:
	pass
import os
import logging
import sys
import rcsparse
import difflib
from pyPgSQL import PgSQL
from optparse import OptionParser
import mx.DateTime
import dbutil
import popen2
import re

# maximum number of seconds for a complete commit, modify as needed
MAX_TIME_FUDGE = 600

_userCache = {}
_projectCache = {}
_fileCache = {}
_stateCache = {}
_tagCache = {}
RLOG_RE = re.compile(r"^date: [0-9]{4}/[0-9]{1,2}/[0-9]{1,2} [0-9]{2}:[0-9]{2}:[0-9]{2};  author: .*;  state: .*;  lines: \+([0-9]+) -([0-9]+)")

class CVSFile(object):
    """Represents a file a CVS repository
    """
    def __init__(self, path, filename, basename=None):
        object.__init__(self)
        self.basename = basename
        self.path = path
        self.filename = filename
        self.headRevision  = None
        self.principalBranch = None
        self.tags = {}
        self.comment = None
        self.revisions = {}
        self.origPath = path

    def removeAttics(self):
        # work around problems with deleted files
        self.origPath = self.path
        self.path = os.sep.join([x for x in self.path.split(os.sep) if x != 'Attic'])
        self.basename = os.sep.join([x for x in self.basename.split(os.sep) if x != 'Attic'])

class Revision(object):
    """One revision of a CVSFile
    """
    def __init__(self, revision=None, timestamp=None, author=None,
                 state=None, branches=None, next=None, log=None, text=None):
        object.__init__(self)
        self.revision = revision
        self.timestamp = timestamp
        self.author = author
        self.state = state
        self.branches = branches
        self.next = next
        self.log = log
        self.text = text
        self.next = next
        self.previousRevision = None
        self.linesAdded = None
        self.linesRemoved = None

    def getLinesInfo(self):
        """Uses difflib to provide a list of the lines information for this file"""
        if not self.previousRevision:
            return (len(self.text.split("\n")), None, None, None, None, None)
        diff = list(difflib.ndiff(self.previousRevision.text.split("\n"), self.text.split("\n")))
        linesAdded = len([x for x in diff if x[0] == '+'])
        linesRemoved = len([x for x in diff if x[0] == '-'])
        lines = len(self.text.split("\n"))
        charsAdded = sum([len([z for z in x[1:] if z == '+']) for x in diff if x[0] == '?'])
        charsRemoved = sum([len([z for z in x[1:] if z == '-']) for x in diff if x[0] == '?'])
        charsModified = sum([len([z for z in x[1:] if z == '^']) for x in diff if x[0] == '?'])
        return (lines, linesAdded, linesRemoved, charsAdded, charsRemoved, charsModified)
        
        
class CommitSink(rcsparse.Sink):
    """Sink for parsing information from RCS logs

    This requires a CVSFile to be passed to the constructor.  It should
    The sink can be reused by changing the reference to self.comming by
    calling setCVSFile()
    """
    def __init__(self, cvsfile):
        # why does rcsparse.Sink have no __init__ method?
        # rcsparse.Sink.__init__(self)
        self.commit = cvsfile

    def set_head_revision(self, revision):
        self.commit.headRevision = revision

    def set_principal_branch(self, branch_name):
        self.commit.principalBranch = branch_name

    def define_tag(self, name, revision):
        self.commit.tags[name] = revision

    def set_comment(self, comment):
        self.commit.comment = comment
        # print "Comment set: [%s]" % (comment)

    def set_description(self, description):
        self.commit.description = description
        # print "Description set: [%s]" % (description)

    def define_revision(self, revision, timestamp, author, state, branches, next):
        rev = Revision(revision, timestamp, author, state, branches, next)
        # self.commit.addRevision(rev)
        self.commit.revisions[revision] = rev

    def set_revision_info(self, revision, log, text):
        self.commit.revisions[revision].log = log
        self.commit.revisions[revision].text = text
        
    def setCVSFile(self, cvsfile):
        """Changes the file that this commit sink points to
        """
        self.commit = cvsfile
        
def add_project(aname, archivePath, st, db):
    """
    First checks to see if the project is already in the database, if it is, then
    return the project_id, otherwise create a new project and insert it into the
    database.

    @param archivename - the name of the archive
    @param archivePath - the path of the archive
    @param st - a cursor from the database
    @param db - handle the database
    @return the ID # of the existing or new project
    """
    if _projectCache.has_key(aname):
        return _projectCache[aname]
    log.debug("Checking project existence [%s]" % (aname))
    query = "SELECT project_id FROM project WHERE project_name=%s"
    st.execute(query, (aname))
    res = st.fetchall()
    if len(res) > 0:
        project_id = res[0]["project_id"]
        log.debug("Found project_id [%s=%d]" % (aname, project_id))
        _projectCache[aname] = project_id
        return project_id
    else:
        log.debug("Inserting project into database [%s]" % (aname))
        query = "INSERT INTO project(project_name, project_path) VALUES (%s, %s)"
        st.execute(query, (aname, archivePath))
        db.commit()
        return add_project(aname, archivePath, st, db)

def add_tag(tagName, project_id, st, db):
    if _tagCache.has_key(project_id):
        if _tagCache[project_id].has_key(tagName):
            return _tagCache[project_id][tagName]
    else:
        _tagCache[project_id] = {}
    query = "SELECT tag_id FROM tag WHERE project_id=%s and name=%s"
    st.execute(query, (project_id, tagName))
    res = st.fetchall()
    if len(res) > 0:
        tag_id = res[0]["tag_id"]
        _tagCache[project_id][tagName] = tag_id
        return tag_id
    else:
        query = "INSERT INTO tag (project_id, name) VALUES (%s, %s)"
        st.execute(query, (project_id, tagName))
        db.commit()
        return add_tag(tagName, project_id, st, db)
    
def add_file(shortFn, project_id, st, db):
    """
    First checks to see if the file is already in the database.  If it is, then
    we don't recreate it and just return the id of the file.  Otherwise, we add the
    file into the database of files
    """
    if _fileCache.has_key(project_id):
        fileList = _fileCache[project_id]
        if fileList.has_key(shortFn):
            return fileList[shortFn]
    else:
        _fileCache[project_id] = {}
    log.debug("Checking for file existence [%s]" % (shortFn))
    if len(shortFn) > 1023:
	shortFn = shortFn[:1023]
    	log.warn("Filename is too long.  Truncating to 1023 characters")
    query = "SELECT file_id FROM file WHERE file_name=%s AND project_id=%s"
    st.execute(query, (shortFn, project_id))
    res = st.fetchall()
    if len(res) > 0:
        file_id = res[0]["file_id"]
        log.debug("Found file_id [%s=%d]" % (shortFn, file_id))
        _fileCache[project_id][shortFn] = file_id
        return file_id
    else:
        log.debug("Inserting file into databse [%s]" % (shortFn))
        query = "INSERT INTO file (project_id, file_name) VALUES (%s, %s)"
        st.execute(query, (project_id, shortFn))
        db.commit()
        return add_file(shortFn, project_id, st, db)

def find_user(username, project_id, st, db):
    """
    Finds a user in the list of users
    """
    if _userCache.has_key(project_id):
        userList = _userCache[project_id]
        if userList.has_key(username):
            return userList[username]
    else:
        _userCache[project_id] = {}
    log.debug("Attempting to find user [%s] on project [%d]" % (username, project_id))
    query = """SELECT a.user_id FROM users a, project_user b
                WHERE a.user_name=%s AND a.user_id = b.user_id AND b.project_id=%s"""
    st.execute(query, (username, project_id))
    res = st.fetchall()
    if len(res) > 0:
        user_id = res[0]["user_id"]
        log.debug("Found user_id [%s=%d]" % (username, user_id));
        # store the user back in the cache for future reference
        _userCache[project_id][username] = user_id
        return user_id
    else:
        log.debug("Inserting user into database [%s]" % (username))
        query = "INSERT INTO users (user_name) VALUES (%s)"
        st.execute(query, (username))
        db.commit()
        query = "SELECT user_id FROM users WHERE user_name=%s ORDER BY user_id DESC LIMIT 1"
        st.execute(query, (username))
        res = st.fetchall()
        user_id = res[0]["user_id"]
        query = "INSERT INTO project_user (project_id, user_id) VALUES (%s, %s)"
        st.execute(query, (project_id, user_id))
        db.commit()
        _userCache[project_id][username] = user_id
        return user_id
    

def get_cvs_state_id(state, st, db):
    if _stateCache.has_key(state):
        return _stateCache[state];
    
    query = """SELECT cvs_state_id FROM cvs_state WHERE cvs_state_name=%s"""
    st.execute(query,(state))
    res = st.fetchall()
    if len(res) > 0:
        state_id = res[0]["cvs_state_id"]
        _stateCache[state] = state_id
        return state_id
    else:
        query = "INSERT INTO cvs_state(cvs_state_name) VALUES (%s)"
        st.execute(query, (state))
        db.commit()
        return get_cvs_state_id(state, st, db)
        
def get_cvs_commit(user_id, project_id, date, message, st, db):
    """queries the database to see if this commit currently resides somewhere
    related to another file.
    """
    query = """SELECT cvs_commit_id, start_date, stop_date, message
                 FROM cvs_commit
                WHERE project_id=%s AND user_id=%s AND message_intro=%s"""
    st.execute(query,(project_id, user_id, message[:250]))
    res = st.fetchall()
    dts = mx.DateTime.TimestampFrom(date)
    commit_id = None
    for thisRec in res:
        # commit_id = res[0]['cvs_commit_id']
        start_date = thisRec['start_date']
        stop_date = thisRec['stop_date']
	thisMsg = thisRec['message']
        diff = start_date - dts
        absDiff = diff.absvalues()
        if thisMsg == message and absDiff[0] == 0 \
           and abs(absDiff[1]) < MAX_TIME_FUDGE:
            commit_id = thisRec['cvs_commit_id']
            break
    if commit_id != None:
        return commit_id
    else:
	log.debug("Inserting new cvs commit: project_id=%d, user_id=%d, start_date=%s, stop_date=%s, message=%s",
                   project_id, user_id, date, date, message)
        query = """INSERT INTO cvs_commit(project_id, user_id, start_date,
                                          stop_date, message_intro, message)
                        VALUES (%s, %s, %s, %s, %s, %s)"""
        st.execute(query,(project_id, user_id, date, date, message[:250], message))
        db.commit()
	log.debug("new cvs commit inserted")
        return get_cvs_commit(user_id, project_id, date, message, st, db)

def add_cvs_commit(file_id, fn, project_id, st, db):
    """
    Adds a cvs commit to the log of CVS commits
    """
    try:
        lg = cvs.log(fn)
    except:
        return 0
	commits = 0
    log.debug("number of entries to insert: %d" % (len(lg)))
    for l in lg:
        # get the user ID of the committing user
        if l.has_key('author') and l.has_key('date') and l.has_key('revision') and l.has_key('state'):
            user_id = find_user(l["author"], project_id, st, db)
            date = l['date']
            message = l['message']
            revision = l['revision']
            state = l['state']
            commit_id = get_cvs_commit(user_id, project_id, date, message, st, db)
            state_id = get_cvs_state_id(state, st, db)
            log.debug("Inserting commit for date: %s" % (date))
            if l.has_key('lines'):
                query = """INSERT INTO file_cvs_commit(file_id, cvs_commit_id, date, revision, cvs_state_id, lines, lines_added, lines_removed)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
                lines = l['lines']
                linesAdded, linesRemoved = lines.split()
                linesAdded = abs(int(linesAdded))
                linesRemoved = abs(int(linesRemoved))
                st.execute(query,(file_id, commit_id, date, revision, state_id, lines, linesAdded, linesRemoved))
            else:
                query = """INSERT INTO file_cvs_commit(file_id, cvs_commit_id, date, revision, cvs_state_id)
                    VALUES (%s, %s, %s, %s, %s)"""
                st.execute(query,(file_id, commit_id, date, revision, state_id))
            commits = commits + 1
            log.debug("new linkage created")
        else:
            log.warn("missing keys: %s" % (str(l.keys())))
    db.commit()
    return commits

def storeCVSFile(fl, project_id, st, db):
    """Stores all the information about a CVS commit in the database
    """
    file_id = add_file(fl.basename, project_id, st, db)
    (logout, login) = popen2.popen2("rlog %s" % (fl.origPath + os.sep + fl.filename))
    login.close()
    lines = logout.readlines()
    logout.close()
    for x in xrange(0, len(lines)):
        if lines[x] == '----------------------------\n':
            rev = lines[x+1].split(" ")[1].strip()
            gps = RLOG_RE.match(lines[x+2].strip())
            if gps:
                try:
                    fl.revisions[rev].linesAdded = gps.groups()[0]
                    fl.revisions[rev].linesRemoved = gps.groups()[1]
                except:
                    pass

#     for rev in fl.revisions.itervalues():
#         for branch in rev.branches:
#             fl.revisions[branch].previousRevision = rev
#         if rev.next:
#             rev.previousRevision = fl.revisions[rev.next]
    # iterate over each of the revisions
    for rev in fl.revisions.itervalues():
        # print rev.revision, rev.getLinesInfo()
        # print rev.text
        user_id = find_user(rev.author, project_id, st, db)
        date = mx.DateTime.localtime(rev.timestamp)

        commit_id = get_cvs_commit(user_id, project_id, date, rev.log, st, db)
        state_id = get_cvs_state_id(rev.state, st, db)
        revision = rev.revision
       
        log.debug("processing file_id=%d, commit_id=%d, date=%s, revision=%s, state_id=%s", file_id, commit_id, date, revision, state_id)
        if rev.linesAdded:
                    query = """INSERT INTO file_cvs_commit(file_id, cvs_commit_id, date,
                                               revision, cvs_state_id, lines_added, lines_removed)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                    st.execute(query, (file_id, commit_id, date, revision, state_id, rev.linesAdded, rev.linesRemoved))
        else:
            query = """INSERT INTO file_cvs_commit(file_id, cvs_commit_id, date,
                                                   revision, cvs_state_id)
                            VALUES (%s, %s, %s, %s, %s)"""
            st.execute(query, (file_id, commit_id, date, revision, state_id))
    tagMapping = {}
    for tagName in fl.tags.keys():
        tagMapping[tagName] = add_tag(tagName, project_id, st, db)

    if tagMapping:
        query = "SELECT file_cvs_commit_id, revision FROM file_cvs_commit WHERE file_id=%s"
        st.execute(query,(file_id))
        revisionMapping = {}
        for res in st.fetchall():
            revisionMapping[res[1]] = res[0]

        pairings = []
        for tagName, revision in fl.tags.iteritems():
            try:
                pairings.append((tagMapping[tagName], revisionMapping[revision]))
            except:
                log.debug("error: tag=%s, revision=%s", tagName, revision)
        if pairings:
            query = """INSERT INTO file_cvs_commit_tag (tag_id, file_cvs_commit_id) VALUES (%s, %s)"""
            st.executemany(query, pairings)
        
    db.commit()
    
        
        
    
    
def mine(aname, archive):
    """Mines a repository for commit information if you do not have access to the repository.

    If you've got direct access to the underlying files, you should look at the
    mine_repository function.

    @param aname - user friendly name for the archive
    @param archive - the directory of the archive
    """
    log.debug("mining path [name=%s] [path=%s]", aname, archive)
    log.debug("connecting to database")
    db = PgSQL.connect(database="cvsminer", user="patrick")
    st = db.cursor()
    log.debug("database connection succeeded")

    project_id = add_project(aname, archive, st, db)

    for x in os.walk(archive, topdown=True):
        # remove the CVS subdirectory so we don't get errors
        if "CVS" in x[1]:
            x[1].remove("CVS")
        else:
            log.error("Path does not appear to be under CVS control: %s", x[0])
        if ".cvsignore" in x[2]:
            x[2].remove(".cvsignore")
        vcFiles = [i.split("/")[1] for i in open(x[0]+os.sep+"CVS"+os.sep+"Entries").readlines() if len(i.split("/")) > 1]
        for y in x[2]:
            # build the complete file name
            fn = os.path.normpath(x[0] + os.sep + y)
            log.info("%s", fn)
            shortFn = fn[len(archive+os.sep):]
            if y not in vcFiles:
                log.warn("File is not under CVS control: %s", fn)
            else:
                file_id = add_file(shortFn, project_id, st, db)
                add_cvs_commit(file_id, fn, project_id, st, db)
                
def mine_repository(shortname, cvspath, username, password, database):
    """Mines a repository that you have direct access to.  This should contain all of the
    RCS files for a given project.

    @param shortname - user friendly name for the archive
    @param cvspath - path to the CVS repository
    @param username - username to connect to the database as
    @param database - name of the database to connect to
    @param password - password to use for the database connection
    """
    log.debug("mining repository [name=%s] [path=%s]", shortname, cvspath)
    db, st = dbutil.database_connect(username, password, database)

    # get the project id
    project_id = add_project(shortname, cvspath, st, db)
    
    cs = CommitSink(cvsfile=None)
    for path, dirs, files in os.walk(cvspath, topdown=True):
        # we only care about RCS files, not everything else
        for fn in [x for x in files if x[-2:] == ',v']:
            fname = path + os.sep + fn
            print fname
            fl = CVSFile(path=path, filename=fn)
            # get rid of the path elements and the ,v trailer
            fl.basename = fname[len(cvspath):-2].strip(os.sep)
            log.debug("fname: %s  basename: %s", fname, fl.basename)
            cs.setCVSFile(fl)
            # apparently there are some files that are not valid, but in the set
            try:
                rcsparse.Parser().parse(open(fname), cs)
            except Exception, e:
                log.exception("Unable to parse file: %s", fname)
            if fl.headRevision != None:
                fl.removeAttics()
                storeCVSFile(fl, project_id, st, db)
            
        
def print_usage():
    print("Usage: cvsminer.py [options] ARCHIVENAME ARCHIVEPATH\n")
    print("For more information try 'cvsminer.py -h'\n")
    
    sys.exit()

if __name__ == "__main__":
    logging.basicConfig()
    log = logging.getLogger("cvsminer")
    log.setLevel(logging.INFO)

    parser = OptionParser()
    parser.add_option("-v", "--verbose", dest="verbose",
                      help="print verbose degugging messages",
                      action="store_true", default=False)

    parser.add_option("-u", "--username", dest="username",
                      help="set username to connect to database with",
                      action="store", default=os.getenv("USER",""))

    parser.add_option("-d", "--database", dest="database",
                      help="set database name to manipulate",
                      action="store", default="cvsminer")

    parser.add_option("--host", dest="host",
                      help="database host to connect to",
                      action="store", default=None)

    parser.add_option("-p", "--password", dest="password",
                      help="database password for user",
                      action="store", default=None)

    parser.add_option("-r", "--repository", dest="repository",
                      help="path is a repository, not a checkout",
                      action="store_true", default=False)
    
    (options, args) = parser.parse_args()
    
    if options.verbose:
        log.setLevel(logging.DEBUG)

    if len(args) != 2:
        print_usage();
    else:
        if not options.repository:
            log.info("Mining archive found in path: %s" % (args[1]))
            mine(args[0], args[1])
            log.info("Done mining archive: %s" % (args[1]))
        else:
            log.info("Mining repository found in path: %s" % (args[1]))
            mine_repository(args[0], args[1], options.username,
                            options.password, options.database)
            log.info("Done mining repository: %s" % (args[1]))
            
        
