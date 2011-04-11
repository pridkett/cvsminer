#!/usr/bin/python
"""
timeutil.py

Simple utility class to help manage time differences.  This creates some
python 2.3+ datetime objects that can then be compared with simple commands
like a <  b
"""

import time
import sys

MONTHS=["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]

FLAVOR_MX = 1
FLAVOR_STL = 2
datetime = None
try:
    import mx.DateTime
    flavor = FLAVOR_MX
    dummyMxObj = mx.DateTime.DateTime(2000)
except:
    dummyMxObj = None

if sys.version_info[0] > 2 or (sys.version_info[0] == 2 and sys.version_info[1] >= 3):
    # datetime is only on Python 2.3 and newer
    import datetime
    flavor = FLAVOR_STL


if datetime:
    # ripped from the Python documentation
    class FixedOffsetTZ(datetime.tzinfo):
        """Fixed offset in minutes east from UTC."""
    
        def __init__(self, offset, name):
            if offset[0] == '+':
                tzSign = -1
            else:
                tzSign = 1
    
            hours = int(offset[1:3])
            hours = hours - time.timezone/3600 + time.daylight
            minutes = int(offset[3:])
            delta = datetime.timedelta(minutes=(60 * hours + minutes * tzSign))
    
            self.__offset = delta
            self.__name = name
    
        def utcoffset(self, dt):
            return self.__offset
    
        def tzname(self, dt):
            return self.__name
    
        def dst(self, dt):
            return datetime.timedelta(0)

def normalizeDateTime(dt):
    if flavor==FLAVOR_MX and type(dt) is datetime.datetime:
        return makeDateTimeFromTuple(dt.timetuple())
    elif flavor==FLAVOR_STL and type(dt) is type(dummyMxObj):
        return makeDateTimeFromTuple([int(x) for x in dt.tuple()])
    return dt

def makeDateTimeFromTuple(tuple):
    if datetime:
        return datetime.datetime.fromtimestamp(time.mktime(tuple))
    else:
        return mx.DateTime.DateTimeFromTicks(time.mktime(tuple))
    
def makeDateTimeFromString(dateString, useTZ=False):
    """Creates a date time object either with or without timezone info.

    If no timezone info is provided, time will be converted into UTC.

    Expects a string like: 'Tue, 3 May 2005 14:18:31 +0500'
    """

    # occassionally a message will come across with an improperly formatted date
    # this attempts to fix that problem
    dateString = " ".join(dateString.split()[:6])
    if useTZ and datetime:
        timestamp = time.mktime(time.strptime(dateString,"%a, %d %b %Y %H:%M:%S " + dateString[-5:]))
        tz = FixedOffsetTZ(dateString[-5:],dateString[-5:])
        return datetime.datetime.fromtimestamp(timestamp, tz)
        
    timestamp = time.mktime(time.strptime(dateString,"%a, %d %b %Y %H:%M:%S " + dateString[-5:]))
    offset = dateString[-5:]
    hours = int(offset[1:3])
    minutes = int(offset[3:])
    sign = offset[0]
    # always remember that + time zones are ahead of UTC, so we must subtract
    if sign == '+':
        timestamp = timestamp - (hours * 60 + minutes) * 60
    else:
        timestamp = timestamp + (hours * 60 + minutes) * 60
    if datetime:
        return datetime.datetime.fromtimestamp(timestamp)
    return mx.DateTime.DateTimeFromTicks(timestamp)
    

def makeDateTime(dateString, forceMx=False):
    return makeDateTimeFromShortString(dateString, forceMx)

def makeDateTimeFromShortString(dateString, forceMX=False):
    formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y%m%d", "%Y%m%d %H:%M", "%Y-%m-%d"]
    dateString = dateString.strip()
    timestamp = None
    for fmt in formats:
        try:
            timestamp = time.mktime(time.strptime(dateString,fmt))
            break
        except:
            pass
    if not timestamp:
        raise Exception("Unable to format string: %s" % (dateString))
    if datetime and not forceMX:
        return datetime.datetime.fromtimestamp(timestamp)
    return mx.DateTime.DateTimeFromTicks(timestamp)

def makeDateTimeShort(dateString):
    """Creates a datetime object based on input string.  Expects
    string to be formatted like: '20050531'
    """
    print "Using deprecated function: makeDateTimeShort -- use makeDateTimeFromShortString"
    if datetime:
        return datetime.datetime(year=int(dateString[:4]),
                                 month=int(dateString[4:6]),
                                 day=int(dateString[6:]))
    else:
        return mx.DateTime.DateTime(int(dateString[:4]),
                                    int(dateString[4:6]),
                                    int(dateString[6:]))

def makeTimeDelta(weeks=0, days=0, hours=0, minutes=0, seconds=0):
    if datetime:
        return datetime.timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds)
    else:
        return mx.DateTime.TimeDelta(hours=(weeks*7*24)+(days*24)+hours, minutes=minutes, seconds=seconds)

def roundDate(dto):
    """Rounds a date down to the nearest day."""
    return dto - makeTimeDelta(hours=dto.hour, minutes=dto.minute, seconds=dto.second)

def getMonth(monthString):
    """Gets the integer value of the month from the long English string"""
    if monthString.lower() in MONTHS:
        return MONTHS.index(monthString.lower()) + 1
    return None

def addMonths(dto, months):
    """Simple function to add X months to a datetime object"""
    vals = list(dto.timetuple())
    vals[1] = vals[1] + months
    # FIXME: probably should us modulus here
    while vals[1] < 0:
        vals[1] = vals[1] + 12
        vals[0] = vals[0] - 1
    while vals[1] > 12:
        vals[1] = vals[1] - 12
        vals[0] = vals[0] + 1
    return makeDateTimeFromTuple(tuple(vals))

def shortStringDate(dto):
    return "%4d-%02d-%02d %02d:%02d:%02d" % (dto.year, dto.month, dto.day, dto.hour, dto.minute, dto.second)

if __name__ == '__main__':
	if datetime:
		print "Using Python 2.3+ datetime module"
	else:
		print "Using mx.DateTime"

    

 
