#!/usr/bin/env python

import os
import sys
import glob

from debian import deb822
from xml.dom.minidom import Document
from dateutil.parser import parse as date_parse


def main(basedir):
    e = []
    error = False
    num = 0

    doc = Document()
    events = doc.createElement('data')
    doc.appendChild(events)

    filenames = glob.glob(os.path.join(basedir, '*'))

    for filename in sorted(filenames):
        if e:
            print >>sys.stderr
        print >>sys.stderr, "Reading events from %s" % filename,
        input = file(filename).read().decode('utf-8').split('\n')

        e = []
        para_num = 0
        for para in deb822.Deb822.iter_paragraphs(input, use_apt_pkg=False):
            if 'Title' not in para:
                title = "para %s" % para_num
                e.append("Start-Date should be before End-Date for %s" % title)
            else:
                title = para['Title']
            dates = {}
            for header in ('Date', 'Start-Date', 'End-Date'):
                if header not in para:
                    continue
                try:
                    dates[header] = date_parse(para[header])
                except (TypeError, ValueError):
                    e.append("Invalid date header %s for %s" % (header, title))
            if 'Start-Date' in para and 'End-Date' in para:
                if 'Start-Date' in dates and 'End-Date' in dates:
                    if dates['Start-Date'] > dates['End-Date']:
                        e.append("Start-Date is after End-Date for %s" % title)
            elif 'Start-Date' in para or 'End-Date' in para:
                e.append("Missing Start-Date or End-Date for %s" % title)
            elif 'Date' not in para:
                e.append("Missing date or date range for %s" % title)
            events.appendChild(create_event(doc, para))
            sys.stderr.write('.')
            num += 1
            para_num += 1
        print >>sys.stderr
        if e:
            for error in e:
                print >>sys.stderr, error
            error = True

    if error:
        return 1
    print >>sys.stderr, "Writing %s events" % num

    print '<!-- Generated from %s/* - do not edit -->' % basedir
    print events.toprettyxml(indent='  ').encode('utf-8')


def create_event(doc, para):
    entry = doc.createElement('entry')
    entry.setAttribute('title', para['Title'])

    if 'Start-Date' in para:
        entry.setAttribute('isDuration', 'true')
        entry.setAttribute('start', para['Start-Date'])
        entry.setAttribute('end', para['End-Date'])
    else:
        entry.setAttribute('start', para['Date'])

    if 'Source' in para:
        text = doc.createTextNode('<a href="%s" target="debian-timeline-source">Source</a>' % para['Source'])
        entry.appendChild(text)

    return entry

if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
