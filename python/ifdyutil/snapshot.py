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
import re

def snapshot_zfs( lvtarget, vgtarget ):
    print "ZFS snapshot functionality not yet available."
    return False

def snapshot_lvm( lvtarget, vgtarget, size, ssname=None ):
    if None == ssname:
        # No snapshot name was defined, so use today's date.
        ssname = date.today().strftime( '%Y%m%d' )

    # Code the snapshot according to today's date.
    command = [
        'lvcreate',
        '-L%s' % size,
        '-s',
        '-n',
        '%s%s' % (lvtarget, ssname),
        '%s/%s' % (vgtarget, lvtarget)
    ]

    # Call the command.
    try:
        subprocess.check_call( command )
    except:
        return False

    # No news is good news.
    return True

def clean_snapshots_lvm( lvtarget, vgtarget, maxdays ):
    # TODO: Iterate through existing snapshots and drop snapshots older than
    #         maxdays.
    print "Snapshot cleanup is not yet available."
    return False

def list_mounts_lvm():
    pattern_mapper = re.compile( r'^/dev/mapper/(\S*)\s*(\S*)' )
    lvm_mounts = [] # A list of tuples describing mounted LVM volumes.
    try:
        with open( '/proc/mounts', 'r' ) as file_mounts:
            for line in file_mounts:
                line_match = pattern_mapper.match( line )
                if None != line_match:
                    lvm_mounts.append( line_match.groups() )
    except:
        return []

    return lvm_mounts

