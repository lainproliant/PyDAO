#
# MySQL Schematizer
#
# Interprets the given MySQL database as an abstract
# DatabaseSchema.
#
# Uses MySQLdb connection objects.
#
# Part of the PyDAO package.
#
# (c) August 2011 Lee Supe (lain_proliant)
# Released under the GNU General Public License, version 3.
#

from PyDAO.SchematizerException import *
from PyDAO.SchematizerBase import *
from PyDAO.Schema import *

#--------------------------------------------------------------------
class MySQLSchematizerException (SchematizerException): pass

#--------------------------------------------------------------------
class MySQLSchematizer (SchematizerBase):
   """
      Expresses a MySQL database as an abstract DatabaseSchema.

      Please note that this is a MySQL specific schematizer.
      It is advised that codegen modules for PyDAO use the
      DatabaseSchema object which is returned as a result of
      the Schematizer.schematize () method.
   """
   
   def __init__ (self, mysqlConnection, databaseName):
      """
         Initializes a MySQLSchematizer.

         mysqlConnection:
            An open MySQLdb connection object.  
            Must have read access to the `information_schema`
            database.

            This connection will be automatically closed
            once the object is cleaned up, or can be
            closed by calling closeConnection ().

         databaseName:
            The name of the database to be schematized.
      """
      
      self._mysqlConnection = mysqlConnection
      self.databaseName = databaseName


   def __del__ (self):
      """
         Cleans up a MySQLSchematizer upon deletion.
      """

      self.closeConnection ()

   
   def schematize (self):
      """
         Collects all possible information about the
         database, its tables, their columns and indexes
         into a DatabaseSchema object.
      """

      schema = DatabaseSchema (self.getDatabaseName ())

      tableNames = self.getTableNames ()

      for tableName in tableNames:
         schema.addTable (self.schematizeTable (tableName))

      return schema


   def schematizeTable (self, tableName):
      """
         Collects all possible information about the given table
         in the database and returns it 
      """

      tableSchema = TableSchema (tableName)
      
      columns = self.getTableColumns (tableName)
      indexes = self.getTableIndexes (tableName)

      for column in columns:
         tableSchema.addColumn (column)

      for index in indexes:
         tableSchema.addIndex (index)

      return tableSchema


   def schematizeColumn (self, columnName, dataType, isNullable, extra):
      """
         Compiles the information provided into a ColumnSchema object.
      """

      column = ColumnSchema (columnName, dataType, isNullable, extra)
      return column
   

   def schematizeTableIndex (self, tableName, indexName, nonUnique):
      """
         Compiles the information provided into an IndexSchema object
         and queries the information schema for all of the columns
         in the index.
      """
      
      index = IndexSchema (indexName, nonUnique)

      cursor = self.getConnection ().cursor ()

      cursor.execute ("""
         select column_name
            from information_schema.statistics

         where table_schema = %s and table_name = %s
            and index_name = %s

         order by seq_in_index
         """, (self.getDatabaseName (), tableName, indexName))

      results = cursor.fetchall ()

      columnNames = [row [0] for row in results]
      
      for columnName in columnNames:
         index.addColumn (columnName)

      return index

   
   def getConnection (self):
      """
         Fetches the MySQL database connection assigned
         to this schematizer.

         Override this method to define a different way
         to provide a connection for the schematizer.
      """

      return self._mysqlConnection


   def closeConnection (self):
      """
         A cleanup method called upon deletion.

         Closes the database connection.

         Override this method to define different behavior
         when the database would otherwise be closed.

         Users may close the connection early, but subsequent
         calls to schematizer methods will fail.
      """
   
      if self._mysqlConnection is not None:
         self._mysqlConnection.close ()
         self._mysqlConnection = None

   
   def getDatabaseName (self):
      return self.databaseName


   def getTableNames (self):
      """
         Retrieves the names of all of the tables in the database.
      """
      
      cursor = self.getConnection ().cursor ()

      cursor.execute ("""
         select table_name from information_schema.tables where
            table_schema = %s
         """, (self.databaseName,))

      results = cursor.fetchall ()
      cursor.close ()

      if not results:
         raise MySQLSchematizerException, 'The database "%s" does not exist or has no tables.' % self.databaseName

      tableNames = [row [0] for row in results]
      return tableNames


   def getTableColumns (self, tableName):
      """
         Fetch a list of all of the columns in the named table. 
      """
      
      columns = []

      cursor = self.getConnection ().cursor ()

      cursor.execute ("""
         select column_name, data_type, is_nullable, extra
            from information_schema.columns

         where table_schema = %s and table_name = %s
         """, (self.getDatabaseName (), tableName))

      results = cursor.fetchall ()
      cursor.close ()
      
      if not results:
         raise MySQLSchematizerException, 'The table "%s.%s" does not exist or has no columns.' % (databaseName, tableName)

      for row in results:
         column = self.schematizeColumn (*row)
         columns.append (column)

      return columns


   def getTableIndexes (self, tableName):
      """
         Fetch a list of all of the indexes on the named table.
      """

      indexes = []

      cursor = self.getConnection ().cursor ()

      cursor.execute ("""
         select distinct index_name, non_unique
            from information_schema.statistics

         where table_schema = %s and table_name = %s
         """, (self.getDatabaseName (), tableName))

      results = cursor.fetchall ()

      for row in results:
         index = self.schematizeTableIndex (tableName, *row)
         indexes.append (index)

      return indexes

   
   def getIndexConstraint (self, tableName, indexName):
      """
         Fetch the constraint associated with the given index,
         if there is one.
      """

      constraint = None

      cursor = self.getConnection ().cursor ()

      cursor.execute ("""
         select constraint_type
            from information_schema.table_constraints

         where 
            table_schema = %s and
            table_name = %s and
            constraint_name = %s
      """, (self.getDatabaseName (), tableName))

      result = cursor.fetchone ()

      if result is not None:
         constraintType = result [0]

      else:
         # There is no constraint associated with this index.
         return None

      

