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
import shutil

from PyDAO.IndentWriter import *
from PyDAO.GeneratorException import *
from PyDAO.GeneratorBase import *
from PyDAO.Mapping import registerGenerator

MYSQLI_FILES_DIR = "mysqli_files"
DAO_EXCEPTION_FILENAME = "DAOException.php"
LOGGER_FILENAME = "Logger.php"
DAO_PATH_NAME = "DAO"

NO_PRIMARY_KEY_SAVE_NOTE = """
/*
 * This table does not have a primary key.
 * Override this method to update an entry
 * in the table however is appropriate.
 */
""".strip ()

NO_PRIMARY_KEY_DELETE_NOTE = """
/*
 * This table does not have a primary key.
 * Override this method to delete an entry
 * in the table however is appropriate.
 */
""".strip ()

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
def getPackageFilename (filename):
   """
      Gets a full path to the given package filename.
   """
   
   packageDir, packageFilename = os.path.split (__file__)
   return os.path.join (packageDir, filename)


#--------------------------------------------------------------------
def parseBoolean (boolString):
   """
      Parses a string to be True, False, 1, or 0 in any case.
      If it does not match these criterion, an exception is thrown.
   """

   if boolString.lower () == "true" or boolString == "1":
      return True

   elif boolString.lower () == "false" or boolString == "0":
      return False

   else:
      raise Exception ("Invalid boolean value string: %s" % boolString)


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

      self.voSuffix = 'VO'
      self.daoSuffix = 'DAO'
      self.dbConnectStatement = 'databaseConnect ();'
      self.loggerStatement = 'new Logger (sprintf ("%s.log.txt", get_class ()), Logger::LEVEL_DEBUG);'
      self.printHeader = True
      self.includeLogger = False

      if kwargs.has_key ('voSuffix'):
         self.voSuffix = kwargs ['voSuffix']

      if kwargs.has_key ('daoSuffix'):
         self.daoSuffix = kwargs ['daoSuffix']

      if kwargs.has_key ('connection'):
         self.dbConnectStatement = kwargs ['connection']

      if kwargs.has_key ('logger'):
         self.loggerStatement = kwargs ['logger']

      if kwargs.has_key ('printHeader'):
         self.printHeader = parseBoolean (kwargs ['printHeader'])

      if kwargs.has_key ('includeLogger'):
         self.includeLogger = parseBoolean (kwargs ['includeLogger'])


   def generate (self, schema, outputPath, overwrite = False):
      """
         Writes Value Objects (*VO) and Data Access Objects (*DAO)
         to various PHP source files in the given output directory.
      """
      
      daoOutputPath = os.path.join (outputPath, DAO_PATH_NAME)
      
      for path in (outputPath, daoOutputPath):
         if not os.path.exists (path):
            os.mkdir (path)
         
         elif not os.path.isdir (path):
            raise MySQLiGeneratorException (
                  "Output path is not a directory: '%s'." % path)
      
      self.generateExceptionClass (daoOutputPath, overwrite)
      self.generateLoggingClass (outputPath, overwrite)

      tables = schema.getTableNames ()
       
      for tableName in tables:
         self.generateTableVO  (tableName, schema, outputPath, overwrite)
         self.generateTableDAO (tableName, schema, daoOutputPath, overwrite)

   
   def generateTableVO (self, tableName, schema, outputPath, overwrite = False):
      """
         Generates a VO class file for the given table.
      """
      
      tableSchema = schema.getTable (tableName)
      voClassName = tableSchema.getAlias () + self.voSuffix
      daoClassName = tableSchema.getAlias () + self.daoSuffix
      voClassFilePath = os.path.join (outputPath, '%s.php' % voClassName)
      daoRelativeClassFilePath = 'DAO/%s.php' % daoClassName
      daoClassFilePath = os.path.join (outputPath, daoRelativeClassFilePath)
      
      if os.path.exists (voClassFilePath) and not overwrite:
         printOverwriteWarning (voClassFilePath)
         return False

      tableSchema = schema.getTable (tableName)
     
      # Does the table have a primary key with auto_increment?
      # If so, the primary key is assumed to contain only one column.
      autoIncrementColumn = None
      primaryKey = tableSchema.getPrimaryKey ()
      
      if primaryKey is not None and len (primaryKey.getColumns ()) == 1:
         primaryKeyColumn = tableSchema.getColumn (primaryKey.getColumns () [0])

         if primaryKeyColumn.getExtra () == 'auto_increment':
            autoIncrementColumn = primaryKeyColumn
      
      # Open the VO class file for writing.
      outFile = open (voClassFilePath, 'w')

      iw = IndentWriter (outFile)

      iw ('<?php')
      iw ('include_once "%s";' % daoClassFilePath)
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
               iw ()

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
               iw ()
         
         # Print a fetchAll method to retrieve all rows.
         iw ('public static function fetchAll () {')
         with iw:
            iw ('$dao = new %s ();' % daoClassName)
            iw ('$objs = array ();')
            iw ('foreach ($dao->fetchAll () as $result) {')
            with iw:
               iw ('$objs [] = static::fromResult ($result);')

            iw ('}')
            iw ()
            iw ('return $objs;')
         iw ('}')
         iw ()

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
               iw ('$data ["%s"] = $this->%s;' % (
                  column.getName (), lower (column.getAlias ())))

            iw ('return $data;')
         iw ('}')
         iw ()

         # Print an insert method for saving new entries
         iw ('public function insert () {')
         with iw:
            iw ('$dao = new %s ();' % daoClassName)

            if autoIncrementColumn is not None:
               iw ('$this->%s = $dao->insert ($this->toData ());' %
                     lower (autoIncrementColumn.getAlias ()))

            else:
               iw ('$dao->insert ($this->toData ());')

         iw ('}')
         iw ()

         # Print a save method.
         iw ('public function save () {')
         with iw:
            iw ('$dao = new %s ();' % daoClassName)
            iw ('$dao->save ($this->toData ());')
         
         iw ('}')
         iw ()

         # Print a delete method.
         iw ('public function delete () {')
         with iw:
            iw ('$dao = new %s ();' % daoClassName)
            keyColumns = None

            if primaryKey is not None:
               keyColumns = [
                     tableSchema.getColumn (c) for c in primaryKey.getColumns ()]

            else:
               keyColumns = tableSchema.getAllColumns ()

            params = ', '.join (['$%s' % lower (c.getName ()) for c in keyColumns])

            iw ('$dao->delete (%s);' % params)

         iw ('}')
         iw ()

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
   

   def generateTableDAO (self, tableName, schema, outputPath, overwrite = False):
      """
         Generates a DAO class file for the given table.
      """
      
      tableSchema = schema.getTable (tableName)
      daoClassName = tableSchema.getAlias () + self.daoSuffix
      daoClassFilePath = os.path.join (outputPath, '%s.php' % daoClassName)
      
      if os.path.exists (daoClassFilePath) and not overwrite:
         printOverwriteWarning (daoClassFilePath)
         return False

      tableSchema = schema.getTable (tableName)
     
      # Does the table have a primary key with auto_increment?
      # If so, the primary key is assumed to contain only one column.
      autoIncrementColumn = None
      primaryKey = tableSchema.getPrimaryKey ()
      
      if primaryKey is not None and len (primaryKey.getColumns ()) == 1:
         primaryKeyColumn = tableSchema.getColumn (primaryKey.getColumns () [0])

         if primaryKeyColumn.getExtra () == 'auto_increment':
            autoIncrementColumn = primaryKeyColumn
      
      # Open the DAO class file for writing.
      outFile = open (daoClassFilePath, 'w')

      iw = IndentWriter (outFile)

      iw ('<?php')
      iw ('include_once "DAOException.php";')

      if self.includeLogger:
         iw ('include_once "../Logger.php";')

      iw ()

      iw ('class %s {' % daoClassName)
      with iw:
         # Print the constructor.
         #
         # This method uses the 'dbConnectStatement' above to fetch
         # a MySQLi connection object.  This can be overwritten to 
         # contain any statement which returns a valid MySQLi connection.
         #
         # Also uses 'loggerStatement' above to fetch an instance of a Logger
         # class.  This class may be a Logger, or any class which implements
         # the methods in Logger.  See 'mysqli_files/Logger.php' in the package
         # file path for more details.
         #
         # These statements are not validated, and may represent a security risk.

         iw ('function __construct () {')
         with iw:
            iw ('$this->db = %s' % self.dbConnectStatement)
            iw ('$this->log = %s' % self.loggerStatement)
         iw ('}')
         iw ()

         # Print a static get-by method for the primary key, with support
         # for composite primary keys.  If the primary key is a
         # composite key, the method will be called 'byPrimaryKey'.
         # This method does not get printed if there is no primary key.
         if primaryKey is not None:
            keyColumns = [
                  tableSchema.getColumn (c) for c in primaryKey.getColumns ()]

            methodName = None
            params = ', '.join (['$%s' % lower (c.getName ()) for c in keyColumns])

            if len (keyColumns) == 1:
               methodName = cap (keyColumns [0].getAlias ())
            else:
               methodName = 'PrimaryKey'

            iw ('public function by%s (%s) {' % (
               methodName, params))
            
            with iw:
               statement = 'select %s from %s where %s' % (
                     ', '.join ([c.getName () for c in tableSchema.getAllColumns ()]),
                     tableSchema.getName (),
                     ' and '.join (['%s = ?' % c.getName () for c in keyColumns]))

               iw ('$stmt = $this->db->prepare ("%s");' % statement)
               iw ('if ($stmt == FALSE) {')
               with iw:
                  iw ('$this->log->logFatal (sprintf ("<%%s::%%s> Prepared statement failed: %%s", __CLASS__, __FUNCTION__, $this->db->error));')
                  iw ('throw new DAOException ("Prepared statement failed.", $this->db->error);')
               iw ('}')
               iw ('$stmt->bind_param ("%s", %s);' % (
                  ''.join ([self.interpolateType (c.getDataType ()) for c in keyColumns]),
                  ', '.join (['$%s' % lower (c.getName ()) for c in keyColumns])))
               iw ('$stmt->execute ();')
               iw ('$stmt->store_result ();')
               iw ('$stmt->bind_result (%s);' % (
                  ', '.join (
                     ['$results ["%s"]' % c.getName () \
                           for c in tableSchema.getAllColumns ()])))
               iw ('$stmt->fetch ();')
               iw ('if ($stmt->num_rows < 1) {')
               with iw:

                  iw ('$results = NULL;')
               iw ('}')
               iw ()
               iw ('$stmt->close ();')
               iw ('return $results;')
            
            iw ('}')
            iw ()

         # Print a get-by method for each index.
         # Prints either a fetch or list-by method depending upon
         # whether or not the index is unique.
         #
         # The fetch method ('byIndexName') will return either one
         # result or NULL.  The list-by method ('listByIndexName')
         # will return an array of zero or more results.
         for index in tableSchema.getAllIndexes ():
            keyColumns = [
                  tableSchema.getColumn (c) for c in index.getColumns ()]

            methodName = 'by%s' % cap (index.getAlias ())
            params = ', '.join (['$%s' % lower (c.getName ()) for c in keyColumns])

            statement = "select %s from %s where %s" % (
                  ', '.join ([c.getName () for c in tableSchema.getAllColumns ()]),
                  tableSchema.getName (),
                  ' and '.join (['%s = ?' % c.getName () for c in keyColumns]))
            
            # Is the index unique?  If it is not, we must process
            # and return multiple results in an array.
            if index.isUnique ():
               # The index is unique, we can return one result or NULL.
               iw ('public function %s (%s) {' % (
                  methodName, params))

               with iw:
                  iw ('$stmt = $this->db->prepare ("%s");' % statement)
                  iw ('if ($stmt == FALSE) {')
                  with iw:
                     iw ('$this->log->logFatal (sprintf ("<%%s::%%s> Prepared statement failed: %%s", __CLASS__, __FUNCTION__, $this->db->error));')
                     iw ('throw new DAOException ("Prepared statement failed.", $this->db->error);')
                  iw ('}')
                  iw ('$stmt->bind_param ("%s", %s);' % (
                     ''.join ([self.interpolateType (c.getDataType ()) for c in keyColumns]),
                     ', '.join (['$%s' % lower (c.getName ()) for c in keyColumns])))
                  iw ('$stmt->execute ();')
                  iw ('$stmt->store_result ();')
                  iw ('$stmt->bind_result (%s);' % (
                     ', '.join (
                        ['$results ["%s"]' % c.getName () for c in tableSchema.getAllColumns ()])))
                  iw ('$stmt->fetch ();')
                  iw ('if ($stmt->num_rows < 1) {')
                  with iw:
                     iw ('$results = NULL;')
                  iw ('}')
                  iw ()
                  iw ('$stmt->close ();')
                  iw ('return $results;')

               iw ('}')
               iw ()

            else:
               # The index is not unique, we must return an array
               # of zero or more results.
               methodName = 'list' + cap (methodName)

               iw ('public function %s (%s) {' % (
                  methodName, params))

               with iw:
                  iw ('$resultsList = array ();')
                  iw ('$results = array ();')
                  iw ('$stmt = $this->db->prepare ("%s");' % statement)
                  iw ('if ($stmt == FALSE) {')
                  with iw:
                     iw ('$this->log->logFatal (sprintf ("<%%s::%%s> Prepared statement failed: %%s", __CLASS__, __FUNCTION__, $this->db->error));')
                     iw ('throw new DAOException ("Prepared statement failed.", $this->db->error);')
                  iw ('}')
                  iw ('$stmt->bind_param ("%s", %s);' % (
                     ''.join ([self.interpolateType (c.getDataType ()) for c in keyColumns]),
                     ', '.join (['$%s' % lower (c.getName ()) for c in keyColumns])))
                  iw ('$stmt->execute ();')
                  iw ('$stmt->store_result ();')
                  iw ('$lambda = create_function (\'$a\', \'return $a;\');')
                  iw ('$stmt->bind_result (%s);' % (
                     ', '.join (
                        ['$results ["%s"]' % c.getName () for c in tableSchema.getAllColumns ()])))
                  iw ('while ($stmt->fetch ()) {')
                  with iw:
                     iw ('$resultsList [] = array_map ($lambda, $results);')
                  iw ('}')
                  iw ()
                  iw ('$stmt->close ();')
                  iw ('return $resultsList;')

               iw ('}')
               iw ()
         
         # Print a fetchAll method.
         # Returns zero or more results for each row in the table.
         statement = "select %s from %s" % (
               ', '.join ([c.getName () for c in tableSchema.getAllColumns ()]),
               tableSchema.getName ())

         iw ('public function fetchAll () {')
         with iw:
            iw ('$resultsList = array ();')
            iw ('$results = array ();')
            iw ('$stmt = $this->db->prepare ("%s");' % statement)
            iw ('if ($stmt == FALSE) {')
            with iw:
               iw ('$this->log->logFatal (sprintf ("<%%s::%%s> Prepared statement failed: %%s", __CLASS__, __FUNCTION__, $this->db->error));')
               iw ('throw new DAOException ("Prepared statement failed.", $this->db->error);')
            iw ('}')
            iw ('$stmt->execute ();')
            iw ('$stmt->store_result ();')
            iw ('$lambda = create_function (\'$a\', \'return $a;\');')
            iw ('$stmt->bind_result (%s);' % (
               ', '.join (
                  ['$results ["%s"]' % c.getName () for c in tableSchema.getAllColumns ()])))
            iw ('while ($stmt->fetch ()) {')
            with iw:
               iw ('$resultsList [] = array_map ($lambda, $results);')
            iw ('}')
            iw ()
            iw ('$stmt->close ();')
            iw ('return $resultsList;')
         iw ('}')
         iw ()

         # Print a search method for generic search based on parameters.
         # The search method is a very simplistic select query builder
         # and may be useful in certain circumstances to expand upon
         # the search behavior provided by the default fetch and list.
         iw ('public function search ($params, $postfix = "") {')
         with iw:
            iw ('$resultsList = array ();')
            iw ('$results = array ();')
            iw ('$bindTypes = "";')
            iw ('foreach (array_values ($params) as $val) {')
            with iw:
               iw ('if (is_int ($val)) { $bindTypes .= "i"; }')
               iw ('elseif (is_string ($val)) { $bindTypes .= "s"; }')
               iw ('elseif (is_float ($val)) { $bindTypes .= "d"; }')
               iw ('else {')
               with iw:
                  iw ('throw new DAOException ("Couldn\'t interpolate a search parameter.");')
               iw ('}')
            iw ('}')
            
            statement = 'select %s from %s where %%s' % (
                  ', '.join ([c.getName () for c in tableSchema.getAllColumns ()]),
                  tableSchema.getName ())

            iw ('$query = sprintf ("%s", implode (" and ", array_keys ($params)));' %
                  statement)
            iw ('$query .= " " . $postfix;')
            iw ('$bindParamArgs = array (&$bindTypes);')
            iw ('foreach ($params as $key => $value) {')
            with iw:
               iw ('$bindParamArgs [$key] = &$params [$key];')
            iw ('}')
            iw ('$stmt = $this->db->prepare ($query);')
            iw ('if ($stmt == FALSE) {')
            with iw:
               iw ('$this->log->logFatal (sprintf ("<%%s::%%s> Prepared statement failed: %%s", __CLASS__, __FUNCTION__, $this->db->error));')
               iw ('throw new DAOException ("Prepared statement failed.", $this->db->error);')
            iw ('}')
            iw ('call_user_func_array (array ($stmt, "bind_param"), $bindParamArgs);')
            iw ('$stmt->execute ();')
            iw ('$stmt->store_result ();')
            iw ('$lambda = create_function (\'$a\', \'return $a;\');')
            iw ('$stmt->bind_result (%s);' % (
               ', '.join (
                  ['$results ["%s"]' % c.getName () for c in tableSchema.getAllColumns ()])))
            iw ('while ($stmt->fetch ()) {')
            with iw:
               iw ('$resultsList [] = array_map ($lambda, $results);')
            iw ('}')
            iw ()
            iw ('$stmt->close ();')
            iw ('return $resultsList;')
         iw ('}')
         iw ()
         
         # Print an insert method.
         iw ('public function insert ($data) {')
         with iw:
            insertColumns = [c for c in tableSchema.getAllColumns () if c is not autoIncrementColumn]
            statement = "insert into %s (%s) values (%s)" % (
                  tableSchema.getName (),
                  ', '.join ([c.getName () for c in insertColumns]),
                  ', '.join (['?' for c in insertColumns]))

            iw ('$stmt = $this->db->prepare ("%s");' % statement)
            iw ('if ($stmt == FALSE) {')
            with iw:
               iw ('$this->log->logFatal (sprintf ("<%%s::%%s> Prepared statement failed: %%s", __CLASS__, __FUNCTION__, $this->db->error));')
               iw ('throw new DAOException ("Prepared statement failed.", $this->db->error);')
            iw ('}')
            iw ('$stmt->bindParam ("%s", %s);' % (
               ''.join ([self.interpolateType (c.getDataType ()) for c in insertColumns]),
               ', '.join (['$data ["%s"]' % c.getName () for c in insertColumns])))
            iw ('$stmt->execute ();')
            iw ('if ($stmt->affected_rows != 1) {')
            with iw:
               iw ('throw new DAOException ("Couldn\'t insert new record in table \\"%s\\"", $stmt->error, $stmt->affected_rows);' % tableSchema.getName ())
            iw ('}')

            iw ('return $this->db->insert_id;')
         iw ('}')
         iw ()

         # Print a save (update) method.
         # This method will be empty if there is no primary key,
         # and can be implemented by subclasses if necessary.
         iw ('public function save ($data) {')
         if primaryKey is not None:
            with iw:
               updateColumns = [c for c in tableSchema.getAllColumns () if c is not autoIncrementColumn]
               keyColumns = [tableSchema.getColumn (c) for c in primaryKey.getColumns ()]
               bindColumns = updateColumns + keyColumns

               statement = 'update %s set %s where %s' % (
                     tableSchema.getName (),
                     ', '.join (['%s = ?' % c.getName () for c in updateColumns]),
                     ' and '.join (['%s = ?' % c.getName () for c in keyColumns]))
               
               iw ('$stmt = $this->db->prepare ("%s");' % statement)
               iw ('if ($stmt == FALSE) {')
               with iw:
                  iw ('$this->log->logFatal (sprintf ("<%%s::%%s> Prepared statement failed: %%s", __CLASS__, __FUNCTION__, $this->db->error));')
                  iw ('throw new DAOException ("Prepared statement failed.", $this->db->error);')
               iw ('}')
               iw ('$stmt->bind_param ("%s", %s);' % (
                  ''.join ([self.interpolateType (c.getDataType ()) for c in bindColumns]),
                  ', '.join (['$data ["%s"]' % c.getName () for c in bindColumns])))

               iw ('$stmt->execute ();')
               iw ('if ($stmt->affected_rows != 1) {')
               with iw:
                  iw ('throw new DAOException ("Couldn\'t save existing record in table \\"%s\\"", $stmt->error, $stmt->affected_rows);' % tableSchema.getName ())

               iw ('}')

         else:
            with iw:
               iw.printLines (NO_PRIMARY_KEY_SAVE_NOTE)

         iw ('}')
         iw ()
         
         # Print a delete method.
         # This method will be empty if there is no primary key,
         # and can be implemented by subclasses if necessary.
         iw ('public function delete ($data) {')
         if primaryKey is not None:
            with iw:
               keyColumns = [tableSchema.getColumn (c) for c in primaryKey.getColumns ()]

               statement = 'delete from %s where %s' % (
                     tableSchema.getName (),
                     ' and '.join (['%s = ?' % c.getName () for c in keyColumns]))
               
               iw ('$stmt = $this->db->prepare ("%s");' % statement)
               iw ('if ($stmt == FALSE) {')
               with iw:
                  iw ('$this->log->logFatal (sprintf ("<%%s::%%s> Prepared statement failed: %%s", __CLASS__, __FUNCTION__, $this->db->error));')
                  iw ('throw new DAOException ("Prepared statement failed.", $this->db->error);')
               iw ('}')
               iw ('$stmt->bind_param ("%s", %s);' % (
                  ''.join ([self.interpolateType (c.getDataType ()) for c in keyColumns]),
                  ', '.join (['$data ["%s"]' % c.getName () for c in keyColumns])))

               iw ('$stmt->execute ();')
               iw ('if ($stmt->affected_rows != 1) {')
               with iw:
                  iw ('throw new DAOException ("Couldn\'t delete record in table \\"%s\\"", $stmt->error, $stmt->affected_rows);' % tableSchema.getName ())

               iw ('}')

         else:
            with iw:
               iw.printLines (NO_PRIMARY_KEY_DELETE_NOTE)

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

      daoExceptionSourcePath = getPackageFilename (os.path.join (
         MYSQLI_FILES_DIR, DAO_EXCEPTION_FILENAME))

      shutil.copy (daoExceptionSourcePath, daoExceptionPath)
      
   
   def generateLoggingClass (self, outputPath, overwrite = False):
      """
         Generates a class file named Logger.php.
         This class is used by the DAO objects to log reads and writes.
      """
      
      loggerPath = os.path.join (outputPath, LOGGER_FILENAME)
      
      if os.path.exists (loggerPath) and not overwrite:
         printOverwriteWarning (loggerPath)
         return False

      loggerSourcePath = getPackageFilename (os.path.join (
         MYSQLI_FILES_DIR, LOGGER_FILENAME))

      shutil.copy (loggerSourcePath, loggerPath)


   def interpolateType (self, datatype):
      """
         Returns a character for mysqli_stmt_bind_param corresponding
         to the given datatype.

         Types that do not appear here are currently not supported
         by this generator.
      """
      
      if datatype.upper () in ['CHAR', 'VARCHAR', 'TINYTEXT', 'TEXT', 'MEDIUMTEXT', 'LONGTEXT',
            'DATE', 'DATETIME', 'TIMESTAMP', 'TIME', 'ENUM', 'SET', 'DECIMAL']:
         return 's'

      elif datatype.upper () in ['INT', 'TINYINT', 'SMALLINT', 'MEDIUMINT', 'BIGINT', 'YEAR']:
         return 'i'

      elif datatype.upper () in ['FLOAT', 'DOUBLE']:
         return 'd'

      else:
         raise MySQLiGeneratorException (
               "Unsupported SQL datatype in mysqli interpolation: '%s'." % datatype)


#--------------------------------------------------------------------
# Register this generator in PyDAO.Mapping.
#
registerGenerator ('PHP/MySQLi', MySQLiGenerator)
