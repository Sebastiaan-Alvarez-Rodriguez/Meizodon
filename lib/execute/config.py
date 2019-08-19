#!/usr/bin/env python

import lib.execute.apk as apkfile
import lib.independence.fs as fs
import lib.settings as s
import lib.ui.menu as menu

# The greater purpose of (functions in) this file is 
# to ask, load and store a list of apk's to execute

# Main function it is all about: Here we get a list of apk objects.
# We may obtain it by asking a user for a list of apk objects,
# or by asking a user to choose a saved list
def get_apks():
    fs.mkdir(s.execconfdir, exist_ok=True)
    if len(get_config_files()) != 0 and menu.standard_yesno('Choose existing configuration?'):
        return ask_config()
    else:
        return ask_user()

# Get execution configuration files
def get_config_files():
    configs = []
    for item in fs.ls(s.execconfdir):
        if not fs.isdir(s.execconfdir, item) and item.endswith('.conf'):
            configs.append(fs.join(s.execconfdir,item))
    configs.sort()
    return configs

# Asks user to choose a config file and returns chosen config
# Returns config where user must provide paths, if there are no config files to choose from
def ask_config():
    configs = get_config_files()
    if len(configs) == 0:
        print('No config files found!')
        return ask_user()

    optionsdict = menu.make_optionsdict(configs)
    while True:
        for item in optionsdict:
            print('\t\t[{0}] - {1}'.format(str(item),fs.basename(optionsdict[item])))

        choice = input('Please choose an execution config: ')
        if choice.isdigit() and int(choice) in optionsdict:
            chosenitem = optionsdict[int(choice)]
            return from_file(chosenitem)
        else:
            print('Unknown option "{0}"'.format(choice))

# Ask user for input to make an execution configuration
def ask_user():
    apks = ask_apks()
    if ask_store_conf():
        filename = menu.ask_filename('Please name this config: ', s.execconfdir, '.conf')
        to_file(filename, apks)
    return apks

# Make array of paths to apk's. paths may be relative to working directory
def make_apkpath(path):
    if path.endswith('.apk'):
        return [path]
    elif fs.isdir(path):
        result=[]
        for item in fs.ls(path):
            if not fs.isdir(path, item) and item.endswith('.apk'):
                result.append(fs.join(path,item))
        print('Found {0} apk\'s in directory'.format(len(result)))
        return result
    return []

# Test if given testpath leads to an .apk file or a dir containing a .apk file
def test_apkpath(testpath):
    try:
        if fs.isfile(testpath) and testpath.endswith('.apk'):
            return True
        elif fs.isdir(testpath):
            for item in fs.ls(testpath):
                if fs.isfile(fs.join(testpath,item)) and item.endswith('.apk'):
                    return True
            print('Specified directory has no apk files in it')
            return False
    except Exception as e:
        print('{0} does not exist'.format(testpath))
        return False

# Ask for apk path(s), and construct apk-objects
def ask_apks():
    apks = []
    while True:
        choice = menu.ask_path('Please give location for testset/apk')
        
        if test_apkpath(choice):
            malware = menu.standard_yesno('Is/Are given apk(s) malware?')
            for apkpath in make_apkpath(choice):
                apks.append(apkfile.Apk(apkpath, malware))

        if len(apks) != 0 and not menu.standard_yesno('Specify another path?'):
            return apks
        print('')

# Ask user if he wants to store list
def ask_store_conf():
    print('Storing above input means you do not have to provide it again next time.')
    return menu.standard_yesno('Do you want to store input?')

# Write given list to a file (to be able to read it in later)
def to_file(name, apks):
    filepath = fs.join(s.execconfdir,name+'.conf')
    with open(filepath, 'w') as conf:
        for apk in apks:
            conf.write(apkfile.Apk.get_string(apk)+'\n')

# Construct list from stored file
def from_file(configfile):
    apks = []
    with open(configfile, 'r') as conf:
        for line in conf:
            if line[-1] == '\n':
                line = line[:-2] if line[-2] == '\r' else line[:-1]

            if line == '\n' or line == '\r\n' or line =='':
                continue
            else:
                apks.append(apkfile.Apk.from_string(line))
    return apks