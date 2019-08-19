#!/usr/bin/env python

import lib.analysis.component as cmpnt
import lib.firepool.firepool as fpool
import lib.independence.fs as fs
import lib.logger.logger as lgr
import lib.settings as s
import lib.ui.color as printer
import lib.ui.menu as menu

# The greater purpose of (functions in) this file is to
# execute result analyses


# Make directory to store analysis outcome
def make_resultdirectory(analysecomponent):
    fs.mkdir(s.analyseddir, exist_ok=True)
    if fs.exists(analysecomponent.analysisresult_path):
        fs.rm(analysecomponent.analysisresult_path)
    fs.mkdir(analysecomponent.analysisresult_path)

# Get a logger object to write analysis results to
def get_logger(analysecomponent):
    default_name = fs.split(analysecomponent.runresult_path)[-3]
    default_path = fs.join(s.analyseddir,default_name,'out.csv')
    return lgr.Logger(default_path)

# Generate required arguments for each specified apk to be multiprocessed
def arg_generator(analysecomponents, logger):
    args = []
    for analysecomponent in analysecomponents:
        args.append((analysecomponent,logger.logqueue,))
    return args

# Returns line in execution csv starting with method+apk_name
# If there is no such line, raises exception
def get_csv_line(analysecomponent):
    result_csv = analysecomponent.resultfile
    method = analysecomponent.methodcomponent
    apk_name = fs.basename(analysecomponent.runresult_path)
    with open(result_csv, 'r') as csv:
        for line in csv:
            if line[-1] == '\n':
                line = line[:-2] if line[-2] == '\r' else line[:-1]
            if line == '\n' or line == '\r\n' or line =='':
                continue
            if line.startswith('{0},{1}'.format(method,apk_name)):
                return line
    raise RuntimeError('Error: Could not find {0} in {1}'.format(apk_name, result_csv))


# Print starting method
def print_start(comp, apk_name):
    color_comp = printer.format(comp, printer.Color.CAN)
    print('[{0}] Starting outcome-analysis of {1}'.format(color_comp,apk_name))

# Print exit status when finished
def print_finish(comp, apk_name, is_malware, analysis_malware):
    color_comp = printer.format(comp, printer.Color.CAN)
    basicstring = '[{0}] Finished outcome-analysis of {1}'.format(color_comp,apk_name)
    if is_malware == analysis_malware:
        color_success = printer.format('with match', printer.Color.GRN)
        successstring = '{0} {1}'.format(basicstring, color_success)
        if analysis_malware:
            print('{0} (confirmed malware)'.format(successstring))
        else:
            print('{0} (confirmed non-malware)'.format(successstring))
    else:
        color_error = printer.format('with mismatch', printer.Color.RED)
        part1string = '{0} {1}'.format(basicstring, color_error)
        if is_malware:
            part2string = '(is malware but undetected)'
        else:
            part2string = '(is not malware but detected)'
        print('{0} {1}'.format(part1string, part2string))

# Function which handles setup before running an analysis
# Unsuitable for parallelization e.g. due to possible user input requests
def prepare_analysis(analysecomponent):
    make_resultdirectory(analysecomponent)
    analysecomponent.prepare_analyse()

# Function where analysis is handled
# Suitable for parallelization
def parallel_analyse(analysecomponent, resultqueue):
    line = get_csv_line(analysecomponent)
    arr = line.split(',')
    cmp_name = arr[0]
    apk_name = arr[1]
    is_malware = arr[2] == 'True'
    exec_time = arr[3]
    had_warnings = arr[4] == 'True'
    had_succes = arr[5] == 'True'
    had_timeout = arr[6] == 'True'
    apk_size = arr[7]
    if (not had_succes) or had_timeout:
        resultqueue.put('{0},{1},{2},{3},{4},{5},{6},{7},{8}'.format(
            cmp_name,
            apk_name,
            is_malware,
            exec_time,
            had_warnings,
            had_succes,
            had_timeout,
            apk_size,
            False
        ))
        return
    print_start(cmp_name, apk_name)
    malicious = analysecomponent.analyse()
    print_finish(cmp_name, apk_name, is_malware, malicious)
    resultqueue.put('{0},{1},{2},{3},{4},{5},{6},{7},{8}'.format(
        cmp_name,
        apk_name,
        is_malware,
        exec_time,
        had_warnings,
        had_succes,
        had_timeout,
        apk_size,
        malicious
    ))

# Run analysis on multiple apk analyse execution results
def analyse_all(analysecomponents):
    safe_comps = []
    for analysecomponent in analysecomponents:
        if not analysecomponent.check_can_analyse():
            print('Cannot find analyse.py for method component "{0}"'.format(str(analysecomponent.methodcomponent)))
        else:
            safe_comps.append(analysecomponent)
            prepare_analysis(analysecomponent)
    if len(safe_comps) == 0:
        return

    logger = get_logger(safe_comps[0])
    firepool = fpool.Firepool(ask_RAM=False)
    args = arg_generator(safe_comps, logger)

    logger.start()
    firepool.fire(parallel_analyse, args)
    logger.stop()