#!/usr/bin/env python
import os
import urllib.request
import tarfile
import zipfile
import gzip
import shutil
import threading
import sys

def abspath(path):
    return os.path.abspath(path)

def basename(path):
    return os.path.basename(path)

def cp(path_src, path_dst):
    shutil.copyfileobj(path_src, path_dst)

def cwd():
    return os.getcwd()

def dirname(path):
    return os.path.dirname(path)

def exists(path, *args):
    return os.path.exists(join(path,*args))

def isdir(path, *args):
    return os.path.isdir(join(path,*args))

def isfile(path, *args):
    return os.path.isfile(join(path,*args))

def join(directory, *args):
    returnstring = directory
    for arg in args:
        returnstring = os.path.join(returnstring, str(arg))
    return returnstring

def ls(directory, *args):
    return os.listdir(join(directory, *args))

def lsonlydir(directory, full_paths=False):
    contents = os.listdir(directory)
    if not full_paths:
        return [name for name in contents if isdir(directory, name)]
    else:
        return [join(directory, name) for name in contents if isdir(directory, name)]

def mkdir(path, exist_ok=False):
    os.makedirs(path, exist_ok=exist_ok)

def mkdir(path, *args, exist_ok=False):
    os.makedirs(join(path, *args), exist_ok=exist_ok)

def mv(path_src, path_dst):
    shutil.move(path_src, path_dst)

def rm(directory, *args, ignore_errors=False):
    path = join(directory, *args)
    if isdir(path):
        shutil.rmtree(path, ignore_errors=ignore_errors)
    else:
        os.remove(path)

# Return size of file in bytes
def sizeof(path):
    if not isfile(path):
        raise RuntimeError('Error: "{0}" is no path to a file'.format(path))
    return os.path.getsize(path)

def split(path):
    return path.split(os.sep)