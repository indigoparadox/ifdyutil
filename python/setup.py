#!/usr/bin/env python

'''
This file is part of IFDYUtil.

IFDYUtil is free software: you can redistribute it and/or modify it under the 
terms of the GNU Lesser General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

IFDYUtil is distributed in the hope that it will be useful, but WITHOUT ANY 
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more 
details.

You should have received a copy of the GNU Lesser General Public License along
with IFDYUtil.  If not, see <http://www.gnu.org/licenses/>.
'''

import sys
import os
import subprocess
from distutils.core import setup

if 'test' in sys.argv:
   # Documentation isn't clear *at all* and too lazy to go find examples in
   # other projects. You know your language has a problem when something is
   # simpler to do in Java.
   os.chdir( './ifdyutil/tests' )
   subprocess.call( ['nosetests', 'file_tests.py'] )
   subprocess.call( ['nosetests', 'config_tests.py'] )
   exit()

setup(
   name='ifdyutil',
   # TODO: Figure out a way to grab the repo revision or something.
   version='0.1',
   packages=['ifdyutil']
)

