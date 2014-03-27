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
import logging

FS_ATTRIBS_OPPOSITE = {
   'rw': 'ro',
   'ro': 'rw',
   'exec': 'noexec',
   'noexec': 'exec',
}

FS_REMOUNT_LOCK_PATH = '/var/lock/qnrmount'

class RemountException( Exception ):
   pass

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

def _check_remount_lock( fs_mount_path, perm ):

   ''' Make sure we can perform the requested remount. Return True if we can,
   or False otherwise. '''

   logger = logging.getLogger( 'util.remount.lock' )

   for pid_entry_iter in os.listdir( FS_REMOUNT_LOCK_PATH ):
      pid_lock_path = os.path.join( FS_REMOUNT_LOCK_PATH, pid_entry_iter )
      with open( pid_lock_path ) as pid_lock_file:
         for fs_line in pid_lock_file:
            fs_status = fs_line.strip().split( ':' )

            if fs_status[0] == fs_mount_path:
               if perm == FS_ATTRIBS_OPPOSITE[fs_status[1]]:
                  logger.warn(
                     '"{}" is in use, not remounting with "{}".'.format(
                        fs_status[0], perm
                     )
                  )
                  return False

   # No locks found.
   return True

def remount( fs_mount_path, perm ):

   logger = logging.getLogger( 'util.remount' )

   if not perm in FS_ATTRIBS_OPPOSITE.keys():
      raise RemountException( 'Unsupported perms: "{}"'.format( perm ) )

   if _check_remount_lock( fs_mount_path, perm ):
      logger.debug( 'Remounting "{}" with "{}".'.format( fs_mount_path, perm ) )

      # Perform the remount and verify its success.
      mount_proc = subprocess.Popen(
         ['mount', '-o', 'remount,' + perm, fs_mount_path]
      )
      mount_proc.communicate()
      if mount_proc.returncode:
         raise Remounting( 'Mount process failed.' )
      else:
         logger.debug( 'Remount completed successfully.' )

   # TODO: Schedule automatic remount with opposite FS attrib for script exit.

def create_lock( lock_path ):

   ''' Create a lock file containing the PID of the current process. '''

   if not os.path.isfile( lock_path ):
      with open( lock_path, 'w' ) as pid_file:
         pid_file.write( '{}'.format( os.getpid() ) )

def check_lock( lock_path, unlink_old=True ):

   ''' Make sure the existing lock file (if any) doesn't point to a running
   process. Return true if it does, false if it doesn't. '''

   if os.access( lock_path, os.F_OK ):
      with open( lock_path, 'r' ) as pid_file:
         pid_file.seek( 0 )
         existing_pid = pid_file.readline()
         if os.path.exists( '/proc/{}'.format( existing_pid ) ):
            return True
         else:
            if unlink_old:
               os.unlink( lock_path )
            return False

