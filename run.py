#!/usr/bin/env python
import sys

# Checks python version and exits if it is too low
# Must be specified before any lib imports (using v3.3) are done
def check_version():
    if sys.version_info < (3,3):
        print('I am sorry, but this script is for python3.3+ only!')
        exit(1)
check_version()

import lib.analysis.menu as amenu
import lib.dynamic.component as cmpnt
import lib.execute.menu as emenu
import lib.execute.restart.menu as resmenu
import lib.independence.fs as fs
import lib.install.menu as imenu
import lib.reconfigure.menu as recmenu
import lib.settings as s
import lib.ui.menu as menu


# Get absolute path to this script
def get_loc():
    return fs.abspath(fs.dirname(sys.argv[0]))

# Get all installer directories
def get_installer_dirs():
    if not fs.isdir(s.installersdir):
        print('Error: Installersdirectory ({0}) not found!'.format(s.installersdir))
        exit(1)

    installerlist = fs.ls(s.installersdir)
    for item in list(installerlist):
        if not fs.isdir(s.installersdir,item):
            installerlist.remove(item)
    return installerlist

# Builds all components and returns them
def get_components():
    components = []
    installers = get_installer_dirs()
    for item in installers:
        if not fs.isfile(s.installersdir,item,'install.py'):
            print('Error in "{0}": No install.py found!'.format(item))
            continue
        elif not fs.isfile(s.installersdir,item,'run.py'):
            print('Error in "{0}": No run.py found!'.format(item))
            continue
        elif not fs.isfile(s.installersdir,item,'analyse.py'):
            print('Error in "{0}": No analyse.py found!'.format(item))
            continue
        installmod = 'installers.{0}.install'.format(item)
        runmod = 'installers.{0}.run'.format(item)
        analysemod = 'installers.{0}.analyse'.format(item)

        installerloc = fs.join(s.installersdir,item)
        installloc = fs.join(s.installdir,item)
        component = cmpnt.Component(installmod, runmod, analysemod, installerloc, installloc)
        components.append(component)
    components.sort()
    return components

# Main function of this framework. Prints current installation state and
# allows user to install, execute and reconfigure, dependening on this state
def main():
    s.init(get_loc())
    components = get_components()

    while True:
        installedstate = menu.installed_states(components)
        anythinginstalled = len(installedstate[True]) > 0
        anyresultsunanalysed = amenu.should_show(components)
        anyexecutionunfinished = resmenu.should_show(components)
        if anythinginstalled:
            print('')
            print('Installed:')
            for item in installedstate[True]:
                print(item)
        print('')
        print('Not installed:')
        for item in installedstate[False]:
            print(item)
        print('')

        if anyresultsunanalysed:
            print('\t[A]nalyse')
        if anythinginstalled:
            print('\t[E]xecute')
        if anyexecutionunfinished:
            print('\tRe[S]tart')
        print('\t[I]nstall')
        if anythinginstalled:
            print('\t[R]econfigure')
        print('[Q]uit/[B]ack')
        choice = input('Please make a choice: ')
        choice = choice.upper()
        if anyresultsunanalysed and choice in ('A', 'ANALYSE'):
            amenu.analysis_menu(components)
        elif anythinginstalled and choice in ('E', 'EXECUTE'):
            emenu.execute_menu(components)
        elif anyexecutionunfinished and choice in ('S', 'RESTART'):
            resmenu.restart_execute_menu(components)
        elif choice in ('I', 'INSTALL'):
            imenu.install_menu(components)
        elif anythinginstalled and choice in ('R', 'RECONFIGURE'):
            recmenu.reconfig_menu(components)
        elif choice in ('Q', 'QUIT', 'B', 'BACK'):
            return
        else:
            print('Please choose something valid')

if __name__ == '__main__':
    main()
    # try:
    # except KeyboardInterrupt as e:
    #     print('\nKeyboard interrupt: bye!')