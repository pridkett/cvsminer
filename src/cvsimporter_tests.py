#!/usr/bin/python2.4
"""
cvsimporter_tests.py

@author: Patrick Wagstrom
@contact: patrick@wagstrom.net
@copyright: Copyright (c) 2008 Patrick Wagstrom
@license: GNU General Public License Version 2
"""

import unittest

from cvsimporter import process_patchset, process_data
import datetime

SAMPLETEXT = """PatchSet 2 
Date: 2001/11/05 12:34:21
Author: jeff
Branch: HEAD
Tag: (none) 
Log:
update core->ui

Members:
    main.html:1.1->1.2

Index: pde-ui-home/main.html
===================================================================
RCS file: /home/data/eclipse/cvsroot/eclipse/pde-ui-home/main.html,v
retrieving revision 1.1
retrieving revision 1.2
diff -u -r1.1 -r1.2
--- pde-ui-home/main.html\t2 Nov 2001 19:38:36 -0000\t1.1
+++ pde-ui-home/main.html\t5 Nov 2001 17:34:21 -0000\t1.2
@@ -8,8 +8,8 @@
 <body bgcolor="#FFFFFF" text="#000000">^M
 <table border=0 cellspacing=5 cellpadding=2 width="100%" >^M
   <tr> ^M
-    <td align=left width="72%"> <font class=indextop> pde core </font> <br>
-      <font class=indexsub> plug-in development core </font></td>
+    <td align=left width="72%"> <font class=indextop> pde ui </font> <br>
+      <font class=indexsub> plug-in development ui </font></td>
     <td width="28%"><img src="http://dev.eclipse.org/images/Idea.jpg" height=86 width=120></td>
   </tr>
 </table>"""

MULTILOCATION_PATCH = """PatchSet 3 
Date: 2001/11/05 17:05:44
Author: vlad
Branch: HEAD
Tag: (none) 
Log:
*** empty log message ***

Members: 
    main.html:1.2->1.3 

Index: pde-ui-home/main.html
===================================================================
RCS file: /home/data/eclipse/cvsroot/eclipse/pde-ui-home/main.html,v
retrieving revision 1.2
retrieving revision 1.3
diff -u -r1.2 -r1.3
--- pde-ui-home/main.html    5 Nov 2001 17:34:21 -0000    1.2
+++ pde-ui-home/main.html    5 Nov 2001 22:05:44 -0000    1.3
@@ -31,8 +31,16 @@
   </tr>
   <tr> 
     <td> 
-      <p><font color="#FF0000">&lt;component problem space, goals, approach, etc 
-        here&gt;</font></p>
+      <p>The Plug-In Development Environment (PDE) is a collection of integrated tools targeted at you, the plug-in developer.
+        Whether you are writing plug-ins for a solution using Eclipse, or are writing plug-ins for Eclipse itself,
+        the objective of PDE is to assist you in:
+        <ul>
+          <li>plug-in project setup</li>
+          <li>code generation based on recommended Eclipse patterns</li>
+          <li>testing your plug-in</li>
+          <li>troubleshooting your plug-in</li>
+          <li>packaging your plug-in for Eclipse update</li>
+        </ul></p>
       </td>
   </tr>
 </table>
@@ -45,12 +53,8 @@
     <td> 
       <p>Over the next 6 months the major focus points are:</p>
       <ul>
-        <li><font color="#FF0000">&lt;main work item themes&gt;</font></li>
-        </ul>
-      <p>In the more immediate term, efforts for the next milestone (end of November) 
-        are focused on:</p>
-      <ul>
-        <li><font color="#FF0000">&lt;immediate work items&gt;</font></li>
+        <li>packaging support for new Eclipse Update formats</li>
+        <li>consolidated self-hosting support for Eclipse development</li>
         </ul>
       <p>For more detailed information, check out the <a href="dev.html">Development 
         Resources</a>.</p>
@@ -68,9 +72,9 @@
         check out the developer's mailing list: <a href="http://dev.eclipse.org/mailman/listinfo/pde-ui-dev">pde-ui-dev@eclipse.org</a>. 
         Chat with people there about your problems and interests, and find out 
         what you can do to help.</p>
-      <p><font color="#FF0000">&lt;rough description of the kind of developer 
-        who would be interested and fit will with the work and people in this 
-        component&gt;</font></p>
+      <p>In particular, if you have written (or have ideas for) any utilities, "spy" functions, code generators, transformers,
+        importers, exporters, or any other code that you find useful (or would find useful) for development of plug-ins, and
+        would like to get involved in getting the function integrated as part of PDE, we would like to hear from you.</p>
       <p>For more detailed information, check out the <a href="dev.html">Development 
         Resources</a>.</p>
       </td>"""
       
STREAM_PATCHES = """PatchSet 4 
Date: 2001/11/15 11:43:00
Author: droberts
Branch: HEAD
Tag: (none) 
Log:
Fix bugzilla queries

Members: 
    dev.html:1.1->1.2 

Index: pde-ui-home/dev.html
===================================================================
RCS file: /home/data/eclipse/cvsroot/eclipse/pde-ui-home/dev.html,v
retrieving revision 1.1
retrieving revision 1.2
diff -u -r1.1 -r1.2
--- pde-ui-home/dev.html    2 Nov 2001 19:38:36 -0000    1.1
+++ pde-ui-home/dev.html    15 Nov 2001 16:43:00 -0000    1.2
@@ -16,11 +16,11 @@
     <td align=right valign=top width="2%"><img src="http://dev.eclipse.org/images/Adarrow.gif" border=0 height=16 width=16></td>
     <td width="98%"> <b>Bugs</b> 
       <ul>
-        <li><a href="http://dev.eclipse.org/bugs/buglist.cgi?bug_status=UNCONFIRMED&bug_status=NEW&bug_status=ASSIGNED&bug_status=REOPENED&priority=P1&email1=&emailtype1=substring&emailassigned_to1=1&email2=&emailtype2=substring&emailreporter2=1&bugidtype=include&bug_id=&changedin=&votes=&chfieldfrom=&chfieldto=Now&chfieldvalue=&product=PDE&version=2.0&component=UI&short_desc=&short_desc_type=allwordssubstr&long_desc=&long_desc_type=allwordssubstr&keywords=&keywords_type=anywords&field0-0-0=noop&type0-0-0=noop&value0-0-0=&cmdtype=doit&order=Reuse+same+sort+as+last+time" target="_top">Priority 
+        <li><a href="http://dev.eclipse.org/bugs/buglist.cgi?bug_status=UNCONFIRMED&bug_status=NEW&bug_status=ASSIGNED&bug_status=REOPENED&priority=P1&email1=&emailtype1=substring&emailassigned_to1=1&email2=&emailtype2=substring&emailreporter2=1&bugidtype=include&bug_id=&changedin=&votes=&chfieldfrom=&chfieldto=Now&chfieldvalue=&product=PDE&version=&component=UI&short_desc=&short_desc_type=allwordssubstr&long_desc=&long_desc_type=allwordssubstr&keywords=&keywords_type=anywords&field0-0-0=noop&type0-0-0=noop&value0-0-0=&cmdtype=doit&order=Reuse+same+sort+as+last+time" target="_top">Priority 
           1</a></li>
         <li><a href="http://dev.eclipse.org/bugs/buglist.cgi?bug_status=NEW&bug_status=ASSIGNED&bug_status=REOPENED&email1=&emailtype1=substring&emailassigned_to1=1&email2=&emailtype2=substring&emailreporter2=1&bugidtype=include&bug_id=&changedin=&votes=&chfieldfrom=&chfieldto=Now&chfieldvalue=&product=PDE&component=UI&short_desc=&short_desc_type=allwordssubstr&long_desc=&long_desc_type=allwordssubstr&keywords=&keywords_type=anywords&field0-0-0=noop&type0-0-0=noop&value0-0-0=&cmdtype=doit&newqueryname=&order=Reuse%2Bsame%2Bsort%2Bas%2Blast%2Btime" target="_top" >New, 
           Assigned and Reopened</a> </li>
-        <li><a href="http://dev.eclipse.org/bugs/buglist.cgi?bug_status=RESOLVED&bug_status=VERIFIED&bug_status=CLOSED&email1=&emailtype1=substring&emailassigned_to1=1&email2=&emailtype2=substring&emailreporter2=1&bugidtype=include&bug_id=&changedin=7&votes=&chfield=resolution&chfieldfrom=&chfieldto=Now&chfieldvalue=&product=PDE&version=2.0&component=UI&short_desc=&short_desc_type=allwordssubstr&long_desc=&long_desc_type=allwordssubstr&keywords=&keywords_type=anywords&field0-0-0=noop&type0-0-0=noop&value0-0-0=&cmdtype=doit&order=Reuse+same+sort+as+last+time" target="_top">Resolved 
+        <li><a href="http://dev.eclipse.org/bugs/buglist.cgi?bug_status=RESOLVED&bug_status=VERIFIED&bug_status=CLOSED&email1=&emailtype1=substring&emailassigned_to1=1&email2=&emailtype2=substring&emailreporter2=1&bugidtype=include&bug_id=&changedin=7&votes=&chfield=resolution&chfieldfrom=&chfieldto=Now&chfieldvalue=&product=PDE&version=&component=UI&short_desc=&short_desc_type=allwordssubstr&long_desc=&long_desc_type=allwordssubstr&keywords=&keywords_type=anywords&field0-0-0=noop&type0-0-0=noop&value0-0-0=&cmdtype=doit&order=Reuse+same+sort+as+last+time" target="_top">Resolved 
           in the last week</a></li>
       </ul>
     </td>
---------------------
PatchSet 5 
Date: 2001/11/22 08:07:08
Author: droberts
Branch: HEAD
Tag: (none) 
Log:
Fix mail archive links

Members: 
    dev.html:1.2->1.3 

Index: pde-ui-home/dev.html
===================================================================
RCS file: /home/data/eclipse/cvsroot/eclipse/pde-ui-home/dev.html,v
retrieving revision 1.2
retrieving revision 1.3
diff -u -r1.2 -r1.3
--- pde-ui-home/dev.html    15 Nov 2001 16:43:00 -0000    1.2
+++ pde-ui-home/dev.html    22 Nov 2001 13:07:08 -0000    1.3
@@ -48,8 +48,7 @@
     <td width="98%"> <b>Mailing Lists</b> 
       <ul>
         <li><a href="http://dev.eclipse.org/mailman/listinfo/pde-ui-dev">pde-ui-dev@eclipse.org</a> 
-          (<a href="mailto:pde-ui-dev@eclipse.org">post</a>, <a href="http://dev.eclipse.org/pipermail/pde-ui-dev/">archives</a>, 
-          <a href="http://www.mail-archive.com/pde-ui-dev%40eclipse.org/">search</a>)</li>
+          (<a href="mailto:pde-ui-dev@eclipse.org">post</a>, <a href="http://dev.eclipse.org/mhonarc/lists/pde-ui-dev/maillist.html">archives</a>)</li>
       </ul>
     </td>
   </tr>
---------------------
PatchSet 6 
Date: 2001/12/04 13:37:46
Author: vlad
Branch: HEAD
Tag: (none) 
Log:
*** empty log message ***

Members: 
    dev.html:1.3->1.4 

Index: pde-ui-home/dev.html
===================================================================
RCS file: /home/data/eclipse/cvsroot/eclipse/pde-ui-home/dev.html,v
retrieving revision 1.3
retrieving revision 1.4
diff -u -r1.3 -r1.4
--- pde-ui-home/dev.html    22 Nov 2001 13:07:08 -0000    1.3
+++ pde-ui-home/dev.html    4 Dec 2001 18:37:46 -0000    1.4
@@ -20,7 +20,7 @@
           1</a></li>
         <li><a href="http://dev.eclipse.org/bugs/buglist.cgi?bug_status=NEW&bug_status=ASSIGNED&bug_status=REOPENED&email1=&emailtype1=substring&emailassigned_to1=1&email2=&emailtype2=substring&emailreporter2=1&bugidtype=include&bug_id=&changedin=&votes=&chfieldfrom=&chfieldto=Now&chfieldvalue=&product=PDE&component=UI&short_desc=&short_desc_type=allwordssubstr&long_desc=&long_desc_type=allwordssubstr&keywords=&keywords_type=anywords&field0-0-0=noop&type0-0-0=noop&value0-0-0=&cmdtype=doit&newqueryname=&order=Reuse%2Bsame%2Bsort%2Bas%2Blast%2Btime" target="_top" >New, 
           Assigned and Reopened</a> </li>
-        <li><a href="http://dev.eclipse.org/bugs/buglist.cgi?bug_status=RESOLVED&bug_status=VERIFIED&bug_status=CLOSED&email1=&emailtype1=substring&emailassigned_to1=1&email2=&emailtype2=substring&emailreporter2=1&bugidtype=include&bug_id=&changedin=7&votes=&chfield=resolution&chfieldfrom=&chfieldto=Now&chfieldvalue=&product=PDE&version=&component=UI&short_desc=&short_desc_type=allwordssubstr&long_desc=&long_desc_type=allwordssubstr&keywords=&keywords_type=anywords&field0-0-0=noop&type0-0-0=noop&value0-0-0=&cmdtype=doit&order=Reuse+same+sort+as+last+time" target="_top">Resolved 
+        <li><a href="http://dev.eclipse.org/bugs/buglist.cgi?bug_status=RESOLVED&bug_status=VERIFIED&bug_status=CLOSED&email1=&emailtype1=substring&emailassigned_to1=1&email2=&emailtype2=substring&emailreporter2=1&bugidtype=include&bug_id=&changedin=7&votes=&chfield=&chfieldfrom=&chfieldto=Now&chfieldvalue=&product=PDE&version=&component=UI&short_desc=&short_desc_type=allwordssubstr&long_desc=&long_desc_type=allwordssubstr&keywords=&keywords_type=anywords&field0-0-0=noop&type0-0-0=noop&value0-0-0=&cmdtype=doit&order=Reuse+same+sort+as+last+time" target="_top">Resolved 
           in the last week</a></li>
       </ul>
     </td>
---------------------
PatchSet 7 
Date: 2002/03/22 20:10:09
Author: dejan
Branch: HEAD
Tag: (none) 
Log:
Initial version of self-hosting documents.

Members: 
    .project:INITIAL->1.1 
    dev.html:1.4->1.5 
    selfhosting/classpath.jpg:INITIAL->1.1 
    selfhosting/import1.jpg:INITIAL->1.1 
    selfhosting/import2.jpg:INITIAL->1.1 
    selfhosting/launcher1.jpg:INITIAL->1.1 
    selfhosting/launcher2.jpg:INITIAL->1.1 
    selfhosting/launcher3.jpg:INITIAL->1.1 
    selfhosting/preferences.jpg:INITIAL->1.1 
    selfhosting/runant.jpg:INITIAL->1.1 
    selfhosting/selfhosting-checklist.html:INITIAL->1.1 
    selfhosting/selfhosting.html:INITIAL->1.1 

Index: pde-ui-home/dev.html
===================================================================
RCS file: /home/data/eclipse/cvsroot/eclipse/pde-ui-home/dev.html,v
retrieving revision 1.4
retrieving revision 1.5
diff -u -r1.4 -r1.5
--- pde-ui-home/dev.html    4 Dec 2001 18:37:46 -0000    1.4
+++ pde-ui-home/dev.html    23 Mar 2002 01:10:09 -0000    1.5
@@ -30,6 +30,11 @@
     <td width="98%"> <b>Documents</b> 
       <ul>
         <li><a href="http://dev.eclipse.org/conventions.html">coding conventions</a></li>
+        <li>Eclipse self-hosting</li>
+           <ul>
+        <li><a href="file:///D:/eclipse20020321/eclipse/workspace/pde-ui-home/selfhosting/selfhosting-checklist.html">Quick self-hosting checklist (short)</a></li>
+        <li><a href="file:///D:/eclipse20020321/eclipse/workspace/pde-ui-home/selfhosting/selfhosting.html">Eclipse self-hosting using PDE (long)</a></li>
+        </ul>
       </ul>
     </td>
   </tr>
---------------------"""

def get_filedelta():
    """
    Simple helper function that produces a new file delta from the default
    patch above
    """
    patchset = process_patchset(SAMPLETEXT)
    return patchset.deltas["main.html"]

def get_multi_filedelta():
    """
    Just like get_filedelta, except it loads a patch that hits multiple locations
    """
    patchset = process_patchset(MULTILOCATION_PATCH)
    return patchset.deltas["main.html"]

def get_patchset():
    """
    Creates a sample patchset for the test harness
    """
    return process_patchset(SAMPLETEXT)

def get_patchstream():
    """
    Returns information on a stream of patches
    """
    return process_data(STREAM_PATCHES)

class TestSinglePatch(unittest.TestCase):
    """
    Test harness for examining a single patch
    """
    def test_author_parse(self):
        """
        Ensures that the author element is properly parsed
        """
        patchset = get_patchset()
        self.assertEquals(patchset.author, "jeff")
        
    def test_date_parse(self):
        """
        Ensures that the date element is properly parsed
        """
        patchset = get_patchset()
        self.assertEquals(patchset.date, datetime.datetime(2001, 11, 5, 12, 34, 21))

    def test_log(self):
        """
        Ensure the log was properly saved
        """
        patchset = get_patchset()
        self.assertEquals(patchset.log, "update core->ui\n")
        
    def test_branch(self):
        """
        Make sure the branch was handled properly
        """
        patchset = get_patchset()
        self.assertEquals(patchset.branch, "HEAD")
        
    def test_tag(self):
        patchset = get_patchset()
        self.assertEquals(patchset.tag, None)
        
        
class TestFileDelta(unittest.TestCase):
    """
    Tests issues around particular FileDelta objects
    """
    def test_lines_added_removed(self):
        """
        Ensures that the script is accurately processing lines added and removed
        """
        filedelta = get_filedelta()
        self.assertEquals(filedelta.linesadded, 2)
        self.assertEquals(filedelta.linesremoved, 2)
        
    def test_filename(self):
        """
        Ensures the filename in the filedelta is correct
        """
        filedelta = get_filedelta()
        self.assertEquals(filedelta.filename, "main.html")
        
    def test_version(self):
        """
        Ensures the the version of the file is correct
        """
        filedelta = get_filedelta()
        self.assertEquals(filedelta.oldver, "1.1")
        self.assertEquals(filedelta.newver, "1.2")
       
    def test_multi_file_delta(self):
        """
        Tests cases with multiple locations of changes in a single file
        """
        filedelta = get_multi_filedelta()
        self.assertEquals(filedelta.linesadded, 15)
        self.assertEquals(filedelta.linesremoved, 11)
        
class TestMultiplePatches(unittest.TestCase):
    """
    This handles multiple patches in a sequence
    """
    
    def test_number_patchsets(self):
        """
        Check to make sure it found all of the patch sets
        """
        patchsets = get_patchstream()
        self.assertEquals(len(patchsets), 4)
        
    def test_authors(self):
        """
        Check to make sure it found the authors
        """
        patchsets = get_patchstream()
        self.assertEquals(patchsets[0].author, "droberts")
        self.assertEquals(patchsets[1].author, "droberts")
        self.assertEquals(patchsets[2].author, "vlad")
        self.assertEquals(patchsets[3].author, "dejan")
        
    def test_number_files(self):
        """
        Check to make sure each patchstream has the right number of files
        """
        patchsets = get_patchstream()
        self.assertEquals(len(patchsets[0].deltas), 1)
        self.assertEquals(len(patchsets[1].deltas), 1)
        self.assertEquals(len(patchsets[2].deltas), 1)
        self.assertEquals(len(patchsets[3].deltas), 12)
        
if __name__ == "__main__":
    unittest.main()