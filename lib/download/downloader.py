#!/usr/bin/env python

import gzip
import sys
import tarfile
import threading
import urllib.request
import zipfile

import lib.download.task as task
import lib.independence.fs as fs
import lib.ui.color as printer

# The greater purpose of (functions in) this file is
# to download a list of DownloadTasks

class Downloader(object):
    '''Object to facilitate downloading'''

    # Constructor
    # tasklist is the list of DownloadTasks which should be downloaded
    def __init__(self, tasklist):
        self.tasklist = tasklist

    # Returns True if the name suggests it is a tar archive, otherwise False
    def is_tar(self, name):
        return name.endswith('.tar') or name.endswith('tar.xz')\
        or name.endswith('tar.gz') or name.endswith('.tgz')

    # Returns True if the name suggests it is a zip archive, otherwise False
    def is_zip(self, name):
        return name.endswith('.zip')

    # Returns True if the name suggests it is a gzip archive, otherwise False
    def is_gzip(self, name):
        return name.endswith('.gz')

    # Extract output of downloaded file, if it has a compatible format
    # task is the task for which the file is downloaded
    def extract(self, task):
        target = fs.join(task.directory,task.name)
        basicstring = printer.format('extracter', printer.Color.CAN)
        extractstring = printer.format('extracting', printer.Color.YEL)
        print('[{0}] {1} {2}'.format(basicstring, extractstring, task.name))

        if self.is_tar(task.url):
            ttar = tarfile.open(target, 'r')
            ttar.extractall(path=task.directory)
        elif self.is_zip(task.url):
            tzip = zipfile.ZipFile(target, 'r')
            tzip.extractall(task.directory)
            tzip.close()
        elif self.is_gzip(task.url):
            with gzip.open(target, 'rb') as f_in:
                with open(task.directory, 'wb') as f_out:
                    fs.cp(f_in, f_out)
        else:
            return

        finishedstring = printer.format('extracted', printer.Color.GRN)
        print('[{0}] {1} {2}'.format(basicstring, finishedstring, task.name))

        fs.rm(fs.join(task.directory, task.name))

        dircontents = fs.ls(task.directory)
        if len(dircontents) == 1 and fs.isdir(task.directory,dircontents[0]):
            subdircontents = fs.ls(task.directory,dircontents[0])
            for file in subdircontents:
                path = fs.join(task.directory,dircontents[0])
                fs.mv(fs.join(path,file), task.directory)
            fs.rm(task.directory, dircontents[0], ignore_errors=True)

    # Downloads a DownloadTask and prints some user information
    # task is the downloadtask which contains the download information
    def download(self, task):
        basicstring = printer.format('downloader', printer.Color.CAN)
        downloadstring = printer.format('downloading', printer.Color.YEL)
        print('[{0}] {1} {2}'.format(basicstring, downloadstring, task.name))

        u = urllib.request.urlopen(task.url)
        with open(fs.join(task.directory,task.name), 'wb') as out_file:
            out_file.write(u.read())

        finishedstring = printer.format('downloaded', printer.Color.GRN)
        print('[{0}] {1} {2}'.format(basicstring, finishedstring, task.name))

    # Parallel function, which is called to download all tasks
    # task is the downloadtask which should be operated on
    def parallel_exec(self, task):
        self.download(task)

        if self.is_tar(task.url)\
        or self.is_zip(task.url)\
        or self.is_gzip(task.url):
            self.extract(task)

    # Main function to call. Each DownloadTask will be performed
    def download_all(self):
        threads = []
        for task in self.tasklist:
            threads.append(threading.Thread(target=self.parallel_exec, args=(task,)))

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()