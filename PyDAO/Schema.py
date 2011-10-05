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

from PyDAOException import *
from Mapping import NamedObject
from IndentWriter import *

#--------------------------------------------------------------------
class SchemaException (PyDAOException): pass
class DatabaseSchemaException (SchemaException): pass
class TableSchemaException (SchemaException): pass
class ColumnSchemaException (SchemaException): pass
class IndexSchemaException (SchemaException): pass

#--------------------------------------------------------------------
class DatabaseSchema (NamedObject):
   """
      Abstract representation of a relational database schema.
   """

   def __init__ (self, databaseName):
      """
         Initializes a DatabaseSchema.
      """
      
      NamedObject.__init__ (self, databaseName)

      self.tables = []

      self.tableMap = {}

   
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
      sb = IndentStringBuilder ()

      sb ('<database name="%s">' % self.getName ())
      
      with sb:
         for table in self.getAllTables ():
            sb.printLines (str (table))
            sb.newline ()

      sb ('</database>')

      return str (sb)


#--------------------------------------------------------------------
class TableSchema (NamedObject):
   """
      An abstract representation of a table in a database.
   """
   
   def __init__ (self, tableName):
      """
         Initializes a TableSchema.
      """
   
      NamedObject.__init__ (self, tableName)

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
      sb = IndentStringBuilder ()
      
      sb ('<table name="%s">' % self.getName ())
      
      with sb:
         for column in self.getAllColumns ():
            sb.printLines (str (column))
      
      sb.newline ()
   
      with sb:
         for index in self.getAllIndexes ():
            sb.printLines (str (index))

      sb ('</table>')
      
      return str (sb)


#--------------------------------------------------------------------
class ColumnSchema (NamedObject):
   """
      An abstract representation of a column in a database table.
   """

   def __init__ (self, name, datatype, isNullable, extra):
      """
         Initializes a ColumnSchema.
      """

      NamedObject.__init__ (self, name)

      self.datatype = datatype
   
      if isNullable == 'YES':
         self.isNullableVal = True

      elif isNullable == 'NO':
         self.isNullableVal = False

      else:
         raise ColumnSchemaException ('An unexpected value was encountered for field: isNullable = "%s"' % isNullable)

      self.extra = extra

   
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
class IndexSchema (NamedObject):
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

      self.name = indexName
      self.isUniqueVal = not isUnique
      self.constraint = None

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


   def getConstraint (self):
      """
         Fetch the constraint on this index, or None
         if there is no constraint.
      """

      return self.constraint


   def setConstraint (self, constraint):
      """
         Set the constraint on this index.
      """

      self.constraint = constraint


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
      sb = IndentStringBuilder ()
      
      sb ('<index name="%s" unique="%s">' % (
            self.getName (),
            str (self.isUnique ())))
      
      with sb:
         for column in self.getColumns ():
            sb ('<column name="%s"/>' % column)
   
      sb ('</index>')

      return str (sb)


#--------------------------------------------------------------------
class Constraint (object):
   """
      An abstract class for constraints.

      In PyDAO, constraints are properties of indexes which allow the 
      DAO generators to understand the nature of the index.

      Constraints allow the DAO generators to make informed decisions
      regarding what type and how many parameters to return from
      generated methods, and what sorts of exceptions to expect.
   """
   
   def __init__ (self, constraintType):
      """
         Initializes an abstract Constraint.
      """

      self.constraintType = constraintType
      self.columns = []
   
   
   def addColumn (self, columnName):
      """
         Adds the named column to the constraint.
      """

      self.columns.append (columnName)


   def getColumns (self):
      """
         Gets a list of all column names in this constraint.
      """
      
      return self.columns


   def getType ():
      """
         Gets the type of the constraint.
      """
      return self.constraintType


#--------------------------------------------------------------------
class UniqueConstraint (Constraint):
   """
      An object representing a unique key constraint.
   """

   def __init__ (self):
      """
         Initializes a UniqueConstraint.
      """

      Constraint.__init__ (self, "UNIQUE")


#--------------------------------------------------------------------
class PrimaryKeyConstraint (Constraint):
   """
      An object representing a primary key constraint.
   """

   def __init__ (self):
      """
         Initializes a PrimaryKeyConstraint.
      """

      Constraint.__init__ (self, "PRIMARY_KEY")


#--------------------------------------------------------------------
class ForeignKeyConstraint (Constraint):
   """
      A object representing a foreign key constraint.

      Supports multi-column foreign keys and foreign keys
      into tables in different databases.
   """

   def __init__ (self, tableName, databaseName = None):
      """
         Initializes a ForeignKeyConstraint.
      """

      Constraint.__init__ (self, "FOREIGN_KEY")
      
      self.columnMap = {}
      self.tableName = tableName
      self.databaseName = databaseName


   def mapColumn (self, column, foreignColumn):
      """
         Maps the given local column to the given foreign column.
      """

      self.columnMap [column] = foreignColumn


   def getMapping (self, column):
      """
         Gets the foreign mapping for the given column,
         or None if no mapping exists.
      """
   
      if self.columnMap.has_key (column):
         return self.columnMap [column]

      else:
         return None


