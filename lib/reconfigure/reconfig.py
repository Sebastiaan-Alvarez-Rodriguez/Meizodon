#!/usr/bin/env python

import lib.dynamic.component as cmpnt

# The greater purpose of (functions in) this file is to 
# reconfigure given tools

# Reconfigure all given components. Only function for one or more
# components now, since there is no optimalization possible for
# 1 component versus >1 components
def reconfigure_all(components):
    for component in components:
       component.reconfigure()