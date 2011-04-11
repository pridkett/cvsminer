#!/usr/bin/python
"""
dbutil.py provides a set of helper functions for connecting to databases
and executing calls on those databases.  This largely relies on the python
database API.
"""
try:
    import psycopg2
    HAVE_PSYCOPG2=True
except ImportError, imperr:
    HAVE_PSYCOPG2=False
try:
    from pyPgSQL import PgSQL
    HAVE_PGSQL=True
except ImportError, e:
    HAVE_PGSQL=False
try:
    import MySQLdb
    HAVE_MYSQL=True
except ImportError, e:
    HAVE_MYSQL=False
import logging

# need to call the logging functions
logging.basicConfig()
log = logging.getLogger("dbutil")
log.setLevel(logging.INFO)

def connect(*args, **kwargs):
    """Shorthand for database_connect
    """
    return apply(database_connect, args, kwargs)

def database_connect(*args, **kwargs):
    """Connects to database to store all of the results in

    This function accepts almost any keyword.  All keywords with the exception
    of "engine" are passed to the connect function.  The engine argument
    specifies whether to use MySQL, PostgreSQL or some other engine.
    """
    if HAVE_PGSQL:
        engine = "psql"
    else:
        engine = "mysql"
        
    engineHash = {}
    if HAVE_PGSQL:
        engineHash["psql"] = PgSQL.connect
    if HAVE_MYSQL:
        engineHash["mysql"] = MySQLdb.connect
    if HAVE_PSYCOPG2:
        engineHash["psycopg"] = psycopg2.connect
        
    callArgs = {}
    if len(args) > 0:
        callArgs["user"] = args[0]
    if len(args) > 1:
        callArgs["password"] = args[1]
    if len(args) > 2:
        callArgs["database"] = args[2]
    if len(args) > 3:
        callArgs['host'] = args[3]
        
    for key, val in kwargs.iteritems():
        if callArgs.has_key(key):
            log.error("Argument [%s] specified twice, ignoring value [%s]", key, val)
        if key == "engine":
            engine = val
        else:
            if val != None:
                callArgs[key] = val

    if (engine == 'psql' or engine == 'psycopg') and callArgs.has_key('db') and not callArgs.has_key('database'):
        callArgs['database'] = callArgs['db']
        del(callArgs['db'])
    elif engine == 'mysql' and callArgs.has_key('database') and not callArgs.has_key('db'):
        callArgs['db'] = callArgs['database']
        del(callArgs['database'])
    if engine == "mysql":
        callArgs["charset"] = "utf8"
        callArgs["use_unicode"] = True
        
    db = apply(engineHash[engine.lower()],(), callArgs)

    st = db.cursor()

    return db, st

class GenericCache(object):
    """Provides a base line for which to create generic caches that
    query a database for items in the cache
    """
    def __init__(self, query, db, st, fallback=None, default=None):
        object.__init__(self)
        self.db = db
        self.st = st
        self.query = query
        self.cache = {}
        self.default = default
        self.fallback = fallback
        
    def __getitem__(self, key):
        """Generic method to get an item from the cache
        """
        if self.cache.has_key(key):
            return self.cache[key]
        else:
            try:
                self.st.execute(self.query, (key))
                res = self.st.fetchall()
                if self.st.rowcount == 0 and self.fallback == None:
                    return self.default
                elif self.st.rowcount == 0:
                    self.cache[key] = self.fallback[key]
                    return self.cache[key]
                self.cache[key] = res[0][0]
                return res[0][0]
            except:
                return self.default
        
