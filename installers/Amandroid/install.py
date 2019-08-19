#!/usr/bin/env python
import os
import subprocess
import shutil
import stat

def moveall(src, dest):
    files = os.listdir(src)
    for f in files:
        shutil.move(src+f, dest)

def pre_install(installerloc, installloc, deploc, support):
    return

def install(installerloc, installloc, deploc, support):
    if os.path.isdir(installloc+'/installer/amandroid-build-master/sireum-amandroid-build/'):
        moveall(installloc+'/installer/amandroid-build-master/sireum-amandroid-build/', installloc+'/installer/')
        os.rmdir(installloc+'/installer/amandroid-build-master/sireum-amandroid-build/')

    env = support.get_java_env()
    env['HOME'] = installloc

    subprocess.call(['sh',
        installloc+'/installer/tools/bin/sbt',
        'clean',
        'clean-files',
        'compile',
        'package-bin',
        'build-amandroid '+installloc+'/Amandroid false'], 
        cwd=installloc+'/installer/', env=env)

    shutil.rmtree(installloc+'/installer/')

    os.makedirs(installloc+'/Amandroid/platform', exist_ok=True)
    if not os.path.exists(installloc+'/Amandroid/platform/java'):
        os.symlink(env['JAVA_HOME'], installloc+'/Amandroid/platform/java')
    if not os.path.exists(installloc+'/Amandroid/platform/scala'):
        os.symlink(deploc+'/Scala', installloc+'/Amandroid/platform/scala')
    os.chmod(deploc+'/Scala/bin/scala', 0o775)

def post_install(installerloc, installloc, deploc, support):
    shutil.copy(installerloc+'/execute.scala', installloc+'/Amandroid/');

def reconfigure(installerloc, installloc, deploc, support):
    return