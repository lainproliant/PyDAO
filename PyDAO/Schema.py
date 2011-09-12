#
# Schema
#
# A set of classes representing a relational database schema.
#
# Part of the PyDAO package.
#
# (c) August 2011 Lee Supe (lain_proliant)
# Released under the GNU General Public License, version 3.
#

from collections import defaultdict
from PyDAOException import *

#--------------------------------------------------------------------
class SchemaException (PyDAOException): pass
class DatabaseSchemaException (SchemaException): pass
class TableSchemaException (SchemaException): pass
class ColumnSchemaException (SchemaException): pass
class IndexSchemaException (SchemaException): pass

#--------------------------------------------------------------------
class DatabaseSchema (object):
   """
      Abstract representation of a relational database schema.
   """

   def __init__ (self, databaseName):
      """
         Initializes a DatabaseSchema.
      """

      self.name = databaseName
      self.tables = []

      self.tableMap = {}

   
   def getName (self):
      """
         Gets the name of this database.
      """

      return self.name


   def addTable (self, table):
      """
         Adds the given table to the database.
      """
      
      if self.hasTable (table.getName ()):
         raise DatabaseSchemaException ('A table by this name already exists: "%s"' % table.name)

      self.tables.append (table)
      self.tableMap [table.getName ()] = table

   
   def getTable (self, tableName):
      """
         Gets the named table if it exists.
      """

      if self.hasTable (tableName):
         return self.tableMap [tableName]

      else:
         return None


   def getAllTables (self):
      """
         Gets all of the tables in the database.
      """

      return self.tables


   def getTableNames (self):
      """
         Gets all of the names of the tables in the database.
      """

      return self.tableMap.keys ()


   def hasTable (self, tableName):
      """
         Gets whether the database contains the named table.
      """

      return self.tableMap.has_key (tableName)


   def removeTable (self, tableName):
      """
         Removes the given named table if it exists.
      """

      if self.hasTable (tableName):
         table = getTable (tableName)
         del tableMap [tableName]
         self.tables.remove (table)

   
   def __repr__ (self):
      s = '<database name="%s">\n' % self.getName ()
      tableReprs = []

      for table in self.getAllTables ():
         tableReprs.append (str (table))

      for reprStr in tableReprs:
         for line in reprStr.splitlines (True):
            s += '\t' + line

      s += '</database>'
      return s


#--------------------------------------------------------------------
class TableSchema (object):
   """
      An abstract representation of a table in a database.
   """
   
   def __init__ (self, tableName):
      """
         Initializes a TableSchema.
      """
   
      # The name of the table.
      self.tableName = tableName

      # A sequential list of the columns in the table.
      self.columns = []

      # A list of the indexes in the table.
      self.indexes = []

      # An list of zero or more columns in the table's primary key.
      self.primaryKey = []
      
      # A map of column names to columns, for fast lookups.
      # columnName: col
      self.columnMap = {}

      # A map of index names to indexes, for fast lookups.
      # indexName: index
      self.indexMap = {}

   
   def getName (self):
      """
         Returns the name of this table.
      """

      return self.tableName


   def addColumn (self, column):
      """
         Adds the given column to the table.
      """
      
      if self.hasColumn (column.getName ()):
         raise TableSchemaException ('A column by the name "%s" already exists in the table "%s"' % (column.getName (), table.getName ()))

      self.columns.append (column)
      self.columnMap [column.name] = column


   def getColumn (self, columnName):
      """
         Gets the named column if it exists.
      """

      if self.hasColumn (columnName):
         return self.columnMap [columnName]
      else:
         return None


   def getAllColumns (self):
      """
         Gets a list of all columns in the table.
      """

      return self.columns


   def getColumnNames (self):
      """
         Gets a list of all column names in the table.
      """

      return self.columnMap.keys ()


   def hasColumn (self, columnName):
      """
         Checks if the table contains the named column.
      """
      
      return self.columnMap.has_key (columnName)


   def removeColumn (self, columnName):
      """
         Removes the given named column if it exists.
      """

      if self.hasColumn (columnName):
         column = self.getColumn (columnName)
         del self.columnMap [columnName]
         self.columns.remove (column)

   
   def addIndex (self, index):
      """
         Adds the given index to the table.
      """

      self.indexes.append (index)
      self.indexMap [index.name] = index

   
   def getIndex (self, indexName):
      """
         Gets the named index if it exists.
      """

      if self.hasIndex (indexName):
         return self.indexMap [indexName]
      else:
         return None


   def getAllIndexes (self):
      """
         Gets a list of all indexes.
      """

      return self.indexes


   def getIndexNames (self):
      """
         Gets a list of all index names.
      """

      return self.indexMap.keys ()


   def hasIndex (self, indexName):
      """
         Checks if the table contains the named index.
      """

      return self.indexMap.has_key (indexName)


   def removeIndex (self, indexName):
      """
         Removes the given named index if it exists.
      """
      
      if self.hasIndex (indexName):
         index = self.getIndex (indexName)
         del self.indexMap [indexName]
         self.indexes.remove (index)


   def __repr__ (self):
      s = '<table name="%s">\n' % self.getName ()
      childReprs = []
      
      for column in self.getAllColumns ():
         childReprs.append (str (column))
      
      childReprs.append ('\n')

      for index in self.getAllIndexes ():
         childReprs.append (str (index)) 

      for reprStr in childReprs:
         for line in reprStr.splitlines (True):
            s += '\t' + line

      s += '</table>\n'
      return s


#--------------------------------------------------------------------
class ColumnSchema (object):
   """
      An abstract representation of a column in a database table.
   """

   def __init__ (self, name, datatype, isNullable, extra):
      """
         Initializes a ColumnSchema.
      """

      self.name = name
      self.datatype = datatype
   
      if isNullable == 'YES':
         self.isNullableVal = True

      elif isNullable == 'NO':
         self.isNullableVal = False

      else:
         raise ColumnSchemaException ('An unexpected value was encountered for field: isNullable = "%s"' % isNullable)

      self.extra = extra

   
   def getName (self):
      """
         Gets the name of this column.
      """

      return self.name


   def getDataType (self):
      """
         Gets the data type of this column.
      """

      return self.datatype


   def isNullable (self):
      """
         Returns whether the column is nullable.
      """

      return self.isNullableVal
   

   def getExtra (self):
      """
         Get extra properties associated with the table.
      """

      return self.extra


   def __repr__ (self):
      s = '<column name="%s" type="%s" nullable="%s"/>\n' % (
            self.getName (),
            self.getDataType (),
            self.isNullable ())
   
      return s


#--------------------------------------------------------------------
class IndexSchema (object):
   """
      An abstract representation of a named index on a table,
      composed of columns within the table.

      In practice this will include the primary key, indexed columns,
      unique indexes, composite keys/indexes, and foreign keys. 
   """

   def __init__ (self, indexName, isUnique):
      """
         Initializes an Index.
      """

      self.name = indexName;
      self.isUniqueVal = not isUnique;

      self.columns = []

   
   def addColumn (self, columnName):
      """
         Adds the named column to the index.
      """
      
      self.columns.append (columnName)


   def getColumns (self):
      """
         Gets a list of all column names in this index.
      """

      return self.columns


   def getName (self):
      """
         Gets the name of this index.
      """

      return self.name


   def isUnique (self):
      """
         Get the index type.  The representation of index
         type as recorded from information_schema may differ
         between schematizers.
      """

      return self.isUniqueVal


   def __repr__ (self):
      s = '<index name="%s" unique="%s">\n' % (
            self.getName (),
            str (self.isUnique ()))
      
      for column in self.getColumns ():
         s += '\t<column>%s</column>\n' % column

      s += '</index>\n'

      return s

