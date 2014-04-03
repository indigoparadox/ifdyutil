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

UNKNOWN = 3
CRITICAL = 2
WARNING = 1
OK = 0

import sys

def exit_unknown( message ):
   print( 'UNKNOWN - {}'.format( message ) )
   sys.exit( UNKNOWN )

def exit_critical( message ):
   print( 'CRITICAL - {}'.format( message ) )
   sys.exit( CRITICAL )

def exit_warning( message ):
   print( 'WARNING - {}'.format( message ) )
   sys.exit( WARNING )

def exit_ok( message ):
   print( 'OK - {}'.format( message ) )
   sys.exit( OK )

