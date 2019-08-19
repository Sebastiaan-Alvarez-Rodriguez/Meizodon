#!/usr/bin/env python

class ExecutionTask(object):
    """Object to store execution tasks"""

    # Constructor:
    # methodcomponent is the methodcomponent to use for analysis
    # apk is the apk-object to analyze
    # resultpath is the full path to the location where results should appear
    def __init__(self, methodcomponent, apk, resultpath):
        self.methodcomponent = methodcomponent
        self.apk = apk
        self.resultpath = resultpath