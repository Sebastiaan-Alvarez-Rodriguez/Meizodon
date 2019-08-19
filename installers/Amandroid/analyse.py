#!/usr/bin/env python
import os

# Prepare for analysis
# runresultpath is path where results of run are, which should be analysed
# analysisresultpath is path where result of analysis should be stored.
# support is a support-object
def prepare_analyse(runresultpath, analysisresultpath, support):
    return

# Analyse given results and store outcome in given path
# analysepath is path where results of run are, which should be analysed
# resultpath is path to a dir where results can be stored, if needed
def analyse(runresultpath, analysisresultpath, support):
    generated_dir = (os.path.basename(runresultpath))[:-4]
    resultfile = runresultpath+'/'+generated_dir+'/result/AppData.txt'
    if not os.path.isfile(resultfile):
        print('No exists: '+resultfile)
        return False
    with open(resultfile, 'r') as file:
        for line in file:
            if line.endswith('TaintPath:\n'):
                return True
    return False