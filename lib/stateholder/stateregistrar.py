#!/usr/bin/env python

class Registrar(object):
    '''Generic object to register variables and maintain states'''
    # Just uses a dictionary internally

    # Constructor
    def __init__(self):
        self.registry = {}
    
    # Enter pair in registry. Returns True on success.
    # If key exists and override is not set to True, then returns False
    def register(self, registryid, regvalue, override=False):
        if registryid in self.registry and not override:
            return False
        self.registry[str(registryid)]=regvalue

    # Delete pair from registry. Returns True on success.
    # If invalid key is specified, returns False
    def unregister(self, registryid):
        if registryid in self.registry:
            del self.registry[registryid]
            return True
        return False

    # Consults the registry. Returns found object on success, 
    # Returns None otherwise
    def get(self, registryid):
        if registryid in self.registry:
            return self.registry[registryid]
        return None