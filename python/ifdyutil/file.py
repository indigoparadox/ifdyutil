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
import atexit
import time

FS_ATTRIBS_OPPOSITE = {
   'rw': 'ro',
   'ro': 'rw',
   'exec': 'noexec',
   'noexec': 'exec',
}

FS_REMOUNT_LOCK_PATH = '/var/lock/qnrmount'
FS_MOUNT_LOCK_PATH = '/var/lock/qnmount'

LOCK_TYPE_REMOUNT = 1
LOCK_TYPE_MOUNT = 2

CRYPT_UNMAP_TRIES_MAX = 5

class CryptException( Exception ):
   pass

class MountException( Exception ):
   pass

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

def _create_fs_lock( fs_mount_path, lock_type, perm='' ):

   # Determine our lock dir and make sure it exists.
   if LOCK_TYPE_REMOUNT == lock_type:
      lock_dir = FS_REMOUNT_LOCK_PATH
   elif LOCK_TYPE_MOUNT == lock_type:
      lock_dir = FS_MOUNT_LOCK_PATH

   if not os.path.isdir( lock_dir ):
      os.makedirs( lock_dir )

   # Create/append to the lock file.
   pid_lock_path = os.path.join( lock_dir, str( os.getpid() ) )
   if os.path.exists( pid_lock_path ):
      # Append to the existing lock file.
      with open( pid_lock_path, 'a' ) as pid_lock_file:
         pid_lock_file.write( '\n{}:{}'.format( fs_mount_path, perm ) )
   else:
      # Create a new lock file.
      with open( pid_lock_path, 'w' ) as pid_lock_file:
         pid_lock_file.write( '{}:{}'.format( fs_mount_path, perm ) )

def _check_fs_lock( fs_mount_path, lock_type, perm='' ):

   ''' Make sure no other ifdy processes are still using the given mount.
   Return True if none are, or False otherwise. '''

   logger = logging.getLogger( 'util.mount.lock' )

   if LOCK_TYPE_REMOUNT == lock_type:
      lock_path = FS_REMOUNT_LOCK_PATH
   elif LOCK_TYPE_MOUNT == lock_type:
      lock_path = FS_MOUNT_LOCK_PATH

   for pid_entry_iter in os.listdir( lock_path ):
      pid_lock_path = os.path.join( lock_path, pid_entry_iter )

      # Check to make sure we're not looking at our own lock file.
      if int( pid_entry_iter ) == os.getpid():
         continue

      # Check if the iterated process is still active.
      try:
         os.getsid( int( pid_entry_iter ) )
      except OSError:
         logger.warn(
            'No process found for PID {}. Removing lock...'.format(
               pid_entry_iter
            )
         )
         os.unlink( pid_lock_path )
         continue

      # Check if the iterated process is locking this mount.
      with open( pid_lock_path ) as pid_lock_file:
         for fs_line in pid_lock_file:
            fs_status = fs_line.strip().split( ':' )
            if fs_status[0] == fs_mount_path:
               if LOCK_TYPE_REMOUNT == lock_type:
                  if perm == FS_ATTRIBS_OPPOSITE[fs_status[1]]:
                     logger.warn(
                        '"{}" in use by {}, not remounting with "{}".'.format(
                           fs_status[0], pid_entry_iter, perm
                        )
                     )
                     return False
               elif LOCK_TYPE_MOUNT == lock_type:
                  logger.warn(
                     '"{}" in use by {}, not unmounting.'.format(
                        fs_status[0], pid_entry_iter
                     )
                  )
                  return False

   # No locks found.
   return True

def remount( fs_mount_path, perm, register_cleanup=True ):

   logger = logging.getLogger( 'util.remount' )

   if not perm in FS_ATTRIBS_OPPOSITE.keys():
      raise RemountException( 'Unsupported perms: "{}"'.format( perm ) )

   if _check_fs_lock( fs_mount_path, LOCK_TYPE_REMOUNT, perm=perm ):
      logger.info( 'Remounting "{}" with "{}".'.format( fs_mount_path, perm ) )

      # Create lock for this mount.
      _create_fs_lock( fs_mount_path, LOCK_TYPE_REMOUNT, perm=perm )

      # Perform the remount and verify its success.
      mount_proc = subprocess.Popen(
         ['mount', '-o', 'remount,' + perm, fs_mount_path]
      )
      mount_proc.communicate()
      if mount_proc.returncode:
         raise RemountException( 'Mount process failed.' )
      #else:
      #   logger.debug( 'Remount completed successfully.' )

      # Schedule automatic remount with opposite FS attrib for script exit.
      if register_cleanup:
         atexit.register(
            remount, fs_mount_path, FS_ATTRIBS_OPPOSITE[perm], False
         )

def _mount_check( mount_path ):
   
   ''' Check that mount_path is not already mounted. '''

   with open( '/proc/mounts', 'r' ) as mounts_file:
      for line_iter in mounts_file:
         line_array = line_iter.strip().split( ' ' )
         if line_array[1] == mount_path:
            return True
   return False

def mount_crypt(
   block_path, map_name, mount_path, key_path, register_cleanup=True
):

   map_path = '/dev/mapper/{}'.format( map_name )

   if not os.path.exists( key_path ):
      raise CryptException( 'Could not locate key file: {}'.format( key_path ) )

   if os.path.exists( map_path ):
      raise CryptException( 'Mapper already exists: {}'.format( map_path ) )
   
   if not os.path.exists( block_path ):
      raise MountException( 'Could not locate device: {}'.format( block_path ) )

   if not os.path.isdir( mount_path ):
      raise MountException( 'Bad mount path: {}'.format( mount_path ) )

   if _mount_check( mount_path ):
      raise MountException( 'Path already mounted: {}'.format( mount_path ) )

   # Create the lock and cleanup hook early in case we abort midway through
   # mounting.
   _create_fs_lock( mount_path, LOCK_TYPE_MOUNT )

   # Register atexit unmount.
   if register_cleanup:
      atexit.register( umount_crypt, map_name, mount_path )

   # Perform the device setup.
   crypt_command = \
      ['cryptsetup', 'luksOpen', block_path, '--key-file', key_path, map_name];

   crypt_proc = subprocess.Popen(
      crypt_command,
      stdout=subprocess.PIPE, stderr=subprocess.PIPE
   )
   crypt_proc.communicate()

   if crypt_proc.returncode:
      # Try it read-only.
      crypt_command.insert( 2, '--readonly' )
      crypt_proc = subprocess.Popen(
         crypt_command,
         stdout=subprocess.PIPE, stderr=subprocess.PIPE
      )
      crypt_proc.communicate()
      if crypt_proc.returncode:
         raise CryptException(
            'Could not open crypt volume: {}'.format( block_path )
         )

   # Check that the mapper exists.
   if not os.path.exists( map_path ):
      raise CryptException( 'Mapper file not created: {}'.format( map_path ) )

   # Mount secforce if it's not already mounted.
   mount_proc = subprocess.Popen(
      ['mount', map_path, mount_path],
      stdout=subprocess.PIPE, stderr=subprocess.PIPE
   )
   mount_proc.communicate()
   if mount_proc.returncode:
      raise MountException( 'Could not mount: {}'.format( mount_path ) )

def umount_crypt( map_name, mount_path ):
   if _check_fs_lock( mount_path, LOCK_TYPE_MOUNT ):

      # Make sure it's actually mounted before trying to unmount.
      if _mount_check( mount_path ):
         mount_proc = subprocess.Popen(
            ['umount', mount_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
         )
         mount_proc.communicate()
         if mount_proc.returncode:
            raise MountException( 'Could not unmount: {}'.format( mount_path ) )

      # Don't make sure the device is mapped before trying to unmap because
      # cryptsetup might be taking its sweet time. Just forcibly try to unmap
      # it until it goes.
      unmap_result = 1
      crypt_unmap_tries = 0
      while crypt_unmap_tries < CRYPT_UNMAP_TRIES_MAX and unmap_result:
         crypt_proc = subprocess.Popen(
            ['cryptsetup', 'luksClose', map_name],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
         )
         crypt_proc.communicate()
         unmap_result = crypt_proc.returncode
         crypt_unmap_tries += 1
         if unmap_result:
            # Try sleeping for a little.
            time.sleep( 1 )

      if unmap_result:
         raise CryptException( 'Could not close map: {}'.format( map_name ) )

def create_lock( lock_path ):

   ''' Create a lock file containing the PID of the current process. '''

   if not os.path.isfile( lock_path ):
      with open( lock_path, 'w' ) as pid_file:
         pid_file.write( '{}'.format( os.getpid() ) )
   else:
      # TODO: If lock_path exists, add our pid to it.
      pass

def check_lock( lock_path, unlink_old=True ):

   ''' Make sure the existing lock file (if any) doesn't point to a running
   process. Return true if it does, false if it doesn't. '''

   if os.access( lock_path, os.F_OK ):
      with open( lock_path, 'r' ) as pid_file:
         
         # TODO: Iterate through *all* pids in the lock file.

         pid_file.seek( 0 )
         existing_pid = pid_file.readline()
         if os.path.exists( '/proc/{}'.format( existing_pid ) ):
            return True
         else:
            if unlink_old:
               os.unlink( lock_path )
            return False

