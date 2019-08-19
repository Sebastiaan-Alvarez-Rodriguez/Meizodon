#!/usr/bin/env python

import os
import re
import subprocess

import lib.independence.fs as fs
import lib.settings as s
import lib.stateholder.stateregistrar as registrar

class Support(object):
    '''Object with functions to support installers in general. Most 
    installers require Android-SDK to have some platforms, per example.'''

    def __init__(self):
        self.registrar = registrar.Registrar()

    # Resets the registry
    def reset_registry(self):
        self.registrar = registrar.Registrar()

    # Returns filename for error log
    def get_error_log(self):
        return s.errorlog

    # Returns filename for output log
    def get_out_log(self):
        return s.outlog

    # Gets environment copy, with changes such that local java is chosen
    def get_java_env(self):
        if not fs.isdir(s.dependencydir, 'jdk8'):
            raise RuntimeError('Error: Could not find jdk8 directory in {0}'.format(s.dependencydir))
        path_to_java = fs.join(s.dependencydir, 'jdk8')
        env = os.environ.copy()
        env['JAVA_HOME']=path_to_java
        env['PATH']='{0}:{1}'.format(os.path.join(path_to_java, 'bin'), env['PATH'])
        return env;

    # Download android platform for android versions 
    # (using yes command to not bug user)
    # versions parameter can be int list or int
    def download_android_linux(self, versions):
        if type(versions) is int:
            versions=[versions]

        path_to_java = fs.join(s.dependencydir, 'jdk8')
        env = os.environ.copy()
        env['JAVA_HOME']=path_to_java
        env['PATH']='{0}:{1}'.format(fs.join(path_to_java, 'bin'), env['PATH'])

        print('Downloading android platforms {0}'.format(versions))
        if not fs.exists(s.dependencydir,'Android-SDK') \
            or not fs.exists(s.dependencydir,'Android-SDK','tools','bin','sdkmanager'):
            print('Error: Android-SDK not found. Cannot download platforms')
            return

        downloadversions = []
        for version in versions:
            if not fs.exists(s.dependencydir, 'Android-SDK','platforms','android-{0}'.format(str(version))):
                downloadversions.append(version)

        if len(downloadversions) == 0:
            return

        downloadarray = ['sh',fs.join(s.dependencydir,'Android-SDK','tools','bin','sdkmanager')]

        for version in downloadversions:
            downloadarray.append('platforms;android-{0}'.format(str(version)))

        ps = subprocess.Popen(['yes'], stdout=subprocess.PIPE)

        subprocess.call(
            downloadarray, stdin=ps.stdout, 
            stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, env=env)
        ps.terminate()