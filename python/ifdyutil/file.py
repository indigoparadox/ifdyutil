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

import os
import errno
import mimetypes
import subprocess
import re

FS_ATTRIBS_OPPOSITE = {
   'rw': 'ro',
   'ro': 'rw',
   'exec': 'noexec',
   'noexec': 'exec',
}

def mkdir_p( path ):
   try:
      os.makedirs( path )
   except OSError as exc: # Python >2.5
      if exc.errno == errno.EEXIST and os.path.isdir( path ):
         pass
      else: raise

def listdir_mime( path, mimetypes_in ):
   entries_out = []
   for entry in os.listdir( path ):
      if mimetypes.guess_type( entry )[0] in mimetypes_in:
         entries_out.append( entry )
   return entries_out

def get_process_pid( process_name, strict=True, uid=None ):
   # Build the args list.
   args = []
   if strict:
      args.append( '-f' )

   if None != uid:
      args.append( '-u' )
      args.append( uid )
      
   # Get a list of processes matching the name.
   command = ['pgrep'] + args + ['^{}$'.format( process_name )]
   kill_proc = subprocess.Popen( command, stdout=subprocess.PIPE )

   # Iterate through all found PID.
   pids_out = []
   while True:
      pid_kill = kill_proc.stdout.readline().rstrip()
      if pid_kill.isdigit():
         pids_out.append( pid_kill )
      else:
         break

   return pids_out

def remount( path, lock_dir_path ):
   print ' '
   # TODO: Check for existing lock on this mount.
   for lock_iter in os.listdir( lock_dir_path ):
      print os.path.join( lock_dir_path, lock_iter )
      #re.match( r'(.*):(.*)', lock_contents )

   # TODO: Schedule automatic remount with opposite FS attrib for script exit.
   #, str( os.getpid() )

   # TODO: Perform remount.

