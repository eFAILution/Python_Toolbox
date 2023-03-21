# -*- coding: utf-8 -*-
import pkg_resources
import pip
from IPython.display import clear_output
# import subprocess
import sys


class verify_modules:

    def __init__(self, required: {}):
        """
        Tries to install missing requried modules.

        Parameters:
            required : dict
                dict of 'module':'version'

        Returns:
            None
        """
        # list of currently installed modules
        installed = [str(d) for d in pkg_resources.working_set]
        installed_dict = {}
        # convert list to dictionary
        for i in installed:
            package = tuple(i.split(" "))
            installed_dict.update({package[0]: package[1]})
        # find modules in required that are missing in installed_dict
        missing = {k: required.get(k)
                   for k in required
                   if installed_dict.get(k) != required.get(k)}

        def import_with_auto_install(missing):
            for i in missing.items():
                pkg = i[0]
                ver = i[1]
                print("Installing " + pkg, ver)
                if ver:
                    pip.main(['install', f'{pkg}=={ver}'])
                else:
                    pip.main(['install', '-U', pkg])

                # future pip will not support pip.main installs
                # subprocess.check_call will be the only way, but this does not
                # report install status to the user very well.
                # if ver:
                #     subprocess.check_call(
                #         [sys.executable, '-m', 'pip', 'install', f'{pkg}=={ver}'])
                # else:
                #     subprocess.check_call(
                #         [sys.executable, '-m', 'pip', 'install', , '-U', f'{pkg}'])

        if missing:
            print("Installing missing modules. ...")
            import_with_auto_install(missing)
            clear_output()  # clears ipython console output
            print("Successfully installed:\n" +
                  "\n".join(f'{i[0]} {i[1]}' for i in missing.items()))
        else:
            print('Required Modules Verified 🥳')


if __name__ == '__main__':
    verify_modules()

"""
HOW TO USE:

from toolbox.verify_modules import verify_modules
required_modules = {
    'seaborn': '0.11.2',
    'matplotlib': '3.5.2',
    'bs4': '0.0.1'
}
verify_modules(required_modules)

Script will install modules from required_modules{} that aren't already
installed.

****Errors due to typos or unavailable modules is not handled****
"""
