#!/usr/bin/python2.4
"""
matrixDependecy.py

Calculates the matrix dependencies between different files for
a project
"""

__author__ = "Patrick Wagstrom <pwagstro@andrew.cmu.edu>"
__copyright__ = "Copyright (c) 2006 Patrick Wagstrom"
__license__ = "GNU General Public License Version 2"

import logging
import timeutil
from optparse import OptionParser
from dbobjects import *
from sets import Set
import numpy
import scipy, scipy.io
import sys
from dynet import *

# these are default values for ths simulation, they can be overruled
# using the command line parameters
CLASSPARENTS = {}

def buildParentClassDict():
    """For each class in the database, this calculates what their root parent is"""
    global CLASSPARENTS
    tdict = {}
    fdict = {}
    pc = FileClass.select()
    for t in pc:
        tdict[t.id] = t
    for t in tdict.keys():
        tid = t
        telem = tdict[t]
        while telem.parentID != None:
            telem = telem.parent
        fdict[t] = telem
    CLASSPARENTS = fdict

def enumerateFiles(project):
    """Performs an enumeration on all of the files, starting from 0
    in the order there were saved in the database"""
    f = File.select(AND(File.q.projectID == Project.q.id,
                        Project.q.masterProjectID == project.id),
                    orderBy=File.q.id)
    ctr = 0
    mapHash = {}
    for tf in f:
        mapHash[tf.id] = ctr
        ctr = ctr + 1
    return mapHash


def buildDynetML(project, nonew, nodead, threshold, threshavg, mult=False, onlySource=False):
    """Build a Dynet ML file where each 'agent' is a file, and two
    'agents' are linked together if they were modified at the same
    time"""
    
    network = DynamicNetwork()
    metaMatrix = MetaMatrix()
    network.addMetaMatrix(metaMatrix)
    files = NodeSet(id="agent", type="agent")
    metaMatrix.addNodeSet(files)
    graph = Graph(sourceType=files, targetType=files, directed=False)
    metaMatrix.addGraph(graph)

    
    buildParentClassDict()
    mapHash = enumerateFiles(project)
    commits = CVSCommit.select(AND(CVSCommit.q.projectID == Project.q.id,
                                   Project.q.masterProjectID == project.id))
    interactionMatrix = numpy.zeros((len(mapHash),len(mapHash)), dtype=int)
    deadState = CVSState.byName("dead")
    
    # iterate over each of the commits
    for com in commits:
        tf = []
        if nonew and nodead:
            cf = File.select(AND(File.q.id == FileCommit.q.fileID,
                                 FileCommit.q.cvsCommitID == com.id,
                                 FileCommit.q.stateID != deadState.id,
                                 OR(FileCommit.q.linesAdded != 0, FileCommit.q.linesRemoved != 0),
                                 OR(FileCommit.q.linesAdded != None, FileCommit.q.linesRemoved != None)))
        elif nodead:
            cf = File.select(AND(File.q.id == FileCommit.q.fileID,
                                 FileCommit.q.cvsCommitID == com.id,
                                 FileCommit.q.stateID != deadState.id))
        elif nonew:
            cf = File.select(AND(File.q.id == FileCommit.q.fileID,
                                 FileCommit.q.cvsCommitID == com.id,
                                 OR(FileCommit.q.linesAdded != 0, FileCommit.q.linesRemoved != 0),
                                 OR(FileCommit.q.linesAdded != None, FileCommit.q.linesRemoved != None)))
        else:
            cf = com.files

        # if we're only worried about source code files, then only select those files
        if onlySource:
            cf = [x for x in cf if CLASSPARENTS[x.fileClassID or 6].name == "Source Code"]
            
        # iterate over each of the files
        for f in cf:
            tf.append(f.id)
            # go through and try to find the
            if not files.has_key(f.id):
                fileNode = Node(id=f.id)
                files.addNode(fileNode)

                fileNode.addProperty(NodeProperty(name="fileName", type="string", value=f.name))
                # get property information for each of the nodes
                query = """SELECT distinct person.person_id FROM person, person_user, cvs_commit, file_cvs_commit
                            WHERE cvs_commit.cvs_commit_id = file_cvs_commit.cvs_commit_id
                                  AND file_cvs_commit.file_id = %d
                                  AND person.person_id = person_user.person_id
                                  AND person_user.user_id = cvs_commit.user_id""" % (f.id)
                numUsers = File._connection.queryAll(query)
                fileNode.addProperty(NodeProperty(name="numUsers", type="int", value=len(numUsers)))

                # get the number of commercial programmers
                query = """SELECT distinct person.person_id
                             FROM person, person_user, cvs_commit, file_cvs_commit, person_corporation
                            WHERE cvs_commit.cvs_commit_id = file_cvs_commit.cvs_commit_id
                                  AND file_cvs_commit.file_id = %d
                                  AND person.person_id = person_user.person_id
                                  AND person_user.user_id = cvs_commit.user_id
                                  AND person.person_id = person_corporation.person_id
                                  """ % (f.id)
                corpUsers = File._connection.queryAll(query)
                fileNode.addProperty(NodeProperty(name="corpUsers", type="int", value=len(corpUsers)))
                fileNode.addProperty(NodeProperty(name="volunteerUsers", type="int", value=len(numUsers)-len(corpUsers)))
                fileNode.addProperty(NodeProperty(name="fracCorpUsers", type="double", value=float(len(corpUsers))/float(len(numUsers))))
                
                query = """SELECT count(distinct file_cvs_commit_id) FROM file_cvs_commit
                            WHERE file_id = %d""" % (f.id)
                numCommits = File._connection.queryAll(query)[0][0]
                fileNode.addProperty(NodeProperty(name="numCommits", type="int", value=numCommits))
                query = """SELECT count(distinct file_cvs_commit_id)
                             FROM file_cvs_commit, cvs_commit, person_user, person, person_corporation
                            WHERE file_cvs_commit.file_id = %d AND file_cvs_commit.cvs_commit_id = cvs_commit.cvs_commit_id
                                  AND cvs_commit.user_id = person_user.user_id
                                  AND person_user.person_id = person.person_id AND person.person_id = person_corporation.person_id""" % (f.id)
                numCorpCommits = File._connection.queryAll(query)[0][0]
                fileNode.addProperty(NodeProperty(name="numCorpCommits", type="int", value=numCorpCommits))
                fileNode.addProperty(NodeProperty(name="numVolCommits", type="int", value=numCommits - numCorpCommits))
                fileNode.addProperty(NodeProperty(name="fracCorpCommits", type="double", value=float(numCorpCommits)/float(numCommits)))
                fileNode.addProperty(NodeProperty(name="fileClass", type="int", value=f.fileClassID))
                fileNode.addProperty(NodeProperty(name="fileClassRoot", type="int", value=CLASSPARENTS[f.fileClassID or 6].id))
                
                
        tf = list(Set(tf))
        for i in xrange(0,len(tf)):
            sourceNode = files[tf[i]]
            for j in xrange(i+1,len(tf)):
                targetNode = files[tf[j]]
                if targetNode.id == sourceNode.id:
                    log.warn("Something weird -- self referencing node")
                thisEdge = graph.getEdge(sourceNode, targetNode)
                if not thisEdge:
                    thisEdge = Edge(source=sourceNode, target=targetNode, type="int", value=0)
                    graph.addEdge(thisEdge)
                thisEdge.value = thisEdge.value + 1

    # FIXME: need to support thresholding again!

    # FIXME: should I support multiplication here?

    # write the file out...
    fn = project.name.replace("/","_")+".dynetml"
    network.saveToFile(fn)
    
def buildMatrix(project, nonew, nodead, threshold, threshavg, mult, onlySource=False):
    buildParentClassDict()
    mapHash = enumerateFiles(project)
    commits = CVSCommit.select(AND(CVSCommit.q.projectID == Project.q.id,
                                   Project.q.masterProjectID == project.id))
    interactionMatrix = numpy.zeros((len(mapHash),len(mapHash)), dtype=int)
    deadState = CVSState.byName("dead")
    
    # iterate over each of the commits
    for com in commits:
        tf = []
        if nonew and nodead:
            cf = File.select(AND(File.q.id == FileCommit.q.fileID,
                                 FileCommit.q.cvsCommitID == com.id,
                                 FileCommit.q.stateID != deadState.id,
                                 OR(FileCommit.q.linesAdded != 0, FileCommit.q.linesRemoved != 0),
                                 OR(FileCommit.q.linesAdded != None, FileCommit.q.linesRemoved != None)))
        elif nodead:
            cf = File.select(AND(File.q.id == FileCommit.q.fileID,
                                 FileCommit.q.cvsCommitID == com.id,
                                 FileCommit.q.stateID != deadState.id))
        elif nonew:
            cf = File.select(AND(File.q.id == FileCommit.q.fileID,
                                 FileCommit.q.cvsCommitID == com.id,
                                 OR(FileCommit.q.linesAdded != 0, FileCommit.q.linesRemoved != 0),
                                 OR(FileCommit.q.linesAdded != None, FileCommit.q.linesRemoved != None)))
        else:
            cf = com.files

        # if we're only worried about source code files, then only select those files
        if onlySource:
            cf = [x for x in cf if CLASSPARENTS[x.fileClassID or 6].name == "Source Code"]

        # iterate over each of the files
        for f in cf:
            tf.append(f.id)
        tf = list(Set(tf))
        for i in xrange(0,len(tf)):
            for j in xrange(i,len(tf)):
                fv = mapHash[tf[i]]
                sv = mapHash[tf[j]]
                interactionMatrix[fv,sv] = interactionMatrix[fv,sv] + 1
                interactionMatrix[sv,fv] = interactionMatrix[sv,fv] + 1

    # now we see if there is thresholding that needs to be done
    if threshavg:
        threshold = numpy.average(numpy.average(interactionMatrix))
    if threshold != 0:
        log.debug("Thresholding at " + str(threshold))
        interactionMatrix = interactionMatrix*numpy.greater_equal(interactionMatrix, threshold)

        
    # write the matrix to a file
    fn = project.name.replace("/","_")+".matrix"
    scipy.io.write_array(fn, interactionMatrix, separator=' ', linesep='\n')

    # this does a matrix multiply if we desire
    if mult:
        log.debug("Performing matrix multiplication (size=%s)", shape)
        interactionMatrix = numpy.dot(interactionMatrix,numpy.transpose(interactionMatrix))
        fn = project.name.replace("/","_")+".mmatrix"
        scipy.io.write_array(fn, interactionMatrix, separator=' ', linesep='\n')
        
    outputLines = []
    for x in mapHash.keys():
        f = File.get(x)
        query = """SELECT count(distinct user_id) FROM cvs_commit, file_cvs_commit
                    WHERE cvs_commit.cvs_commit_id = file_cvs_commit.cvs_commit_id
                          AND file_cvs_commit.file_id = %d""" % (f.id)
        numUsers = File._connection.queryAll(query)[0][0]
        
        query = """SELECT count(file_cvs_commit_id) FROM file_cvs_commit
                    WHERE file_id = %d""" % (f.id)
        numCommits = File._connection.queryAll(query)[0][0]
        outputLines.append([mapHash[x], f.id, f.fileClassID or 6, CLASSPARENTS[f.fileClassID or 6].id, numUsers, numCommits, f.name])
    outputLines.sort(key=lambda x: x[0])
    f = open(project.name.replace("/","_")+".key","w")
    f.write("# id, file_id, class_id, parent_id, numUsers, numCommits\n")
    for output in outputLines:
        f.write(", ".join(["%d"%(y) for y in output[:-1]]) + ", " + output[-1] + "\n")
    f.close()
    
logging.basicConfig()
log = logging.getLogger("matrixDependency.py")
log.setLevel(logging.INFO)

if __name__ == "__main__":
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
    parser.add_option("-l", "--loglevel", dest="loglevel",
                      help="Manually specify logging level (DEBUG, INFO, WARN, etc)",
                      default="INFO", action="store")   
    parser.add_option("-p", "--project", action="store", dest="project",
                      type="string", default=None, help="load data only for this project")
    parser.add_option("--nonew", action="store_true", dest="nonew",
                      default=False, help="ignore new files")
    parser.add_option("--nodead", action="store_true", dest="nodead",
                      default=False, help="ignore dead files")
    parser.add_option("-t", "--threshold", action="store", dest="threshold",
                      type="int", default=0, help="minimum level to threshold at")
    parser.add_option("--threshavg", action="store_true", dest="threshavg",
                      default=False, help="threshold above the minimum level")
    parser.add_option("-m", "--multiply", action="store_true", dest="multiply",
                      default=False, help="Performance matrix multiple for full dependencies")
    parser.add_option("-x", "--dynetml", action="store_true", dest="dynetml",
                      default=False, help="Output DynetML instead")
    parser.add_option("--onlysource", action="store_true", dest="onlySource",
                      default=False, help="Use only source code files")
                     
    log.debug("parsing command line arguments")
    (options, args) = parser.parse_args()

    if options.debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(getattr(logging,options.loglevel.upper()))

    # connect to the database
    log.debug("connecting to database: %s - debug=%s", options.uri, options.debug)
    connect(options.uri, debug=options.debug)

    project = MasterProject.select(MasterProject.q.name == options.project)[0]
    if not options.dynetml:
        buildMatrix(project, options.nonew, options.nodead, options.threshold, options.threshavg, options.multiply, options.onlySource)
    else:
        buildDynetML(project, options.nonew, options.nodead, options.threshold, options.threshavg, options.multiply, options.onlySource)
