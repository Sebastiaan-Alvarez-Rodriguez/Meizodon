#!/usr/bin/env python

class Apk(object):
    """Object to store information about apks"""

    # Constructor:
    # path is the path to the apk
    # malware is a boolean indicating whether this apk is malware or not
    def __init__(self, path, malware):
        self.path = path
        self.malware = malware

    @staticmethod
    def get_string(item):
        return str(item)

    @staticmethod
    def from_string(string):
        path = string.split(',')[0]
        malware = string.split(',')[1] == 'True'
        return Apk(path, malware)
    
    def __str__(self):
        return '{0},{1}'.format(self.path, self.malware)