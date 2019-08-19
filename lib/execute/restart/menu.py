#!/usr/bin/env python

import lib.execute.restart.restart as r
import lib.execute.component as comp
import lib.independence.fs as fs
import lib.ui.menu as menu
import lib.settings as s

# The greater purpose of (functions in) this file is to
# ask users which execution should be restarted


# Returns whether restart-menu should show up at all
def should_show(components):
    unfinished_components = get_incomplete_executions(get_execution_components(components))
    
    installed = []
    for item in components:
        if item.is_installed():
            installed.append(item)

    for item in unfinished_components:
        if set(item.methodcomponents).issubset(installed):
            return True
    return False

# Get apknames of already finished tasks from results.csv
def get_finished_apknames(result_csv):
    returnlist = []
    if not fs.isfile(result_csv):
        return []
    with open(result_csv) as csv:
        for line in csv:
            returnlist.append(line.split(',', 2)[1])
    return returnlist

# Returns True if given execomponent had finished execution, False otherwise
def is_complete_execution(execomponent):
    finished_names_list = get_finished_apknames(fs.join(execomponent.resultdir, 'results.csv'))
    return len(execomponent.tasks)/len(execomponent.methodcomponents) == len(finished_names_list)

# Returns a list of ExecutionComponents which did not complete during last run
def get_incomplete_executions(execomponents):
    returnlist = []
    for n, execomponent in enumerate(execomponents):
        if fs.isfile(execomponent.resultdir, s.runconf):
            if not is_complete_execution(execomponent):
                returnlist.append(execomponent)
    return returnlist

# Returns a list of ExecutionComponents, representing all executed items currently in results-directory
def get_execution_components(components):
    execomponents = []
    if fs.isdir(s.resultsdir):
        for item in fs.lsonlydir(s.resultsdir, full_paths=True):
            if fs.isfile(item, s.runconf):
                execomponents.append(comp.ExecutionComponent(components, fs.join(item, s.runconf)))
    return execomponents

# Shows user a menu to install components
def restart_execute_menu(components):
    execomponents = get_execution_components(components)

    options = get_incomplete_executions(execomponents)
    print('Found {0} executions which did not conclude.'.format(len(options)))
    print('Which execution do you want to continue?')

    chosen, _ = menu.standard_menu(options, lambda x: fs.basename(x.resultdir))

    if len(chosen) != 0:
        r.restart(chosen)