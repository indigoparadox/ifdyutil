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

import pynotify
import subprocess
import os
import file

DESKTOP_ENVS = ['awesome']

def notify( message, title=None ):
    if title is None:
        title = "Script"
    else:
        title = title
    pynotify.init( "qn-script" )
    notice = pynotify.Notification( title, message )
    notice.show()

def desktop_up():

    ''' Return true if a known graphical desktop environment is running. '''

    for env in DESKTOP_ENVS:
        if [] != file.get_process_pid( env, strict=False, uid=str(os.geteuid()) ):
            return True

    return False
        
