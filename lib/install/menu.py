#!/usr/bin/env python

import lib.install.install as i
import lib.ui.menu as menu

# The greater purpose of (functions in) this file is to 
# ask user what tools should be installed

# Shows user a menu to install components
def install_menu(components):
    not_installed = menu.installed_states(components)[False]
    print('What do you want to install?')
    chosen, _ = menu.standard_menu(not_installed, lambda x: str(x))
    if len(chosen) == 1:
        i.install(chosen[0])
    elif len(chosen) > 1:
        i.install_all(chosen)