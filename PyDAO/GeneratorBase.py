#
# GeneratorBase
#
# An abstract base class for generators.
#
# (c) September 2011 Lee Supe (lain_proliant)
# Released under the GNU General Public License, version 3.
#

from abc import ABCMeta, abstractmethod

class GeneratorBase (object):
   """
      Abstract base class for Generators.

      A generator is an object which accepts an abstract
      DatabaseSchema representation and outputs source code
      with which to access the database using a particular
      language and database access system.

      Generators also accept a Mapping object, which is used
      to control the code generation process.
   """
   
   __metaclass__ = ABCMeta
  
   @abstractmethod
   def generate (self, schema, outputDir = '.', overwrite = False):
      """
         Writes classes to various output files in the given
         directory, the current working directory by default.

         Generator implementations are at liberty to write
         whatever source files are necessary to represent
         an API to access a database with the given schema,
         so long as these files are written in the given
         output directory or subdirectories therein.

         Note that reflection can be used in the mapping XML
         to set arbitrary parameters on generators.  For more
         information, see the Mapping class documentation.

         This method is abstract and must be implemented
         by subclasses to generate code in the appropriate
         language for the appropriate toolkit/API.
      """

      pass

