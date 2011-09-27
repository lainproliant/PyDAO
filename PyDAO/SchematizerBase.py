#
# SchematizerBase
#
# An abstract base class for schematizers.
#
# (c) September 2011 Lee Supe (lain_proliant)
# Released under the GNU General Public License, version 3.
#

from abc import ABCMeta, abstractmethod

class SchematizerBase (object):
   """
      Abstract base class for Schematizers.

      A schematizer is an object which reads a database schema
      and represents its structure as a DatabaseSchema.
   """

   __metaclass__ = ABCMeta

   @abstractmethod
   def schematize (self):
      """
         Collects all possible information about the
         database, its tables, their columns and indexes
         into a DatabaseSchema object.

         This method is abstract and must be implemented
         by subclasses to interpret a database in whatever
         scheme is appropriate.
      """

      pass

