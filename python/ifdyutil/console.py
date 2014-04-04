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
import sys

class InvalidPromptResponse( Exception ):
   pass

def set_title( title ):

   ''' Set terminal window/tab title. '''

   # TODO: Handle other platforms.
   if os.getenv( 'STY' ):
      # We're inside GNU Screen.
      sys.stdout.write( '\033k{}\033\\'.format( title ) )
   else:
      # We're in UNIX.
      sys.stdout.write( '\x1b]2;{}\x07'.format( title ) )

def prompt_yn( prompt ):
   
   ''' Prompt a user to answer a simple Y/N question. '''

   print( '{} ([Y]es/[N]o)'.format( prompt ) )
   response = raw_input()
   if 'yes'.startswith( response.lower() ):
      return True
   elif 'no'.startswith( response.lower() ):
      return False
   else:
      raise InvalidPromptResponse()

