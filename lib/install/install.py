#!/usr/bin/env python

import os
import threading

import lib.download.component as dldcmpnt
import lib.dynamic.component as cmpnt
import lib.download.config as cnf
import lib.download.downloader as dldr
import lib.firepool.firepool as fpool
import lib.independence.fs as fs
import lib.settings as s

# The greater purpose of (functions in) this file is
# to execute result analyses

# Make installdir for given component
def make_installdirectory():
    os.makedirs(s.installdir, exist_ok=True)
    os.makedirs(s.dependencydir, exist_ok=True)

# function to call when multiple components should be installed
def parallel_install(component):
    component.install()
    component.post_install()

# Install given component
def install(component):
    make_installdirectory()

    component.pre_install()
    
    downloadcomp = dldcmpnt.DownloadComponent.init_from_component(component)
    downloadcomp.download()

    component.install()
    component.post_install()

# Install all given components in parallel, with amount of components as
# max quantity of cores
def install_all(components):
    firepool = fpool.Firepool(ask_RAM=False, max_cores=len(components))
    make_installdirectory()

    for component in components:
        component.pre_install()

    downloadcomp = dldcmpnt.DownloadComponent.init_from_components(components)
    downloadcomp.download()

    firepool.fire(parallel_install, [(x,) for x in components])