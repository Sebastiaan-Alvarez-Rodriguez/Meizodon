#!/usr/bin/env python

import lib.execute.component as comp
import lib.execute.execute as e
import lib.ui.menu as menu

# The greater purpose of (functions in) this file is
# to ask users what should be executed

# Shows user a menu to install components
def execute_menu(components):
    print('What do you want to execute?')
    installed = menu.installed_states(components)[True]
    chosen, _ = menu.standard_menu(installed, lambda x: str(x))
    
    if len(chosen) > 0:
        execomp = comp.ExecutionComponent(chosen)
        e.execute(execomp)