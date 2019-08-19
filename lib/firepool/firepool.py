#!/usr/bin/env python

import multiprocessing

import lib.independence.fs as fs


class Firepool(object):
    '''Object to balance workloads over multiple cores'''

    # Constructor
    # ask_RAM is a flag to set whether user should be asked to provide RAM amount
    # max_cores, if set, is the maximum amount cores a user may specify
    def __init__(self, ask_RAM=True, max_cores=None):
        self.cores = self.ask_cores(max_cores)
        if ask_RAM:
            ramtotal = self.ask_ramload()
            self.rampercore =  ramtotal // self.cores

    # Ask how many cores to use for execution
    def ask_cores(self, max_cores=None):
        if max_cores != None:
            show_max = min(max_cores, multiprocessing.cpu_count())
        else:
            show_max = None
        while True:
            print('You have {0} cores.'.format(multiprocessing.cpu_count()))
            if show_max != None:
                amount = input('How many cores can I use for processing? (max={0}) '.format(show_max))
            else:
                amount = input('How many cores can I use for processing? ')
            if not amount.isdigit():
                print('Please enter a number')
            elif int(amount) < 1:
                print('I need at least 1 core')
            elif int(amount) > multiprocessing.cpu_count():
                print('You do not have {0} cores'.format(amount))
            elif show_max != None and int(amount) > show_max:
                print('Please do not specify more than {0} cores'.format(show_max))
            else:
                return int(amount)

    # Convert amount in unit (e.g. KB) to approximate amount in GB.
    # Always rounding down, so 1100MB becomes 1GB
    def get_GB(self, amount, unit):
        if unit.upper() == 'B':
            return amount // 1024**3
        elif unit.upper() == 'KB':
            return amount // 1024**2
        elif unit.upper() == 'MB':
            return amount // 1024
        elif unit.upper() == 'GB':
            return amount
        elif unit.upper() == 'TB':
            return amount * 1024

    # get available RAM in linux systems rounded down to integer
    def get_available_RAM(self):
        if not fs.isfile('/proc/meminfo'):
            raise ValueError('could not find /proc/meminfo')

        with open('/proc/meminfo') as f:
            for line in f:
                if 'MemAvailable' in line:
                    line = line[:-1]
                    memavailable = line.split(' ')[-2]
                    memtype = line.split(' ')[-1]
                    return self.get_GB(int(memavailable), memtype)
        raise RuntimeError('could not find memAvailable in /proc/meminfo')

    # ask how much RAM the user wishes to allocate for execution
    def ask_ramload(self):
        while True:
            try:
                available = self.get_available_RAM()
                print('You have approximately {0} GB RAM available.'.format(available))
            except RuntimeError as e:
                available = -1
            amount = input('How many GB\'s RAM total would you wish to allocate for execution? ')
            if not amount.isdigit():
                print('Please give an integer')
            else:
                if available < 0:
                    print('Could not check available RAM amount.')
                    print('Specifying more RAM than available may harm your system')
                    proceed = input('Proceed? [Y/n] ')
                    if proceed.upper() == 'Y' or proceed.upper() == 'YES':
                        return int(amount)
                    else:
                        continue
                elif int(amount) > available:
                    print('You have only {0} GB available'.format(available))
                else:
                    return int(amount)

    # Execute multiprocess stage
    def fire(self, func, argarray):
        with multiprocessing.Pool(processes=self.cores) as pool:
            pool.starmap(func, argarray)