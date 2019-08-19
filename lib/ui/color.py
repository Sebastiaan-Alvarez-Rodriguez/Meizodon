#!/usr/bin/env python

from enum import Enum
import os

# The greater purpose of (functions in) this file is
# to convert strings to colored strings

'''An enum to specify what color you want your text to be'''
class Color(Enum):
    RED = '\033[1;31m'
    GRN = '\033[1;32m'
    YEL = '\033[1;33m'
    BLU = '\033[1;34m'
    PRP = '\033[1;35m'
    CAN = '\033[1;36m'
    CLR = '\033[0m'

# Format a string with a color!
def format(string, color):
    if os.name == 'posix':
        return '{0}{1}{2}'.format(color.value, string, Color.CLR.value)
    return string