#!/usr/bin/env python

import lib.independence.fs as fs

class DownloadTask(object):
    '''Object to store information on 1 entry in a download configuration'''
    def __init__(self, name):
        self.name = name
        self.directory = ''
        self.url = ''

    def __eq__(self, other): 
        if not isinstance(other, DownloadTask):
            return NotImplemented
        else:
            return self.directory == other.directory and self.url == other.url

    # Return string representation of job
    def __str__(self):
        return self.directory+'::::'+self.url

    def __repr__(self):
        return str(self)

    # Hash object for use in sets/dicts
    def __hash__(self):
        return hash(str(self))