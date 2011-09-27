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
   
   def __init__ (self, schema, mapping):
      """
         Initializes the abstract portions of a Generator.
      """

      


