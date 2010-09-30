#!/usr/bin/python
"""
eclipse_dashboard_analysis.py

This script actually has two different major components:
  DashboardLoader - takes the output of eclipse_dashboard.py and then proceeds to process the data
  to load it into the cvsminer database.
  DashboardNetworkMaker - takes the data for a given community out of the cvsminer database and
  processes it to create some dynetml files.
"""

__author__ = """Patrick Wagstrom <patrick@wagstrom.net>"""
__copyright__ = """Copyright (c) 2008 Patrick Wagstrom"""

from dbobjects import connect, Community, MasterProject, User, Project, CVSCommit, CVSState, File, FileCommit, Tag, get_connection, expire_all, Corporation, ProjectInvolvement
from dbobjects import Person, PersonUser, raw_query
from sqlobject import AND, IN
from optparse import OptionParser
import os
import datetime
import logging
import dynet
from dynet.serializer import ElementTreeSerializer as ETs
from dynet.serializer import RawSerializer as RAWs
from dynet.serializer import GDFSerializer as GDFs
import sys
from sets import Set
import re

OUTPUTDIR="eclipse_dashboard_nets"
DATADIR="eclipse_dashboard"
COMMUNITY="eclipse"

def add_month(indate):
    """simple helper function to add a month to a datetime object
    
    @param indate: the date we wish to add a month to
    """
    year = indate.year
    month = indate.month
    day = indate.day
    
    month = month + 1
    while month > 12:
        month = month - 12
        year = year + 1
    return datetime.datetime(year, month, day)
        
class Cacher(object):
    """
    The cacher is a simple object that lets me avoid always hitting the database when
    I'm looking for frequently referenced items, such as companies, individuals, etc
    """
    def __init__(self):
        """
        Just initialize the object and create some dicts to store the data
        """
        self.community_cache = {}
        self.master_project_cache = {}
        self.corporation_cache = {}
        self.user_cache = {}
        
    def get_corporation(self, corporation_name):
        """
        Finds the corporation with the given name, creating it if necessary

        @param community_name: the name of the corporation to example (eg "IBM", "RedHat")
        @return: an SQLObject Corporation entity
        @rtype: dbojects.Corporation
        """
        comm = Corporation.select(Corporation.q.name == corporation_name) #pylint: disable-msg=E1101
        if comm.count():
            self.corporation_cache[corporation_name] = comm[0]
            return comm[0]
        else:
            self.corporation_cache[corporation_name] = Corporation(name=corporation_name)
            return self.corporation_cache[corporation_name]

    def get_community(self, community_name):
        """
        Finds the community with the given name, creating it if necessary

        @param community_name: the name of the community to example (eg "eclipse", "gnome")
        @return: an SQLObject Community entity
        @rtype: dbojects.Community
        """
        comm = Community.select(Community.q.name == community_name) #pylint: disable-msg=E1101
        if comm.count():
            self.community_cache[community_name] = comm[0]
            return comm[0]
        else:
            self.community_cache[community_name] = Community(name=community_name)
            return self.community_cache[community_name]

    def get_master_project(self, community, project):
        """
        Gets a master project for a particular community
        
        @param community: a dbobjects.Community 
        @param project: the name of the community
        """
        if not self.master_project_cache.has_key(community.id):
            self.master_project_cache[community.id] = {}
        if self.master_project_cache[community.id].has_key(project):
            return self.master_project_cache[community.id][project]
        mproject = MasterProject.select(AND(MasterProject.q.name == project,              #pylint: disable-msg=E1101
                                            MasterProject.q.communityID == community.id)) #pylint: disable-msg=E1101
        if mproject.count():
            self.master_project_cache[community.id][project] = mproject[0]
        else:
            self.master_project_cache[community.id][project] = MasterProject(name=project, community=community)
        return self.master_project_cache[community.id][project]

    def get_user(self, username, community):
        """
        Gets a user from the database
        @param username: the name of the user
        @param community: a dbobjects.Community element
        """
        if not self.user_cache.has_key(community.id):
            self.user_cache[community.id] = {}
        if self.user_cache[community.id].has_key(username):
            return self.user_cache[community.id][username]
        user = User.select(AND(User.q.name == username,             #pylint: disable-msg=E1101
                               User.q.communityID == community.id)) #pylint: disable-msg=E1101
        if user.count():
            self.user_cache[community.id][username] = user[0]
        else:
            self.user_cache[community.id][username] = User(name=username, community=community)
        return self.user_cache[community.id][username]

class DashboardLoader(Cacher):
    """
    This method is rather specific to Eclipse.  Read in data from the definied
    data directory, process those commits, and add them to the overall database
    """
    def __init__(self):
        Cacher.__init__(self)
        self.datadir = DATADIR

        logging.basicConfig()
        self.log = logging.getLogger("DashboardLoader")
        self.log.setLevel(logging.INFO)

        self.parser = OptionParser()
        self.parser.add_option("--dburi", "-u", dest="uri",
                               help="database name to connect to",
                               default="postgres://"+os.getenv("USER")+"@/cvsminer",
                               action="store")
        self.parser.add_option("-l", "--loglevel", dest="loglevel",
                               help="Manually specify logging level (DEBUG, INFO, WARN, etc)",
                               default="INFO", action="store") 
        self.parser.add_option("-d", "--debug", action="store_true",
                               dest="debug", default=False,
                               help="sqlobject debugging messages")

        self.community = None
        
    def process_files(self):
        """
        This expects output directly from eclipse_dashboard.py which creates a directory
        filled with files that are in the form of YYYYMM.  Open up the directory of files,
        make sure that they're all in the proper format, and process each individual
        file
        """
        for infile in os.listdir(self.datadir):
            try:
                int(infile)
                self.process_file(path=self.datadir, filename=infile)
            # TODO: this really should be a regex to ensure it matches, not an exception
            except ValueError:
                pass

    def process_file(self, path, filename):
        """
        Processes a single individual file from the list of all files.
        
        @param path: the directory where the file is on the hard drive
        @param filename: the name of the file that should be opened and analyzed
        """
        year = int(filename[:4])
        month = int(filename[4:])
        data = [x.split() for x in open(os.path.normpath(path + os.sep + filename)).readlines() if x.strip()[0] != "#"]
        for thiselem in data:
            try:
                corporation, masterproject, username, numcommits, linesadded = thiselem
            except ValueError, verror:
                self.log.error("Exception thrown [%s] - %s - %s", filename, verror, thiselem)
                continue
                          
            masterproject = masterproject.lower()
            numcommits = int(numcommits)
            linesadded = int(linesadded)

            masterproject = self.get_master_project(self.community, masterproject)
            corporation = self.get_corporation(corporation)
            user = self.get_user(username, self.community)

            ProjectInvolvement(year=year, month=month, corporation=corporation,
                              project=masterproject, user=user, numCommits=numcommits,
                              linesAdded=linesadded, date=datetime.datetime(year, month, 1))
            
    def main(self):
        """
        A replacable main function.  If you wish to use the data loader features of this
        class, you'll need to edit the code at the bottom of this file.
        """
        options, args = self.parser.parse_args()

        self.log.setLevel(getattr(logging, options.loglevel.upper()))

        # connect to the database
        self.log.debug("connecting to database: %s - debug=%s", options.uri, options.debug)
        connect(options.uri, debug=options.debug, autocommit=False)
    
        self.community = self.get_community("eclipse")

        self.process_files()

class GNOMEDashboardLoader(Cacher):
    """
    This is somewhat similar to what already happens in DashboardLoader, except it's customized
    for loading in data from GNOME
    """
    def __init__(self):
        Cacher.__init__(self)
        self.datadir = DATADIR

        logging.basicConfig()
        self.log = logging.getLogger("DashboardLoader")
        self.log.setLevel(logging.INFO)

        self.parser = OptionParser()
        self.parser.add_option("--dburi", "-u", dest="uri",
                               help="database name to connect to",
                               default="postgres://"+os.getenv("USER")+"@/cvsminer",
                               action="store")
        self.parser.add_option("-l", "--loglevel", dest="loglevel",
                               help="Manually specify logging level (DEBUG, INFO, WARN, etc)",
                               default="INFO", action="store") 
        self.parser.add_option("-d", "--debug", action="store_true",
                               dest="debug", default=False,
                               help="sqlobject debugging messages")
        self.parser.add_option("-c", "--community", action="store",
                               dest="community", default=COMMUNITY,
                               help="community to load data for")
        self.community = None
        self.unknowncorp = None
        self.corpmap = {}
        
    def link_project(self, mproject):
        """
        Loads in the commits from a project and then attempts to place new entires in the
        user_corporation_project table (aka ProjectInvolvement) table.
        
        @param mproject: a dbobjects.MasterProject element to load the data for
        """
        # FIXME: this currently has no support for hierarchical master projects
        projects = Project.select(Project.q.masterProjectID == mproject.id) # pylint: disable-msg=E1101
        
        # we'll need this for building SQL queries
        projarr = [x.id for x in projects]
        
        # get the first commit on the project so we know what month to start pumping data at
        firstcommit = CVSCommit.select(AND(CVSCommit.q.startDate > datetime.datetime(1997, 11, 01), # pylint: disable-msg=E1101
                                           IN(CVSCommit.q.projectID, projarr))).min(CVSCommit.q.startDate) # pylint: disable-msg=E1101
                                           
        lastcommit = CVSCommit.select(AND(CVSCommit.q.startDate > datetime.datetime(1997, 11, 01), # pylint: disable-msg=E1101
                                          IN(CVSCommit.q.projectID, projarr))).max(CVSCommit.q.startDate) # pylint: disable-msg=E1101
        if firstcommit == None:
            # do something here to indicate that it couldn't process this time period
            self.log.info("Project %s (id=%s) does not appear to have any commits in the window", mproject.name, mproject.id)
            return
                                       
        self.log.info("%s - %s %s", mproject.name, firstcommit, lastcommit)
        
        # iterate on a monthly basis across the data so we have monthly snapshots, just as we do for Eclipse
        currentdate = datetime.datetime(firstcommit.year, firstcommit.month, 1)
        nextdate = add_month(currentdate)
        while currentdate < lastcommit:
            self.link_project_month(mproject, projarr, currentdate, nextdate)
            currentdate = nextdate
            nextdate = add_month(currentdate)
        
    def link_project_month(self, mproject, projarr, currentdate, nextdate):
        """
        Does the "heavy" lifting for linking individuals to projects over a time period
        
        @param mproject: master project to link to
        @param projarr: the array of child projects
        @param currendate: the date to start looking
        @param nextdate: the date to stop looking
        """
        # get the developers who committed during that period
        people = Person.select(AND(Person.q.id == PersonUser.q.personID, # pylint: disable-msg=E1101
                                   PersonUser.q.userID == CVSCommit.q.userID, # pylint: disable-msg=E1101
                                   CVSCommit.q.startDate >= currentdate, # pylint: disable-msg=E1101
                                   CVSCommit.q.startDate < nextdate, # pylint: disable-msg=E1101
                                   IN(CVSCommit.q.projectID, projarr)), distinct=True) # pylint: disable-msg=E1101
        
        count = 0
        numcorp = 0
        numunknown = 0
        # iterate over each of the people
        for person in people:
            user = User.select(AND(User.q.id == PersonUser.q.userID, # pylint: disable-msg=E1101
                                   PersonUser.q.personID == person.id))[0] # pylint: disable-msg=E1101
                
            # first get their company.  cache it if possible
            if self.corpmap.has_key(person.id):
                corporation = self.corpmap[person.id]
            else:
                corporations = person.corporations
                if len(corporations) == 0:
                    corporation = self.unknowncorp
                else:
                    corporation = corporations[0]
                self.corpmap[person.id] = corporation
            
            # increment some tracking counters
            if corporation == self.unknowncorp:
                numunknown = numunknown + 1
            else:
                numcorp = numcorp + 1
                
            # now, get their commits, we need the number of commits and the number of lines added/removed
            commits = CVSCommit.select(AND(CVSCommit.q.userID == PersonUser.q.userID, # pylint: disable-msg=E1101
                                        PersonUser.q.personID == person.id, # pylint: disable-msg=E1101
                                        CVSCommit.q.startDate >= currentdate, # pylint: disable-msg=E1101
                                        CVSCommit.q.startDate < nextdate, # pylint: disable-msg=E1101
                                        IN(CVSCommit.q.projectID, projarr)), distinct=True) # pylint: disable-msg=E1101
            commitids = [x.id for x in commits]
            numcommits = len(commitids)
            
            # in some cases, we don't have complete information, we just set those to empty here
            linesadded = FileCommit.select(IN(FileCommit.q.cvsCommitID, commitids)).sum(FileCommit.q.linesAdded) or 0 # pylint: disable-msg=E1101
            linesremoved = FileCommit.select(IN(FileCommit.q.cvsCommitID, commitids)).sum(FileCommit.q.linesRemoved) or 0 # pylint: disable-msg=E1101
            linesdelta = linesadded - linesremoved
            
            # commit the object
            newpi = ProjectInvolvement(user=user, corporation=corporation,
                                       project=mproject, year=currentdate.year,
                                       month=currentdate.month, date=currentdate,
                                       numCommits=numcommits, linesAdded=linesadded,
                                       linesRemoved=linesremoved, linesDelta=linesdelta)
            count = count + 1
        self.log.info("%s-%s Added %d links (%d corp, %d unknown)...", currentdate, nextdate, count, numcorp, numunknown) 
        return count
            

    def main(self):
        """
        A replacable main function.  If you wish to use the data loader features of this
        class, you'll need to edit the code at the bottom of this file.
        
        This one is basically connects to the database and then attempts to fire up the
        pairing process.
        
        GNOME doesn't use hierarchical project descriptions, so this should not be nearly
        as big of a deal that we force the parent to be none.
        """
        options, args = self.parser.parse_args()
        
        self.log.setLevel(getattr(logging, options.loglevel.upper()))

        # connect to the database
        self.log.debug("connecting to database: %s - debug=%s", options.uri, options.debug)
        connect(options.uri, debug=options.debug, autocommit=False)
    
        try:
            self.community = Community.select(Community.q.name==options.community)[0] # pylint: disable-msg=E1101
        except IndexError:
            self.log.error("Unable to find community \"%s\"", options.community)
            sys.exit()
        
        self.unknowncorp = Corporation.select(Corporation.q.name=="unknown")[0] # pylint: disable-msg=E1101
        
        projects = MasterProject.select(AND(MasterProject.q.communityID==self.community.id, # pylint: disable-msg=E1101
                                            MasterProject.q.parentID==None)) # pylint: disable-msg=E1101
        for project in projects:
            self.link_project(project)

class DashboardNetworkMaker(object):
    """
    Builds a set of networks out of information about the community
    """
    def __init__(self):
        object.__init__(self)
        
        # these are default names, we can override them in the options
        self.outputdir = OUTPUTDIR
        self.communityname = "eclipse"
        
        # create the default network
        self.network = dynet.DynamicNetwork() # pylint: disable-msg=E1101
        self.metamatrix = dynet.MetaMatrix() # pylint: disable-msg=E1101
        self.network.addMetaMatrix(self.metamatrix)
        
        self.developernodes = dynet.NodeSet(type="agent", id="developers") # pylint: disable-msg=E1101
        self.corporationnodes = dynet.NodeSet(type="agent", id="corporations") # pylint: disable-msg=E1101
        self.projectnodes = dynet.NodeSet(type="resource", id="projects") # pylint: disable-msg=E1101
        for thisnodeset in [self.developernodes, self.corporationnodes, self.projectnodes]:
            self.metamatrix.addNodeSet(thisnodeset)
            
        self.membershipgraph = dynet.Graph(id="corporatemembership", sourceType=self.developernodes, targetType=self.corporationnodes) # pylint: disable-msg=E1101
        self.metamatrix.addGraph(self.membershipgraph)
        
        self.graphs = {"corporatemembership": self.membershipgraph}

        logging.basicConfig()
        self.log = logging.getLogger("DashboardNetworkMaker")
        self.log.setLevel(logging.INFO)

        self.parser = OptionParser()
        self.parser.add_option("--dburi", "-u", dest="uri",
                               help="database name to connect to",
                               default="postgres://"+os.getenv("USER")+"@/cvsminer",
                               action="store")
        self.parser.add_option("-l", "--loglevel", dest="loglevel",
                               help="Manually specify logging level (DEBUG, INFO, WARN, etc)",
                               default="INFO", action="store") 
        self.parser.add_option("-d", "--debug", action="store_true",
                               dest="debug", default=False,
                               help="sqlobject debugging messages")
        self.parser.add_option("-o", "--output", action="store",
                               dest="outputdir", default=OUTPUTDIR,
                               help="default directory to save output to")
        self.parser.add_option("-c", "--community", action="store",
                               dest="community", default=COMMUNITY,
                               help="community to process data from")
        self.parser.add_option("--mincommits", action="store",
                               dest="mincommits", default=0, type="int",
                               help="minimum number of commits to consider a project")
        self.parser.add_option("--mindevelopers", action="store",
                               dest="mindevelopers", default=0, type="int",
                               help="minimum number of developers to consider a project")
        self.parser.add_option("--mincorps", action="store",
                               dest="mincorps", default=0, type="int",
                               help="minimum number of corporations to consider a project")
    def _get_node(self, nodeset, nodename):
        retval = nodeset.getNode(nodename)
        if not retval:
            retval = dynet.Node(id=nodename) # pylint: disable-msg=E1101
            nodeset.addNode(retval)
        return retval
    
    def get_developer_node(self, devname):
        return self._get_node(self.developernodes, devname)
    
    def get_project_node(self, projname):
        return self._get_node(self.projectnodes, projname)
    
    def get_corporation_node(self, corpname):
        return self._get_node(self.corporationnodes, corpname)
    
    def add_membership_edge(self, devnode, corpnode):
        thisedge = self.membershipgraph.getEdge(devnode, corpnode)
        if not thisedge:
            thisedge = dynet.Edge(source=devnode, target=corpnode, type="int", value=0) # pylint: disable-msg=E1101
            self.membershipgraph.addEdge(thisedge)
        thisedge.value = thisedge.value + 1
    
    def add_participation_edge(self, devnode, projnode, year, month, numcommits, linesadded):
        graphkey = "%04d%02d" % (year, month)
        if self.graphs.has_key(graphkey):
            thisgraph = self.graphs[graphkey]
        else:
            thisgraph = dynet.Graph(id=graphkey, sourceType=self.developernodes, targetType=self.projectnodes) # pylint: disable-msg=E1101
            self.graphs[graphkey] = thisgraph
            self.metamatrix.addGraph(thisgraph)
            
        thisedge = thisgraph.getEdge(devnode, projnode)
        if not thisedge:
            thisedge = dynet.Edge(devnode, projnode, type="int", value=0) # pylint: disable-msg=E1101
            thisgraph.addEdge(thisedge)
        thisedge.value = thisedge.value + numcommits
        
        
    def add_involvement(self, devinv):
        devnode = self.get_developer_node(devinv.user.name)
        projnode = self.get_project_node(devinv.project.name)
        corpnode = self.get_corporation_node(devinv.corporation.name)
        
        self.add_membership_edge(devnode, corpnode)
        self.add_participation_edge(devnode, projnode, devinv.year, devinv.month, devinv.numCommits, devinv.linesAdded)
        
    def save_nodenames(self):
        for thisnodeset in [self.developernodes, self.corporationnodes, self.projectnodes]:
            f = open(self.outputdir + os.sep + thisnodeset.id + ".txt", "w")
            for agent in thisnodeset.nodes.keys():
                f.write("%s\n" % (agent))
            f.close()
            
    def save_graph(self, network):
        """
        Dumps a network to a file
        
        @param network: a dynet.Network object to dump to the files
        """
        raws = RAWs.RawSerializer()
        raws.toFile(network, self.outputdir + os.sep + network.id + ".raw")

        gdfs = GDFs.GDFSerializer()
        gdfs.toFile(network, self.outputdir + os.sep + network.id + ".gdf")
        
    
    def get_project_set(self, community, mincommits, mindevelopers, mincorps):
        """
        Queries the database to filter through the projects and only fetch the data for
        the projects that meet criteria.  Useful for GNOME
        
        @param community: the community to filter
        @param mincommits: the minimum number of commits for the project
        @param mindevelopers: the minimum number of developers for the project
        @param mincorps: the minimum number of corporations
        """
        if not(mincommits) and not(mindevelopers) and not(mincorps):
            return None
        # create a default set of projects that includes all master projects
        defaultset = Set([x.id for x in MasterProject.select(MasterProject.q.communityID == community.id)]) # pylint: disable-msg=E1101
        
        # now, if we have a commits filter, lets get that
        if mincommits:
            query = """SELECT master_project.master_project_id, count(*) FROM master_project, project, cvs_commit 
                        WHERE master_project.master_project_id = project.master_project_id
                              AND project.project_id = cvs_commit.project_id
                              AND master_project.community_id=%s
                     GROUP BY master_project.master_project_id""" % (community.id)
            commitset = Set([x[0] for x in raw_query(query) if x[1] >= mincommits])
        else:
            commitset = defaultset
        
        # filter by minimum number of developers, we use cvs commits here
        if mindevelopers:
            query = """SELECT master_project.master_project_id, count(distinct cvs_commit.user_id) FROM master_project, project, cvs_commit
                        WHERE master_project.master_project_id = project.master_project_id
                              AND project.project_id = cvs_commit.project_id
                              AND master_project.community_id=%s
                     GROUP BY master_project.master_project_id""" % (community.id)
            print query
            developerset = Set([x[0] for x in raw_query(query) if x[1] >= mindevelopers])
        else:
            developerset = defaultset
        
        # filter by the minimum number of corporations
        if mincorps:
            query = """SELECT project_id, count(distinct corporation_id) FROM user_corporation_project, master_project
                        WHERE user_corporation_project.project_id = master_project.master_project_id
                              AND master_project.community_id=%s
                     GROUP BY user_corporation_project.project_id""" % (community.id)
            print query
            corpset = Set([x[0] for x in raw_query(query) if x[1] >= mincorps])
             
        else:
            corpset = defaultset
            
        retset = commitset.intersection(developerset).intersection(corpset)
        self.log.info("Filtering Down: original=%d, commits=%d, developers=%d, corporations=%d, final=%d", len(defaultset),
                      len(commitset), len(developerset), len(corpset), len(retset))
        return retset

    def multiply_corporate_participation(self):
        """
        Calculates the corporate participation for each of the time periods
        """
        print self.graphs.keys()
        corporatemembership = self.membershipgraph.transpose()
        rematch = re.compile(r"^[0-9]{6}$")
        for netname in self.graphs.keys():
            if not rematch.match(netname):
                continue
            net2 = self.graphs[netname]
            corpinvolvement = corporatemembership * net2
            corpinvolvement.id = "%s-corp-project" % (netname)
            self.metamatrix.addGraph(corpinvolvement)
            corpcorp = corpinvolvement * corpinvolvement.transpose()
            corpcorp.id = "%s-corp-corp" % (netname)
            self.metamatrix.addGraph(corpcorp)
        
    def main(self):
        """
        Generic main handler for the network maker.
        
        Connects to the database, gets the involvments, calls the network maker,
        save the network.  Awesome.
        """
        options, args = self.parser.parse_args()
        
        # these options can be specified via the command line or through the defaults
        self.outputdir = options.outputdir
        self.communityname = options.community
        
        self.log.setLevel(getattr(logging, options.loglevel.upper()))

        # connect to the database
        self.log.debug("connecting to database: %s - debug=%s", options.uri, options.debug)
        connect(options.uri, debug=options.debug, autocommit=False)

        community = Community.select(Community.q.name==self.communityname)[0] #pylint: disable-msg=E1101

        # get the set of projects if we have filter options
        projectset = self.get_project_set(community, options.mincommits, options.mindevelopers, options.mincorps) # pylint: disable-msg=E1101

        if projectset:
            print len(projectset)
            involvement = ProjectInvolvement.select(AND(ProjectInvolvement.q.projectID == MasterProject.q.id, #pylint: disable-msg=E1101
                                                        MasterProject.q.communityID == community.id, # pylint: disable-msg=E1101
                                                        IN(MasterProject.q.id, projectset)), # pylint: disable-msg=E1101
                                                        distinct=True)
        else:
            involvement = ProjectInvolvement.select(AND(ProjectInvolvement.q.projectID == MasterProject.q.id, #pylint: disable-msg=E1101
                                                        MasterProject.q.communityID == community.id), # pylint: disable-msg=E1101
                                                        distinct=True)
        self.log.info("ProjectInvolvement count: %d", involvement.count())
        ctr = 0
        if involvement.count() > 0:
            for devinv in involvement:
                ctr = ctr + 1
                self.add_involvement(devinv)
                if ctr%100 == 0:
                    self.log.info("processing involvement %d", ctr)
        else:
            self.log.error("No developer involvement found, exiting")
            sys.exit()

        # multiply out the corporate involvement
        self.multiply_corporate_participation()
        
        # create the output directory   
        if not os.path.isdir(self.outputdir):
            os.makedirs(self.outputdir)
            
        outputnetwork = ETs.ElementTreeSerializer().toString(self.network)        
        outfile = open(self.outputdir + os.sep + "%s.dynetml" % (self.communityname), "w")
        outfile.write(outputnetwork)
        outfile.close()
        
        # now, dump all of the networks, yowza
        self.save_nodenames()
        for network in self.graphs.itervalues():
            self.save_graph(network)
 
#   
# to determine the mode of operation, uncomment to appropriate set of lines below
#        
if __name__ == "__main__":
    # dashloader = DashboardLoader()
    # dashloader.main()
    
    dashboardnetworkmaker = DashboardNetworkMaker()
    dashboardnetworkmaker.main()
    
    # dashload = GNOMEDashboardLoader()
    # dashload.main()
    
    
