#!/usr/bin/env python

from enum import Enum

import lib.independence.fs as fs
import lib.download.task as task

# The greater purpose of (functions in) this file is
# to read in installation configs

# Enum to keep track of current state
class State(Enum):
    BEGIN=0
    UNIT=1
    KEYPAIR=3

# Enum to keep track of current branch deps/pkgs/none
class Phase(Enum):
    NONE=0
    DEPS=1
    PKGS=2


class DownloadConfiguration(object):
    '''Object to read in a download configuration file'''

    # Constructor
    # config is the path to the cnfig file which we should read in
    def __init__(self, config):
        try:
            if not fs.isfile(config):
                return
        except Exception as e:
            return
        dictionary = self.reader(config)
        self.deps = dictionary[Phase.DEPS]
        self.pkgs = dictionary[Phase.PKGS]

    # Check if a unit (either 'deps' or 'pkgs') is declared in current line
    def declares_unit(self, line, unitname):
        line = line.lstrip().rstrip()
        return line.replace(' ', '').split('{')[0] == unitname

    # Return how unit is named. e.g. 'mysql {' returns 'mysql'
    def get_unitname(self, line, linenumber):
        line = line.lstrip().rstrip()
        noindentline = line.replace(' ', '')
        if noindentline[0]=='{':
            raise RuntimeError('No unit name found on line '+linenumber)
        return noindentline.split('{')[0]

    # For 'a = b', returns 'b'. Does not go well if there is no '=b'
    def read_assignment(self, line):
        line = line.lstrip().rstrip()
        noindentline = line.replace(' ', '')
        return noindentline.split('=', 1)

    # Interpret lines in BEGIN state (not inside any scope)
    def interpret_begin(self, line, linenumber, phase, state, unitname):
        if '{' in line:
            if self.declares_unit(line, 'deps'):
                return Phase.DEPS, State.UNIT, unitname
            elif self.declares_unit(line, 'pkgs'):
                return Phase.PKGS, State.UNIT, unitname
            else:
                print('Unit "{0}" unknown. Ignoring...'.format(self.get_unitname(line, linenumber)))
        return Phase.NONE, State.BEGIN, unitname

    # Inside either 'dep' or 'pkg' scope
    def interpret_unit(self, line, linenumber, dictionary, phase, state, unitname):
        if '{' in line:
            unitname = self.get_unitname(line, linenumber)
            if unitname in dictionary[phase]:
                print('Warning: overriding previous "{0}"'.format(unitname))
            dictionary[phase][unitname] = task.DownloadTask(unitname)
            return phase, State.KEYPAIR, unitname
        elif line.strip() == '}':
            return Phase.NONE, State.BEGIN, unitname

    # Inside a unit scope, e.g. 'mysql', get 'dir' or 'url' specifications
    def interpret_keypair(self, line, linenumber, dictionary, phase, state, unitname):
        if '=' in line:
            keypair = self.read_assignment(line)
            if keypair[0] == 'dir':
                dictionary[phase][unitname].directory=keypair[1]
            elif keypair[0] == 'url':
                dictionary[phase][unitname].url=keypair[1]
            else:
                print('Key "{0}" unknown. Ignoring...'.format(keypair[0]))
            return phase, state, unitname
        elif line.strip() == '}':
            if dictionary[phase][unitname].url=='':
                raise RuntimeError('Unit "{0}" on line {1} must have url-property'.format(unitname,linenumber))
            return phase, State.UNIT, unitname

    # interpret a single line and return current state information
    def line_interpret(self, line, linenumber, dictionary, phase, state, unitname=None):
        if state==State.BEGIN:
            return self.interpret_begin(line, linenumber, phase, state, unitname)
        elif state == State.UNIT:
            return self.interpret_unit(line, linenumber, dictionary, phase, state, unitname)
        elif state == State.KEYPAIR:
            return self.interpret_keypair(line, linenumber, dictionary, phase, state, unitname)

    # interpret a config, return result as dictionary
    def reader(self, config):
        dictionary = {
            Phase.DEPS: {},
            Phase.PKGS: {},
        }
        phase = Phase.NONE
        state = State.BEGIN
        unitname=''

        with open(config, 'r') as conf:
            for linenumber, line in enumerate(conf):
                if len(line.lstrip()) != 0 and line.lstrip()[0] != '#':
                    phase, state, unitname = self.line_interpret(line.rstrip(), linenumber, dictionary, phase, state, unitname)
            if state != State.BEGIN:
                raise RuntimeError("Missing '}' for unit/keypair in config")
        return dictionary