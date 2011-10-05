#
# Mapping
#
# Controls the DAO code generation process.
#
# Provides a mechanism by which to map database, table
# and column names to friendly names to be used in
# generated code.
#
# Also provides a global mapping scheme for schematizers,
# generators, and connection factories.
#
# (c) September 2011 Lee Supe (lain_proliant)
# Released under the GNU General Public License, version 3.
#

from abc import ABCMeta
from collections import namedtuple, OrderedDict
from PyDAOException import *
from ClassLoader import *

import Schematizers
import Generators

import xml.dom.minidom
import re

# A regular expression pattern matching valid table and alias names.
RE_VALID_NAME = "[A-Za-z_][A-Za-z0-9_]*"

#--------------------------------------------------------------------
class MappingException (PyDAOException): pass


#--------------------------------------------------------------------
def interpretParameter (paramElement):
   """
      Interprets the contents of a 'param' element.  Such element 
      must contain a 'name' and 'value' attribute.  These values
      are returned as a 2-tuple.

      If any of the required attributes are missing,
      a MappingException is thrown.
   """

   if not paramElement.hasAttribute ('name'):
      raise MappingException, "Missing required attribute 'name' in 'param'."

   if not paramElement.hasAttribute ('value'):
      raise MappingException, "Missing required attribute 'value' in 'param'."
   
   return (
         paramElement.getAttribute ('name'),
         paramElement.getAttribute ('value'))


#--------------------------------------------------------------------
class NamedObject (object):
   """
      An object with a named representation that can be mapped
      to another name.
   """

   __metaclass__ = ABCMeta
   
   def __init__ (self, name, alias = None):
      """
         Initializes a mapped object.
      """

      self.name = name
      self.alias = alias


   def getName (self):
      """
         Gets the name of the object.
      """

      return self.name

   
   def getAlias (self):
      """
         Gets the mapped name of the object, or simply
         the name if there is no mapping.
      """

      if self.alias is not None:
         return self.alias

      else:
         return self.getName ()


   def setAlias (self, alias):
      """
         Sets the mapped name.
         Provide None to disable the mapped name.
      """

      self.alias = alias


#--------------------------------------------------------------------
class TableMappingJob (object):
   """
      Keeps track of the mappings for tables, columns, and indexes.

      Attempts to apply this mapping to the DatabaseSchema before
      code generation occurs.
   """
   
   def __init__ (self, databaseJob = None):
      """
         Initializes a TableMappingJob.
      """

      self.databaseJob = databaseJob
      self.name = None
      self.alias = None
      self.columnMapping = OrderedDict ()
      self.indexMapping = OrderedDict ()
      self.allColumns = True
      self.allColumnsExplicit = False
      self.allIndexes = False


   @staticmethod
   def fromXML (tableElement, databaseJob):
      """
         Creates a TableMappingJob from the given XML DOM element.
      """
      
      tableJob = TableMappingJob (databaseJob)
      
      if tableElement.hasAttribute ('name'):
         name = tableElement.getAttribute ('name')
         
         if not re.match (RE_VALID_NAME, name):
            raise MappingException, "Invalid name: '%s'." % name

         tableJob.name = name
      
      else:
         raise MappingException, "Missing required attribute 'name' in 'table'."

      if tableElement.hasAttribute ('as'):
         alias = tableElement.getAttribute ('as')

         if not re.match (RE_VALID_NAME, alias):
            raise MappingException, "Invalid alias: '%s'." % alias

         tableJob.alias = alias

      childElements = [e for e in tableElement.childNodes if \
            e.nodeType == Node.ELEMENT_NODE]

      for element in childElements:
         if element.tagName == 'index':      # Interpret index mappings.

            if not element.hasAttribute ('name'):
               raise MappingException, "Missing required attribute 'name' in 'index'."

            indexName = element.getAttribute ('name')
            indexAlias = None

            if not re.match (RE_VALID_NAME, indexName):
               raise MappingException, "Invalid name: '%s'." % indexName

            if element.hasAttribute ('as'):
               indexAlias = element.getAttribute ('as')

            if not re.match (RE_VALID_NAME, indexAlias):
               raise MappingException, "Invalid alias: '%s'." % indexAlias

            tableJob.mapIndex (indexName, indexAlias)
         
         if element.tagName == 'column':     # Interpret column mappings.

            if not element.hasAttribute ('name'):
               raise MappingException, "Missing required attribute 'name' in 'column'."

            columnName = element.getAttribute ('name')
            columnAlias = None

            if not re.match (RE_VALID_NAME, columnName):
               raise MappingException, "Invalid name: '%s'." % columnName

            if element.hasAttribute ('as'):
               columnAlias = element.getAttribute ('as')

            if not re.match (RE_VALID_NAME, columnAlias):
               raise MappingException, "Invalid alias: '%s'." % columnAlias

            tableJob.mapColumn (columnName, columnAlias)

         if element.tagName == 'allcolumns':  # Interpret allcolumns mapping.
            tableJob.mapAllColumns ()

         if element.tagName == 'allindexes':  # Interpret allindexes mapping.
            tableJob.mapAllIndexes ()

   
   def mapColumn (self, columnName, columnAlias = None):
      """
         Adds a column to include in the mapping, and optionally
         its alias.

         By default, if no columns are included in the mapping
         explicitly, all columns will be included.  If any
         columns are specified, only those columns will be
         included.  To override this behavior, specify
         <allcolumns/> in the table mapping XML or call
         mapAllColumns ().
      """
      
      if not self.columnMapping and not self.allColumnsExplicit:
         self.allColumns = False

      self.columnMapping [columnName] = columnAlias


   def mapIndex (self, indexName, indexAlias = None):
      """
         Adds an index to include in the mapping, and optionally
         its alias.

         By default, no indexes are included in the mapping.
         Only the specified indexes are included, unless
         <allindexes/> is specifed in the table mapping XML
         or mapAllIndexes () is called, in which case all indexes
         are included.
      """
      
      self.indexMapping [indexName] = indexAlias


   def mapAllColumns (self):
      """
         Specifies that all columns in the table schema
         should be mapped in code generation.

         Additional mappings may be specified to provide
         column aliases.
      """

      self.allColumns = True
      self.allColumnsExplicit = True


   def applyMapping (self, schema):
      """
         Apply this table mapping to the given database schema.

         Sets the aliases for this table and each of the table's
         columns and indexes.  Also validates that the contents
         of the mapping exist in the schema.
      """
      
      tableSchema = schema.getTable (self.name)

      if tableSchema is None:
         raise MappingException, "The given database '%s' does not contain a table named '%s'." % (schema.getName (), self.name)

      if self.alias is not None:
         tableSchema.setAlias (self.alias)

      for columnName in self.columnMapping:
         columnSchema = tableSchema.getColumn (columnName)
         columnAlias = self.columnMapping [columnName]

         if columnSchema is None:
            raise MappingException, "The given table '%s.%s' does not contain a column named '%s'." % (schema.getName (), tableSchema.getName (), columnName)

         if columnAlias is not None:
            columnSchema.setAlias (columnAlias)
          

#--------------------------------------------------------------------
class DatabaseJob (object):
   """
      Represents a DAO generation job for a particular database.
   """

   def __init__ (self, mappingJob = None):
      """
         Initializes a DatabaseJob. 
      """

      self.mappingJob = mappingJob
      self.schematizer = None
      self.generator = None
      self.schema = None

      self.tableMapping = OrderedDict ()

      self.allTables = False
      self.allTablesExplicit = False

      self.compiled = False
      self.complete = False


   @staticmethod
   def fromXML (databaseElement, mappingJob):
      """
         Creates a DatabaseJob from the given XML element
         within the given mapping job.
      """

      databaseJob = DatabaseJob (mappingJob)

      childElements = [e for e in databaseElement.childNodes if \
            e.nodeType == Node.ELEMENT_NODE]

      for element in childElements:
         if element.tagName == 'schema':
            databaseJob.interpretSchematizer (element)
         
         elif element.tagName == 'generate':
            databaseJob.interpretGenerator (element)
         
         elif element.tagName == 'alltables':
            databaseJob.mapAllTables ()

         elif element.tagName == 'table':
            databaseJob.interpretTable (element)


   def interpretSchematizer (self, schemaElement):
      """
         Interprets a schema element.  Specifies and provides
         parameters for the schematizer.
      """
      
      schematizerType = None
      params = OrderedDict ()

      if schemaElement.hasAttribute ('xml'):
         schematizerType = 'XML'
         params ['inputFile'] = schemaElement.getAttribute ('xml')

      elif schemaElement.hasAttribute ('type'):
         schematizerType = schemaElement.getAttribute ('type')

      else:
         raise MappingException, "No schema source type provided in 'schema' element."

      schematizerClass = getSchematizerClass (schematizerType)

      if schematizerClass is None:
         raise MappingException, "No schematizer registered for '%s'." % schematizerType

      childElements = [e for e in schemaElement.childNodes if \
            e.nodeType == Node.ELEMENT_NODE]

      for element in childElements:
         if element.tagName == 'param':
            name, value = interpretParam (element)
            params [name] = value

         else:
            raise MappingException, "Unexpected element '%s' in 'schema'." % element.tagName

      

   def interpretTable (self, tableElement):
      """
         Interprets a table element.  Passes the element
         into TableMappingJob.fromXML () and adds to table
         mappings.
      """
      
      tableJob = TableMappingJob.fromXML (tableElement, self)
      self.mapTable (tableJob)
   

   def mapTable (self, tableJob):
      """
         Adds the given table mapping job to this job.
      """

      if not self.tableMapping and not self.allTablesExplicit:
         self.allTables = False

      self.tableMapping [tableJob.name] = tableJob


   def mapAllTables (self):
      """
         Specifies that all tables in the database schema
         should be mapped in code generation

         Additional mappings may be specified to provide
         table, column, and index aliases.
      """

      self.allTables = True
      self.allTablesExplicit = True


   def compile (self):
      """
         Compile all of the pieces necessary for code generation.

         Initializes the schematizer, then fetches the schema.
         Then, applies any mapping aliases to the schema and
         prepares the generator for code generation.
      """



#--------------------------------------------------------------------
class MappingJob (object):
   """
      A controller object for the DAO class generation process.
   """

   def __init__ (self):
      """
         Initializes a MappingJob.
      """
      
      self.document = None
      self.databaseJobs = []
  

   @staticmethod
   def fromXML (document):
      """
         Loads a mapping process from XML DOM.
      """
      
      mappingJob = MappingJob ()

      if document.documentElement.tagName != 'mapping':
         raise MappingException, "Invalid document element, must be 'mapping'."
     
      childElements = [e for e in document.documentElement.childNodes if \
            e.nodeType == Node.ELEMENT_NODE]

      for element in childElements:
         if element.tagName == 'import':
            mappingJob.interpretImport (element)

         elif element.tagName == 'database':
            databaseJob = DatabaseJob.fromXML (mappingJob, element)
            mappingJob.addJob (databaseJob)

         else:
            raise MappingException, "Unexpected element '%s' in 'mapping'" % element.tagName

      return mappingJob


   def interpretImport (self, element):
      """
         Interprets an import element, importing the given python class.
      """
         
      className = None

      if element.hasAttribute ('class'):
         className = element.getAttribute ('class')

      else:
         raise MappingException, "Missing required attribute 'class' in 'import'."
      
      cl = ClassLoader ()
      cl.loadClass (className)


   def runJob (self):
      """
         Runs the mapping job.
      """

      for databaseJob in self.databaseJobs:
         databaseJob.runJob ()


