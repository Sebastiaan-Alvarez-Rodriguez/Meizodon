#!/usr/bin/env python

import configparser
import datetime

import lib.dynamic.component as comp
import lib.execute.apk as apkfile
import lib.execute.config as cnf
import lib.execute.task as task
import lib.independence.fs as fs
import lib.settings as s

class ExecutionComponent(object):
    """Object to facilitate execution runs"""

    # Constructor:
    # methodcomponents is a list of components which we run during execution
    # path is the path to a saved executioncomponent file, which will be
    # read in. If path is not specified, then we ask user for apk paths. 
    # Note: If path is given, all available components should be given in methodcomponents parameter
    def __init__(self, methodcomponents, path=None):
        if path:
            self.from_file(path, methodcomponents)
        else:
            self.resultdir = fs.join(s.resultsdir, self.make_result_dirname())
            self.methodcomponents = methodcomponents

            self.apks = cnf.get_apks()
            self.generate_tasks()

    # Generate a list of execution tasks, based on the current apk paths
    def generate_tasks(self):
        self.tasks = []
        for apk in self.apks:
            apkname = fs.split(apk.path)[-1]
            for component in self.methodcomponents:
                resultpath = fs.join(self.resultdir, str(component), apkname)
                self.tasks.append(task.ExecutionTask(component, apk, resultpath))

    # Generate a directory name for the result
    def make_result_dirname(self):
        now = datetime.datetime.now()
        dirname = '{0}-{1:0=2d}-{2:0=2d}({3:0=2d}:{4:0=2d}:{5:0=2d})'.format(
            now.year,now.month,now.day,now.hour,now.minute,now.second)
        return dirname

    # Primary call-through function to call to prepare execution
    def prepare_execute(self):
        for task in self.tasks:
            fs.mkdir(task.resultpath, exist_ok=True)
        for component in self.methodcomponents:
            component.prepare_run(self.tasks)
        self.to_file(fs.join(self.resultdir, s.runconf))

    # Primary call-through function to call to run execution
    def execute(self, task, ramamount, timeout):
        return task.methodcomponent.run(task, ramamount, timeout)

    # Primary call-through function to call to start post execution
    def post_execute(self):
        for component in self.methodcomponents:
            component.post_run(self.tasks)
        fs.rm(self.resultdir, s.runconf)

    # Write components and apk paths to a file
    def to_file(self, path):
        with open(path, 'w') as runconf:
            runconf.write('[components]\n')
            for component in self.methodcomponents:
                runconf.write(str(component)+'\n')
            runconf.write('[apks]\n')
            
            for apk in self.apks:
                runconf.write(apkfile.Apk.get_string(apk)+'\n')

    # Read components and apk paths to a file
    def from_file(self, path, available_components):
        componentsfound = False
        apksfound = False
        self.resultdir = fs.dirname(path)
        self.methodcomponents = []
        self.apks = []
        with open(path, 'r') as runconf:
            for line in runconf:
                if line[-1] == '\n':
                    line = line[:-2] if line[-2] == '\r' else line[:-1]
                if line == '\n' or line == '\r\n' or line == '':
                    continue

                if line.startswith('[components]'):
                    componentsfound = True
                    apksfound = False
                elif line.startswith('[apks]'):
                    componentsfound = False
                    apksfound = True
                elif componentsfound:
                    self.methodcomponents.append(comp.Component.get_component_for_name(available_components, line))
                elif apksfound:
                    self.apks.append(apkfile.Apk.from_string(line))
        self.generate_tasks()