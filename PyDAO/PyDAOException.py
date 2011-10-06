#
# PyDAOException
#
# A base exception for classes in the PyDAO package.
#
# (c) August 2011 Lee Supe (lain_proliant)
# Released under the GNU General Public License, version 3.
#

class PyDAOException (Exception):
   def __init__ (self, value, cause = None):
      Exception.__init__ (self, value)
      self.value = value
      self.cause = cause

