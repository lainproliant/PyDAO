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
      
      tableSchema = schema.getTable (tableName)
      voClassName = tableSchema.getAlias () + 'VO'
      daoClassName = tableSchema.getAlias () + 'DAO'
      voClassFilePath = os.path.join (outputPath, "%s.php" % voClassName)
      daoClassFilePath = os.path.join (outputPath, "DAO/%s.php" % daoClassName)

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
         primaryKey = tableSchema.getPrimaryKey ()
         if primaryKey is not None:
            keyColumns = [
                  tableSchema.getColumn (c) for c in primaryKey.getColumns ()]

            methodName = None
            params = ', '.join (['$%s' % lower (c.getName ()) for c in keyColumns])

            if len (keyColumns) == 1:
               methodName = cap (keyColumns [0].getAlias ())
            else:
               methodName = 'PrimaryKey'

            iw ('public static function by%s (%s) {' % (
               methodName, params))
            
            with iw:
               iw ('$dao = new %s ();' % daoClassName)
               iw ('return static::fromResult ($dao->by%s (%s));' % (
                  methodName, params))
            
            iw ('}')
            iw ()

         # Print a get-by method for each index.
         for index in tableSchema.getAllIndexes ():
            keyColumns = [
                  tableSchema.getColumn (c) for c in index.getColumns ()]

            methodName = 'by%s' % cap (index.getAlias ())
            params = ', '.join (['$%s' % lower (c.getName ()) for c in keyColumns])

            # Is the index unique?  If it is not, we must process
            # and return multiple results in an array.
            if index.isUnique ():
               iw ('public static function %s (%s) {' % (
                  methodName, params))

               with iw:
                  # The index is unique, we can return one result or NULL.
                  iw ('$dao = new %s ();' % daoClassName)
                  iw ('return static::fromResult ($dao->%s (%s));' % (
                     methodName, params))

               iw ('}')

            else:
               # The index is not unique, we must return an array
               # of zero or more results.
               methodName = 'list' + cap (methodName)

               iw ('public static function %s (%s) {' % (
                  methodName, params))

               with iw:   
                  iw ('$dao = new %s ();' % daoClassName)
                  iw ('$objs = array ();')
                  iw ('foreach ($dao->%s (%s) as $result) {' % (
                     methodName, params))
                  with iw:
                     iw ('$objs [] = static::fromResult ($result);')

                  iw ('}')
                  iw ()
                  iw ('return $objs;')

               iw ('}')


         # Write a static fromResult method.  This method
         # constructs an instance of the VO object from
         # the provided data.  It is used to unpack results
         # from the DAO layer.
         # If the result data is empty, NULL is returned.
         iw ('public static function fromResult ($result) {')
         with iw:
            iw ('if (empty ($result)) {')
            with iw:
               iw ('return NULL;')
            iw ('}')
            iw ()

            iw ('$obj = new static ();')
            for column in tableSchema.getAllColumns ():
               iw ('$obj->%s = $result ["%s"];' % (
                  lower (column.getAlias ()), column.getName ()))

            iw ('return $obj;')

         iw ('}')
         iw ()
         
         # Print a toData method.  This method is used to construct
         # an array of data to be passed into the DAO layer.
         iw ('protected function toData () {')
         with iw:
            iw ('$data = array ();')

            for column in tableSchema.getAllColumns ():
               iw ('$data ["%s"] = $this->%s' % (
                  column.getName (), lower (column.getAlias ())))

            iw ('return $data;')
         iw ('}')


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
