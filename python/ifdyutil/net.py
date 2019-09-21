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

import subprocess

def ssh_command_unsafe( remote_host, command ):

    ''' Execute the given command on a remote host via SSH. The command can be a
    string or it can be a list of strings that will be joined by && and
    executed as one line.
    
    This function is unsane, as its name implies. It should be fine if the
    remote server is resilient against arbitrary SSH commands, though. For
    example, if it's using public key command restriction.'''
    
    if isinstance( command, list ):
        # Iterate through the list and wrap it up.
        command_exec = ' && '.join( command )
    else:
        command_exec = command

    subprocess.call( [ 'ssh', remote_host, command_exec ] )

