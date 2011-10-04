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

#--------------------------------------------------------------------
# Default Mapping of Database Types to Schematizer class names.
# Schematizers can be added or replaced at runtime by calling
# PyDAO.Mapping.registerSchematizer ().

SchematizerMapping = {
      'MySQL':   PyDAO.Schematizer.MySQLSchematizer }


#--------------------------------------------------------------------
# Default Mapping of Languages to Generator class names.
# Generators can be added or replaced at runtime by calling
# PyDAO.Mapping.registerGenerator ().

GeneratorMapping = {
      'PHP':      PyDAO.Generators.PHP.MySQLiGenerator
      'xml':      PyDAO.Generators.SchemaGenerator
      }


#--------------------------------------------------------------------
class MappingException (PyDAOException): pass


#--------------------------------------------------------------------
def registerSchematizer (databaseType, className):
   """
      Registers a fully qualified class name with the given
      database type.

      Use this on module or class import to dynamically add new
      schematizers which can be used in mapping.

      databaseType: Should be specified as the type of database
         for which schematizer support is to be added, e.g.:
         Oracle, MSSQL, PostgreSQL, SQLite, etc.

      className: Should be specified as a fully qualified class name,
         e.g.:
         LeeDAO.Schematizers.PostgreSQLSchematizer,
         LeeDAO.Schematizers.MSSQLSchematizer, etc.
   """

   SchematizerMapping [databaseType] = className


#--------------------------------------------------------------------
def registerGenerator (language, className):
   """
      Registers a fully qualified class name with the given
      programming language or language/toolkit pair.

      Use this on module or class import to dynamically add new
      generators which can be used in code generation.

      language: Should be specified as the name of the language
         or language/toolkit pair for which generation is supported,
         e.g.:
         Perl, Perl/DBI, C++, Python/MySQLdb, C#, etc.

      className: Should be specified as a fully qualified class name,
         e.g.:
         LeeDAO.Generators.CXX.Connector,
         LeeDAO.Generators.Java.JDBC,
         LeeDAO.Generators.Python.MySQLdb, etc.
   """

   GeneratorMapping [language] = className


#--------------------------------------------------------------------
def registerConnectionFactory (databaseType, className):
   """
      Registers a fully qualified class name with the given
      database type.

      Use this on module or class import to dynamically add
      new connection factories.
   """
   
   ConnectionFactoryMapping [databaseType] = className


#--------------------------------------------------------------------
def loadSchematizer (databaseType, *args, **kwargs):
   """
      Loads a schematizer object with the given parameters.
   """

   cl = ClassLoader ()
   schematizerClass = cl.loadClass (SchematizerMapping [databaseType])
   return schematizerClass (*args, **kwargs)


#--------------------------------------------------------------------
def loadGenerator (language, *args, **kwargs):
   """
      Loads a generator object with the given parameters.
   """

   cl = ClassLoader ()
   generatorClass = cl.loadClass (GeneratorMapping [language])
   return generatorClass (*args, **kwargs)


#--------------------------------------------------------------------
class NamedObject (object):
   """
      An object with a named representation that can be mapped
      to another name.
   """

   __metaclass__ = ABCMeta
   
   def __init__ (self, name, mappedName = None):
      """
         Initializes a mapped object.
      """

      self.name = name
      self.mappedName = mappedName


   def getName (self):
      """
         Gets the name of the object.
      """

      return self.name

   
   def getMappedName (self):
      """
         Gets the mapped name of the object, or simply
         the name if there is no mapping.
      """

      if self.mappedName is not None:
         return self.mappedName

      else:
         return self.getName ()


   def setMappedName (self, mappedName):
      """
         Sets the mapped name.
         Provide None to disable the mapped name.
      """

      self.mappedName = mappedName


#--------------------------------------------------------------------
class TableMappingJob (object):
   """
      Keeps track of the mappings for tables, columns, and indexes.
   """
   
   def __init__ (self, databaseJob = None):
      """
         Initializes a TableMappingJob.
      """

      self.databaseJob = databaseJob
      self.name = None
      self.mappedName = None
      self.columnMapping = OrderedDict ()
      self.indexMapping = OrderedDict ()


   @staticmethod
   def fromXML (tableElement, databaseJob):
      """
         Creates a TableMappingJob from the given XML DOM element.
      """
      
      tableJob = TableMappingJob (databaseJob)
      
      if tableElement.hasAttribute ('name'):
      





        
   

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

      self.tableMappings = OrderedDict ()

      self.allTables = False


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
            databaseJob.allTables = True

         elif element.tagName == 'table':

         

         
      


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
            raise MappingException, "Unrecognized element: '%s'" % element.tagName
   

   def interpretImport (self, element):
      """
         Interprets an import tag, importing the given python class.
      """
         
      className = None

      if element.hasAttribute ('class'):
         className = element.getAttribute ('class')

      else:
         raise MappingException, "'import' element missing required 'class' attribute."
      
      cl = ClassLoader ()
      cl.loadClass (className)


   def runJob (self):
      """
         Runs the mapping job.
      """

      for databaseJob in self.databaseJobs:
         databaseJob.runJob ()


