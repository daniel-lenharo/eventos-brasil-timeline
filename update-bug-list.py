#!/usr/bin/env python

## Originally written by Rafael Laboissiere in 2015.
##
## This script is hereby placed into the public domain, no rights reserved.

## Use this script for updating file data/events/bugs with more recent
## bugs.  Launch the script from the top level directory, like this:
##
##    ./update-bug-list.py
##
## The file data/events/bugs will be overwritten.

import re
import SOAPpy
from debian import deb822
from datetime import datetime

### This is the granularity for inclusion of bugs in the events database
granularity = 10000

### URL of the Debian bugs website
debbug_url = 'https://bugs.debian.org'

### Initialize the SOAP server for accessing the Debian bugs database
url = '%s/cgi-bin/soap.cgi' % debbug_url
namespace = 'Debbugs/SOAP'
server = SOAPpy.SOAPProxy (url, namespace)

### Get the newest bug number
newest_bug = server.newest_bugs (1) [0]

### Read the bugs database
bug_events_file = 'data/events/bugs'
input = file (bug_events_file).read ().decode ('utf-8').split ('\n')
current_bugs = []
bug_list = deb822.Deb822.iter_paragraphs (input, use_apt_pkg = False)

### Initialize the array for storing the information on the bugs
bug_paras = []

### Regular expression for getting the bug number from the source field
debbug_url_re = re.compile ('%s/(\d+)' % debbug_url)

### Iterate over the paragraphs, storing the bug numbers and building
### their string representation
for para in bug_list:
    m = debbug_url_re.search (para ['source'])
    if m:
        current_bugs.append (int (m.group (1)))
    bug_paras.append ('''Title: %s
Date: %s
Source: %s''' % (para ['title'], para ['date'], para ['source']))

### Get the bug recorded with highest number
last_recorded_bug = max (current_bugs)

### Regular expression for extracting the full name of the bug origniator
email_re = re.compile ('([^<]+)')

### Check whether there are new bugs to retrieve
if newest_bug >= last_recorded_bug + granularity:

    ## Yes : get them
    for i in range (1, 1 + (newest_bug - last_recorded_bug) / granularity):

        ## Get next bug
        bug = last_recorded_bug + i * granularity
        status = server.get_status (bug) [0]

        ## Get the full name of the submitter
        originator = status.value.originator
        m = email_re.search (originator)
        if m:
            originator = m.group (1).rstrip ()

        ## Get the date of submission
        date =  datetime.fromtimestamp (status.value.date).strftime ("%b %d %Y")

        ## Add paragraph to the database
        bug_paras.append ('\n'.join (['Title: Debian Bug #%d reported by %s' % (bug, originator),
                                      'Date: %s' % date,
                                      'Source: %s/%d' % (debbug_url, bug)]))
        print 'New bug found: #%d' % bug

    ## Write the new database
    output = open (bug_events_file, 'w')
    output.write ('\n\n'.join (bug_paras).encode ('utf-8') + '\n')
    output.close ()

else:
    ## No: nothing to do
    print "No new bugs."
