#!/usr/bin/python
"""
networkGenerator

builds the network of commits for a project
"""

from pyPgSQL import PgSQL
from optparse import OptionParser
import logging
import os
import re
import network
import sys
import dynet
import dbutil

SKIP_REGEXPS = []

def build_skip_regexps(filename):
    """Build a list of regular expressions from a file that
    represent all of the filenames that we should skip.
    """
    rv = []
    if not filename:
        return rv
    f = open(filename)
    rv = [re.compile(x.strip()) for x in f.readlines() \
          if len(x.strip()) > 0 and x.strip()[0] != '#']
    f.close()
    SKIP_REGEXPS = rv
    return rv

    
def build_all_networks(username, password, database, dl=false):
    log.debug("Connecting to database")
    db, st = dbutil.database_connect(username, password, database)
    # db = PgSQL.connect(database="cvsminer")
    # st = db.cursor()
    log.debug("database connection succeeded")

    query = """SELECT project_id FROM project"""
    st.execute(query)
    res = st.fetchall()
    for x in res:
        if dl:
            build_network_dl(x[0], db, st)
        else:
            build_network_dynet(x[0], db, st)
        

def valid_filename(fileName):
    """Checks to see if a file is a valid filename
    """
    for x in SKIP_REGEXPS:
        if x.search(fileName):
            log.debug("Skipping file: %s", fileName)
            return False
    return True
        
    
def build_network_dl(project_id, db=None, st=None):
    fileNameMap = {}
    fileIdMap = {}
    revFileNameMap = {}
    revFileIdMap = {}

    log.info("Start creating dataset %d", project_id)

    if db==None:
        log.debug("Connecting to database")
        db = PgSQL.connect(database="cvsminer")
        st = db.cursor()
        log.debug("database connection succeeded")


    query = """SELECT project_name FROM project WHERE project_id=%s"""
    st.execute(query,(project_id))
    res = st.fetchall()
    outfile = "%s.dl" % (res[0][0].replace(".",""))
               
    query = """SELECT file_id, file_name FROM file WHERE project_id=%s ORDER BY file_id"""
    st.execute(query,(project_id))
    res = st.fetchall()
    ctr = 0
    ignored = 0
    log.debug("Found %d results for project %d" , len(res), int(project_id))
    for x in res:
        fileId = x[0]
        fileName = x[1]
        if valid_filename(fileName):
            fileNameMap[fileName] = ctr
            revFileNameMap[ctr] = fileName
            fileIdMap[fileId] = ctr
            revFileIdMap[ctr] = fileId
            ctr = ctr + 1
        else:
            ignored  = ignored + 1
    log.debug("Loaded %d files, skipped %d files", ctr, ignored)
    files = ctr

    n = network.Network((files, files))
    fileNames = [revFileNameMap[x] for x in xrange(files)]
    n.agentNames = fileNames

    query = """SELECT cvs_commit_id FROM cvs_commit WHERE project_id=%s"""
    st.execute(query,(project_id))
    res = st.fetchall()
    for commit_id in [x[0] for x in res]:
        query2 = """SELECT file_id FROM file_cvs_commit WHERE cvs_commit_id=%s"""
        st.execute(query2, commit_id)
        res2 = st.fetchall()
        for i in xrange(len(res2)):
            # log.debug("%d of %d", i, len(res2))
            for j in xrange(i+1, len(res2)):
                if fileIdMap.has_key(res2[i][0]) and fileIdMap.has_key(res2[j][0]):
                    id1 = fileIdMap[res2[i][0]]
                    id2 = fileIdMap[res2[j][0]]
                    n.setLink(id1, id2, n.getLink(id1, id2)+1)
                    n.setLink(id2, id1, n.getLink(id2, id1)+1)
                
        
        
    log.debug("Dumping DL file")
    n.dumpDL(outfile)
    fn, ext = os.path.splitext(outfile)
    log.debug("Dumping Symmetric Normalized DL File")
    n.normalizeSymmetric(fn+"Sym"+ext)
    log.debug("Dumping Normalized DL File")
    n.normalize(fn+"Norm"+ext)
    
    log.info("Done creating dataset %d", project_id)

def build_network_dynet(project_id, db=None, st=None):
    fileNameMap = {}
    fileIdMap = {}
    revFileNameMap = {}
    revFileIdMap = {}

    log.info("Start creating dataset %d", project_id)

    if db==None:
        log.debug("Connecting to database")
        db = PgSQL.connect(database="cvsminer")
        st = db.cursor()
        log.debug("database connection succeeded")


    query = """SELECT project_name FROM project WHERE project_id=%s"""
    st.execute(query,(project_id))
    res = st.fetchall()
    outfile = "%s.xml" % (res[0][0].replace(".",""))
               
    query = """SELECT file_id, file_name FROM file WHERE project_id=%s ORDER BY file_id"""
    st.execute(query,(project_id))
    res = st.fetchall()
    ctr = 0
    ignored = 0
    log.debug("Found %d results for project %d" , len(res), int(project_id))
    for x in res:
        fileId = x[0]
        fileName = x[1]
        if valid_filename(fileName):
            fileNameMap[fileName] = ctr
            revFileNameMap[ctr] = fileName
            fileIdMap[fileId] = ctr
            revFileIdMap[ctr] = fileId
            ctr = ctr + 1
        else:
            ignored  = ignored + 1
    log.debug("Loaded %d files, skipped %d files", ctr, ignored)
    files = ctr

    n = dynet.DynamicNetwork()
    m = dynet.MetaMatrix()
    n.addMetaMatrix(m)

    ns = dynet.NodeSet(id="files", type="agent")
    m.addNodeSet(ns)

    # create the graph
    g = dynet.Graph(sourceType=ns, targetType=ns, directed=False)
    m.addGraph(g)

    log.debug("Adding in nodes")
    for fn in [revFileNameMap[x] for x in xrange(files)]:
        nd = dynet.Node(id=fn)
        ns.addNode(nd)
        
    # get all the cvs commits for this project
    query = """SELECT cvs_commit_id FROM cvs_commit WHERE project_id=%s"""
    st.execute(query,(project_id))
    res = st.fetchall()
    # work over each individual CVS commit
    log.debug("Adding in edges")
    for commit_id in [x[0] for x in res]:
        query2 = """SELECT b.file_name FROM file_cvs_commit a, file b
                     WHERE a.cvs_commit_id=%s AND b.file_id = a.file_id"""
        st.execute(query2, commit_id)
        res2 = st.fetchall()
        for i in xrange(len(res2)):
            # log.debug("%d of %d", i, len(res2))
            for j in xrange(i+1, len(res2)):
                name1 = res2[i][0]
                name2 = res2[j][0]
                # see if the edge already exists
                edge = g.getEdge(ns.getNode(name1), ns.getNode(name2))
                if edge != None:
                    # increment the value if it does
                    edge.value = edge.value + 1
                else:
                    try:
                        # otherwise create new edge
                        edge = dynet.Edge(source=ns.nodes[name1], target=ns.nodes[name2], value=1)
                        g.addEdge(edge)
                    except:
                        log.debug("Source/Target Unknown: %s %s", name1, name2)

                

    f = open(outfile, "w")
    f.write(n.toXml().serialize(format=1))
    f.close()
    
    log.info("Done creating dataset %d", project_id)

if __name__ == "__main__":
    logging.basicConfig()
    log = logging.getLogger("networkGenerator")
    log.setLevel(logging.INFO)

    parser = OptionParser()
    parser.add_option("-v", "--verbose", dest="verbose",
                      help="print verbose debugging messages",
                      action="store_true", default=False)
    parser.add_option("-d", "--dl", dest="dl",
                      help="output DL files instead of dynetml",
                      action="store_true", default=False)
    parser.add_option("-s", "--skiplist", dest="skiplist",
                      help="filename to use as a skip list",
                      metavar="SKIPLIST", action="store", default=None)
    parser.add_option("--startdate", dest="startdate",
                      help="start date for analysis (eq 20050731)",
                      metavar="STARTDATE",
                      action="store", default=None)
    parser.add_option("--stopdate", dest="stopdate",
                      help="stop date for analysis (eg 20050901",
                      metavar="STOPDATE",
                      action="store", default=None)
    parser.add_option("-u", "--username", dest="username",
                      help="set username to connect to database with",
                      action="store", default="patrick")
    parser.add_option("-d", "--database", dest="database",
                      help="set database name to manipulate",
                      action="store", default="cvsminer")
    parser.add_option("--host", dest="host",
                      help="database host to connect to",
                      action="store", default=None)
    parser.add_option("-p", "--password", dest="password",
                      help="database password for user",
                      action="store", default=None)

                      
    (options, args) = parser.parse_args()

    if options.verbose:
        log.setLevel(logging.DEBUG)

    if (len(args) != 1):
        build_all_networks(options.username,
                           options.password,
                           options.database,
                           dl=options.dl)
    else:
        db, st = dbutil.database_connect(username=options.username,
                                         password=options.password,
                                         databsae=options.database)
        for x in args:
            if options.dl:
                build_network_dl(int(x), db, st)
            else:
                build_network_dynet(int(x), db, st)

        
