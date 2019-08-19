#!/usr/bin/env python

from enum import Enum

import lib.independence.fs as fs

# The greater purpose of (functions in) this file is
# to provide standard user-interaction functions

# Return dict mapping true to all currently installed components,
# and false to all non-installed components
def installed_states(components):
    statedict = {}
    statedict[True] = []
    statedict[False] = []
    for component in components:
        statedict[component.is_installed()].append(component)
    return statedict

# Simple method to ask user a yes/no question. Result returned as boolean.
# Returns True if user responded positive, otherwise False
def standard_yesno(question):
    while True:
        choice = input(question+' [Y/n] ').upper()
        if choice in ('Y', 'YES'):
            return True
        elif choice in ('N', 'NO'):
            return False
        else:
            print('Invalid option "{0}"'.format(choice))

# ask user for a directory
# must_exist determines whether given dir explicitly must or must not exist
def ask_directory(question, must_exist=True):
    while True:
        print(question)
        print('Paths may be absolute or relative to your working directory')
        print('Working directory: {0}'.format(fs.cwd()))
        print('Please specify a directory:')
        choice = input('')
        choice = fs.abspath(choice)
        if must_exist:
            if not fs.isdir(choice):
                print('Error: no such directory - "{0}"'.format(choice))
            else:
                return choice
        else:
            if fs.isdir(choice):
                print('"{0}" already exists'.format(choice))
                if standard_yesno('continue?'):
                    return choice
            else:
                return choice
        print('')

# ask user for a path (directory+file)
# must_exist determines whether given path explicitly must or must not exist
def ask_path(question, must_exist=True):
    while True:
        print(question)
        print('Paths may be absolute or relative to your working directory')
        print('Working directory: {0}'.format(fs.cwd()))
        print('Please specify a path:')
        choice = input('')
        choice = fs.abspath(choice)
        if not fs.isdir(fs.dirname(choice)):
            print('Error: no such directory - "{0}"'.format(fs.dirname(choice)))
        elif must_exist:
            if fs.exists(choice):
                return choice
            else:
                print('"{0}" does not exist'.format(choice))
        else:
            if fs.isfile(choice):
                if standard_yesno('"{0}" exists, override?'.format(choice)):
                    return choice
            elif fs.isdir(choice):
                print('"{0}" is a directory'.format(choice))
        print('')

# Ask for a filename
# question is the question to be asked
# directory is the directory where filename will be stored
# extension is the extension you plan on appending to filename
def ask_filename(question, directory, extension):
    while True:
        choice = input(question)
        if len(choice) == 0:
            print('Please provide a name')
        elif '{0}{1}'.format(choice,extension) in fs.ls(directory):
            if standard_yesno('{0} already exists. Override?'.format(choice)):
                return choice
        else:
            return choice
        print('')

# Maps numbers (starting from 0 of course) to components for user select
def make_optionsdict(objects):
    returndict={}
    for number, obj in enumerate(objects):
        returndict[number] = obj
    return returndict

# Enum to represent menu choice made
class MenuResults(Enum):
    CHOSEN=0
    EVERYTHING=1
    BACK=2

# Give a list of choices and handles input
# Returns selected options and type of return: Chosen, Back, Everything
# Back type is returned when user selects 'Back' option.
# Everything is returned when user selects 'Everything' option.
# Chosen is returned when user selects one or more items
def standard_menu(choice_list, display_lambda):
    optionsdict = make_optionsdict(choice_list)
    while True:
        for item in optionsdict:
            print('\t\t[{0}] - {1}'.format(str(item),display_lambda(optionsdict[item])))
        print('\t[E]verything')
        print('\t[B]ack')
        choice = input('Please make a choice (or multiple, comma-separated): ').upper()
        chosenarray = []
        words = choice.split(',')
        for word in words:
            if word in ('B', 'BACK'):
                return [], MenuResults.BACK
            elif word in ('E', 'EVERYTHING'):
                return choice_list, MenuResults.EVERYTHING
            elif word.isdigit() and int(word) in optionsdict:
                chosenarray.append(optionsdict[int(word)])
            else:
                print('Unknown option "{0}"'.format(word))
        if len(chosenarray) > 0:
            return chosenarray, MenuResults.CHOSEN