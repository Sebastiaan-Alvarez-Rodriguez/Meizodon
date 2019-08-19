#!/usr/bin/env python

import os

import lib.download.config as cnf
import lib.download.task as task
import lib.download.downloader as dldr
import lib.independence.fs as fs
import lib.settings as s

class DownloadComponent(object):
    '''Object to facilitate downloading (requirements of) analysis tools'''
    @staticmethod
    def init_from_components(components):
        dldcmp = DownloadComponent()
        dldcmp.taskset = set()
        for component in components:
            config = cnf.DownloadConfiguration(fs.join(component.installerloc,'conf.conf'))
            dldcmp.taskset.update(DownloadComponent.get_downloads(component,config))
        return dldcmp

    @staticmethod
    def init_from_component(component):
        dldcmp = DownloadComponent()
        dldcmp.taskset = set()
        config = cnf.DownloadConfiguration(fs.join(component.installerloc,'conf.conf'))
        dldcmp.taskset.update(DownloadComponent.get_downloads(component,config))
        return dldcmp

    # Constructor, which reads config in given installerloc's location
    # installerloc is the location of the installer directory for the tool
    # installedloc is the location where the tool should be installed
    def __init__(self):
        self.taskset = None
        return

    # Determines whether a DownloadTask should be downloaded
    # location specifies where DownloadTask is to be installed
    @staticmethod
    def should_download(location):
        for dirname, subdirlist, filelist in os.walk(location):
            if filelist:
                return False
        return True

    # Returns a list of DownloadTasks, which should be downloaded
    # config is the downloadconfig to get DownloadTasks from
    @staticmethod
    def get_downloads(component, config):
        taskset = set()
        for name in config.deps:
            deploc = fs.join(s.dependencydir,config.deps[name].directory)
            depurl = config.deps[name].url
            current_task = task.DownloadTask(name)
            current_task.directory = deploc
            current_task.url = depurl
            if DownloadComponent.should_download(deploc):
                taskset.add(current_task)

        for name in config.pkgs:
            pkgloc = fs.join(component.installationloc,config.pkgs[name].directory)
            pkgurl = config.pkgs[name].url
            current_task = task.DownloadTask(name)
            current_task.directory = pkgloc
            current_task.url = pkgurl
            if DownloadComponent.should_download(pkgloc):
                taskset.add(current_task)

        return taskset

    # Make required directories for all deps and pkgs
    def make_dirs(self):
        for task in self.taskset:
            fs.mkdir(task.directory, exist_ok=True)

    # Most important function: performs downloading!
    def download(self):
        self.make_dirs()
        downloader = dldr.Downloader(list(self.taskset))
        downloader.download_all()