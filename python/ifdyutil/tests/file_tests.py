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

import unittest
import mimetypes
from .. import file

class FileTests( unittest.TestCase ):
   def runTest( self ):
      pass

   def test_listdir_mime( self ):
      test_list = file.listdir_mime( '.', ['application/x-python-code'] )
      assert [] != test_list
      for entry in test_list:
         assert 'application/x-python-code' == mimetypes.guess_type( entry )[0]

