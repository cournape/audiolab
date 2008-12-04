#! /usr/bin/env python
# Last Change: Thu Nov 02 12:00 PM 2006 J

# Small module to parse header files, and other tools to use libraries with ctype
# David Cournapeau 2006

import re

def get_dict(content, nameregex, valueregex = '([ABCDEF\dx]*)'):
    """Read the content of a header file, parse for a regex nameregex,
    and get the corresponding value (HEX values 0x by default)
    
    This is useful to parse enumerations in header files"""
    sf_dict     = {}
    regex       = re.compile(nameregex + '[\s]*= ' + valueregex)
    for i in content:
        m   = regex.search(i)
        if m:
            sf_dict[m.group(1)]    = m.group(2)
    return sf_dict

def put_dict_file(dict, name):
    items   = dict.items()
    string  = name + ' = {\n\t' + '\'' + items[0][0] + '\'\t: ' + items[0][1]
    for i in range(1, len(items)):
        #print "Putting key %s, value %s" % (items[i][0], items[i][1])
        string  += ',\n\t\'' + items[i][0] + '\'\t: ' + items[i][1]
    string  += '\n}'
    return string

# Functions used to substitute values in File.
# Kind of like config.h and autotools 
import re
def do_subst_in_file(sourcefile, targetfile, dict):
    """Replace all instances of the keys of dict with their values.
    For example, if dict is {'%VERSION%': '1.2345', '%BASE%': 'MyProg'},
    then all instances of %VERSION% in the file will be replaced with 1.2345 etc.
    """
    #print "sourcefile is %s, target is %s" % (sourcefile, targetfile)
    f = open(sourcefile, 'rb')
    contents = f.read()
    f.close()

    for (k,v) in dict.items():
        contents = re.sub(k, v, contents)
        
    f = open(targetfile, 'wb')
    f.write(contents)
    f.close()

