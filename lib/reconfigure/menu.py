#!/usr/bin/env python

import lib.reconfigure.reconfig as r
import lib.ui.menu as menu

# The greater purpose of (functions in) this file is to 
# ask user what installed tools should be reconfigured

# Shows user a menu to install components
def reconfig_menu(components):
    print('Which component(s) do you want to reconfigure?')
    installed = menu.installed_states(components)[True]
    chosen, _ = menu.standard_menu(installed, lambda x: str(x))
    if len(chosen) > 0:
        r.reconfigure_all(chosen)