#! /usr/bin/env python
'''Fix problem with relative paths to fonts in css files.
These are all in the relative urls.
'''
import os
import glob
import re

regex = re.compile('\./')

DIR_THIS_FILE = os.path.abspath(os.path.dirname(__file__))
DIR_THIS_FILE_SLASHED = DIR_THIS_FILE+'/'

# for css files in this dir, rewrite relative urls
cssfiles = glob.glob(DIR_THIS_FILE+"/*.css.in")
print cssfiles
for f in cssfiles:
    outfname = os.path.splitext(f)[0]
    with open(outfname, 'w') as outfoo:
        for l in open(f).readlines():
            newline = regex.sub(DIR_THIS_FILE_SLASHED, l)
            outfoo.write(newline)
