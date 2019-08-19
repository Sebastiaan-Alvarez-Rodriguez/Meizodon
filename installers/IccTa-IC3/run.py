#!/usr/bin/env python
import os
import subprocess
import shutil
import time

# Find any mysqld processes and kill them
def kill_DB(mysqldir):
    output = subprocess.check_output(['ps', '-aux'])
    output = output.decode('utf8')
    for line in output.splitlines():
        if mysqldir in line:
            line = line.split()
            pid = line[1]
            print('Pid {0} runs our mysqld. Killing...'.format(pid))
            try:
                subprocess.call(['kill', pid])
                time.sleep(1)
            except Exception as e:
                print('Exception retrieved: probably did not have permission to kill {0}. Continuing...'.format(pid))

# Boot database server
def boot_DB(mysqldir):
    print('Booting SQL SERVER...')
    subprocess.call([
        mysqldir+'/bin/mysqld',
        '--defaults-file='+mysqldir+'/generated_sql.conf',
        # '--basedir='+mysqldir+'/',
        # '--datadir='+mysqldir+'/datadir',
        # '--general-log-file='+mysqldir+'/sql.log',
        # '--pid-file='+mysqldir+'/sql.pid',
        # '--slow-query-log-file='+mysqldir+'/sql-slow.log',
        # '--socket='+mysqldir+'/sock.sock',
        # '--lc-messages-dir='+mysqldir+'/share',
        # '--lc-messages=en_US',
        '--log-error='+mysqldir+'/error.log',
        '--daemonize'])
    while not os.path.isfile(mysqldir+'/sql.pid'):
        time.sleep(1)
    print('SQL SERVER ready...')
    return

# Check whether analysis was successful
def analysis_success(logpath, errorpath):
    with open(logpath, 'r') as checkfile:
        lines = checkfile.read().splitlines()
        if len(lines) == 0:
            return False
        for line in lines:
            if line.endswith(' connections between sources and sinks'):
                return True
    with open(errorpath, 'r') as errorfile:
        for line in errorfile:
            if line == '[main] ERROR soot.jimple.infoflow.Infoflow - No sources or sinks found, aborting analysis\n':
                return True
            if line == '[main] WARN soot.jimple.infoflow.Infoflow - No results found.\n':
                return True
        return False

# Check whether analysis was successful
def analysis_warnings(filepath):
    with open(filepath, 'r') as checkfile:
        for line in checkfile:
            if line.startswith('[main] WARN '):
                return True
        return False

def append_to_log(logpath, lines):
    with open(logpath, 'a') as checkfile:
        checkfile.write(lines)

def correct_error_log(logpath, errorpath):
    otherfound = False

    linebuf = ''
    foundlines = ''

    with open(errorpath, 'r') as checkfile:
        for line in checkfile:
            if (not otherfound) and line.startswith('[main]') and not line.startswith('[main] INFO'):
                otherfound = True
                foundlines = line
            elif otherfound:
                if line.startswith('[main] INFO'):
                    otherfound = False
                    linebuf += foundlines
                else:
                    foundlines += line + '\n'
    if otherfound and len(foundlines) > 0:
        linebuf += foundlines
    os.remove(errorpath)
    append_to_log(errorpath, linebuf)

def correct_out_log(logpath, errorpath):
    infofound = False
    foundlines = ''
    linenumber = 1
    with open(errorpath, 'r') as checkfile:
        for line in checkfile:
            if (not infofound) and line.startswith('[main] INFO'):
                infofound = True
                foundlines = line
            elif infofound:
                if line.startswith('[main]'):
                    append_to_log(logpath, foundlines)
                    infofound = False
                    if line.startswith('[main] INFO'):
                        infofound = True
                        foundlines = line
                else:
                    foundlines += line
            linenumber += 1
    if infofound and len(foundlines) > 0:
        append_to_log(logpath, foundlines)

# Prepare for apk analysis launch
def prepare_run(installloc, deploc, apkpaths, resultpaths, support):
    mysqldir = deploc+'/mysql'
    kill_DB(mysqldir)
    boot_DB(mysqldir)

# Run analysis on apk
def run(installloc, deploc, apkpath, resultpath, ramamount, timeout, support):
    os.makedirs(resultpath+'/output_iccta', exist_ok=True)
    os.makedirs(resultpath+'/output', exist_ok=True)
    os.makedirs(resultpath+'/testspace', exist_ok=True)

    output_path = resultpath+'/'+support.get_out_log()
    error_path = resultpath+'/'+support.get_error_log()
    output_file = open(output_path, 'wb', 0)
    error_file = open(error_path, 'wb', 0)

    env = support.get_java_env()
    env['HOME'] = resultpath
    apkname = os.path.basename(apkpath)
    retargetedPath = resultpath+'/testspace/'+apkname+'.apk/retargeted/retargeted/'+apkname
    forceAndroidJar=deploc+'/Android-SDK/platforms/android-19/android.jar'

    has_timeout = False
    try:
        start = time.time()
        subprocess.call([
            'java',
            '-Xmx'+str(ramamount)+'g',
            '-jar',
            installloc+'/soot-infoflow-android-iccta/iccProvider/ic3/RetargetedApp.jar',
            forceAndroidJar,
            apkpath,
            retargetedPath], cwd=resultpath, env=env,
            stderr=error_file, stdout=output_file, timeout=timeout)
        end = time.time()
        totaltime = end - start
        timeout = timeout - totaltime
    except subprocess.TimeoutExpired:
        has_timeout = True

    if not has_timeout:
        try:
            start = time.time()
            subprocess.call([
                'java',
                '-Xmx'+str(ramamount)+'g',
                '-jar',
                installloc+'/soot-infoflow-android-iccta/iccProvider/ic3/ic3-0.1.0-full.jar',
                '-apkormanifest',
                apkpath,
                '-input',
                retargetedPath,
                '-cp',
                forceAndroidJar,
                '-db',
                installloc+'/soot-infoflow-android-iccta/iccProvider/ic3/cc.properties'],
                cwd=resultpath, env=env,
                stderr=error_file, stdout=output_file, timeout=timeout)
            end = time.time()
            totaltime = end - start
            timeout = timeout - totaltime
        except subprocess.TimeoutExpired:
            has_timeout = True

    if not os.path.exists('{0}/res'.format(resultpath)):
        os.symlink(installloc+'/soot-infoflow-android-iccta/res','{0}/res'.format(resultpath))

    if not os.path.exists('{0}/AndroidCallbacks.txt'.format(resultpath)):
        os.symlink('{0}/soot-infoflow-android-iccta/AndroidCallbacks.txt'.format(installloc),'{0}/AndroidCallbacks.txt'.format(resultpath))

    if not has_timeout:
        try:
            start = time.time()
            subprocess.call([
                'java',
                '-Xmx'+str(ramamount)+'g',
                '-jar',
                installloc+'/soot-infoflow-android-iccta/release/IccTA.jar',
                '-intentMatchLevel',
                '3',
                '-apkPath',
                apkpath,
                '-androidJars',
                deploc+'/Android-SDK/platforms',
                '-iccProvider',
                installloc+'/soot-infoflow-android-iccta/iccProvider/ic3'],
                cwd=resultpath, env=env,
                stderr=error_file, stdout=output_file, timeout=timeout)
            end = time.time()
            totaltime = end - start
            timeout = timeout - totaltime
        except subprocess.TimeoutExpired:
            has_timeout = True
    output_file.close()
    error_file.close()

    correct_out_log(output_path, error_path)
    correct_error_log(output_path, error_path)
    success = analysis_success(output_path,error_path)
    warnings= analysis_warnings(error_path)
    if has_timeout:
        return warnings, False, True
    return warnings, success, has_timeout

def post_run(installloc, deploc, apkpaths, resultpaths, support):
    mysqldir = deploc+'/mysql'
    kill_DB(mysqldir)
    # There is no stopping this (not even environment manipulation)
    if os.path.isdir('{0}/debug'.format(os.environ['HOME'])):
        shutil.rmtree('{0}/debug'.format(os.environ['HOME']))