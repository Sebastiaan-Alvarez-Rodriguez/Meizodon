#!/usr/bin/env python

import lib.dynamic.component as cmpnt
import lib.execute.execute as e
import lib.firepool.firepool as fpool
import lib.independence.fs as fs
import lib.logger.logger as lgr

# The greater purpose of (functions in) this file is
# to restart executions

# Get already finished tasks from results.csv
def get_finished_apknames(execomponent):
    if not fs.isfile(execomponent.resultdir,'results.csv'):
        return []
    returnlist = []
    with open(fs.join(execomponent.resultdir,'results.csv')) as csv:
        for line in csv:
            returnlist.append(line.split(',', 2)[1])
    return returnlist

# Removes already finished tasks from an execution component
def remove_finished_tasks(execomponent):
    finished_names_list = get_finished_apknames(execomponent)
    new_task_list = []
    for task in execomponent.tasks:
        if not fs.basename(task.resultpath) in finished_names_list:
            new_task_list.append(task)
    execomponent.tasks = new_task_list


# Run given component on execution configuration
def restart(execomponents):
    firepool = fpool.Firepool()

    for execomponent in execomponents:
        remove_finished_tasks(execomponent)
        e.prepare_execute(execomponent)
        timeout = e.ask_timeout()
        logger = lgr.Logger(fs.join(execomponent.resultdir,'results.csv'))
        args = e.arg_generator(execomponent, firepool, logger, timeout)
        logger.start()
        firepool.fire(e.parallel_execute, args)
        logger.stop()
        e.post_execute(execomponent)