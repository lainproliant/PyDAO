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

from collections import namedtuple
from PyDAOException import *

#--------------------------------------------------------------------
class MappingException (PyDAOException): pass

#--------------------------------------------------------------------
class Mapping (object):
   """
      An object which controls the DAO code generation process.

      Provides a mechanism by which to map database, table,
      and column names to friendly names for generated code.

      The mapping object is typically loaded from an XML
      mapping definition file (*.pydao.xml).
   """

   DatabaseMapping = namedtuple ("DatabaseMapping",
         ["mappedName", "tableMappings"])
   TableMapping = namedtuple ("TableMapping",
         ["mappedName", "columnMappings", "indexMappings"])
   TableMapping = namedtuple ("ColumnMapping",
         ["mappedName"])
   IndexMapping = namedtuple ("IndexMapping",
         ["mappedName"])


   def __init__ (self):
      """
         Initializes a Mapping controller object.
      """

      self.schematizerName = None
      self.generatorName = None
      self.databaseName = None
      
      # A list of DatabaseMapping tuples.
      self.nameMapping = {}

   

