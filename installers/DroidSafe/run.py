#!/usr/bin/env python
import os
import subprocess
import shutil
import time

# Check whether analysis was successful
def analysis_success(filepath):
    with open(filepath, 'r') as checkfile:
        for line in checkfile:
            if line.startswith('Finished!'):
                return True
        return False

# Check whether analysis was successful
def analysis_warnings(filepath):
    with open(filepath, 'r') as checkfile:
        for line in checkfile:
            if line.startswith('WARN: '):
                return True
        return False

def append_to_log(logpath, lines):
    with open(logpath, 'a') as checkfile:
        checkfile.write(lines)

def copy_warnings(logpath, errorpath):
    warnfound = False
    foundlines = ''
    linebuf = ''
    with open(logpath, 'r') as log:
        for line in log:
            if (not warnfound) and line.startswith('WARN: '):
                warnfound = True
                foundlines = line
            elif warnfound and line.startswith('WARN: '):
                foundlines += line
            elif warnfound:
                warnfound = False
                linebuf += foundlines + '\n'
                foundlines = ''
    if warnfound and len(foundlines) > 0:
        linebuf += foundlines + '\n'
    append_to_log(errorpath, linebuf)

def copy_errors(logpath, errorpath):
    errorfound = False
    foundlines = ''
    linebuf = ''
    with open(logpath, 'r') as log:
        for line in log:
            if (not errorfound) and line.startswith('ERROR: '):
                errorfound = True
                foundlines = line
            elif errorfound and line.startswith('\t'):
                foundlines += line
            elif errorfound:
                errorfound = False
                linebuf += foundlines + '\n'
                foundlines = ''
    if errorfound and len(foundlines) > 0:
        linebuf += foundlines + '\n'
    append_to_log(errorpath, linebuf)

def correct_out_log(logpath, errorpath):
    copy_warnings(logpath, errorpath)
    copy_errors(logpath, errorpath)
    otherfound = False
    foundlines = ''
    linebuf = ''
    with open(logpath, 'r') as log:
        for line in log:
            other = (not line.startswith('WARN: ')) \
                and (not line.startswith('ERROR: ')) \
                and (not line.startswith('\t'))

            if (not otherfound) and other:
                otherfound = True
                foundlines = line
            elif otherfound and other:
                foundlines += line
            elif otherfound:
                otherfound = False
                linebuf += foundlines + '\n'
                foundlines = ''
    if otherfound and len(foundlines) > 0:
        linebuf += foundlines + '\n'

    os.remove(logpath)
    append_to_log(logpath, linebuf)

# Prepare for apk analysis launch
def prepare_run(installloc, deploc, apkpaths, resultpaths, support):
    return

# Run analysis
def run(installloc, deploc, apkpath, resultpath, ramamount, timeout, support):
    env = support.get_java_env()
    env['DROIDSAFE_MEMORY'] = str(ramamount)
    env['DROIDSAFE_SRC_HOME'] = installloc
    env['ANDROID_SDK_HOME'] = deploc+'/Android-SDK'
    env['DROIDSAFE_APAC_HOME'] = env['ANDROID_SDK_HOME']
    env['ANT_OPTS'] = '-Xmx2g'
    env['SDK'] = env['ANDROID_SDK_HOME']
    env['ANDROID_HOME'] = env['ANDROID_SDK_HOME']
    env['PATH'] = env['ANDROID_SDK_HOME']+'/tools:'\
    +env['ANDROID_SDK_HOME']+'/platform-tools:'\
    +env['PATH']
    env['HERE'] = resultpath
    env['APK'] = apkpath
    env['TARGET'] = 'android-28'
    env['LIB'] = env['DROIDSAFE_SRC_HOME']+'/lib'
    env['CLASSPATH'] = '.:'+env['DROIDSAFE_SRC_HOME']+'/classes/main:'\
    +env['DROIDSAFE_SRC_HOME']+'/bin/*:'\
    +env['LIB']+'/asmutil.jar:'\
    +env['LIB']+'/slf4j-api-1.7.2.jar:'\
    +env['LIB']+'/logback-classic-1.0.7.jar:'\
    +env['LIB']+'/logback-core-1.0.7.jar:'\
    +env['LIB']+'/soot-2.5.0.jar'

    apkname = os.path.basename(apkpath)
    if apkname.endswith('.apk'):
        apkname = apkname[:-4]

    env['SPEC'] = apkname
    env['DBDIR'] = 'droidsafe-gen'
    env['GOOGLE'] = env['DROIDSAFE_SRC_HOME']+'/lib/guava-r09.jar'

    out_path = resultpath+'/'+support.get_out_log()
    error_path = resultpath+'/'+support.get_error_log()
    output_file = open(out_path, "wb", 0)
    error_file = open(error_path, "wb", 0)
    
    has_timeout = False
    try:
        #ant-compiles
        start = time.time()
        subprocess.call([deploc+'/Ant/bin/ant',
            'compile-ds'],
            cwd=installloc, env=env,
            stdout=output_file, stderr=error_file,timeout=timeout)
        end = time.time()
        totaltime = end - start
        timeout = timeout - totaltime
        start = time.time()
        subprocess.call([deploc+'/Ant/bin/ant',
            'compile-model'],
            cwd=installloc, env=env,
            stdout=output_file, stderr=error_file,timeout=timeout)
        end = time.time()
        totaltime = end - start
        timeout = timeout - totaltime
        start = time.time()
        subprocess.call([
            deploc+'/Ant/bin/ant', 
            'compile-manual-model'],
            cwd=installloc, env=env,
            stdout=output_file, stderr=error_file,timeout=timeout)
        end = time.time()
        totaltime = end - start
        timeout = timeout - totaltime

        # unpack-apk
        start = time.time()
        subprocess.call([
            installloc+'/bin/apktool',
            '--frame-path',
            installloc+'/bin/apktool-framework',
            '-f', '-o', 'apktool-gen', 'd', apkpath],
            cwd=resultpath, env=env,
            stdout=output_file, stderr=error_file,timeout=timeout)
        end = time.time()
        totaltime = end - start
        timeout = timeout - totaltime

        if os.path.isdir(resultpath+'/res'):
            shutil.rmtree(resultpath+'/res')
        shutil.move(resultpath+'/apktool-gen/res', resultpath)

        if not os.path.isfile(resultpath+'/AndroidManifest.xml'):
            shutil.move(resultpath+'/apktool-gen/AndroidManifest.xml', resultpath)

        # Specdump-apk
        start = time.time()
        subprocess.call(['java',
         '-cp',
         installloc+'/bin/droidsafe-core.jar:'\
         +installloc+'/bin/droidsafe-libs.jar:'\
         +installloc+'/config-files:'\
         +resultpath,
         '-Djava.library.path='+installloc+'/lib',
         '-Xms1g',
         '-Xmx'+str(ramamount)+'g',
         '-Dfile.encoding=UTF-8',
         'droidsafe.main.Main',
         '-approot',
         resultpath,
         '-apkfile',
         apkpath,
         '-t',
         'specdump'
        ], cwd=resultpath, env=env,
        stdout=output_file, stderr=error_file,timeout=timeout)
        end = time.time()
        totaltime = end - start
        timeout = timeout - totaltime
    except subprocess.TimeoutExpired:
        has_timeout = True

    # print('Output found: {0}'.format(output_std))
    # output_file.write(output_std)
    output_file.close()
    error_file.close()

    correct_out_log(out_path, error_path)
    success = analysis_success(out_path)
    warnings= analysis_warnings(error_path)

    if has_timeout:
        return warnings, False, True

    return warnings, success, has_timeout


# Clean up
def post_run(installloc, deploc, apkpaths, resultpaths, support):
    return