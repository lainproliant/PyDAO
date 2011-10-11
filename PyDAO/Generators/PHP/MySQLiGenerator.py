#
# PHP/MySQLi Generator
#
# Generates PHP DAO class code for the given database
# schema using MySQLi libraries.
#
# (c) September 2011 Lee Supe (lain_proliant)
# Released under the GNU General Public License, version 3.
#

import os
import sys

from PyDAO.IndentWriter import *
from PyDAO.GeneratorException import *
from PyDAO.GeneratorBase import *
from PyDAO.Mapping import registerGenerator

DAO_EXCEPTION_FILENAME = "DAOException.php"

#--------------------------------------------------------------------
class MySQLiGeneratorException (GeneratorException): pass


#--------------------------------------------------------------------
def lower (s):
   """
      Lower the first character of the given string.
   """

   return s[0].lower () + s[1:]


#--------------------------------------------------------------------
def cap (s):
   """
      Capitalize the first character of the given string.
   """

   return s[0].capitalize () + s[1:]


#--------------------------------------------------------------------
def printOverwriteWarning (filename):
   """
      Prints a warning regarding the given file about overwrites.
      For internal use only.
   """

   iw = IndentWriter (sys.stderr) 
   iw ("WARNING (\'%s\'): Output file already exists, refused to overwrite." % filename)


#--------------------------------------------------------------------
class MySQLiGenerator (GeneratorBase):
   """
      Writes a series of PHP class files to the given output directory.
      These class files represent an API which can be used to access
      a MySQL database matching the given schema.
   """

   def __init__ (self, **kwargs):
      """
         Initializes a MySQLiGenerator.
      """

      GeneratorBase.__init__ (self)


   def generate (self, schema, outputPath, overwrite = False):
      """
         Writes Value Objects (*VO) and Data Access Objects (*DAO)
         to various PHP source files in the given output directory.
      """
      
      if not os.path.exists (outputPath):
         os.mkdir (outputPath)

      elif not os.path.isdir (outputPath):
         raise MySQLiGeneratorException (
               "Output path is not a directory: '%s'." % outputPath)
      
      self.generateExceptionClass (outputPath, overwrite)

      tables = schema.getTableNames () 
       
      for tableName in tables:
         self.generateTableVO  (tableName, schema, outputPath, overwrite)
         #self.generateTableDAO (tableName, schema, outputDir, overwrite)

   
   def generateTableVO (self, tableName, schema, outputPath, overwrite = False):
      """
         Generates a VO class file for the given table.
      """
      
      voClassName = schema.getTable (tableName).getAlias () + 'VO'
      voClassFilePath = os.path.join (outputPath, "%s.php" % voClassName)

      if os.path.exists (voClassFilePath) and not overwrite:
         printOverwriteWarning (voClassFilePath)
         return False

      tableSchema = schema.getTable (tableName)

      outFile = open (voClassFilePath, 'w')

      iw = IndentWriter (outFile)

      iw ('<?php')
      iw ('include_once "DAOException.php";')
      iw ()

      iw ('class %s {' % voClassName)
      with iw:
         # Declare a variable for each column.
         iw ('var %s;' % (
            ', '.join (['$%s' % lower (
               c.getAlias ()) for c in tableSchema.getAllColumns ()])))
         iw ()
         
         # Print a static get-by method for the primary key, with support
         # for composite primary keys.  If the primary key is a
         # composite key, the method will be called 'byPrimaryKey'.
         indexSchema = 

         # Write a simple get/set method pair for each variable.
         # TODO: Intelligently pack and unpack date values and
         # other sorts of values with different representations
         # in PHP than in the MySQL database.
         for column in tableSchema.getAllColumns ():
            iw ('public function get%s () {' % cap (column.getAlias ()))
            with iw:
               iw ('return $this->%s;' % lower (column.getAlias ()))
            iw ('}')
            iw ()

            iw ('public function set%s ($%s) {' % (cap (column.getAlias ()),
                  lower (column.getAlias ())))
            with iw:
               iw ('$this->%s = $%s;' % (lower (column.getAlias ()),
                     lower (column.getAlias ())))
            iw ('}')
            iw ()

      iw ('}')
      iw ()
      iw ('?>')

      outFile.close ()
     

   def generateExceptionClass (self, outputPath, overwrite = False):
      """
         Generates a class file named DAOException.php.
         If this file already exists, it will not be overwritten
         unless overwrite is specified.
      """
      
      daoExceptionPath = os.path.join (outputPath, DAO_EXCEPTION_FILENAME)
      
      if os.path.exists (daoExceptionPath) and not overwrite:
         printOverwriteWarning (daoExceptionPath)
         return False

      outFile = open (daoExceptionPath, 'w')

      iw = IndentWriter (outFile)

      iw ('<?php')
      iw ('class DAOException extends Exception {')
      with iw:
         iw ('function __construct ($message, $error, $affected_rows) {')
         with iw:
            iw ('parent::__construct ($message);')
            iw ('$this->error = $error;')
            iw ('$this->affected_rows = $affected_rows;')
         iw ('}')
      iw ('}')
      iw ('?>')

      outFile.close ()


   def interpolateType (self, datatype):
      """
         Returns a character for mysqli_stmt_bind_param corresponding
         to the given datatype.

         Types that do not appear here are currently not supported
         by this generator.
      """
      
      if datatype in ['CHAR', 'VARCHAR', 'TINYTEXT', 'TEXT', 'MEDIUMTEXT', 'LONGTEXT',
            'DATE', 'DATETIME', 'TIMESTAMP', 'TIME', 'ENUM', 'SET', 'DECIMAL']:
         return 's'

      elif datatype in ['INT', 'TINYINT', 'SMALLINT', 'MEDIUMINT', 'BIGINT', 'YEAR']:
         return 'i'

      elif datatype in ['FLOAT', 'DOUBLE']:
         return 'd'

      else:
         raise MySQLiGeneratorException (
               "Unsupported SQL datatype in mysqli interpolation: '%s'." % datatype)


#--------------------------------------------------------------------
# Register this generator in PyDAO.Mapping.
#
registerGenerator ('PHP/MySQLi', MySQLiGenerator)
