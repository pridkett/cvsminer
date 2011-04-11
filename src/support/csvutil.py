"""
csvutil.py

A general purpose library for access and manipulating CSV files

Copyright (c) 2005-2007 Patrick Wagstrom <pwagstro@andrew.cmu.edu>

Licensed under the terms of the GNU General Public License v2
"""

import logging
import csv

def cleanElement(e):
    """Cleans up a particular element in a data row"""
    funcs = (lambda x: int(x),
             lambda x: float(x))
    for f in funcs:
        try:
            return f(e)
        except:
            pass
    # last ditch, return the original
    return e
    
def cleanData(arr):
    return [cleanElement(x) for x in arr]
        
class CSVFile (list):
    def __init__(self, filename):
        self.filename = filename
        self.header = None
        list.__init__(self, [])
        self.data = self
        self._load()

    def column(self, name):
        return self.header.index(name)

    def addColumn(self, name, data):
        """Adds a column to the CSV file"""
        self.header.append(name)
        for x in xrange(len(data)): self[x].append(data[x])
            
    def _load(self):
        reader = csv.reader(open(self.filename, "rb"))
        ctr = 0
        for row in reader:
            if ctr == 0 and row[0][0] == "#":
                self.header = [x.strip().strip("#").strip() for x in row]
            else:
                self.append(cleanData(row))
        
    def sort(self, columnname):
        """Sorts all of the elements in a CSV file"""
        if columnname not in self.header:
            raise Exception("unknown column %s", columnname)
        list.sort(self, key=lambda x: x[self.header.index(columnname)])

    def reverse(self):
        self.reverse()

    def __getitem__(self, key):
        if key in self.header:
            clm = self.column(key)
            return [x[clm] for x in self]
        return list.__getitem__(self, key)
