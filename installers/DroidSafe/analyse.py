#!/usr/bin/env python
import os

# Prepare for analysis
# analysepath is path where results of run are, which should be analysed
# resultpath is path where result of analysis should be stored.
def prepare_analyse(runresultpath, analysisresultpath, support):
    pass

def get_report_path(resultpath):
    contents = os.listdir(resultpath+'/droidsafe-gen/')
    for item in contents:
        if os.path.isfile(resultpath+'/droidsafe-gen/'+item) and item.endswith('_pta-report.txt'):
            return resultpath+'/droidsafe-gen/'+item

# Analyse given results and store outcome in given path
# analysepath is path where results of run are, which should be analysed
# resultpath is path where result of analysis should be stored.
def analyse(runresultpath, analysisresultpath, support):
    taint_paths = 0
    report_path = get_report_path(runresultpath)
    with open(report_path, 'r') as report:
        for line in report:
            if line.startswith('Flows into sinks'):
                total_taint_paths=int(line.split(' ')[-1])
                if total_taint_paths > 0:
                    return True
    return False