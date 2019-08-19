#!/usr/bin/env python

import datetime
import time

import lib.firepool.firepool as fpool
import lib.independence.fs as fs
import lib.logger.logger as lgr
import lib.settings as s
import lib.ui.menu as menu
import lib.ui.color as printer

# The greater purpose of (functions in) this file is
# to run executions

# Function which handles setup before running an execution
# Unsuitable for parallelization e.g. due to possible user input requests
def prepare_execute(execomponent):
    execomponent.prepare_execute()

# Print starting method (success/warnings/errors)
def print_start(comp, apk_name):
    color_comp = printer.format(comp, printer.Color.CAN)
    print('[{0}] Starting analysis of {1}'.format(color_comp,apk_name))

# Print exit status when finished (success/warnings/errors/timeout)
def print_finish(comp, apk_name, warnings, success, timeout):
    color_comp = printer.format(comp, printer.Color.CAN)
    basicstring = '[{0}] Finished analysis of {1}'.format(color_comp,apk_name)

    if success:
        color_success = printer.format('with success', printer.Color.GRN)
        successstring = '{0} {1}'.format(basicstring, color_success)
        if warnings:
            print('{0} (and warnings)'.format(successstring))
        else:
            print(successstring)
    elif timeout:
        color_timeout = printer.format('with timeout', printer.Color.PRP)
        print('{0} {1}'.format(basicstring, color_timeout))
    else:
        color_error = printer.format('with errors', printer.Color.RED)
        print('{0} {1}'.format(basicstring, color_error))

# Function which handles the running of one analysis.
# This function is suitable for parallelization
def parallel_execute(execomponent, task, ramamount, timeout, logqueue):
    print_start(task.methodcomponent, fs.basename(task.apk.path))

    start = time.time()
    warnings, success, had_timeout = execomponent.execute(task, ramamount, timeout)
    end = time.time()
    totaltime = end - start
    apk_size = fs.sizeof(task.apk.path)
    logqueue.put('{0},{1},{2},{3},{4},{5},{6},{7}'.format(
        str(task.methodcomponent),
        fs.basename(task.apk.path),
        task.apk.malware,
        totaltime,
        warnings,
        success if not had_timeout else False,
        had_timeout,
        apk_size
    ))
    print_finish(task.methodcomponent, fs.basename(task.apk.path), warnings, success, had_timeout)

# Function which handles cleaning things up after running an analysis
# Unsuitable for parallelization since it just cleans up (e.g. stop a database)
def post_execute(execomponent):
    execomponent.post_execute()

# Generate required arguments for each specified apk to be multiprocessed
def arg_generator(execomponent, firepool, logger, timeout):
    args = []
    for task in execomponent.tasks:
        args.append((execomponent,task,firepool.rampercore,timeout,logger.logqueue,))
    return args

# Ask for a timeout
def ask_timeout():
    while True:
        timeout = input('Please give a timeout (seconds) for a single analysis execution: ')
        if timeout.isdigit() and int(timeout) > 0:
            return int(timeout)
        else:
            print('Print a number > 0')

# Run given component on execution configuration
def execute(execomponent):
    prepare_execute(execomponent)

    logger = lgr.Logger(fs.join(execomponent.resultdir,'results.csv'))
    firepool = fpool.Firepool()
    timeout = ask_timeout()
    args = arg_generator(execomponent, firepool, logger, timeout)


    logger.start()
    firepool.fire(parallel_execute, args)
    logger.stop()

    post_execute(execomponent)