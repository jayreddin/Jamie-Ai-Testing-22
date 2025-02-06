"""
PyInstaller build script for Jamie Ai Compute
"""

import os
import platform
import sys

import PyInstaller.__main__

from app.version import version

def build(signing_key=None):
    input('Did you remember to increment version.py? ' + str(version))
    app_name = 'Jamie Ai Compute'

    compile(signing_key)

    macos = platform.system() == 'Darwin'
    if macos and signing_key:
        os.system(
            f'codesign --deep --force --verbose --sign "{signing_key}" dist/{app_name}.app --options runtime')
        # ... rest of build function remains the same
