#!/usr/bin/python2.4
"""
cvsimporter_eclipse.py

@author: Patrick Wagstrom
@copyright: copyright (c) 2008 Patrick Wagstrom
@contact: patrick@wagstrom.net
@license: GNU General Public License Version 2 
"""

from dbobjects import connect, Community, MasterProject, User, Project, CVSCommit, CVSState, File, FileCommit, Tag, get_connection, expire_all
from sqlobject import AND
from optparse import OptionParser
import cvsimporter
import os
import logging
import sys
import codecs

COMMUNITY_CACHE = {}
MASTER_PROJECT_CACHE = {}
USER_CACHE = {}
TAG_CACHE = {}
FILE_CACHE = {}
PROJECT_CACHE = {}
CVS_STATE_CACHE = {}

def flush_all_caches():
    """
    Hopefully this helps to free up some memory, users, tags, files, and projects
    
    It intentionally does not clear out communities, master projects, and cvs_state
    """
    global USER_CACHE, TAG_CACHE, FILE_CACHE, PROJECT_CACHE
    USER_CACHE = {}
    TAG_CACHE = {}
    FILE_CACHE = {}
    PROJECT_CACHE = {}
    expire_all()

def get_community(community_name):
    """
    Finds the community with the given name, creating it if necessary
    
    @param community_name: the name of the community to example (eg "eclipse", "gnome")
    @return: an SQLObject Community entity
    @rtype: dbojects.Community
    """
    comm = Community.select(Community.q.name == community_name)
    if comm.count():
        COMMUNITY_CACHE[community_name] = comm[0]
        return comm[0]
    else:
        COMMUNITY_CACHE[community_name] = Community(name=community_name)
        return COMMUNITY_CACHE[community_name]
    
def get_repositories(cvsroot):
    """
    Given a directory, get the sub repositories that are present in the directory
    
    @param cvsroot: the pathname of the cvs root to examine
    """
    subrepos = os.listdir(cvsroot)
    return subrepos

def get_master_project(community, project):
    """
    Gets a master project for a particular community
    
    @param community: a dbobjects.Community 
    @param project: the name of the community
    """
    if not MASTER_PROJECT_CACHE.has_key(community.id):
        MASTER_PROJECT_CACHE[community.id] = {}
    if MASTER_PROJECT_CACHE[community.id].has_key(project):
        return MASTER_PROJECT_CACHE[community.id][project]
    mproject = MasterProject.select(AND(MasterProject.q.name == project,
                                        MasterProject.q.communityID == community.id))
    if mproject.count():
        MASTER_PROJECT_CACHE[community.id][project] = mproject[0]
    else:
        MASTER_PROJECT_CACHE[community.id][project] = MasterProject(name=project, community=community)
    return MASTER_PROJECT_CACHE[community.id][project]

def get_user(username, community):
    """
    Gets a user from the database
    @param username: the name of the user
    @param community: a dbobjects.Community element
    """
    if not USER_CACHE.has_key(community.id):
        USER_CACHE[community.id] = {}
    if USER_CACHE[community.id].has_key(username):
        return USER_CACHE[community.id][username]
    user = User.select(AND(User.q.name == username,
                           User.q.communityID == community.id))
    if user.count():
        USER_CACHE[community.id][username] = user[0]
    else:
        USER_CACHE[community.id][username] = User(name=username, community=community)
    return USER_CACHE[community.id][username]

def get_project(projectname, masterproject, repopath):
    """
    Gets a project from the database
    
    @param projectname: name of the project
    @param masterproject: parent of the project
    @param repopath: path of the project
    """
    if not PROJECT_CACHE.has_key(masterproject.id):
        PROJECT_CACHE[masterproject.id] = {}
    if PROJECT_CACHE[masterproject.id].has_key(projectname):
        return PROJECT_CACHE[masterproject.id][projectname]
    
    project = Project.select(AND(Project.q.name == projectname,
                                Project.q.masterProjectID == masterproject.id))
    if project.count():
        PROJECT_CACHE[masterproject.id][projectname] = project[0]
    else:
        PROJECT_CACHE[masterproject.id][projectname] = Project(name=projectname, masterProject=masterproject, path=repopath)
    return PROJECT_CACHE[masterproject.id][projectname]

def process_repository(cvsroot, repo, community, cache=False):
    """
    The top level parser for a CVS repository
    
    @param cvsroot: sorta a misnomer, actually a string representing the parent of all CVS repositories
    @param repo: the name of the repository to examine
    @param community: a dbojects.Community object
    """
    masterproject = get_master_project(community=community, project=repo)
    subprojects = os.listdir(cvsroot + os.sep + repo)
    for projectname in subprojects:
        dirname = cvsroot + os.sep + repo + os.sep + projectname
        if os.path.isdir(dirname):
            log.info("Processing project: %s", projectname)
            project = get_project(projectname, masterproject, repopath=cvsroot+os.sep+repo+os.sep+projectname)
            process_project(cvsroot=cvsroot+os.sep+repo, project=project, community=community, cache=cache)
        else:
            log.info("Not processing %s -- %s is not a directory", projectname, dirname)

def get_file(filename, project):
    """
    Gets a dbobjects.File object from the database
    
    @param filename: the name of the file to load
    @param project: dobjects.Project for file
    """
    if not FILE_CACHE.has_key(project.id):
        FILE_CACHE[project.id] = {}
    if FILE_CACHE[project.id].has_key(filename):
        return FILE_CACHE[project.id][filename]
    fileobj = File.select(AND(File.q.name == filename,
                              File.q.projectID == project.id))
    if fileobj.count():
        FILE_CACHE[project.id][filename] = fileobj[0]
    else:
        log.debug("Creating new file: %s", filename)
        FILE_CACHE[project.id][filename] =  File(projectID=project.id, name=filename)
    return FILE_CACHE[project.id][filename]

def get_cvs_state(filedelta):
    """
    Given a FileDelta object, get the corresponding CVSState object from the database
    
    @param filedelta: cvsimporter.FileDelta object
    """
    if filedelta.oldver == "INITIAL":
        statename = "New"
    elif filedelta.state == "(DEAD)":
        statename = "dead"
    else:
        statename = "Exp"
    if CVS_STATE_CACHE.has_key(statename):
        return CVS_STATE_CACHE[statename]

    filestate = CVSState.select(CVSState.q.name==statename)
    if filestate.count():
        CVS_STATE_CACHE[statename] = filestate[0]
    else:
        CVS_STATE_CACHE[statename] = CVSState(name=statename)
    return CVS_STATE_CACHE[statename]

def get_tag(tagname, project):
    """
    Fetches a CVS tag from a repository
    
    @param tagname: name of the tag
    @param project: dbobjects.Project object
    """
    if not TAG_CACHE.has_key(project.id):
        TAG_CACHE[project.id] = {}
    if TAG_CACHE[project.id].has_key(tagname):
        return TAG_CACHE[project.id][tagname]
    outtag = Tag.select(AND(Tag.q.name==tagname,
                            Tag.q.projectID == project.id))
    if outtag.count():
        TAG_CACHE[project.id][tagname] = outtag[0]
    else:
        TAG_CACHE[project.id][tagname] = Tag(name=tagname, project=project)
    return TAG_CACHE[project.id][tagname]
    
def process_delta(commit, delta, tag=None):
    """
    Processes the changes from a file delta
    
    @param commit:
    @param delta:
    """
    fileobj = get_file(delta.filename, project=commit.project)
    
    filestate = get_cvs_state(delta)
    filecommit = FileCommit(file=fileobj, cvsCommit=commit,
                            date=commit.startDate, revision=delta.newver,
                            linesAdded=delta.linesadded, linesRemoved=delta.linesremoved,
                            state=filestate)
    if tag:
        filecommit.addTag(tag) # IGNORE:E1101
    
def process_project(cvsroot, project, community, cache=False):
    """
    This is a shell function the begins to process a project.
    
    Originally the contents of process_patch_stream were in here too, but those
    were moved out when the testing ability was added to the system.
    
    @param cvsroot: the root directory to examine
    @param project: dbobjects.Project object
    @param community: dbobjects.Community
    """
    flush_all_caches()
    log.info("Using cache for loading project %s", project.name)
    patchsets = cvsimporter.import_module(cvsroot, project.name, cache=cache)
    process_patch_stream(patchsets, project, community)
    
def process_patch_stream(patchsets, project, community):
    """
    This function does the meat of handling a patch stream.
    
    @param patchsets: a list of cvsimporter.PatchSet objects
    @param project: dbobjects.Project object
    @param community: dbobjects.Community
    """
    log.info("%d patchsets to process", len(patchsets))
    trans = get_connection().transaction()
    for seqnum, pset in enumerate(patchsets):
        log.debug("patchset %d - %s", seqnum, pset)
        # first get the user
        user = get_user(username=pset.author, community=community)
        # create the commit
        commit = CVSCommit(project=project, user=user,
                           startDate=pset.date, stopDate=pset.date,
                           intro=pset.log[:255], message=pset.log,
                           branch=pset.branch)
        # if there is a tag, get it
        tag = None
        if pset.tag:
            tag = get_tag(pset.tag, project)
            
        # iterate over each of the file modifications
        for delta in pset.deltas.itervalues():
            process_delta(commit, delta, tag)
    trans.commit()
            
def show_test_error():
    """
    Show the error message when utilizing any of the test functions
    """
    print "When running a test, make sure that --test, --masterproject, and --project are set"
    print ""
    print "Not all values set -- exiting"
    
def process_test(community, infile, masterproject, project):
    """
    Runs a test import from a particular file
    
    @param community: dbobject.Community
    @param infile: string of file to read in
    @param masterproject: string of name of master project to use
    @param project: string of name of project to use
    """
    masterproj = get_master_project(community, masterproject)
    proj = get_project(project, masterproj, "::DUMMY::" + project)
    # note -- this is just a guess, I'm not 100% certain that cvsps is latin-1
    patchsets = cvsimporter.process_data(codecs.open(infile, "r", "latin-1").read())
    log.info("dump file successfully read")
    process_patch_stream(patchsets, proj, community)
    
def main():
    """
    Default handler for importing all of the eclipse data
    """
    parser = OptionParser()
    parser.add_option("--dburi", "-u", dest="uri",
                      help="database name to connect to",
                      default="postgres://"+os.getenv("USER")+"@/cvsminer",
                      action="store")
    parser.add_option("-l", "--loglevel", dest="loglevel",
                      help="Manually specify logging level (DEBUG, INFO, WARN, etc)",
                      default="INFO", action="store") 
    parser.add_option("-d", "--debug", action="store_true",
                      dest="debug", default=False,
                      help="sqlobject debugging messages")
    parser.add_option("--cvsroot", dest="cvsroot",
                      help="root CVS directory",
                      action="store", default="/home/data/eclipse/cvsroot")
    parser.add_option("--test", dest="test",
                      help="test system by importing a particular file",
                      action="store", default=None)
    parser.add_option("--masterproject", dest="testmasterproject",
                      help="test system master project name",
                      action="store", default=None)
    parser.add_option("--project", dest="testproject",
                      help="test system project name",
                      action="store", default=None)
    parser.add_option("--usecache", dest="usecache",
                      help="if a text dump of cvsps exists, use it",
                      action="store_true", default=False)
        
    (options, args) = parser.parse_args() # IGNORE:W0612
    
    log.setLevel(getattr(logging, options.loglevel.upper()))

    # connect to the database
    log.debug("connecting to database: %s - debug=%s", options.uri, options.debug)
    connect(options.uri, debug=options.debug, autocommit=False)
    
    community = get_community("eclipse")
    
    if options.test or options.testmasterproject or options.testproject:
        if not (options.test and options.testmasterproject and options.testproject):
            show_test_error()
            sys.exit()
        log.info("running tests")
        process_test(community=community, infile=options.test,
                     masterproject=options.testmasterproject,
                     project=options.testproject)
    else:
        master_projects = get_repositories(options.cvsroot)
        for mproject in master_projects:
            process_repository(cvsroot=options.cvsroot, repo=mproject,
                               community=community, cache=options.usecache)
        
if __name__ == "__main__":
    logging.basicConfig()
    log = logging.getLogger("cvsimporter_eclipse")
    log.setLevel(logging.INFO)
    main()
    
    
