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
import logging
import StringIO
import zipfile
import pbkdf2
import struct
import whoosh.qparser
import whoosh.fields
import whoosh.query
import whoosh.filedb.filestore
from Crypto import Random
from Crypto.Cipher import AES

CHUNK_LEN = 64 * 1024

archive_size = 0
archive_current = 0

def _salt_paths( archive_path ):
   return [
      os.path.join( os.path.dirname( archive_path ), 'salt.txt' ),
      os.path.join( os.path.expanduser( '~' ), '.saltzaes.txt' ),
   ]

def extract( archive_file, extract_path, files=None ):

   logger = logging.getLogger( 'ifdyutil.archive.extract' )

   # Make sure extract_path exists.
   try:
      os.mkdir( extract_path )
      logger.info( 'Created directory {}.'.format( extract_path ) )
   except:
      pass

   # TODO: Implement files extract list.
   archive_file.extractall( extract_path )

def search( archive_file, search_phrase ):

   ''' Search the given archive for logs with the given terms. '''

   logger = logging.getLogger( 'ifdyutil.archive.search' )

   # Load the index into a storage unit.
   ix_storage = whoosh.filedb.filestore.RamStorage()
   for zipped_name in archive_file.namelist():
      if zipped_name.startswith( '/index' ):
         zipped_base = os.path.basename( zipped_name )
         with archive_file.open( zipped_name ) as zipped_file:
            with ix_storage.create_file( zipped_base ) as ix_file:
               ix_file.write( zipped_file.read() )

   schema = whoosh.fields.Schema(
      path=whoosh.fields.ID(stored=True),
      content=whoosh.fields.TEXT
   )
   ix = ix_storage.open_index( schema=schema )

   # Perform the search.
   with ix.searcher() as searcher:

      qp = whoosh.qparser.SimpleParser( 'content', schema )
      results = searcher.search( qp.parse( search_phrase ) )

      # TODO: Display the results.
      result_list = []
      for hit in results:
         # TODO: Use a more portable root.
         hit_file = archive_file.open( '/' + hit.get( 'path' ) )
         result_list.append( {
            'filename': hit.get( 'path' ),
            'contents': hit_file.read()
         } )

   return result_list

def handle( archive_path, key, salt=None ):
   
   ''' Open the given archive and return a zipfile handle. '''

   global archive_size

   # Try to load the salt from a salt file.
   # TODO: Add a versioning system to the file with salt in header.
   if not salt:
      for salt_path in _salt_paths( archive_path ):
         try:
            with open( salt_path, 'r' ) as salt_file:
               salt = salt_file.readline().strip()
            break
         except:
            pass

   with open( archive_path, 'rb' ) as archive_file:
      archive_size = struct.unpack(
         '<Q', archive_file.read( struct.calcsize('Q') )
      )[0]
      iv = archive_file.read( 16 )

      # Begin decrypting the archive data.
      key_crypt = pbkdf2.PBKDF2( key, salt ).read( 32 )
      decryptor = AES.new( key_crypt, AES.MODE_CBC, iv )
      plain_string = ''
      while True:
         chunk = archive_file.read( CHUNK_LEN )
         if 0 == len( chunk ):
            break
         plain_string = plain_string + decryptor.decrypt( chunk )

   # Open the decrypted string as a ZIP file.
   arcio = StringIO.StringIO( plain_string )
   return zipfile.ZipFile( arcio )

def create( archive_path, key, salt=None, item_list=[] ):

   ''' Item list must be in the format:
   [{'path_abs', 'path_rel, 'contents'}] '''

   # TODO: Move this function to ifdyutil.

   logger = logging.getLogger( 'ifdyutil.archive.create' )

   # Try to load the salt from a salt file.
   # TODO: Add a versioning system to the file with salt in header.
   if not salt:
      for salt_path in _salt_paths( archive_path ):
         try:
            with open( salt_path, 'r' ) as salt_file:
               salt = salt_file.readline().strip()
            break
         except:
            pass

   # Create the search index for the archive.
   schema = whoosh.fields.Schema(
      path=whoosh.fields.ID(stored=True),
      content=whoosh.fields.TEXT
   )
   ix_storage = whoosh.filedb.filestore.RamStorage()
   ix = ix_storage.create_index( schema )
   ix_writer = ix.writer()
   
   # Read all of the logs and write them to the archive ZIP.
   arcio = StringIO.StringIO()
   total_bytes = 0
   with zipfile.ZipFile( arcio, 'w', zipfile.ZIP_DEFLATED ) as arcz:
      for item in item_list:
         logger.info( 'Indexing {}...'.format( item['path_rel'] ) )
         ix_writer.add_document(
            path=item['path_rel'][1:].decode( 'ascii' ),
            content=item['contents']
         )
         logger.info( 'Storing {}...'.format( item['path_rel'] ) )
         arcz.writestr(
            item['path_rel'], item['contents'].encode( 'utf-8' )
         )
         total_bytes += len( item['contents'] )

      # Write the search index to the ZIP.
      ix_writer.commit()
      for ix_file_name in ix_storage.list():
         with ix_storage.open_file( ix_file_name ) as ix_file:
            logger.info( 'Storing {}...'.format( ix_file_name ) )
            ix_contents = ix_file.read()
            arcz.writestr(
               os.path.join( '/index', ix_file_name ),
               ix_contents
            )
            total_bytes += len( ix_contents )

   logger.info( 'Stored {} bytes.'.format( total_bytes ) )

   # Setup the encryptor. Expand and set the key.
   iv = Random.get_random_bytes( 16 )
   key_crypt = pbkdf2.PBKDF2( key, salt ).read( 32 )
   encryptor = AES.new( key_crypt, AES.MODE_CBC, iv )

   # Open the output file and start writing.
   arcio.seek( 0, os.SEEK_SET )
   with open( archive_path, 'wb' ) as archive_file:
      archive_file.write( struct.pack( '<Q', len( arcio.getvalue() ) ) )
      archive_file.write( iv )
      # Process each chunk of the ZIP.
      while True:
         chunk = arcio.read( CHUNK_LEN )
         if len( chunk ) == 0:
            # We're done!
            break
         elif 0 != len( chunk ) % 16:
            # Handle the trailing end.
            chunk += ' ' * (16 - len( chunk ) % 16)
         archive_file.write( encryptor.encrypt( chunk ) )

