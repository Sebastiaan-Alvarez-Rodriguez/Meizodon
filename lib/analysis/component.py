#!/usr/bin/env python

import lib.independence.fs as fs
import lib.settings as s

class AnalysisComponent(object):
    '''Object to facilitate analysis runs'''

    # Constructor
    # runresultpath is path where results of run are, which should be analysed.
    # analysisresultpath is path where result of analysis should be stored.
    # methodcomponent is the methodcomponent which produced results.
    def __init__(self, runresultpath, analysisresultpath, methodcomponent, resultfile):
        self.runresult_path = runresultpath
        self.analysisresult_path = analysisresultpath
        self.methodcomponent = methodcomponent
        self.resultfile = resultfile

    # Primary call-through for prepare_analyse function
    def prepare_analyse(self):
        self.methodcomponent.prepare_analyse(self.runresult_path, self.analysisresult_path)

    # Primary call-through for analyse function
    def analyse(self):
        return self.methodcomponent.analyse(self.runresult_path, self.analysisresult_path)

    # Check whether methodcomponent has analysis code
    def check_can_analyse(self):
        return fs.isfile(s.installersdir,str(self.methodcomponent),'analyse.py')