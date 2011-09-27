#
# Mapping
#
# Controls the DAO code generation process.
#
# Provides a mechanism by which to map database, table
# and column names to friendly names to be used in
# generated code.
#
# (c) September 2011 Lee Supe (lain_proliant)
# Released under the GNU General Public License, version 3.
#

from abc import ABCMeta
from collections import namedtuple
from PyDAOException import *
from ClassLoader import *

import xml.sax

#--------------------------------------------------------------------
class MappingException (PyDAOException): pass

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
class MappingParser (xml.sax.ContentHandler):
   """
      An object which controls the DAO code generation process.

      Provides a mechanism by which to map database, table,
      and column names to friendly names for generated code.

      The mapping object is typically loaded from an XML
      mapping definition file (*.pydao.xml).
   """

   def __init__ (self):
      """
         Initializes a Mapping controller object.
      """

      self._databaseCycleInit ()

   
   def _databaseCycleInit (self):
      """
         Re-initializes variables used to process each database element.
      """
      
      self.schematizer = None
      self.generator = None
      self.schema = None
      self.generateAllTables = False
      self.databaseAlias = None
      self.outputPath = '.'
      
      self.tableMapping = {}

      self.stack = []


   def getSchematizer (self):
      """
         Fetches the schematizer object.
         This object does not exist until a <schematizer/>
         element is parsed.
      """

      return self.schematizer
   

   def getGenerator (self):
      """
         Fetches the generator object.
      """

      return self.generator


   def getSchema (self):
      """
         Fetches the current database schema.
      """

      return self.schema


   def startDocument (self):
      """
         SAX Event Handler: Start of Document.
      """

      # Nothing to do for now.
      pass


   def endDocument (self):
      """
         SAX Event Handler: End of Document.
      """

      # Nothing to do for now.
      pass


   def startElement (self, name, attrs):
      """
         SAX Event Handler: Start of Element.
      """
      
      lname = name.lower ()
      stack.push (lname)

      if not stack:
         if name.lower () == 'mapping':
            self.startMapping (name, attrs) 

         else:
            raise MappingException, "Invalid document element, must be 'mapping'."

      if lname == 'database':
         self.startDatabase (name, attrs)

      elif lname == 'schematizer':
         self.startSchematizer (name, attrs)

      elif lname == 'generator':
         self.startGenerator (name, attrs)

      elif lname == 'alltables':
         self.startAlltables (name, attrs)

      elif lname == 'table':
         self.startTable (name, attrs)

      else:
         raise MappingException, "Unrecognized document element: '%s'." % name


   def endElement (self, name):
      """
         SAX Event Handler: End of Element.
      """
      
      if name.lower () == 'database':
         self.endDatabase (name)


   def startMapping (name, attrs):
      """
         Called upon a <mapping/> element. 
      """
      
      # Nothing to do for now.
      pass


   def startSchematizer (name, attrs):
      """
         Called upon a <schematizer/> element.
         Must be contained within <database/>
      """
      
      if attrs.has_key ('name'):
         className = attrs ['name']

      else:
         raise MappingException, "Missing required attribute 'name'."


      cl = ClassLoader ()
      
      self.schematizerClass = cl.loadClass (className)


   def startDatabase (name, attrs):
      """
         Called upon a <database/> element.
         Must be contained within <mapping/>

         Generates a DatabaseSchema object for the database.
         When the <database/> element ends, code will be generated.
      """
      
      self._databaseCycleInit ()

      if attrs.has_key ('as'):
         self.databaseAlias = attrs ['as']

      if attrs.has_key ('output')
         self.outputPath = attrs ['output']


   def endDatabase (name):
      """
         Called upon the closing of a <database/> element.
         
         This is the step at which code generation occurs.
         This method will throw an ImportError if the given
         schematizer or generator classes cannot be loaded.
      """

      # LRS-TODO: Implement this method.
      pass

