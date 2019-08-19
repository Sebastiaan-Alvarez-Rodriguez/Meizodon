#!/usr/bin/env python

import lib.independence.fs as fs

# The greater purpose of this file is
# to set some global variables that are used at many places

def init(_path):
    global root
    root = _path
    global installersdir
    installersdir=fs.join(_path,'installers')
    global installdir
    installdir=fs.join(_path,'installed')
    global dependencydir
    dependencydir=fs.join(installdir,'dependencies')
    global resultsdir
    resultsdir=fs.join(_path,'results')
    global analyseddir
    analyseddir=fs.join(_path,'analysed')
    global execconfdir
    execconfdir=fs.join(_path,'executionconfigs')
    global runconf
    runconf = 'run.conf'
    global errorlog
    errorlog = 'errors.log'
    global outlog
    outlog = 'out.log'