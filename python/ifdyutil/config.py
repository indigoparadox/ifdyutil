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

import re
import os

def load():

   ''' Return the config for ifdy-scripts. Conglomerate system-wide config in
   etc with user-specific config in ~/.qnvars.sh. '''

   pattern_config_var = re.compile( r'^(#)?(\S*)=(\S*)' )

   cfg = {}

   with open( '/etc/qnvars.sh' ) as system_config_file:
      # Load the system-wide config.
      for line in system_config_file:
         config_match = pattern_config_var.match( line )
         if None != config_match and None == config_match.groups()[0]:
            print config_match.groups()
            cfg[config_match.groups()[1]] = config_match.groups()[2]

   try:
      with open( os.path.join( os.path.expanduser( '~' ), 'qnvars.sh' ) ) \
      as system_config_file:
         # Override settings with those found in the per-user config.
         for line in system_config_file:
            config_match = pattern_config_var.match( line )
            if None != config_match and None == config_match.groups()[0]:
               print config_match.groups()
               cfg[config_match.groups()[1]] = config_match.groups()[2]
   except:
      # Per-user config is optional.
      pass

   return cfg

