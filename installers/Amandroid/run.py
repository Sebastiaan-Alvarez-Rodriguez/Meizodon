#!/usr/bin/env python
import os
import subprocess

# Returns true if analysis was successful, false otherwise
def analysis_success(output_path):
    with open(output_path, 'r') as checkfile:
        lines = checkfile.read().splitlines()
        if len(lines) == 0:
            return False
        last_line = lines[-1]
        return last_line == 'Done!'

def append_to_log(logpath, lines):
    with open(logpath, 'a') as checkfile:
        checkfile.write(lines)

def correct_error_log(output_path, error_path):
    otherfound = False

    linebuf = ''
    foundlines = ''

    with open(error_path, 'r') as checkfile:
        for line in checkfile:
            if (not otherfound) and not line.startswith('ERROR'):
                otherfound = True
                foundlines = line
            elif otherfound:
                if not line.startswith('ERROR'):
                    foundlines += line + '\n'
                else:
                    otherfound = False
                    linebuf += foundlines
    if otherfound and len(foundlines) > 0:
        linebuf += foundlines
    append_to_log(output_path, linebuf)

# Prepare for apk analysis launch
def prepare_run(installloc, deploc, apkpaths, resultpaths, support):
    return
# Run analysis on given apk
def run(installloc, deploc, apkpath, resultpath, ramamount, timeout, support):
    env = support.get_java_env()

    output_path = resultpath+'/'+support.get_out_log()
    error_path = resultpath+'/'+support.get_error_log()
    output_file = open(output_path, 'wb', 0)
    error_file = open(error_path, 'wb', 0)

    env['CLASSPATH']='.:'+installloc+'/Amandroid/lib/*';
    env['HOME']=installloc;
    env['JAVA_OPTS'] = '-Xmx'+str(ramamount)+'g'
    env['AMANDROID_DIST'] = 'true'
    env['SCALA_HOME'] = installloc+'/Amandroid/platform/scala'
    env['PATH'] = env['SCALA_HOME']+':'+env['PATH']
    env['AMANDROID_HOME'] = installloc+'/Amandroid'
    env['SIREUM_HOME'] = installloc+'/Amandroid'
    has_timeout = False
    try:
        subprocess.call([
            deploc+'/Scala/bin/scala',
            '-target:jvm-1.8',
            '-nocompdaemon',
            '-savecompiled',
            '-classpath',
            env['CLASSPATH'],
            installloc+'/Amandroid/execute.scala',
            installloc+'/Amandroid',
            'org.sireum.amandroid.cli.TaintAnalysis',
            'DATA_LEAKAGE', # <module: DATA_LEAKAGE, INTENT_INJECTION, PASSWORD_TRACKING, OAUTH_TOKEN_TRACKING, COMMUNICATION_LEAKAGE>
            'false', # debug
            apkpath,
            resultpath],
            cwd=installloc+'/Amandroid/', env=env,
            stdout=output_file, stderr=error_file,timeout=timeout)
    except subprocess.TimeoutExpired:
        has_timeout = True

    output_file.close()
    error_file.close()

    success = analysis_success(output_path)
    warnings = os.stat(error_path).st_size != 0
    correct_error_log(output_path, error_path)

    if has_timeout:
        return warnings, False, True

    return warnings, success, has_timeout

def post_run(installloc, deploc, apkpaths, resultpaths, support):
    return