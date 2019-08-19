#!/usr/bin/env python
import os
import subprocess
import time
import getpass
import shutil

# Create a lot of confiuration
def create_DB_config(mysqldir):
    contents = '[mysqld]\n'
    contents += 'basedir='+mysqldir+'/\n'
    contents += 'datadir='+mysqldir+'/datadir\n'
    contents += 'general-log-file='+mysqldir+'/sql.log\n'
    contents += 'pid-file='+mysqldir+'/sql.pid\n'
    contents += 'slow-query-log-file='+mysqldir+'/sql-slow.log\n'
    contents += 'socket='+mysqldir+'/sock.sock\n'
    contents += 'lc-messages-dir='+mysqldir+'/share\n'
    contents += 'lc-messages=en_US\n'
    contents += 'offline-mode=TRUE\n'
    contents += 'port=1234\n'
    with open(mysqldir+'/generated_sql.conf', 'w') as conf:
        conf.write(contents)

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

# Initialize database (and ge temporary password, so we can change it later)
def init_DB(mysqldir):
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
        '--initialize-insecure'], stderr=subprocess.DEVNULL)

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

# Change password to 'pass'
def change_pass(mysqldir):
    subprocess.call([mysqldir+'/bin/mysql',
    '--connect-expired-password',
    '--socket='+mysqldir+'/sock.sock',
    '-uroot',
    '-e ALTER USER \'root\'@\'localhost\' IDENTIFIED BY \'pass\';'], 
    stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

# Give server a database named 'cc'
def create_DB(mysqldir):
    print('Creating db')
    subprocess.call([mysqldir+'/bin/mysql',
    '--socket='+mysqldir+'/sock.sock',
    '-uroot',
    '-ppass',
    '-e CREATE DATABASE cc DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;'],
    stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

# Give user 'root' (default user) full rights to database 'cc'
def elevate_user(mysqldir):
    print('Elevating user in database')
    subprocess.call([mysqldir+'/bin/mysql',
    '--socket='+mysqldir+'/sock.sock',
    '-uroot',
    '-ppass',
    '-e GRANT ALL PRIVILEGES ON cc.* TO \'root\'@\'localhost\';'],
    stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

# Insert all tables required for iccta in database 'cc'
def insert_tables(mysqldir, installerdir):
    print('Inserting tables...')
    p0 = subprocess.Popen(
        mysqldir+'/bin/mysql -uroot -ppass --socket='+mysqldir+'/sock.sock cc < '+installerdir+'/schema',
        shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL
    )
    p0.wait()

# Share our android platform versions in iccta/android-platforms with 
# others by moving them to the right place in Android-SDK directory
def move_android(installloc, deploc):
    srcdir = installloc+'/soot-infoflow-android-iccta/android-platforms'
    platforms = os.listdir(srcdir)
    for platform in platforms:
        if not os.path.exists(deploc+'/Android-SDK/platforms/'+platform):
            shutil.move(srcdir+'/'+platform, deploc+'/Android-SDK/platforms/'+platform)
    os.environ['ANDROID_SDK_HOME'] = deploc+'/Android-SDK/'

def pre_install(installerloc, installloc, deploc, support):
    mysqldir = deploc+'/mysql'
    kill_DB(mysqldir)

def install(installerloc, installloc, deploc, support):
    mysqldir = deploc+'/mysql'
    create_DB_config(mysqldir)
    if not os.path.isdir(mysqldir+'/datadir'):
        init_DB(mysqldir)
    boot_DB(mysqldir)
    change_pass(mysqldir)
    create_DB(mysqldir)
    elevate_user(mysqldir)
    insert_tables(mysqldir, installerloc)

# Prepare jdbc.xml file to connect with our database
def prepare_XML(installloc):
    with open(installloc+'/soot-infoflow-android-iccta/res/jdbc.xml', 'w') as conf:
        conf.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        conf.write('<databases>\n')
        conf.write('\t<database>\n')
        conf.write('\t\t<name>cc</name>\n')
        conf.write('\t\t<driver>com.mysql.jdbc.Driver</driver>\n')
        conf.write('\t\t<url>jdbc:mysql://127.0.0.1:1234/cc</url>\n')
        conf.write('\t\t<username>root</username>\n')
        conf.write('\t\t<password>pass</password>\n')
        conf.write('\t\t<charset>N/A</charset>\n')
        conf.write('\t</database>\n')
        conf.write('</databases>\n')

# Prepare cc.properties file to connect with our database
def prepare_CC(installloc):
    with open(installloc+'/soot-infoflow-android-iccta/iccProvider/ic3/cc.properties', 'w') as conf:
        conf.write('user=root\n')
        conf.write('password=pass\n')
        conf.write('characterEncoding=ISO-8859-1\n')
        conf.write('useUnicode=true\n')

def post_install(installerloc, installloc, deploc, support):
    mysqldir = deploc+'/mysql'
    kill_DB(mysqldir)
    prepare_XML(installloc)
    prepare_CC(installloc)
    move_android(installloc, deploc)
    support.download_android_linux(list(range(3, 29)))

def reconfigure(installerloc, installloc, deploc, support):
    mysqldir = deploc+'/mysql'
    pre_install(installerloc, installoc, deploc)
    shutil.rmtree(mysqldir+'/datadir')
    install(installerloc, installloc, deploc)
    post_install(installerloc, installloc, deploc)