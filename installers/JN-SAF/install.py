#!/usr/bin/env python
import os
import shutil

def pre_install(installerloc, installloc, deploc, support):
    return

def install(installerloc, installloc, deploc, support):
    if not os.path.isfile(installloc+'/argus-saf_2.12-3.2.0-assembly.jar'):
        if os.path.isfile(installloc+'/argus-saf/argus-saf'):
            shutil.move(installloc+'/argus-saf/argus-saf', installloc+'/argus-saf_2.12-3.2.0-assembly.jar')
        else:
            raise RuntimeError('Did not find downloaded "argus-saf"')
    if os.path.isdir(installloc+'/argus-saf/'):
        shutil.rmtree(installloc+'/argus-saf/')

def post_install(installerloc, installloc, deploc, support):
    return

def reconfigure(installerloc, installloc, deploc, support):
    return