#!/usr/bin/env python

import os
import importlib

import lib.independence.fs as fs
import lib.settings as s
import lib.supporter.support as sprt

class Component(object):
    '''Object to facilitate calling dynamically imported modules'''

    # Constructor, which reads config and gets necessary strings
    def __init__(self, installmoduleloc, runmoduleloc, analysemoduleloc, installerloc, installationloc):
        self.installmoduleloc = installmoduleloc
        self.runmoduleloc = runmoduleloc
        self.analysemoduleloc = analysemoduleloc
        self.installerloc = installerloc
        self.installationloc = installationloc
        self.support = sprt.Support()

    # Takes a list of components and name of a component.
    # Returns a component.
    # An error is raised if no matching component is found
    @staticmethod
    def get_component_for_name(components, name):
        for component in components:
            if name == str(component):
                return component
        raise RuntimeError('Error: Could not find component "{0}"!'.format(name))

    # Handles anything that needs to happen before installation
    def pre_install(self):
        tmpmodule=importlib.import_module(self.installmoduleloc)
        tmpmodule.pre_install(self.installerloc, self.installationloc, s.dependencydir, self.support)

    # Handles installation of component
    def install(self):
        tmpmodule=importlib.import_module(self.installmoduleloc)
        tmpmodule.install(self.installerloc, self.installationloc, s.dependencydir, self.support)

    # Handles any loose ends after installing
    def post_install(self):
        tmpmodule=importlib.import_module(self.installmoduleloc)
        tmpmodule.post_install(self.installerloc, self.installationloc, s.dependencydir, self.support)
        self.support.reset_registry()

    # Reconfigure component
    def reconfigure(self):
        tmpmodule=importlib.import_module(self.installmoduleloc)
        tmpmodule.reconfigure(self.installerloc, self.installationloc, s.dependencydir, self.support)

    # Prepare apk(s) in path to be run
    def prepare_run(self, tasks):
        tmpmodule=importlib.import_module(self.runmoduleloc)
        apkpathlist = []
        resultpathlist = []
        for task in tasks:
            apkpathlist.append(task.apk.path)
            resultpathlist.append(task.resultpath)
        tmpmodule.prepare_run(self.installationloc, s.dependencydir, apkpathlist, resultpathlist, self.support)

    # Run apk(s). Returns pair (tuple) of bools.
    # First of pair is True if there were warnings during analysis, otherwise false
    # Second of pair is True if analysis was successful, false otherwise 
    def run(self, task, ramamount, timeout):
        tmpmodule=importlib.import_module(self.runmoduleloc)
        retval = tmpmodule.run(self.installationloc, s.dependencydir, task.apk.path, task.resultpath, ramamount, timeout, self.support)
        self.support.reset_registry()
        return retval

    # Perform final operations after running
    def post_run(self, tasks):
        tmpmodule=importlib.import_module(self.runmoduleloc)
        apkpathlist = []
        resultpathlist = []
        for task in tasks:
            apkpathlist.append(task.apk.path)
            resultpathlist.append(task.resultpath)
        tmpmodule.post_run(self.installationloc, s.dependencydir, apkpathlist, resultpathlist, self.support)

    # Prepare results to be analysed
    # resultpath is a path to a result to be analysed
    # analysisresultpath is a path to use during analysis if needed
    def prepare_analyse(self, resultpath, analysisresultpath):
        tmpmodule=importlib.import_module(self.analysemoduleloc)
        tmpmodule.prepare_analyse(resultpath, analysisresultpath, self.support)

    # Analyse results
    # resultpath is a path to a result to be analysed
    # analysisresultpath is a path to use during analysis if needed
    def analyse(self, resultpath, analysisresultpath):
        tmpmodule=importlib.import_module(self.analysemoduleloc)
        return tmpmodule.analyse(resultpath, analysisresultpath, self.support)

    # Returns whether component is installed or not
    def is_installed(self):
        try:
            if os.path.isdir(self.installationloc):
                return len(os.listdir(self.installationloc)) > 0
            else:
                return False
        except Exception as ignored:
            return False

    # Return string representation of component
    def __str__(self):
        return fs.split(self.installerloc)[-1]
    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(str(self))

    # For ordering alphabetically: implementation of less-than operator
    def __lt__(self, other):
        return str(self) < str(other)
    # For ordering alphabetically and comparisons: implementation of equal operator
    def __eq__(self, other):
        return str(self) == str(other)