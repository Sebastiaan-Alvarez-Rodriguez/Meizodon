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
    support.download_android_linux(28)
    env = support.get_java_env()
    downloaded_dir = '{0}/droidsafe-src-master/'.format(installloc)
    for item in os.listdir(downloaded_dir):
        shutil.move('{0}/{1}'.format(downloaded_dir, item), installloc)
    os.rmdir(downloaded_dir)

    os.environ['DROIDSAFE_SRC_HOME'] = installloc+'/'
    os.environ['ANDROID_SDK_HOME'] = deploc+'/Android-SDK/'
    os.chmod(deploc+'/Ant/bin/ant', 0o775)
    subprocess.call([deploc+'/Ant/bin/ant', 'clean', 'compile'], cwd=installloc, env=env)

def post_install(installerloc, installloc, deploc, support):
    if os.path.isfile(installloc+'/bin/README.md'):
        os.remove('{0}/bin/README.md'.format(installloc))

    for item in os.listdir('{0}/bin'.format(installloc)):
        if os.path.isfile('{0}/bin/{1}'.format(installloc, item)) and not item.endswith('.jar'):
            st = os.stat('{0}/bin/{1}'.format(installloc, item))
            os.chmod('{0}/bin/{1}'.format(installloc, item), st.st_mode | stat.S_IEXEC)

    shutil.move('{0}/apktool'.format(installloc), '{0}/bin/apktool.jar'.format(installloc))
    if (os.path.isfile('{0}/android-apps/Makefile.common'.format(installloc))):
        os.remove('{0}/android-apps/Makefile.common'.format(installloc))
    shutil.copy('{0}/Makefile.common'.format(installerloc), '{0}/android-apps/Makefile.common'.format(installloc))

def reconfigure(installerloc, installloc, deploc, support):
    os.environ['DROIDSAFE_SRC_HOME'] = installloc
    os.environ['ANDROID_SDK_HOME'] = deploc+'/Android-SDK'
    del os.environ['DROIDSAFE_MEMORY']
    
    if (os.path.isfile('{0}/android-apps/Makefile.common'.format(installloc))):
        shutil.rmtree('{0}/android-apps/Makefile.common'.format(installloc))
    shutil.copy('{0}/Makefile.common'.format(installerloc), '{0}/android-apps/Makefile.common'.format(installloc))
