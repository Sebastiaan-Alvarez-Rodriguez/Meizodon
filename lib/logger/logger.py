#!/usr/bin/env python

import multiprocessing
import threading

class Logger(object):
    """Object to handle asynchronous file write requests"""
    # After constructing a Logger object, put strings
    # in the logger.logqueue, which will be written to specified file
    # when logger is started with start(), until the point where
    # logger is stopped with stop(). Stop is automatically called
    # if the object gets out of scope and is destroyed

    # Constructor
    # logpath: path to logpath
    def __init__(self, logpath):
        self.logpath = logpath
        self.logqueue = multiprocessing.Manager().Queue()
        self.logthread = threading.Thread(target=self.log)

    # Main log loop: Receives write requests from queue and handles them
    # While loop stops on receiving empty message
    def log(self):
        with open(self.logpath, 'a') as log:
            while True:
                message = self.logqueue.get()
                if message == '':
                    break
                log.write(message+'\n')

    # Start the logger
    def start(self):
        self.logthread.start()
        print("Logger started")

    # Stop logger
    def stop(self):
        self.logqueue.put('')
        self.logthread.join()
        print("Logger stopped")

    # Upon deleting this object, stops logthread if it still exists.
    # This may happen if a start() has no matching stop() and this object
    # gets out of scope
    def __del__(self):
        if self.logthread.isAlive():
            self.stop()