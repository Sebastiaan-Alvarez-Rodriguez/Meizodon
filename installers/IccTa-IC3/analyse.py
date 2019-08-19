#!/usr/bin/env python

# Prepare for analysis
# analysepath is path where results of run are, which should be analysed
# resultpath is path where result of analysis should be stored.
def prepare_analyse(runresultpath, analysisresultpath, support):
    pass

# Analyse given results and store outcome in given path
# analysepath is path where results of run are, which should be analysed
# resultpath is path where result of analysis should be stored.
def analyse(runresultpath, analysisresultpath, support):
    taint_paths = 0
    with open(runresultpath+'/out.log', 'r') as conf:
        for line in conf:
            if line.endswith('connections between sources and sinks\n'):
                # [main] INFO soot.jimple.infoflow.data.pathBuilders
                # .ContextSensitivePathBuilder - Obtainted 3 
                # connections between sources and sinks
                taint_paths = int(line.split(' ')[-6])
                if taint_paths > 0:
                    return True
    return False